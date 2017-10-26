import requests
import sys
import time
import threading
import smtplib
import datetime
import json
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

now = datetime.datetime.now()


class Spinner:
    busy = False
    delay = 0.1

    @staticmethod
    def spinning_cursor():
        while 1:
            for cursor in '|/-\\': yield cursor

    def __init__(self, delay=None):
        self.spinner_generator = self.spinning_cursor()
        if delay and float(delay): self.delay = delay

    def spinner_task(self):
        while self.busy:
            sys.stdout.write(next(self.spinner_generator))
            sys.stdout.flush()
            time.sleep(self.delay)
            sys.stdout.write('\b')
            sys.stdout.flush()

    def start(self):
        self.busy = True
        threading.Thread(target=self.spinner_task).start()

    def stop(self):
        self.busy = False
        time.sleep(self.delay)


def build_all_list_body(nopwn_list, pwn_list):
    new_nopwn_list = []
    new_pwn_dict = {}
    new_pwn_list = []
    for i in nopwn_list:
        new_nopwn_list.append('<br />{}<br />'.format(i))

    for k in pwn_list:
        str1 = ''
        for site in pwn_list[k]:
            str1 += ' {}, '.format(site)
            new_pwn_dict[k] = str1

    for k in new_pwn_dict:
        new_pwn_list.append('<p><br />{key} :{list}</p>'.format(key=k, list=new_pwn_dict[k]))

    html = """\
    <html>

    <head></head>

    <body>
    <p>Hi (your name),</p>
    <h4>These Emails have not been pwned:</h4>{new_nopwn_list}
    <h4>Oh no! These emails have been pwned:</h4>
    {new_pwn_list}
    <h4><br />Yours Truly,<br /> (your name) ;)</h4>
    </body>

    </html>
    """.format(new_nopwn_list=''.join(new_nopwn_list), new_pwn_list='\n'.join(new_pwn_list))
    return html


"""Returns a list of sites where email was pwned"""


def check(email, url):
    full_url = url + email
    final_data = []
    r = requests.get(full_url)
    if r:
        data = r.text.strip('[').strip(']')
        data = data.split(',')
        for site in data:
            final_data.append(site.strip('"'))
    return final_data


def build_nopwn_body(email):
    html = """\
    <html>

    <head></head>
    
    <body>
        <h4>Hi,</h4>
        <h4>Congrats! Your email: <strong><span style="color: #ff0000;">"{email}"</span></strong> has not been pwned.</h4>
        <h4>To verify you can go to: https://haveibeenpwned.com/</h4>
        <h4><br />Yours Truly,<br />(your name) ;)</h4>
    </body>
    
    </html>
    """.format(email=email)

    return html


def build_pwn_body(email, sites):
    str1 = """\
    <html>

<head></head>

<body>
    <p>Hi,
        <br />
        <br />Sorry! Your email: <span style="color: #ff0000;"><em><strong>"{email}"</strong></em></span> has been pwned. These sites have been compromised containing your email:
    """.format(email=email)
    str2 = """\
            <br />
            <br />You should change your password on each of these sites ASAP.
            <br />
            <br />To verify you can go to: https://haveibeenpwned.com/
            <br />
            <br />
            <br />Yours Truly,
            <br />(your name)</p>
    </body>

    </html>
        """.format(email=email)

    for site in sites:
        string = '<br /><strong>- {site}</strong>'.format(site=site)
        str1 += string

    html = str1 + str2
    return html


# This function sends a confirmation email and text
def send_email(currentEmail, body):
    #Fill in service account information / credentials
    gmail_user = ""
    gmail_pwd = ""
    FROM = ""
    TOEMAIL = currentEmail if type(currentEmail) is list else [currentEmail]
    SUBJECT = 'checkpwned {}'.format(now.date())
    HTML = body

    # Create message container - the correct MIME type is multipart/alternative.
    msg = MIMEMultipart('alternative')
    msg['Subject'] = SUBJECT
    msg['From'] = FROM
    msg['To'] = ",".join(TOEMAIL)

    # # Record the MIME types of both parts - text/plain and text/html.
    part2 = MIMEText(HTML, 'html')
    #
    # # Attach parts into message container.
    # # According to RFC 2046, the last part of a multipart message, in this case
    # # the HTML message, is best and preferred.
    msg.attach(part2)

    try:
        server_ssl = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        server_ssl.ehlo()  # optional, called by login()
        server_ssl.login(gmail_user, gmail_pwd)
        server_ssl.sendmail(msg['From'], msg['To'], msg.as_string())
        server_ssl.close()
        return 'Succesfully sent the Email confirmation to: {}'.format(currentEmail)
    except ValueError as e:
        return "Failed to send mail because of:\n{}".format(e)
