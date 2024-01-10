import smtplib
from email.message import EmailMessage

def email_alert(subject, body, to):
    msg = EmailMessage()
    msg.set_content(body)
    msg['subject'] = subject
    msg['to'] = to

    user = "franciscoboudagh1@gmail.com"
    msg['from'] = user
    password = "utwzrzqzadlphhxm"

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(user, password)
    server.send_message(msg)
    server.quit()

email_alert("Detta är ett test", "Test ämne", "franciscoboudagh1@gmail.com")