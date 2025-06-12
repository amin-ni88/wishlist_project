#!/usr/bin/env python3
"""
Security Features Test Script
"""

import requests
import json
import time

API_BASE = 'http://127.0.0.1:8001'
HEADERS = {'Content-Type': 'application/json'}


def test_captcha():
    print("Testing Captcha Generation...")
    url = f"{API_BASE}/anti-bot/generate-captcha/"
    response = requests.post(url, headers=HEADERS)

    if response.status_code == 200:
        data = response.json()
        print(f"✅ Captcha: {data}")
        return True
    else:
        print(f"❌ Captcha Error: {response.status_code}")
        return False


def test_email_verification():
    print("Testing Email Verification...")
    url = f"{API_BASE}/auth/send-email-verification/"
    payload = {"email": "test@example.com", "verification_type": "LOGIN"}

    response = requests.post(url, headers=HEADERS, json=payload)
    print(f"Email Test: {response.status_code} - {response.text}")


def test_google_oauth():
    print("Testing Google OAuth URL...")
    url = f"{API_BASE}/auth/google/url/"
    response = requests.get(url, headers=HEADERS)

    if response.status_code == 200:
        data = response.json()
        print(f"✅ Google OAuth URL generated")
        return True
    else:
        print(f"❌ Google OAuth Error: {response.status_code}")
        return False


def main():
    print("🛡️ Security Test Suite Starting...")

    # Test individual features
    test_captcha()
    test_email_verification()
    test_google_oauth()

    print("🎉 Tests completed!")


if __name__ == "__main__":
    main()
