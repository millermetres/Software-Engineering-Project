import pymysql.cursors
from events import EventsCollection, Event
from transactions import TransactionsCollection, Transaction

def getConn():
        conn = pymysql.connect(host='localhost',
            port=8889,
            user='root',
            password='root',
            db='ticketbooth',
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )

        return conn

class AccountsCollection:

    @staticmethod
    def loginCustomer(email, password):
        conn = getConn()
        cursor = conn.cursor()

        query = 'SELECT * FROM customer WHERE email = %s AND password = %s'
        cursor.execute(query, (email, password))
        data = cursor.fetchone()

        cursor.close()

        return data

    @staticmethod
    def loginOrganiser(email, password):
        conn = getConn()
        cursor = conn.cursor()

        query = 'SELECT * FROM organiser WHERE email = %s AND password = %s'
        cursor.execute(query, (email, password))
        data = cursor.fetchone()

        cursor.close()

        return data

    @staticmethod
    def findCustomer(email):
        conn = getConn()
        cursor = conn.cursor()

        query = 'SELECT * FROM customer WHERE email = %s'
        cursor.execute(query, (email))
        data = cursor.fetchone()

        cursor.close()

        if data: 
            return True
        else:
            return False

    @staticmethod
    def findOrganiser(email):
        conn = getConn()
        cursor = conn.cursor()

        query = 'SELECT * FROM organiser WHERE email = %s'
        cursor.execute(query, (email))
        data = cursor.fetchone()

        cursor.close()

        if data: 
            return True
        else:
            return False

    @staticmethod
    def addCustomer(name, email, password, user_type):
        conn = getConn()
        cursor = conn.cursor()
        query = "INSERT INTO customer (name, email, password, user_type) VALUES (%s, %s, %s, %s);"
        cursor.execute(query, (name, email, password, user_type))
        conn.commit()
        cursor.close()

    @staticmethod
    def addOrganiser(name, email, password, user_type):
        conn = getConn()
        cursor = conn.cursor()
        query = "INSERT INTO organiser (name, email, password, user_type) VALUES (%s, %s, %s, %s);"
        cursor.execute(query, (name, email, password, user_type))
        conn.commit()
        cursor.close()


class Account:
    def __init__(self, name, email, password, user_type):
        self.name = name
        self.email = email
        self.password = password
        self.user_type = user_type

    @staticmethod
    def login(email, password, user_type):
        if user_type == 'customer':
            data = AccountsCollection.loginCustomer(email, password)
            if data:
                return Customer(data['name'], data['email'], data['password'], data['user_type'])
            else:
                return None
        else:
            data = AccountsCollection.loginOrganiser(email, password)
            if data:
                return Organiser(data['name'], data['email'], data['password'], data['user_type'])
            else:
                return None

    @staticmethod
    def register(name, email, password, user_type):
        if user_type == 'customer':
            exists = AccountsCollection.findCustomer(email)
            if not exists:
                AccountsCollection.addCustomer(name, email, password, user_type)
                return Customer(name, email, password, user_type)
            else:
                return None
        else:
            exists = AccountsCollection.findOrganiser(email)
            if not exists:
                AccountsCollection.addOrganiser(name, email, password, user_type)
                return Organiser(name, email, password, user_type)
            else:
                return None
    
    @staticmethod
    def fromDict(dic):
        if dic['user_type'] == 'customer':
            return Customer(dic['name'], dic['email'], dic['password'], dic['user_type'])
        else:
            return Organiser(dic['name'], dic['email'], dic['password'], dic['user_type'])

    def searchEvents(self, location, name, date, event_type):
        events = EventsCollection.getEvents(location, name, date, event_type)
        return events


class Customer(Account):
    def __init__(self, name, email, password, user_type):
        super().__init__(name, email, password, user_type)

    def purchaseTickets(self, event, num_tix):
        transaction = Transaction(self.email, event.name, event.location, event.date, num_tix)
        TransactionsCollection.addNewTransaction(transaction)

class Organiser(Account):
    def __init__(self, name, email, password, user_type):
        super().__init__(name, email, password, user_type)

    def createEvent(self, event):
        EventsCollection.addEvent(event)