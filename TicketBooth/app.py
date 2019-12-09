from flask import render_template, Flask, request, session, url_for, redirect
import pymysql.cursors
import hashlib
import sys

app = Flask(__name__)

# conn = pymysql.connect(host='localhost',
#                        port=8889,
#                        user='root',
#                        password='root',
#                        db='ticketbooth',
#                        charset='utf8mb4',
#                        cursorclass=pymysql.cursors.DictCursor
#                     )

@app.route('/')
def hello():
    if 'user' in session:
        return redirect(url_for('home'))

    return render_template('index.html')

@app.route('/login')
def login():
    user_type = request.args.get('user_type')
    return render_template('login.html', user_type=user_type)

@app.route('/loginAction', methods=['POST'])
def loginAction():
    email = request.form['email']
    password = request.form['password']
    user_type = request.form['user_type']

    if user_type == 'customer':
        # customer = UserCollection.loginCustomer(email, password)
        customer = {
                "type": 'customer',
                "email": email,
                "password": password
        } #temp

        if customer:
            session['user'] = customer
            return redirect(url_for('home'))
        else:
            error = 'Invalid email address or password'
            return render_template('login.html', user_type=user_type, error=error)
    else:
        # organiser = UserCollection.loginOrganiser(email, password)
        organiser = {
                "type": 'organiser',
                "email": email,
                "password": password
        } #temp

        if organiser:
            session['user'] = organiser
            return redirect(url_for('home'))
        else:
            error = 'Invalid email address or password'
            return render_template('login.html', user_type=user_type, error=error)

@app.route('/signup')
def signup():
    user_type = request.args.get('user_type')
    return render_template('signup.html', user_type=user_type)

@app.route('/signupAction', methods=['POST'])
def signupAction():
    email = request.form['email']
    password = request.form['password']
    verify_password = request.form['verify_password']
    user_type = request.form['user_type']

    if(password != verify_password):
        error = 'Passwords do not match'
        return render_template('signup.html', user_type=user_type, error=error)

    if user_type == 'customer':
        # exists = UserCollection.findCustomer(email)
        exists = False #temp
        if not exists:
            # customer = UserCollection.addCustomer(email, password)
            customer = {
                "type": 'customer',
                "email": email,
                "password": password
            } #temp

            session['user'] = customer
            return redirect(url_for('home'))
        else:
            error = 'Customer account with that email already exists'
            return render_template('signup.html', user_type=user_type, error=error)
    else:
        # exists = UserCollection.findOrganiser(email)
        exists = False #temp
        if not exists:
            # organiser = UserCollection.addOrganiser(email, password)
            organiser = {
                "type": 'organiser',
                "email": email,
                "password": password
            } #temp

            session['user'] = organiser
            return redirect(url_for('home'))
        else:
            error = 'Organiser account with that email already exists'
            return render_template('signup.html', user_type=user_type, error=error)

@app.route('/logoutAction')
def logoutAction():
    session.clear()
    return redirect("/", code=302)

@app.route('/home')
def home():
    user = session['user']
    user_type = user['type']

    if user_type == 'customer':
        return render_template('custHome.html')
    else:
        return render_template('orgHome.html')

app.secret_key = 'secret :)'
if __name__ == "__main__":
    app.run('127.0.0.1', 5000, debug = True)