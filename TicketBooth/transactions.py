import pymysql.cursors
from tbsystem import TicketBoothSystem

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

class TransactionsCollection:
    @staticmethod
    def addNewTransaction(transaction):
        conn = getConn()
        cursor = conn.cursor()

        query = "INSERT into transactions (ID, email, name, location, date, quantity, price) VALUES (%s, %s, %s, %s, DATE(%s), %s, %s)"
        cursor.execute(query, (transaction.event_id, transaction.email, transaction.name, transaction.location, transaction.date, transaction.quantity, transaction.price))
        conn.commit()
        cursor.close()

        TicketBoothSystem.sendConfirmationNotification(transaction)

    @staticmethod
    def removeTransactions(event_id):
        conn = getConn()
        cursor = conn.cursor()
        query = "SELECT * from transactions WHERE ID = %s"
        cursor.execute(query, (event_id))
        data = cursor.fetchall()

        query = "DELETE from transactions WHERE ID = %s"
        cursor.execute(query, (event_id))
        conn.commit()
        cursor.close()

        TicketBoothSystem.sendCancelNotifications(data)

    @staticmethod
    def editTransactions(event_id):
        conn = getConn()
        cursor = conn.cursor()
        query = "SELECT * from transactions WHERE ID = %s"
        cursor.execute(query, (event_id))
        data = cursor.fetchall()

        query = "UPDATE transactions SET refundable = TRUE WHERE ID = %s"
        cursor.execute(query, (event_id))
        conn.commit()
        cursor.close()

        TicketBoothSystem.sendEditedEventNotification(data)
            
    @staticmethod
    def getUserTransactions(email):
        conn = getConn()
        cursor = conn.cursor()
        query = "SELECT * from transactions WHERE email = %s ORDER BY purchase_date DESC"
        cursor.execute(query, (email))
        data = cursor.fetchall()
        cursor.close()

        transactions = []
        for d in data:
            transactions.append(Transaction(d['ID'], d['email'], d['name'], d['location'], d['date'], d['quantity'], d['price'], d['purchase_date'], d['refundable'], d['requested']))
        return transactions

    @staticmethod
    def requestRefund(email, event_id, purchase_date):
        conn = getConn()
        cursor = conn.cursor()
        
        query = "UPDATE transactions SET refundable = FALSE, requested = TRUE WHERE ID = %s AND email = %s AND purchase_date = TIMESTAMP(%s)"
        cursor.execute(query, (event_id, email, purchase_date))
        conn.commit()
        cursor.close()

    @staticmethod
    def getRefundRequests():
        conn = getConn()
        cursor = conn.cursor()
        
        query = "SELECT * from transactions WHERE requested = TRUE ORDER BY purchase_date DESC"
        cursor.execute(query)
        data = cursor.fetchall()
        cursor.close()

        transactions = []
        for d in data:
            transactions.append(Transaction(d['ID'], d['email'], d['name'], d['location'], d['date'], d['quantity'], d['price'], d['purchase_date'], d['refundable'], d['requested']))
        return transactions

    @staticmethod
    def approveRefund(email, event_id, purchase_date, data):
        conn = getConn()
        cursor = conn.cursor()
        query = "DELETE from transactions WHERE ID = %s AND email = %s AND purchase_date = TIMESTAMP(%s)"
        cursor.execute(query, (event_id, email, purchase_date))
        conn.commit()
        cursor.close()
        
        TicketBoothSystem.sendRequestApprovalNotification(data)

    @staticmethod
    def getSingleTransaction(email, event_id, purchase_date):
        conn = getConn()
        cursor = conn.cursor()
        query = "SELECT * from transactions WHERE ID = %s AND email = %s AND purchase_date = TIMESTAMP(%s)"
        cursor.execute(query, (event_id, email, purchase_date))
        data = cursor.fetchone()
        return data

class Transaction:
    def __init__(self, event_id, email, name, location, date, quantity, price, purchase_date, refundable, requested):
        self.email = email
        self.event_id = event_id
        self.name = name
        self.location = location
        self.date = date
        self.quantity = quantity
        self.price = price
        self.purchase_date = purchase_date
        self.refundable = refundable
        self.requested = requested