# -*- coding: utf-8 -*-

import smtplib
from twilio.rest import Client

def send_email(subject, text):
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()

    #Next, log in to the server
    server.login("jiefeijason119@gmail.com", "69580663")

    #Send the mail
    msg = 'Subject: {}\n\n{}'.format(subject, text.encode('utf-8'))
    server.sendmail("jiefeijason119@gmail.com", "weijiejason119@gmail.com", msg)
    server.sendmail("jiefeijason119@gmail.com", "dinghuanxiong@163.com", msg)
    server.sendmail("jiefeijason119@gmail.com", "shuji39@163.com", msg)
    server.quit()

def send_sms(text):
    account_sid = ''
    auth_token = ''
    client = Client(account_sid, auth_token)

    message = client.messages \
                    .create(
                         body=text,
                         from_='+12175744252',
                         to='+12178196113'
                     )

    print(message.sid)

if __name__ == '__main__':
    send_sms("this is twilio text")
    send_email("this is testing from weijie", "this is testing from weijie")