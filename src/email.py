

from flask_mail import Message

from flask_mail import Mail

mail = Mail()


def send_email(to, subject, template):
    msg = Message(
        subject,
        recipients=[to],
        html=template,
        sender=('LCMS Balakong Unity Church', 'fyneos88@gmail.com')
    )
    mail.send(msg)
