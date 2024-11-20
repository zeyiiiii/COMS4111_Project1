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

from flask import Flask, request, render_template, g, redirect, Response, session, abort, flash, jsonify, redirect, url_for
from datetime import datetime

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
# #
# @app.route('/')
# def index():
#   """
#   request is a special object that Flask provides to access web request information:

#   request.method:   "GET" or "POST"
#   request.form:     if the browser submitted a form, this contains the data in the form
#   request.args:     dictionary of URL arguments e.g., {a:1, b:2} for http://localhost?a=1&b=2

#   See its API: http://flask.pocoo.org/docs/0.10/api/#incoming-request-data
#   """

#   # DEBUG: this is debugging code to see what request looks like
#   print(request.args)


#   #
#   # example of a database query
#   #
#   cursor = g.conn.execute(text("SELECT name FROM test"))
#   names = []
#   for result in cursor.mappings():
#     names.append(result['name'])  # can also be accessed using result[0]
#   cursor.close()

#   #
#   # Flask uses Jinja templates, which is an extension to HTML where you can
#   # pass data to a template and dynamically generate HTML based on the data
#   # (you can think of it as simple PHP)
#   # documentation: https://realpython.com/blog/python/primer-on-jinja-templating/
#   #
#   # You can see an example template in templates/index.html
#   #
#   # context are the variables that are passed to the template.
#   # for example, "data" key in the context variable defined below will be 
#   # accessible as a variable in index.html:
#   #
#   #     # will print: [u'grace hopper', u'alan turing', u'ada lovelace']
#   #     <div>{{data}}</div>
#   #     
#   #     # creates a <div> tag for each element in data
#   #     # will print: 
#   #     #
#   #     #   <div>grace hopper</div>
#   #     #   <div>alan turing</div>
#   #     #   <div>ada lovelace</div>
#   #     #
#   #     {% for n in data %}
#   #     <div>{{n}}</div>
#   #     {% endfor %}
#   #
#   context = dict(data = names)
#   posts = []
#   page = int(request.args.get('page', 1))
#   posts_per_page = 5
#   offset = (page - 1) * posts_per_page
#   current_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
#   try:
#       query = text(f"""
#             SELECT * FROM surveys_fill_out
#             WHERE time >= :current_date
#             ORDER BY time ASC
#             LIMIT {posts_per_page} OFFSET {offset}
#       """)
#       cursor = g.conn.execute(query, {'current_date': current_date})
#       for row in cursor.mappings():
#           posts.append({
#               'survey_id': row['survey_id'],
#               'user_id': row['user_id'],
#               'meal_title': row['meal_title'],
#               'time': row['time'].strftime('%Y-%m-%d %H:%M'),  # Format the datetime
#               'state': row['state'],
#               'city': row['city'],
#               'address': row['address'],
#               'menu': row['menu'],
#               'number_of_people': row['number_of_people'],
#               'in_return': row['in_return']
#           })
#       cursor.close()
      
#       # Get the total number of posts for pagination controls
#       total_query = text("SELECT COUNT(*) AS total FROM surveys_fill_out WHERE time >= :current_date")
#       total_cursor = g.conn.execute(total_query, {'current_date': current_date})
#       total_posts = total_cursor.scalar()
#       total_cursor.close()
#       total_pages = (total_posts + posts_per_page - 1) // posts_per_page
#   except Exception as e:
#       print(f"Error fetching data from surveys_fill_out: {e}")
#       total_pages = 1

#   #
#   # render_template looks in the templates/ folder for files.
#   # for example, the below file reads template/index.html
#   #
#   if not session.get('logged_in'):
#     return render_template('login.html')
#   else:
#     username = session.get('username', None)
#     return render_template("index.html", username=username, posts=posts, page=page, total_pages=total_pages)

# @app.route('/')
# def index():
#     username = session.get('username') if session.get('logged_in') else None
    
#     posts = []
#     page = int(request.args.get('page', 1))
#     posts_per_page = 5
#     offset = (page - 1) * posts_per_page
#     current_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

#     try:
#         query = text("""
#             SELECT 
#                 s.survey_id,
#                 s.user_id,
#                 s.meal_title,
#                 s.time,
#                 s.state,
#                 s.city,
#                 s.address,
#                 s.menu,
#                 s.in_return,
#                 u.username
#             FROM surveys_fill_out AS s
#             JOIN users AS u ON s.user_id = u.user_id
#             WHERE s.time >= :current_date
#             ORDER BY s.time ASC
#             LIMIT :limit OFFSET :offset
#         """)
#         cursor = g.conn.execute(query, {
#             'current_date': current_date,
#             'limit': posts_per_page,
#             'offset': offset
#         })

#         for row in cursor.mappings():
#             posts.append({
#                 'survey_id': row['survey_id'],
#                 'user_id': row['user_id'],
#                 'username': row['username'],
#                 'meal_title': row['meal_title'],
#                 'time': row['time'].strftime('%Y-%m-%d %H:%M'),
#                 'state': row['state'],
#                 'city': row['city'],
#                 'address': row['address'],
#                 'menu': row['menu'],
#                 'in_return': row['in_return']
#             })
#         cursor.close()

#         total_query = text("""
#             SELECT COUNT(*) AS total
#             FROM surveys_fill_out AS s
#             WHERE s.time >= :current_date
#         """)
#         total_cursor = g.conn.execute(total_query, {'current_date': current_date})
#         total_posts = total_cursor.scalar()
#         total_cursor.close()
#         total_pages = (total_posts + posts_per_page - 1) // posts_per_page

#     except Exception as e:
#         print(f"Error fetching posts: {e}")
#         total_pages = 1

#     if not username:
#         return render_template("login.html")
#     else: 
#         return render_template(
#             "index.html", username=username, posts=posts, page=page, total_pages=total_pages
#         )


@app.route('/', methods=['GET', 'POST'])
def index():
    username = session.get('username') if session.get('logged_in') else None
    posts = []
    page = int(request.args.get('page', 1))
    posts_per_page = 5
    offset = (page - 1) * posts_per_page
    current_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    query_conditions = ["s.time >= :current_date"]
    params = {'current_date': current_date, 'limit': posts_per_page, 'offset': offset}
    filters = {}
    filter_id = None

    # Handle filter logic
    if request.method == 'POST' or any(key in request.args for key in [
        'start-datetime', 'end-datetime', 'state', 'city', 'dietary-restrictions', 'meal-types', 'in-return']):
        
        # Get filters from POST or GET
        for key in ['start-datetime', 'end-datetime', 'state', 'city', 'dietary-restrictions', 'meal-types', 'in-return']:
            value = request.form.get(key) or request.args.get(key)
            if value:
                filters[key] = value
                if key == 'start-datetime':
                    query_conditions.append("s.time >= :start_time")
                    params['start_time'] = value
                elif key == 'end-datetime':
                    query_conditions.append("s.time <= :end_time")
                    params['end_time'] = value
                elif key == 'state':
                    query_conditions.append("s.state = :state")
                    params['state'] = value
                elif key == 'city':
                    query_conditions.append("s.city = :city")
                    params['city'] = value
                elif key == 'dietary-restrictions':
                    query_conditions.append("s.dietary_restriction = :dietary")
                    params['dietary'] = value
                elif key == 'meal-types':
                    query_conditions.append("s.meal_type = :meal_type")
                    params['meal_type'] = value
                elif key == 'in-return':
                    query_conditions.append("s.in_return = :in_return")
                    params['in_return'] = value

        # Insert filter into 'filters' table
        if request.method == 'POST':
          if any(filters.values()):
            try:
                insert_query = """
                    INSERT INTO filters (start_time, end_time, state, city, dietary_restriction, meal_type, in_return)
                    VALUES (:start_time, :end_time, :state, :city, :dietary_restriction, :meal_type, :in_return)
                    RETURNING filter_id
                """
                filter_params = {
                    'start_time': filters.get('start-datetime'),
                    'end_time': filters.get('end-datetime'),
                    'state': filters.get('state'),
                    'city': filters.get('city'),
                    'dietary_restriction': filters.get('dietary-restrictions'),
                    'meal_type': filters.get('meal-types'),
                    'in_return': filters.get('in-return')
                }
                print(f"Attempting to insert filter: {filter_params}")
                filter_id = g.conn.execute(text(insert_query), filter_params).scalar()
                g.conn.commit()
                print(f"Inserted filter with ID: {filter_id}")
                session['filter_id'] = filter_id
            except Exception as e:
                print(f"Error inserting filter: {e}")
          else:
            print("No valid filters provided; skipping filter insertion.")
            
          try:
              query_string = "&".join(f"{key}={value}" for key, value in filters.items())
              return redirect(f"/?{query_string}")
          except Exception as e:
              print(f"Error generating query string or redirecting: {e}")


    # Build query for posts
    where_clause = " AND ".join(query_conditions)
    base_query = f"""
        SELECT 
            s.survey_id,
            s.user_id,
            s.meal_title,
            s.time,
            s.state,
            s.city,
            s.address,
            s.menu,
            s.in_return,
            s.dietary_restriction,
            s.meal_type,
            u.username
        FROM surveys_fill_out AS s
        JOIN users AS u ON s.user_id = u.user_id
        WHERE {where_clause}
        ORDER BY s.time ASC
        LIMIT :limit OFFSET :offset
    """

    try:
        query = text(base_query)
        cursor = g.conn.execute(query, params)

        for row in cursor.mappings():
            posts.append({
                'survey_id': row['survey_id'],
                'user_id': row['user_id'],
                'username': row['username'],
                'meal_title': row['meal_title'],
                'time': row['time'].strftime('%Y-%m-%d %H:%M'),
                'state': row['state'],
                'city': row['city'],
                'address': row['address'],
                'menu': row['menu'],
                'dietary_restriction': row['dietary_restriction'],
                'meal_type': row['meal_type'],
                'in_return': row['in_return']
            })
        cursor.close()

        # Insert filter-post associations into 'filter' table
        filter_id = session.get('filter_id')
        if filter_id:
            print(f"Attempting to insert filter-post associations for filter_id: {filter_id}")
            for post in posts:
                try:
                    insert_filter_post_query = """
                        INSERT INTO filter (filter_id, post_id)
                        VALUES (:filter_id, :post_id)
                    """
                    params = {'filter_id': filter_id, 'post_id': post['survey_id']}
                    print(f"Inserting into filter table: {params}")
                    g.conn.execute(text(insert_filter_post_query), params)
                except Exception as e:
                    print(f"Error inserting filter-post association: {e}")
            try:
                g.conn.commit()
                print(f"Successfully committed filter-post associations for filter_id: {filter_id}")
            except Exception as e:
                print(f"Error committing filter-post associations: {e}")
        else:
            print("No filter_id available; skipping filter-post associations.")


        # Total posts for pagination
        total_query = f"""
            SELECT COUNT(*) AS total
            FROM surveys_fill_out AS s
            WHERE {where_clause}
        """
        total_cursor = g.conn.execute(text(total_query), params)
        total_posts = total_cursor.scalar()
        total_cursor.close()
        total_pages = (total_posts + posts_per_page - 1) // posts_per_page

    except Exception as e:
        print(f"Error fetching posts: {e}")
        total_pages = 1

    if not username:
        return render_template("login.html")
    else:
        return render_template(
            "index.html",
            username=username,
            posts=posts,
            page=page,
            total_pages=total_pages,
            filters=filters
        )


@app.route('/profile/<username>')
def profile(username):
    query = text(f"SELECT user_id FROM users WHERE username = :username")
    uid = g.conn.execute(query, {'username': username}).scalar()
    
    reviews, posts, info = [], [], []

    try:
        # Fetch reviews
        query = text(f"SELECT * FROM reviews_about WHERE user_id = :uid")
        with g.conn.execute(query, {'uid': uid}) as cursor:
            for row in cursor.mappings():
                reviews.append({
                    'rate': row['rate'],
                    'content': row['content']
                })

        # Collect user info
        query = text(f"SELECT * FROM users WHERE user_id = :uid")
        with g.conn.execute(query, {'uid': uid}) as user_info:
            for row in user_info.mappings():
                info.append({
                    'email': row.get('email', 'N/A'),
                    'tags': row.get('tags', '').split(',') if row.get('tags') else []
                })

        # Find average rate
        query = text(f"SELECT AVG(rate) FROM reviews_about WHERE user_id = :uid")
        avg_rate = g.conn.execute(query, {'uid': uid}).scalar() or 0

        # Find users with a higher average rate
        query = text("""
        SELECT COUNT(*) 
        FROM (
            SELECT user_id, AVG(rate) AS avg_rate 
            FROM reviews_about 
            GROUP BY user_id
        ) AS user_avg 
        WHERE user_avg.user_id != :uid AND user_avg.avg_rate > :avg_rate
        """)
        higher_rate = g.conn.execute(query, {'uid': uid, 'avg_rate': avg_rate}).scalar() or 0

        # Count total users
        query = text("SELECT COUNT(*) FROM users")
        total_users = g.conn.execute(query).scalar() or 0

        # Fetch posts
        query = text(f"SELECT * FROM surveys_fill_out WHERE user_id = :uid ORDER BY time DESC")
        with g.conn.execute(query, {'uid': uid}) as cursor:
            for row in cursor.mappings():
                posts.append({
                    'survey_id': row['survey_id'],
                    'user_id': row['user_id'],
                    'meal_title': row['meal_title'],
                    'time': row['time'].strftime('%Y-%m-%d %H:%M'),
                    'state': row['state'],
                    'city': row['city'],
                    'address': row['address'],
                    'menu': row['menu'],
                    'in_return': row['in_return']
                })
    except Exception as e:
        print(f"Error fetching data for profile: {e}")
        return render_template("error.html", message="An error occurred while loading the profile.")

    if session.get('logged_in'):
      return render_template(
          "profile.html",
          username=username,
          uid=uid,
          reviews=reviews,
          posts=posts,
          rating=avg_rate,
          rank=higher_rate + 1,
          total_users=total_users,
          info=info
      )
    else:
      return render_template("login.html")

@app.route('/add_review', methods=['POST'])
def add_review():
    # Get data from the form
    user_id = request.form.get('user_id') 
    content = request.form.get('content')  
    rate = request.form.get('rate') 
    

    if not user_id or not content or not rate:
        flash("All fields are required.")
        return redirect(request.referrer) 

    try:
        query = text("""
            INSERT INTO reviews_about (user_id, content, rate)
            VALUES (:user_id, :content, :rate)
        """)
        g.conn.execute(query, {'user_id': user_id, 'content': content, 'rate': int(rate)})
        g.conn.commit()
        flash("Review submitted successfully!")
        print("Review inserted successfully")
    except Exception as e:
        print(f"Error adding review: {e}")
        flash("An error occurred while submitting the review.")

    return redirect(url_for('profile', username=request.form.get('username')))


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


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        POST_USERNAME = str(request.form.get('username', '')).strip()
        POST_PASSWORD = str(request.form.get('password', '')).strip()

        query = text("SELECT * FROM users WHERE username = :username")
        user = g.conn.execute(query, {"username": POST_USERNAME}).fetchone()

        if user:
            if user[3] == POST_PASSWORD:
                session['logged_in'] = True
                session['username'] = POST_USERNAME
                return redirect(url_for('index'))
            else:
                flash("*Wrong Password!", "error")
                return redirect(url_for('login'))
        else:
            flash("*New Account: Please click sign up instead!", "error")
            return redirect(url_for('login'))

    return render_template('login.html')


@app.route("/logout")
def logout():
  session['logged_in'] = False
  session.pop('username', None)
  return index()

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        POST_USERNAME = str(request.form.get('username', '')).strip()
        POST_PASSWORD = str(request.form.get('password', '')).strip()
        POST_TAGS = str(request.form.get('tags', '')).strip()
        POST_EMAIL = str(request.form.get('email', '')).strip()

        if not POST_USERNAME:
            flash("*Username is required!", "error")
            return redirect(url_for('signup'))

        if not POST_PASSWORD:
            flash("*Password is required!", "error")
            return redirect(url_for('signup'))

        if not POST_EMAIL:
            flash("*Email is required!", "error")
            return redirect(url_for('signup'))

        query = text("SELECT * FROM users WHERE username = :username")
        user = g.conn.execute(query, {"username": POST_USERNAME}).fetchone()

        if user:
            flash("*The account already exists!", "error")
            return redirect(url_for('login'))
        else:
            insert_query = text("""
                INSERT INTO users (tags, username, password, email)
                VALUES (:tags, :username, :password, :email)
            """)

            # Execute the insert query
            g.conn.execute(insert_query, {
                "tags": POST_TAGS,
                "username": POST_USERNAME,
                "password": POST_PASSWORD,
                "email": POST_EMAIL
            })
            g.conn.commit()
            return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/survey', methods=['GET', 'POST'])
def survey():
    if request.method == 'GET':
        return render_template('survey.html')  # Replace 'survey.html' with your template name

    username = session.get('username')
    if not username:
        raise ValueError("No username found in session.")
    
    query = text("SELECT user_id FROM users WHERE username = :username")
    with engine.connect() as connection:
        result = connection.execute(query, {"username": username}).fetchone()
    if not result:
        raise ValueError("No user found with the provided username.")
    
    POST_USER_ID = result[0]
    POST_MEAL_TITLE = str(request.form.get('meal_title', '')).strip()
    
    # Handle time input
    time_str = request.form.get('time', '').strip()
    print(f"Received time input: '{time_str}'")
    if not time_str:
        return "Please provide a valid time.", 400  # Return an error response
    
    try:
        POST_TIME = datetime.strptime(time_str, '%Y-%m-%dT%H:%M')
    except ValueError:
        return "Invalid time format. Please use 'YYYY-MM-DD HH:MM'.", 400

    POST_STATE = str(request.form.get('state', '')).strip()
    POST_CITY = str(request.form.get('city', '')).strip()
    POST_ADDRESS = str(request.form.get('address', '')).strip()
    POST_MENU = str(request.form.get('menu', '')).strip()
    POST_DIETARY_RESTRICTION = str(request.form.get('dietary_restriction', '')).strip()
    POST_MEAL_TYPE = str(request.form.get('meal_type', '')).strip()
    POST_IN_RETURN = str(request.form.get('in_return', '')).strip()
    insert_query = text("""
        INSERT INTO surveys_fill_out (user_id, meal_title, time, state, city, address, menu, dietary_restriction, meal_type, in_return)
        VALUES (:user_id, :meal_title, :time, :state, :city, :address, :menu, :dietary_restriction, :meal_type, :in_return)
    """)

    # Execute the insert query
    g.conn.execute(insert_query, {
        "user_id": POST_USER_ID,
        "meal_title": POST_MEAL_TITLE,
        "time": POST_TIME,
        "state": POST_STATE,
        "city": POST_CITY,
        "address": POST_ADDRESS,
        "menu": POST_MENU,
        "dietary_restriction": POST_DIETARY_RESTRICTION,
        "meal_type": POST_MEAL_TYPE,
        "in_return": POST_IN_RETURN
    })
    g.conn.commit()
    return redirect(url_for('index'))

@app.route('/message', methods=['GET', 'POST'])
def message():
    username = session.get('username')
    if not username:
        raise ValueError("No username found in session.")

    # Fetch user ID based on username
    query = text("SELECT user_id FROM users WHERE username = :username")
    with engine.connect() as connection:
        result = connection.execute(query, {"username": username}).fetchone()

    if not result:
        raise ValueError("No user found with the provided username.")
    
    POST_USER_ID = result[0]

    if request.method == 'GET':
        search_query = request.args.get('search', '')  # Get search term from URL

        # Fetch all messages where the current user is either sender or receiver
        get_messages_query = text("""
            SELECT message_id, sender, receiver, content 
            FROM message_send
            WHERE sender = :user_id OR receiver = :user_id
            ORDER BY message_id
        """)
        with engine.connect() as connection:
            messages = connection.execute(get_messages_query, {"user_id": POST_USER_ID}).fetchall()

        # Group messages by the other user
        conversations = {}
        for message in messages:
            if message.sender != POST_USER_ID:
                other_user_id = message.sender
            else:
                other_user_id = message.receiver
            
            # Fetch the username of the other user
            get_username_query = text("""
                SELECT username FROM users WHERE user_id = :user_id
            """)
            with engine.connect() as connection:
                other_user_result = connection.execute(get_username_query, {"user_id": other_user_id}).fetchone()

            if not other_user_result:
                continue  # Skip if no username found

            other_user_username = other_user_result[0]

            if other_user_id not in conversations:
                conversations[other_user_id] = {
                    'username': other_user_username,
                    'messages': []
                }

            conversations[other_user_id]['messages'].append({
                'message_id': message.message_id,
                'content': message.content,
                'sender': message.sender,
                'receiver': message.receiver
            })

        # If a search query is provided, filter users based on the search term
        if search_query:
            search_users_query = text("""
                SELECT user_id, username
                FROM users
                WHERE username LIKE :search_query
                AND user_id != :user_id
            """)
            with engine.connect() as connection:
                search_results = connection.execute(search_users_query, {"search_query": f"%{search_query}%", "user_id": POST_USER_ID}).fetchall()
        else:
            search_results = []

        return render_template('message.html', 
                               conversations=conversations, 
                               current_user_id=POST_USER_ID, 
                               search_results=search_results, 
                               search_query=search_query)

    elif request.method == 'POST':
        content = request.form.get('content')
        receiver = request.form.get('receiver')
        
        if not content or not receiver:
            raise ValueError("Message content or receiver ID missing.")
        
        # Get the current user's ID
        query = text("SELECT user_id FROM users WHERE username = :username")
        with engine.connect() as connection:
            result = connection.execute(query, {"username": username}).fetchone()

        if not result:
            raise ValueError("No user found with the provided username.")
        
        sender = result[0]

        # Insert the message into the message_send table
        insert_message_query = text("""
            INSERT INTO message_send (sender, receiver, content) 
            VALUES (:sender, :receiver, :content)
        """)
        with engine.connect() as connection:
            connection.execute(insert_message_query, {"sender": sender, "receiver": receiver, "content": content})
            connection.commit()  # Ensure the changes are committed

        # Redirect back to the messages page after sending the message
        return redirect(url_for('message'))

def update_database():
    connection.execute(text("DROP TABLE IF EXISTS users CASCADE;"))
    print("============droped users=============")
    connection.execute(text("""
        CREATE TABLE IF NOT EXISTS users (
            user_id SERIAL PRIMARY KEY,
            tags TEXT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            email TEXT NOT NULL
        );
    """))
    connection.execute(text("""
        INSERT INTO users (tags, username, password, email) VALUES
        ('friendly, good chef', 'Lorraine Xu', '1112', 'yx2950@columbia.edu'),
        ('Chinese food', 'Zeyi Tong', '1111', 'zt2373@columbia.edu'),
        ('vegetarian', 'Bob', '1111', 'bob@gmail.com'),
        ('meat lover', 'Alice', '1111', 'alice@gmail.com'),
        ('party lover', 'Tom', '1111', 'tom@gmail.com'),
        ('Mexican food', 'Amy', '1111', 'amy@gmail.com'),
        ('good chef', 'Alex', '1111', 'alex@gmail.com'),
        ('good at doing dishes', 'Roseanne Park', '1111', 'roseanne@gmail.com'),
        ('make good pasta', 'Lisa', '1111', 'lisa@gmail.com'),
        ('open to all food', 'Jieun Lee', '1111', 'jieun@gmail.com'),
        ('can bring sauces', 'Sam', '1111', 'sam@gmail.com'),
        ('generous about adjusting menu based on your needs', 'May', '1111', 'may@gmail.com');
    """))

    connection.execute(text("DROP TABLE IF EXISTS message_send CASCADE;"))
    connection.execute(text("""
        CREATE TABLE IF NOT EXISTS message_send (
            message_id SERIAL PRIMARY KEY,
            sender int NOT NULL,
            receiver int NOT NULL,
            content text NOT NULL,
            FOREIGN KEY (sender) REFERENCES Users(user_id),
            FOREIGN KEY (receiver) REFERENCES Users(user_id)
        );
    """))
    connection.execute(text("""
        INSERT INTO message_send (sender, receiver, content) VALUES
        (1, 2, 'Hello Zeyi! I saw you reserved to come to my dinner tonight!'),
        (2, 1, 'Hi! Yes, I am excited!'),
        (1, 2, 'Do you have anything specific you want to add to the recipe?'),
        (2, 1, 'Thanks for asking! How about adding more chili?'),
        (1, 2, 'Sure! I love spicy food too!'),
        (8, 9, 'Hey Lisa! Sorry I will be late for 10 minutes!'),
        (9, 8, 'No worries Roseanne! Take your time!'),
        (8, 9, 'I am at the gate of your apartment! Can you let me in?'),
        (9, 8, 'Sorry I just saw your message!'),
        (9, 8, 'Coming downstairs!');
    """))

    connection.execute(text("DROP TABLE IF EXISTS filters CASCADE;"))
    connection.execute(text("""
        CREATE TABLE IF NOT EXISTS filters (
            filter_id SERIAL PRIMARY KEY,
            time timestamp,
            state text,
            city text,
            dietary_restriction text,
            meal_type text,
            in_return text
        );
    """))
    connection.execute(text("""
        INSERT INTO filters (time, state, city, dietary_restriction, meal_type, in_return) VALUES
        ('2024-12-01 12:00:00', 'New York', 'New York City', 'Vegetarian', 'Chinese food', 'Cash'),
        ('2024-12-02 18:30:00', 'California', 'San Francisco', 'Gluten-Free', 'Keto', 'Doing dishes'),
        ('2024-12-03 08:00:00', 'California', 'Los Angeles', 'Vegan', 'Paleo', 'Bringing ingredients'),
        ('2024-12-04 14:00:00', 'Illinois', 'Chicago', 'None', 'Italian', 'Bringing sauces'),
        ('2024-12-05 19:00:00', 'Florida', 'Miami', 'Nut-Free', 'Mexican', 'Cash'),
        ('2024-12-06 11:00:00', 'Washington', 'Seattle', 'Dairy-Free', 'Fusion', 'Doing dishes'),
        ('2024-12-07 17:00:00', 'Texas', 'Austin', 'Halal', 'Indian', 'Bringing ingredients'),
        ('2024-12-08 09:00:00', 'Massachusetts', 'Boston', 'Kosher', 'Mediterranean', 'Bringing sauces'),
        ('2024-12-09 16:00:00', 'Colorado', 'Denver', 'None', 'Seafood', 'Cash'),
        ('2024-12-10 13:00:00', 'Florida', 'Orlando', 'Paleo', 'American', 'Doing dishes');
    """))

    connection.execute(text("DROP TABLE IF EXISTS surveys_fill_out CASCADE;"))
    connection.execute(text("""
        CREATE TABLE IF NOT EXISTS surveys_fill_out (
            survey_id SERIAL PRIMARY KEY,
            user_id int NOT NULL,
            meal_title text,
            time timestamp,
            state text,
            city text,
            address text,
            menu text,
            dietary_restriction text,
            meal_type text,
            in_return text,
            FOREIGN KEY (user_id) REFERENCES users
            ON DELETE CASCADE
        );
    """))
    connection.execute(text("""
        INSERT INTO surveys_fill_out (user_id, meal_title, time, state, city, address, menu, dietary_restriction, meal_type, in_return) VALUES
        (1, 'Italian Feast', '2024-12-01 18:00:00', 'New York', 'New York City', '70 Morningside Drive', 'Pasta, Salad, Wine', 'Vegetarian', 'Chinese food', 'Cash'),
        (2, 'Chinese Banquet', '2024-12-02 19:00:00', 'New York', 'New York City', '71 Morningside Drive', 'Dumplings, Peking Duck', 'Gluten-Free', 'Keto', 'Doing dishes'),
        (3, 'Vegetarian Delight', '2024-12-03 12:30:00', 'North Carolina', 'Davidson', '209 Ridge Road', 'Tofu Stir Fry, Salad', 'Vegan', 'Paleo', 'Bringing ingredients'),
        (4, 'Meat Lovers BBQ', '2024-12-04 17:00:00', 'North Carolina', 'Davidson', '225 Baker Drive', 'BBQ Ribs, Burgers', 'None', 'Italian', 'Bringing sauces'),
        (5, 'Party Feast', '2024-12-05 21:00:00', 'New York', 'New York City', '885 6th Avenue', 'Nachos, Tacos, Beer', 'Nut-Free', 'Mexican', 'Cash'),
        (6, 'Mexican Fiesta', '2024-12-06 18:30:00', 'North Carolina', 'Davidson', '209 Ridge Road', 'Enchiladas, Guacamole', 'Dairy-Free', 'Fusion', 'Doing dishes'),
        (7, 'Chef’s Special', '2024-12-07 19:00:00', 'North Carolina', 'Davidson', '225 Baker Drive', 'Surprise Menu', 'Halal', 'Indian', 'Bringing ingredients'),
        (9, 'Pasta Night', '2024-12-08 18:00:00', 'New York', 'New York City', '70 Morningside Drive', 'Spaghetti, Lasagna', 'Kosher', 'Mediterranean', 'Bringing sauces'),
        (11, 'Professional Chef’s Choice', '2024-12-09 20:00:00', 'New York', 'New York City', '71 Morningside Drive', 'Sushi, Sashimi', 'None', 'Seafood', 'Cash'),
        (12, 'Unique Culinary Experience', '2024-12-10 17:30:00', 'North Carolina', 'Davidson', '225 Baker Drive', 'Fusion Menu', 'Paleo', 'American', 'Doing dishes'),
        (1, 'Italian Brunch', '2024-12-11 11:00:00', 'New York', 'New York City', '70 Morningside Drive', 'Bruschetta, Caprese Salad', 'Vegetarian', 'Chinese food', 'Cash'),
        (2, 'Dim Sum Special', '2024-12-12 12:00:00', 'New York', 'New York City', '71 Morningside Drive', 'Dim Sum, Spring Rolls', 'Gluten-Free', 'Keto', 'Doing dishes'),
        (3, 'Vegan Delight', '2024-12-13 13:30:00', 'North Carolina', 'Davidson', '209 Ridge Road', 'Vegan Burgers, Salad', 'Vegan', 'Paleo', 'Bringing ingredients'),
        (4, 'Steak Night', '2024-12-14 18:30:00', 'North Carolina', 'Davidson', '225 Baker Drive', 'Steak, Mashed Potatoes', 'None', 'Italian', 'Bringing sauces'),
        (5, 'Taco Tuesday', '2024-12-15 19:00:00', 'New York', 'New York City', '885 6th Avenue', 'Tacos, Salsa', 'Nut-Free', 'Mexican', 'Cash'),
        (6, 'Mexican Night', '2024-12-16 20:00:00', 'North Carolina', 'Davidson', '209 Ridge Road, NC', 'Burritos, Tacos', 'Dairy-Free', 'Fusion', 'Doing dishes'),
        (7, 'Surprise Tasting Menu', '2024-12-17 19:30:00', 'North Carolina', 'Davidson', '225 Baker Drive', 'Fried Rice', 'Halal', 'Indian', 'Bringing ingredients'),
        (9, 'Italian Delight', '2024-12-18 18:00:00', 'New York', 'New York City', '70 Morningside Drive', 'Pizza, Pasta', 'Kosher', 'Mediterranean', 'Bringing sauces'),
        (4, 'Pizza Night', '2024-12-19 18:30:00', 'New York', 'New York City', '70 Morningside Drive', 'Pizza, Salad', 'None', 'Italian', 'Bringing sauces'),
        (4, 'BBQ Night', '2024-12-20 19:00:00', 'North Carolina', 'Davidson', '225 Baker Drive', 'Grilled Chicken, Burgers', 'None', 'Seafood', 'Cash');
    """))

    connection.execute(text("DROP TABLE IF EXISTS posts_have CASCADE;"))
    connection.execute(text("""
        CREATE TABLE IF NOT EXISTS posts_have (
            post_id SERIAL PRIMARY KEY,
            user_id int NOT NULL REFERENCES users
            ON DELETE CASCADE
        );
    """))
    connection.execute(text("""
        INSERT INTO posts_have (user_id) VALUES
        (1),
        (2),
        (3),
        (4),
        (5),
        (6),
        (7),
        (9),
        (11),
        (12),
        (1),
        (2),
        (3),
        (4),
        (5),
        (6),
        (7),
        (9),
        (4),
        (4);
    """))

    connection.execute(text("DROP TABLE IF EXISTS reviews_about CASCADE;"))
    connection.execute(text("""
        CREATE TABLE IF NOT EXISTS reviews_about (
            review_id SERIAL PRIMARY KEY,
            user_id int NOT NULL,
            content text,
            rate int CHECK (rate >= 0 AND rate <= 5),
            FOREIGN KEY (user_id) REFERENCES users
            ON DELETE CASCADE
        );
    """))
    connection.execute(text("""
        INSERT INTO reviews_about (user_id, content, rate) VALUES
        (1, 'Great chef, very friendly and open to suggestions.', 5.0),
        (2, 'Expert in Chinese cuisine, highly recommended.', 4.0),
        (3, 'Great vegetarian dishes, though the variety could be improved.', 3.2),
        (4, 'Outstanding meat dishes, a must-try for meat lovers.', 4.5),
        (5, 'Good party atmosphere, but the food quality needs improvement.', 1.0),
        (6, 'Authentic Mexican food, a delightful experience.', 2.8),
        (7, 'Best chef in the area, fantastic culinary skills.', 4.9),
        (9, 'Excellent pasta dishes, highly creative.', 3.5),
        (11, 'Skilled and efficient, highly professional.', 4.0),
        (12, 'Unique flavors and great attention to detail.', 4.7),
        (1, 'Fantastic Italian cuisine, highly recommended.', 4.0),
        (2, 'A true master of Chinese culinary art.', 4.7),
        (3, 'Great variety in vegetarian dishes, very creative.', 4.0),
        (4, 'One of the best BBQ chefs, excellent grilling skills.', 4.7),
        (5, 'Good vibes, but food could be better.', 5.0),
        (6, 'Amazing experience with authentic Mexican dishes.', 4.0),
        (7, 'Top-tier chef with exceptional culinary skills.', 3.2),
        (9, 'Another great pasta experience, highly creative.', 4.5),
        (11, 'Professional and precise, very impressed.', 1.0),
        (12, 'Unique culinary approach, very inventive.', 2.8);
    """))

    connection.execute(text("DROP TABLE IF EXISTS eaters CASCADE;"))
    connection.execute(text("DROP TABLE IF EXISTS chefs CASCADE;"))

    connection.commit()

if __name__ == "__main__":
  import click

  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=8112, type=int)
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
    Run the Flask server, drop and recreate the Users table, and add data.
    """
    from sqlalchemy.exc import SQLAlchemyError
    
    # Connect to the database and manage table creation and data insertion
    with engine.connect() as connection:
    #   print("============Connected to the database successfully.==============")
    #   update_database()

    #   print("=============Database updated successfully.===============")

      # Query and print all data from all tables for verification
      try:
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
