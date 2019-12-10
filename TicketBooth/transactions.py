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

class TransactionsCollection:
    @staticmethod
    def addNewTransaction(transaction):
        conn = getConn()
        cursor = conn.cursor()

        query = "INSERT into transactions (email, name, location, date, quantity) VALUES (%s, %s, %s, DATE(%s), %s)"
        cursor.execute(query, (transaction.email, transaction.name, transaction.location, transaction.date, transaction.quantity))
        conn.commit()
        cursor.close()


class Transaction:
    def __init__(self, email, name, location, date, quantity):
        self.email = email
        self.name = name
        self.location = location
        self.date = date
        self.quantity = quantity