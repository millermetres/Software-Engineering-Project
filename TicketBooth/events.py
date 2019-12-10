import pymysql.cursors
from transactions import TransactionsCollection
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

class EventsCollection:
    @staticmethod
    def getEvents(location, name, date, event_type):
        conn = getConn()
        cursor = conn.cursor()

        locationQuery = 'location = "' + location + '" AND ' if location != '*' else ''
        nameQuery = 'name = "'+name+'" AND ' if name != '*' else ''
        dateQuery = 'date = DATE("' + date + '") AND ' if date != '*' else ''
        typeQuery = 'event_type = "' + event_type + '" AND ' if event_type != '*' else ''

        data = []
        query = ''
        if locationQuery != '' or nameQuery != '' or dateQuery != '' or typeQuery != '':
            query = 'SELECT * FROM event WHERE '+locationQuery+nameQuery+dateQuery+typeQuery
            query = query[0:len(query)-4]
            print(query)
            cursor.execute(query)
            data = cursor.fetchall()
        else:
            query = 'SELECT * FROM event'
            cursor.execute(query)
            data = cursor.fetchall()
        
        cursor.close()

        events = []
        for d in data:
            events.append(Event(d['ID'], d['name'], d['location'], d['event_type'], d['date'], d['capacity'], d['description'], d['price'], d['tickets_remaining'],  d['organiser_email'],  d['last_edited']))

        return events

    @staticmethod
    def getSingleEvent(event_id):
        conn = getConn()
        cursor = conn.cursor()
        query = 'SELECT * FROM event WHERE ID = %s'
        cursor.execute(query, (event_id))
        d = cursor.fetchone()
        cursor.close()

        if d:
            return Event(d['ID'], d['name'], d['location'], d['event_type'], d['date'], d['capacity'], d['description'], d['price'], d['tickets_remaining'], d['organiser_email'], d['last_edited'])
        else:
            return None

    @staticmethod
    def updateTicketAmount(event, num_tix):
        conn = getConn()
        cursor = conn.cursor()
        query = 'SELECT * FROM event WHERE ID = %s'
        cursor.execute(query, (event.ID))
        d = cursor.fetchone()
        new_amt = int(d['tickets_remaining']) - int(num_tix)
        query = 'UPDATE event SET tickets_remaining = %s WHERE ID = %s'
        cursor.execute(query, (new_amt, event.ID))
        conn.commit()
        cursor.close()

        return new_amt

    @staticmethod
    def addEvent(event):
        conn = getConn()
        cursor = conn.cursor()
        query = "INSERT into event (name, location, event_type, date, capacity, description, price, tickets_remaining, organiser_email) VALUES (%s, %s, %s, DATE(%s), %s, %s, %s, %s, %s)"
        cursor.execute(query, (event.name, event.location, event.event_type, event.date, event.capacity, event.description, event.price, event.tickets_remaining, event.organiser_email))
        conn.commit()
        cursor.close()

    @staticmethod
    def deleteEvent(event_id):
        conn = getConn()
        cursor = conn.cursor()
        query = 'DELETE FROM event WHERE ID = %s'
        cursor.execute(query, (event_id))
        conn.commit()
        cursor.close()
        TransactionsCollection.removeTransactions(event_id)

    @staticmethod
    def editEvent(event, n_name, n_location, n_date, n_capacity, n_price):
        conn = getConn()
        cursor = conn.cursor()
        query = 'UPDATE event SET location = %s, name = %s, date = %s, capacity = %s, price = %s, last_edited = CURRENT_TIMESTAMP WHERE ID = %s'
        cursor.execute(query, (n_location, n_name, n_date, n_capacity, n_price, event.ID))
        conn.commit()
        cursor.close()
        TransactionsCollection.editTransactions(event.ID)

class Event:
    def __init__(self, event_id, name, location, event_type, date, capacity, description, price, tickets_remaining, organiser_email, last_edited):
        self.name = name
        self.ID = event_id
        self.location = location
        self.event_type = event_type
        self.date = date
        self.capacity = capacity
        self.description = description
        self.price = price
        self.tickets_remaining = tickets_remaining
        self.organiser_email = organiser_email
        self.last_edited = last_edited

    def updateTicketAmount(self, num_tix):
        self.tickets_remaining = EventsCollection.updateTicketAmount(self, num_tix)