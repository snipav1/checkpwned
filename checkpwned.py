#!/usr/bin/python2

import argparse
import sys
import utils
import time
import logging
import datetime
import os



""" 
    @author: Emmanuel Hernandez

    This script will verify if an email or an email list is pwned via haveibeenpwned.com api
    
    Usage: 
        single address: python checkpwned.py -a foo@bar.com
        email list: python checkpwned.py -l emails.txt
 
"""

banner = '''

------------------------------------------------------------
        __              __                                __
  _____/ /_  ___  _____/ /______ _      ______  ___  ____/ /
 / ___/ __ \/ _ \/ ___/ //_/ __ \ | /| / / __ \/ _ \/ __  / 
/ /__/ / / /  __/ /__/ ,< / /_/ / |/ |/ / / / /  __/ /_/ /  
\___/_/ /_/\___/\___/_/|_/ .___/|__/|__/_/ /_/\___/\__,_/   
                        /_/                                 
------------------------------------------------------------
'''

if not os.geteuid() == 0:
    logging.error("\nOnly root can run this script\n")
    sys.exit("\nOnly root can run this script\n")

print banner
print('[*] Emmanuel Hernandez - @snipa.v1\n\n')

now = datetime.datetime.now()

PWNED_URL = "https://haveibeenpwned.com/api/breachedaccount/"

# Add your master email here
EMAIL = ''

LOG_NAME = 'checkpwned-{}_{}_{}-{}:{}:{}.txt'.format(now.month, now.day, now.year, now.hour, now.minute, now.second)
LOG_PATH = 'checkpwned_logs/{}'.format(LOG_NAME)

logging.basicConfig(filename=LOG_PATH,
                    filemode='w',
                    level=logging.INFO)

parser = argparse.ArgumentParser()
parser.add_argument("-a", "--address",
                    dest="address",
                    help="Check a single email address.",
                    action='store')
parser.add_argument("-l", "--list",
                    dest="usedlist",
                    help="Check a list of email addresses.",
                    action='store')
args = parser.parse_args()
address = args.address if args.address else None
usedlist = args.usedlist if args.usedlist else None
spinner = utils.Spinner()

if len(sys.argv) <= 1:
    # Add path to emails.txt
    usedlist = 'emails.txt'
    logging.info('Using: {}'.format(usedlist))


def main(address=address, usedlist=usedlist):
    send_nopwn_emails = False
    send_pwn_emails = False
    nopwn_list = []
    pwn_list = {}
    list1 = []
    list2 = []

    if address:
        sites_pwned = utils.check(address, PWNED_URL)
        print "\n"
        spinner.start()
        if not sites_pwned:
            print "[.] Congrats! {} has not been pwnd!".format(address)
            spinner.stop()
        else:
            print "[.] Oh no! Email address: {} is found within pwned sites: ".format(address)
            print sites_pwned
            spinner.stop()

    elif usedlist:

        f_file = open(str(usedlist), 'r')
        address_list = f_file.read().replace('\r', '').split('\n')
        for url in address_list:
            print '\nChecking: {}'.format(url)
            logging.info('Checking: {}'.format(url))
            spinner.start()
            time.sleep(2)
            sites_pwned = utils.check(url, PWNED_URL)
            spinner.stop()
            if not sites_pwned:
                logging.info("[.] Congrats! {} has not been pwned!\n".format(url))
                print "[.] Congrats! {} has not been pwned!\n".format(url)
                list1.append(url)
                nopwn_list.append(url)
                send_nopwn_emails = True
            else:
                logging.info("[.] Oh no! Email address: {} is found within pwned sites: ".format(url))
                for index, site in enumerate(sites_pwned, start=1):
                    logging.info('Site {} is: {}'.format(index, site))
                print "[.] Oh no! Email address: {} is found within pwned sites: ".format(url)
                for site in sites_pwned:
                    print site
                for site in sites_pwned:
                    list2.append(url+': '+site)
                pwn_list[url] = sites_pwned
                send_pwn_emails = True
    #Send emails to users who have not been pwned
    if send_nopwn_emails:
        for email in nopwn_list:
            if EMAIL in email:
                continue
            else:
                body = utils.build_nopwn_body(email)
                logging.info(utils.send_email(email, body))
    #Send emails to users who have been pwned
    if send_pwn_emails:
        for email in pwn_list:
            if EMAIL in email:
                continue
            else:
                body = utils.build_pwn_body(email, pwn_list[email])
                logging.info(utils.send_email(email, body))

    if list1 and list2:
        full_list_body = utils.build_all_list_body(list1, pwn_list)
        #Send full list to admin
        logging.info(utils.send_email(EMAIL, full_list_body))
    logging.info('[%]Done.')
    print '[%]Done.'


if __name__ == '__main__':
    main(address=address, usedlist=usedlist)
