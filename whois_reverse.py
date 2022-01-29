# DO NOT JUST RUN THIS.
# EXAMINE AND JUDGE. RUN AT YOUR OWN RISK. 

from requests import get

# Modify the 3 lines below
api_key = '<whoxy.com API KEY>'
company_name = '<Company Name>'
output_file = '<Output File>'

# Do not modifiy past here
def query_yes_no(question, default='yes'):
    valid = {'yes': True, 'y': True, 'ye': True, 'no': False, 'n': False}
    if default is None:
        prompt = ' [y/n] '
    elif default == 'yes':
        prompt = ' [Y/n] '
    elif default == 'no':
        prompt = ' [y/N] '
    else:
        raise ValueError(f'invalid default answer: {default}')
    while True:
        choice = input(question + prompt).lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            print('Please respond with \'yes\' or \'no\'(or \'y\' or \'n\').\n')


base_url = f'https://api.whoxy.com/?key={api_key}'
url = f'{base_url}&account=balance'
data = get(url).json()
print('Checking account balance')
if data['status'] == 0:
    print(f'WHOIS lookup failed {data["status_reason"]}')
    exit()
elif data['reverse_whois_balance'] == 0:
    print('Reverse WHOIS credits have been exhausted, reload account.')
    exit()
elif data['reverse_whois_balance'] > 0:
    print(f'Account balance is {data["reverse_whois_balance"]} credits')
else:
    print(f'WHOIS lookup failed {data["status_reason"]}')
    exit()


check = query_yes_no(f'Do you want reverse WHOIS for "{company_name}"')
if check:
    domains = {}
    page = 1
    pages = 9999
    while page <= pages:
        url = f'{base_url}&reverse=whois&company={company_name}&mode=mini&page={page}'
        data = get(url).json()
        total_pages = data.get('total_pages', 1)
        if total_pages < pages:
            pages = total_pages
        if data.get('status', 0) == 1 and data.get('total_results', 0) > 0:
            for result in data['search_result']:
                domain = result.get('domain_name', '')
                domains[domain] = True
        page += 1
        textfile = open(output_file, 'w')
        for d in domains:
            textfile.write(d + '\n')
        textfile.close()
        check = False
else:
    check = False
