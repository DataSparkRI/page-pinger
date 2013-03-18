import sys, os, time, datetime, signal
import argparse, logging
import ConfigParser
import requests
from provplan_email_lib import *

parser = argparse.ArgumentParser(description='Ping urls and evaluate return status')
#parser.add_argument('-f', action="store", dest="url_file", type=str, help="Path to url config file")
parser.add_argument('-t', action="store", dest="time", type=int,  help='Time between pings')

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
lfh = logging.FileHandler(filename='/var/log/pinger.log')
formatter = logging.Formatter('%(asctime)s - %(levelname)s : %(message)s')
lfh.setFormatter(formatter)
logger.addHandler(lfh)

# get urls from conf
urlconfig = ConfigParser.SafeConfigParser()
urlconfig.read(os.path.join(os.path.dirname(__file__), 'urls.conf'))


mailer = Emailer(config_file=os.path.join(os.path.dirname(__file__),'email.conf'))
admins = mailer.config.get('emails','to').split(',')
down_list = {} # keep track of currently down urls, and counts

def make_message(url, status_code):
    mssg = 'URL {0} Responded with {1}'.format(url, status_code)
    return mssg

def notify(url, status_code):
    # send notification to admins
    logger.error(make_message(url, status_code))
    # send email to admins
    if url not in down_list:
        down_list[url] = 0
    down_list[url] += 1

    # only send down emails periodically
    if down_list[url] % 5 == 0 or down_list[url] == 1:
        for admin in admins:
            mailer.send_email(to_addresses=admin, subject='%s Response from Pinger' % url, body=make_message(url, status_code), from_address='do-not-reply@provplan.org')

def ping(url):
    r = requests.get(url)
    if r.status_code != 200:
        notify(url, r.status_code)
    else:
        # if status code is 200 and this url has been down, take it out of our
        # down list
        if url in down_list:
            del down_list[url]
        logger.info(make_message(url, r.status_code))

def signal_handler(signal, frame):
    print '...Exiting...'
    logger.info('Stopping Ping Process')
    mailer.disconnect()
    sys.exit(0)

def run():
    # register signal
    signal.signal(signal.SIGINT, signal_handler)
    args = parser.parse_args()

    logger.info('Starting Ping Process')

    while True:
        for section in urlconfig.sections():
            url = urlconfig.get(section,'url')
            ping(url)

        time.sleep(args.time)

if __name__ == '__main__':
    run()


