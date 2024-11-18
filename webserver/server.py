#!/usr/bin/env python3

"""
Columbia W4111 Intro to databases
Example webserver

To run locally

    python server.py

Go to http://localhost:8111 in your browser


A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""

import os
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response, session, abort, flash, jsonify

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)


GOOGLE_MAPS_API_KEY = "AIzaSyC2YvwjYGUzO5sINkVXcaEcUlnOIVyRVPw"



# XXX: The Database URI should be in the format of: 
#
#     postgresql://USER:PASSWORD@<IP_OF_POSTGRE_SQL_SERVER>/<DB_NAME>
#
# For example, if you had username ewu2493, password foobar, then the following line would be:
#
#     DATABASEURI = "postgresql://ewu2493:foobar@<IP_OF_POSTGRE_SQL_SERVER>/postgres"
#
# For your convenience, we already set it to the class database

# Use the DB credentials you received by e-mail
DB_USER = "yx2950"
DB_PASSWORD = "hi02402281017"

DB_SERVER = "w4111.cisxo09blonu.us-east-1.rds.amazonaws.com"

DATABASEURI = "postgresql://"+DB_USER+":"+DB_PASSWORD+"@"+DB_SERVER+"/w4111"



#
# This line creates a database engine that knows how to connect to the URI above
#
engine = create_engine(DATABASEURI)


# Here we create a test table and insert some values in it
# engine.execute("""DROP TABLE IF EXISTS test;""")
# engine.execute("""CREATE TABLE IF NOT EXISTS test (
#   id serial,
#   name text
# );""")
# engine.execute("""INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace');""")
with engine.connect() as connection:
  connection.execute(text("DROP TABLE IF EXISTS test;"))
  connection.execute(text("""
        CREATE TABLE IF NOT EXISTS test (
            id serial,
            name text
        );
    """))
  connection.commit()
  connection.execute(text("""
        INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace');
    """))

@app.before_request
def before_request():
  """
  This function is run at the beginning of every web request 
  (every time you enter an address in the web browser).
  We use it to setup a database connection that can be used throughout the request

  The variable g is globally accessible
  """
  try:
    g.conn = engine.connect()
  except:
    print("uh oh, problem connecting to database")
    import traceback; traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception):
    """
    At the end of the web request, this makes sure to close the database connection.
    """
    try:
        g.conn.close()
    except Exception as e:
        print(f"Error during teardown: {e}")


#
# @app.route is a decorator around index() that means:
#   run index() whenever the user tries to access the "/" path using a GET request
#
# If you wanted the user to go to e.g., localhost:8111/foobar/ with POST or GET then you could use
#
#       @app.route("/foobar/", methods=["POST", "GET"])
#
# PROTIP: (the trailing / in the path is important)
# 
# see for routing: http://flask.pocoo.org/docs/0.10/quickstart/#routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
#
@app.route('/')
def index():
  """
  request is a special object that Flask provides to access web request information:

  request.method:   "GET" or "POST"
  request.form:     if the browser submitted a form, this contains the data in the form
  request.args:     dictionary of URL arguments e.g., {a:1, b:2} for http://localhost?a=1&b=2

  See its API: http://flask.pocoo.org/docs/0.10/api/#incoming-request-data
  """

  # DEBUG: this is debugging code to see what request looks like
  print(request.args)


  #
  # example of a database query
  #
  cursor = g.conn.execute(text("SELECT name FROM test"))
  names = []
  for result in cursor.mappings():
    names.append(result['name'])  # can also be accessed using result[0]
  cursor.close()

  #
  # Flask uses Jinja templates, which is an extension to HTML where you can
  # pass data to a template and dynamically generate HTML based on the data
  # (you can think of it as simple PHP)
  # documentation: https://realpython.com/blog/python/primer-on-jinja-templating/
  #
  # You can see an example template in templates/index.html
  #
  # context are the variables that are passed to the template.
  # for example, "data" key in the context variable defined below will be 
  # accessible as a variable in index.html:
  #
  #     # will print: [u'grace hopper', u'alan turing', u'ada lovelace']
  #     <div>{{data}}</div>
  #     
  #     # creates a <div> tag for each element in data
  #     # will print: 
  #     #
  #     #   <div>grace hopper</div>
  #     #   <div>alan turing</div>
  #     #   <div>ada lovelace</div>
  #     #
  #     {% for n in data %}
  #     <div>{{n}}</div>
  #     {% endfor %}
  #
  context = dict(data = names)
  
  posts = []
  page = int(request.args.get('page', 1))
  posts_per_page = 5
  offset = (page - 1) * posts_per_page
  try:
      query = text(f"SELECT * FROM surveys_fill_out LIMIT {posts_per_page} OFFSET {offset}")
      cursor = g.conn.execute(query)
      for row in cursor.mappings():
          posts.append({
              'survey_id': row['survey_id'],
              'user_id': row['user_id'],
              'meal_title': row['meal_title'],
              'time': row['time'].strftime('%Y-%m-%d %H:%M'),  # Format the datetime
              'location': row['location'],
              'menu': row['menu'],
              'number_of_people': row['number_of_people'],
              'in_return': row['in_return']
          })
      cursor.close()
      
      # Get the total number of posts for pagination controls
      total_query = text("SELECT COUNT(*) AS total FROM surveys_fill_out")
      total_cursor = g.conn.execute(total_query)
      total_posts = total_cursor.scalar()
      total_cursor.close()

      total_pages = (total_posts + posts_per_page - 1) // posts_per_page
      
  except Exception as e:
      print(f"Error fetching data from surveys_fill_out: {e}")

  #
  # render_template looks in the templates/ folder for files.
  # for example, the below file reads template/index.html
  #
  if not session.get('logged_in'):
    return render_template('login.html')
  else:
    username = session.get('username', 'Guest')
    return render_template("index.html", username=username, posts=posts, page=page, total_pages=total_pages)


def get_coordinates(address):
    """
    Use the Google Geocoding API to convert an address into geographic coordinates (lat, lng).
    """
    geocode_url = f"https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={GOOGLE_MAPS_API_KEY}"
    response = requests.get(geocode_url)
    data = response.json()

    if data.get('status') == 'OK' and data.get('results'):
        return data['results'][0]['geometry']['location']  # Returns a dictionary with 'lat' and 'lng'
    else:
        raise ValueError("Unable to geocode the address. Please check the input address.")


def fetch_posts_from_db():
    """
    Fetch posts from the database and return as a list of dictionaries.
    """
    posts = []
    try:
        cursor = g.conn.execute(text("SELECT survey_id, user_id, meal_title, time, location, menu, number_of_people, in_return FROM surveys_fill_out"))
        for row in cursor.mappings():
            posts.append({
                'survey_id': row['survey_id'],
                'user_id': row['user_id'],
                'meal_title': row['meal_title'],
                'time': row['time'].strftime('%Y-%m-%d %H:%M'),  # Format datetime for frontend
                'location': row['location'],
                'menu': row['menu'],
                'number_of_people': row['number_of_people'],
                'in_return': row['in_return']
            })
        cursor.close()
    except Exception as e:
        print(f"Database Query Error: {e}")
        raise Exception("Error fetching posts from the database.")
    return posts


def filter_nearby_posts(user_coords, posts):
    """
    Use the Google Distance Matrix API to filter posts within a 1-hour driving distance.
    """
    destinations = "|".join([post['location'] for post in posts])
    distance_matrix_url = (
        f"https://maps.googleapis.com/maps/api/distancematrix/json?origins={user_coords['lat']},{user_coords['lng']}"
        f"&destinations={destinations}&mode=driving&key={GOOGLE_MAPS_API_KEY}"
    )
    response = requests.get(distance_matrix_url)
    data = response.json()

    if data.get('status') == 'OK' and 'rows' in data:
        filtered_posts = []
        for i, element in enumerate(data['rows'][0]['elements']):
            if element['status'] == 'OK' and element['duration']['value'] <= 3600:  # 1 hour = 3600 seconds
                filtered_posts.append(posts[i])
        return filtered_posts
    else:
        raise ValueError("Error fetching driving distances. Please try again.")


@app.route('/profile/<username>')
def profile(username):
  return render_template("profile.html", username=username)


#
# This is an example of a different path.  You can see it at
# 
#     localhost:8111/another
#
# notice that the functio name is another() rather than index()
# the functions for each app.route needs to have different names
#
@app.route('/another')
def another():
  return render_template("anotherfile.html")



# Example of adding new data to the database
@app.route('/add', methods=['POST'])
def add():
  name = request.form['name']
  print(name)
  # Define the SQL command
  cmd = text('INSERT INTO test(name) VALUES (:name1), (:name2)')
  # Execute with a parameter dictionary
  g.conn.execute(cmd, {"name1": name, "name2": name})
  g.conn.commit()
  return redirect('/')


@app.route('/login', methods=['POST'])
def do_admin_login():
  POST_USERNAME = str(request.form['username'])
  POST_PASSWORD = str(request.form['password'])
  if request.form['password'] == '1' and request.form['username'] == 'admin':
    session['logged_in'] = True
    session['username'] = POST_USERNAME
  else:
    flash('wrong password!')
  return index()

@app.route("/logout")
def logout():
  session['logged_in'] = False
  session.pop('username', None)
  return index()


if __name__ == "__main__":
  import click

  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=8111, type=int)
  # def run(debug, threaded, host, port):
  #   """
  #   This function handles command line parameters.
  #   Run the server using

  #       python server.py

  #   Show the help text using

  #       python server.py --help

  #   """

  #   HOST, PORT = host, port
  #   print("running on %s:%d" % (HOST, PORT))
  #   app.secret_key = os.urandom(12)
  #   app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)
  
  def run(debug, threaded, host, port):
    """
    Run the Flask server and print all data from all tables in the database.
    """
    from sqlalchemy.exc import SQLAlchemyError
    
    # Connect to the database and print all table data
    with engine.connect() as connection:
        try:
            # Query for all table names owned by the current user
            result = connection.execute(
                text("SELECT tablename FROM pg_catalog.pg_tables WHERE tableowner = 'yx2950'")
            ).mappings()
            
            print("\n=== Database Tables and Data ===")
            for row in result:
                table_name = row["tablename"]
                print(f"\nTable: {table_name}")
                
                # Fetch all data from the table
                data_result = connection.execute(text(f"SELECT * FROM {table_name}")).mappings()
                data = [dict(data_row) for data_row in data_result]
                
                if data:
                    for record in data:
                        print(record)
                else:
                    print("No data in this table.")
        except SQLAlchemyError as e:
            print(f"Error accessing database: {str(e)}")

    # Start the Flask server
    print(f"\nRunning on {host}:{port}")
    app.secret_key = os.urandom(12)
    app.run(host=host, port=port, debug=True, threaded=threaded)


  run()
