from flask import render_template, Flask, request, session, url_for, redirect, jsonify
import pymysql.cursors
import hashlib
import sys
from accounts import Customer, Account, Organiser
from events import EventsCollection, Event

app = Flask(__name__)

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

    user = Account.login(email, password, user_type)

    if user:
        session['user'] = user.__dict__
        return redirect(url_for('home', events=None))
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
    name = request.form['name']
    password = request.form['password']
    verify_password = request.form['verify_password']
    user_type = request.form['user_type']

    if(password != verify_password):
        error = 'Passwords do not match'
        return render_template('signup.html', user_type=user_type, error=error)
    else:
        user = Account.register(name, email, password, user_type)
        if user:
            session['user'] = user.__dict__
            return redirect(url_for('home', events=None))
        else:
            error = 'Account with that email already exists'
            return render_template('signup.html', user_type=user_type, error=error)
    
@app.route('/searchAction', methods=['POST'])
def searchAction():
    location = request.form['location'] if request.form['location'] != '' else '*'
    name = request.form['name'] if request.form['name'] != '' else '*'
    date = request.form['date'] if request.form['date'] != '' else '*'
    event_type = request.form['event_type'] if request.form['event_type'] != '' else '*'

    user = Account.fromDict(session['user'])
    events = user.searchEvents(location, name, date, event_type)

    return redirect(url_for('home', events=events))


@app.route('/logoutAction')
def logoutAction():
    session.clear()
    return redirect("/", code=302)

@app.route('/home')
def home(events=None):
    if 'user' in session:
        user = Account.fromDict(session['user'])
        user_type = user.user_type
        
        if events == None:
            events = user.searchEvents('*', '*', '*', '*')

        return render_template('home.html', events=events, user_type=user_type)
    else:
        return redirect("/", code=302)

@app.route('/event')
def event():
    if 'user' in session:
        user = Account.fromDict(session['user'])
        name = request.args.get('name')
        location = request.args.get('location')
        date = request.args.get('date')
        event = EventsCollection.getSingleEvent(name, location, date)
        return render_template('event.html', event=event, user_type=user.user_type)

@app.route('/buyTicket', methods=['POST'])
def buyTicket():
    if 'user' in session:
        user = Account.fromDict(session['user'])
        name = request.form['name']
        date = request.form['date']
        location = request.form['location']
        num_tix = request.form['num_tix']

        event = EventsCollection.getSingleEvent(name, location, date)
        user.purchaseTickets(event, num_tix)
        event.updateTicketAmount(num_tix)

        url = "/event?name="+event.name+"&location="+event.location+"&date="+str(event.date)
        return redirect(url, code=302)

@app.route('/createEvent')
def createEvent():
    if 'user' in session:
        user = Account.fromDict(session['user'])
        if user.user_type == 'organiser':
            return render_template('create.html')
        else:
            return redirect(url_for('home', events=None))

@app.route('/createEventAction', methods=['POST'])
def createEventAction():
    if 'user' in session:
        user = Account.fromDict(session['user'])
        name = request.form['name']
        date = request.form['date']
        location = request.form['location']
        event_type = request.form['event_type']
        capacity = request.form['capacity'] 
        description = request.form['description']
        price = request.form['price']
        tickets_remaining = request.form['tickets_remaining']

        event = Event(name, location, event_type, date, capacity, description, price, tickets_remaining)
        user.createEvent(event)
        return redirect(url_for('home', events=None))


        


app.secret_key = 'secret :)'
if __name__ == "__main__":
    app.run('127.0.0.1', 5000, debug = True)