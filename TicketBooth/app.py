from flask import render_template, Flask, request, session, url_for, redirect, jsonify
import pymysql.cursors
import hashlib
import sys
from accounts import Customer, Account, Organiser
from events import EventsCollection, Event
from transactions import TransactionsCollection, Transaction

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


@app.route('/logoutAction')
def logoutAction():
    session.clear()
    return redirect("/", code=302)

@app.route('/home', methods=['GET', 'POST'])
def home(events=None):
    if 'user' in session:
        user = Account.fromDict(session['user'])
        user_type = user.user_type
        events = []

        if request.method == 'GET':
            events = user.searchEvents('*', '*', '*', '*')
        elif request.method == 'POST':
            location = request.form['location'] if request.form['location'] != '' else '*'
            name = request.form['name'] if request.form['name'] != '' else '*'
            date = request.form['date'] if request.form['date'] != '' else '*'
            event_type = request.form['event_type'] if request.form['event_type'] != '' else '*'
            events = user.searchEvents(location, name, date, event_type)

        return render_template('home.html', events=events, user=user)
    else:
        return redirect("/", code=302)

@app.route('/event')
def event():
    if 'user' in session:
        user = Account.fromDict(session['user'])
        event_id = request.args.get('id')
        event = EventsCollection.getSingleEvent(event_id)
        return render_template('event.html', event=event, user=user)

@app.route('/buyTicket', methods=['POST'])
def buyTicket():
    if 'user' in session:
        user = Account.fromDict(session['user'])
        event_id = request.form['id']
        num_tix = request.form['num_tix']

        event = EventsCollection.getSingleEvent(event_id)
        user.purchaseTickets(event, num_tix)
        event.updateTicketAmount(num_tix)

        url = "/event?id="+str(event.ID)
        return redirect(url, code=302)

@app.route('/createEvent')
def createEvent():
    if 'user' in session:
        user = Account.fromDict(session['user'])
        if user.user_type == 'organiser':
            return render_template('create.html', user=user)
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

        event = Event(None, name, location, event_type, date, capacity, description, price, tickets_remaining, user.email, None)
        user.createEvent(event)
        return redirect(url_for('home', events=None))

@app.route('/deleteEvent')
def deleteEvent():
    if 'user' in session:
        user = Account.fromDict(session['user'])
        event_id = request.args.get('id')
        user.deleteEvent(event_id)
        return redirect(url_for('home', events=None))

@app.route('/editEvent')
def editEvent():
    if 'user' in session:
        user = Account.fromDict(session['user'])
        event_id = request.args.get('id')
        event = EventsCollection.getSingleEvent(event_id)
        if user.user_type == 'organiser':
            return render_template('edit.html', user=user, event=event)
        else:
            return redirect(url_for('home', events=None))

@app.route('/editEventAction', methods=['POST'])
def editEventAction():
    if 'user' in session:
        user = Account.fromDict(session['user'])
        event_id = request.form['event_id']
        name = request.form['name']
        date = request.form['date']
        location = request.form['location']
        capacity = request.form['capacity'] 
        price = request.form['price']

        event = EventsCollection.getSingleEvent(event_id)
        user.editEvent(event, name, location, date, capacity, price)
        return redirect(url_for('home', events=None))
        
@app.route('/transactions')
def viewTransactions():
    if 'user' in session:
        user = Account.fromDict(session['user'])
        transactions = TransactionsCollection.getUserTransactions(user.email)
        return render_template('transactions.html', user=user, transactions=transactions)

@app.route('/requestRefund', methods=['POST'])
def requestRefund():
    if 'user' in session:
        user = Account.fromDict(session['user'])
        event_id = request.form['id']
        purchase_date = request.form['purchase_date']
        user.requestRefund(event_id, purchase_date)
        return redirect(url_for('viewTransactions'))


app.secret_key = 'secret :)'
if __name__ == "__main__":
    app.run('127.0.0.1', 5000, debug = True)