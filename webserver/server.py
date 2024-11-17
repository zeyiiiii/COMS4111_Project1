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
from flask import Flask, request, render_template, g, redirect, Response, session, abort, flash

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)



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


  #
  # render_template looks in the templates/ folder for files.
  # for example, the below file reads template/index.html
  #
  if not session.get('logged_in'):
    return render_template('login.html')
  else:
    return render_template("index.html", **context)

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
  else:
    flash('wrong password!')
  return index()

@app.route("/logout")
def logout():
  session['logged_in'] = False
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
    app.run(host=host, port=port, debug=debug, threaded=threaded)


  run()
