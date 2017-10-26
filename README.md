# checkpwned

This script will verify if an email or an email list is pwned via haveibeenpwned.com api and 
send an email to target email or email list.

Setup Instructions:

1. 
        
        sudo pip install -r requirements.txt
        
    
2.      Fill in necessary email address info in utils.py and checkpwned.py

Usage: 

    single address: 
    python checkpwned.py -a foo@bar.com
        
    email list: 
    python checkpwned.py -l emails.txt

Optional:

Very useful if setup as a weekly cronjob.

1. Run command:
    
        sudo crontab -e

2. Insert cronjob:

        5 5 * * 1 /usr/bin/python /<path>/checkpwned.py -l=/<path>/emails.txt > /tmp/checkpwned.log 2>&1
