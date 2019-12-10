import pymysql.cursors

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

        locationQuery = 'location = ' + location + ' AND ' if location != '*' else ''
        nameQuery = 'name = ' + name + ' AND ' if name != '*' else ''
        dateQuery = 'date = DATE(' + date + ') AND ' if date != '*' else ''
        typeQuery = 'event_type = ' + event_type + ' AND ' if event_type != '*' else ''

        data = []
        query = ''
        if locationQuery != '' or nameQuery != '' or dateQuery != '' or typeQuery != '':
            query = 'SELECT * FROM event WHERE '+locationQuery+nameQuery+dateQuery+typeQuery
            query = query[0:len(query)-3]
            cursor.execute(query)
            data = cursor.fetchall()
        else:
            query = 'SELECT * FROM event'
            cursor.execute(query)
            data = cursor.fetchall()
        
        cursor.close()

        events = []
        for d in data:
            events.append(Event(d['name'], d['location'], d['event_type'], d['date'], d['capacity'], d['description'], d['price'], d['tickets_remaining']))

        return events

    @staticmethod
    def getSingleEvent(name, location, date):
        conn = getConn()
        cursor = conn.cursor()
        query = 'SELECT * FROM event WHERE name = %s AND location = %s AND date = DATE(%s)'
        cursor.execute(query, (name, location, date))
        d = cursor.fetchone()
        cursor.close()

        if d:
            return Event(d['name'], d['location'], d['event_type'], d['date'], d['capacity'], d['description'], d['price'], d['tickets_remaining'])
        else:
            return None

    @staticmethod
    def updateTicketAmount(event, num_tix):
        conn = getConn()
        cursor = conn.cursor()
        query = 'SELECT * FROM event WHERE name = %s AND location = %s AND date = DATE(%s)'
        cursor.execute(query, (event.name, event.location, event.date))
        d = cursor.fetchone()
        new_amt = int(d['tickets_remaining']) - int(num_tix)
        query = 'UPDATE event SET tickets_remaining = %s WHERE name = %s AND location = %s AND date = DATE(%s)'
        cursor.execute(query, (new_amt, event.name, event.location, event.date))
        conn.commit()
        cursor.close()

        return new_amt

    @staticmethod
    def addEvent(event):
        conn = getConn()
        cursor = conn.cursor()
        query = "INSERT into event (name, location, event_type, date, capacity, description, price, tickets_remaining) VALUES (%s, %s, %s, DATE(%s), %s, %s, %s, %s)"
        cursor.execute(query, (event.name, event.location, event.event_type, event.date, event.capacity, event.description, event.price, event.tickets_remaining))
        conn.commit()
        cursor.close()



class Event:
    def __init__(self, name, location, event_type, date, capacity, description, price, tickets_remaining):
        self.name = name
        self.location = location
        self.event_type = event_type
        self.date = date
        self.capacity = capacity
        self.description = description
        self.price = price
        self.tickets_remaining = tickets_remaining

    def updateTicketAmount(self, num_tix):
        self.tickets_remaining = EventsCollection.updateTicketAmount(self, num_tix)