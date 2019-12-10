import pymysql.cursors
import smtplib, ssl

port = 465
smtp_server = "smtp.gmail.com"
sender_email = "noreply.ticketbooth@gmail.com"
password = "tbtbtb123"

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

class TicketBoothSystem:
    @staticmethod
    def sendCancelNotifications(data):

        temp_email = """\
Subject: TicketBooth Event Cancellation Notification

The following event: 
    Name: {name}
    Location: {location}
    Date: {date} 
            
has been cancelled. An amount of ${price}.00 has been refunded to your account. Thank you for using TicketBooth.

Sincerely,
The TicketBooth Team."""
        
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
            server.login(sender_email, password)
            for d in data:
                message = temp_email.format(name=d['name'], location=d['location'], date=d['date'], price=d['price'])
                server.sendmail(sender_email, d['email'], message)
