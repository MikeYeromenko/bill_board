from datetime import datetime
from os.path import splitext

from django.core.signing import Signer
from django.template.loader import render_to_string

from bboard.settings import ALLOWED_HOSTS

signer = Signer()


def send_activation_notification(user):
    if ALLOWED_HOSTS:
        host = f'http://{ALLOWED_HOSTS[0]}'
    else:
        host = f'http://localhost:8000'
    context = {'user': user, 'host': host, 'sign': signer.sign(user.username)}
    subject = render_to_string('email/activation_letter_subject.txt', context)
    body_text = render_to_string('email/activation_letter_body.txt', context)
    user.email_user(subject, body_text)


def get_timestamp_path(instance, filename):
    return f'{datetime.now().timestamp()}{splitext(filename)[1]}'


def send_new_comment_notification(comment):
    if ALLOWED_HOSTS:
        host = f'http://{ALLOWED_HOSTS[0]}'
    else:
        host = f'http://localhost:8000'
    user = comment.bb.author
    context = {'user': user, 'host': host, 'comment': comment}
    subject = render_to_string('email/new_comment_letter_subject.txt', context)
    body_text = render_to_string('email/new_comment_letter_body.txt', context)
    user.email_user(subject, body_text)


