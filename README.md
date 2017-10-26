# checkpwned
@author: Emmanuel Hernandez

    This script will verify if an email or an email list is pwned via haveibeenpwned.com api and send an email to target email or email list. Very useful if setup as a cronjob as a weekly job.
    
    Usage: 
        single address: python checkpwned.py -a foo@bar.com
        email list: python checkpwned.py -l emails.txt


Setup Instructions:

1. sudo pip install -r requirements.txt
2. Fill in necessary email address info in utils.py and checkpwned.py

