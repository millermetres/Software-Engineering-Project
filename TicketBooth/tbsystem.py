import pymysql.cursors
import smtplib, ssl
from threading import Thread

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
    def __batchCancelEmailsTask(data):
        temp_email = """\
Subject: TicketBooth Event Cancellation Notification

The following event has been cancelled: 

    Name: {name}

    Location: {location}

    Date: {date} 
                
An amount of ${price}.00 has been refunded to your account. Thank you for using TicketBooth.

Sincerely,
The TicketBooth Team."""
            
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
            server.login(sender_email, password)
            for d in data:
                message = temp_email.format(name=d['name'], location=d['location'], date=d['date'], price=d['price'])
                server.sendmail(sender_email, d['email'], message)

    def __singleConfirmationEmailTask(transaction):
        temp_email = """\
Subject: TicketBooth Ticket Purchase Confirmation

Purchase Confirmation: 

    Name: {name}

    Location: {location}

    Date: {date} 

    Number of Tickets: {quantity}

    Price: ${price}.00
    
Thank you for using TicketBooth.

Sincerely,
The TicketBooth Team."""
            
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
            server.login(sender_email, password)
            message = temp_email.format(name=transaction.name, location=transaction.location, date=transaction.date, quantity=transaction.quantity, price=transaction.price)
            server.sendmail(sender_email, transaction.email, message)

    def __batchEditedEventEmailTask(data):
        temp_email = """\
Subject: TicketBooth Event Edited Notification

The following event you are attending has been edited: 

    Name: {name}

    Location: {location}

    Date: {date} 
                
Visit the site if you wish to view the new details. If you no longer wish to attend, you are eligible for a refund of amount ${price}.00 to your account. Thank you for using TicketBooth.

Sincerely,
The TicketBooth Team."""
            
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
            server.login(sender_email, password)
            for d in data:
                message = temp_email.format(name=d['name'], location=d['location'], date=d['date'], price=d['price'])
                server.sendmail(sender_email, d['email'], message)

    def __singleRefundApprovalEmailTask(d):
        temp_email = """\
Subject: TicketBooth Refund Request Approval Notification

Your refund request for the following event has been approved: 

    Name: {name}

    Location: {location}

    Date: {date} 
                
An amount of ${price}.00 has been refunded to your account. Thank you for using TicketBooth.

Sincerely,
The TicketBooth Team."""

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
            server.login(sender_email, password)
            message = temp_email.format(name=d['name'], location=d['location'], date=d['date'], price=d['price'])
            server.sendmail(sender_email, d['email'], message)

    @classmethod
    def sendCancelNotifications(cls, data):
        process = Thread(target=cls.__batchCancelEmailsTask, args=[data])
        process.start()

    @classmethod
    def sendConfirmationNotification(cls, transaction):
        process = Thread(target=cls.__singleConfirmationEmailTask, args=[transaction])
        process.start()

    @classmethod
    def sendEditedEventNotification(cls, data):
        process = Thread(target=cls.__batchEditedEventEmailTask, args=[data])
        process.start()

    @classmethod
    def sendRequestApprovalNotification(cls, data):
        process = Thread(target=cls.__singleRefundApprovalEmailTask, args=[data])
        process.start()
