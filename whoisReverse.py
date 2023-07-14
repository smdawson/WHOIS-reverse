#!/usr/bin/env python3

from argparse import ArgumentParser
import requests
import logging


def set_log_level(args_level):
    if args_level is None:
        args_level = 0
    log_level = logging.ERROR
    if args_level == 1:
        log_level = logging.WARN
    elif args_level == 2:
        log_level = logging.INFO
    elif args_level > 2:
        log_level = logging.DEBUG
    logging.basicConfig(format='%(levelname)s: %(message)s', level=log_level)


def get_args():
    parser = ArgumentParser()
    parser.add_argument('-c', '--company', help='Search company')
    parser.add_argument('-o', '--output', help='Output file')
    parser.add_argument('-a', '--api', help='whoxy.com API key')
    parser.add_argument('-v', '--verbose', action='count')
    return parser.parse_args()


def check_balance(base_url):
    mode = {'reverse': True}
    url = '{}&account=balance'.format(base_url)
    r = requests.get(url)
    content = r.json()

    logging.info('Checking account balance')

    print(f'Live Whois Balance: {content["live_whois_balance"]}')
    print(f'Whois History Balance: {content["whois_history_balance"]}')
    print(f'Reverse Whois Balance: {content["reverse_whois_balance"]}')
    print("")

    if content['status'] == 0:
        logging.error('WHOIS lookup failed, {}'.format(content['status_reason']))
        exit()
    elif content['status'] == 1:
        if content['reverse_whois_balance'] == 0:
            logging.error('Zero API queries left. Please recharge.')
            mode['reverse'] = False
        elif content['reverse_whois_balance'] < 200:
            logging.warning('Reverse WHOIS lookup credits are getting low. Consider recharging.')
    else:
        logging.error('WHOIS lookup failed, {}'.format(content['status_reason']))
        exit()

    return mode


def reverse_whois_search(base_url, search, find, page=1, pages=9999):
    args = get_args()
    company = args.company
    while page <= pages:
        url = f'{base_url}&reverse=whois&{search}={find}&mode=mini&page={page}'
        r = requests.get(url)
        packages_json = r.json()
        total_pages = packages_json.get('total_pages', 1)
        if total_pages < pages:
            pages = total_pages
            domain_names = packages_json['search_result']
            domain_name_list = [d['domain_name'] for d in domain_names if 'domain_name' in d]
            print(f'### Domain Names for {company} ###')
            for word in domain_name_list:
                print(word)
            if args.output:
                textfile = open(args.output, 'w')
                for e in domain_name_list:
                    textfile.write(e + '\n')
                textfile.close()
        page += 1


def merge(source, destination):
    for key, value in list(source.items()):
        if isinstance(value, dict):
            # get node or create one
            node = destination.setdefault(key, {})
            merge(value, node)
        else:
            destination[key] = value
    return destination


def banner():
    print("")
    print("          _           _       ____                               ")
    print("__      _| |__   ___ (_)___  |  _ \ _____   _____ _ __ ___  ___  ")
    print("\ \ /\ / / '_ \ / _ \| / __| | |_) / _ \ \ / / _ \ '__/ __|/ _ \ ")
    print(" \ V  V /| | | | (_) | \__ \ |  _ <  __/\ V /  __/ |  \__ \  __/ ")
    print("  \_/\_/ |_| |_|\___/|_|___/ |_| \_\___| \_/ \___|_|  |___/\___| ")
    print("")
    print("         A Simple Tool for Reverse Whois on whoxy.com            ")
    print("")


def query_yes_no(question, default='yes'):
    valid = {'yes': True, 'y': True, 'ye': True, 'no': False, 'n': False}
    if default is None:
        prompt = ' [y/n] '
    elif default == 'yes':
        prompt = ' [Y/n] '
    elif default == 'no':
        prompt = ' [y/N] '
    else:
        raise ValueError('invalid default answer: {}'.format(default))

    while True:
        choice = input(question + prompt).lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            print('Please respond with \'yes\' or \'no\'(or \'y\' or \'n\').\n')


def main():
    banner()

    args = get_args()
    company = args.company
    set_log_level(args.verbose)
    api_key = args.api if args.api else "<ENTER YOUR API KEY HERE>"
    base_url = f'https://api.whoxy.com/?key={api_key}'
    print(f'API Key: {api_key}')
    check_balance(base_url)
    if company is None:
        print("")
        print('What are you trying to do burn up all my credits?')
        print('Must enter a company name')
        print('to enter a company <-c CompanyName> - if multiple words use parentheses <-c "Company Name">.')
        print("")
        exit()
    else:
        check = query_yes_no(f'Do you want to check {company}?')
        if check:
            reverse_whois_search(base_url, 'company', company)
        else:
            print("Try Again")
            exit()


if __name__ == '__main__':
    main()
