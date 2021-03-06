"""
Run this script for making a number of requests to the webservice
"""

import sys
import time

import requests
from bs4 import BeautifulSoup

from util import parse_args, save_result


def sleep_until_ready(host):
    """ Waits until the host is up."""
    now = time.time()
    while True:
        try:
            requests.get(host + 'available_languages')
            return
        except Exception:
            time.sleep(1)
            sys.stdout.write('\rWaiting for {} seconds to boot up'.format(int(time.time() - now)))
            sys.stdout.flush()


def monitor_all_endpoints(host):
    """ Enables the monitoring of all endpoints."""
    url_login = host + 'dashboard/login'
    url_rules = host + 'dashboard/rules'

    # Login to the dashboard
    client = requests.session()
    html = client.get(url_login)
    parsed_html = BeautifulSoup(html.text, "html.parser")
    token = parsed_html.body.find(id='csrf_token')['value']
    login_data = dict(csrf_token=token, name='admin', password='admin', submit='Login')
    client.post(url_login, data=login_data, headers=dict(Referer=url_login))

    # Turn on monitoring for all rules
    html = client.get(url_rules)
    parsed_html = BeautifulSoup(html.text, "html.parser")
    token = parsed_html.body.find(id='csrf_token')['value']
    rules_data = {'csrf_token': token}
    for endpoint in parsed_html.findAll('table')[0].findAll('tr')[1:]:
        rules_data[endpoint.find('label')['for']] = 'on'

    client.post(url_rules, data=rules_data, headers=dict(Referer=url_rules))


def measure_execution_time(host, page, n=100):
    """ Call a certain page n times and returns the execution time (in ms) """
    data = []
    for _ in range(n):
        now = time.time()
        try:
            requests.get(host + page)
        except Exception:
            print('Can\'t open url {}{}'.format(host, page))
        data.append((time.time() - now) * 1000)
    return data


if __name__ == '__main__':
    host, name = parse_args()
    sleep_until_ready(host)
    print('\nHost is up.')
    if name == 'with_dashboard':
        print('Enabling monitoring of all endpoints...')
        monitor_all_endpoints(host)
        print('All endpoints are now monitored.')
    print('Testing the overhead now...')
    data = measure_execution_time(host, page='available_languages')
    save_result(data, name + '.txt')
    print('Results saved.')
