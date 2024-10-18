#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup
import sys
import argparse
import logging
import json

# Enable logging for requests library
logging.basicConfig(level=logging.DEBUG)
logging.getLogger("urllib3").setLevel(logging.DEBUG)

def main(username, password, student_id):
    SCOPE = 'cweb'
    SCHOOL_YEAR = '2024 - 2025'
    REPORT_TITLE = 'Student Learning Log'
    USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:131.0) Gecko/20100101 Firefox/131.0'

    # Use a session to persist cookies across requests
    session = requests.Session()

    # Step 1: Get CSRF token from login page
    print("[DEBUG] Fetching login page to extract CSRF token...")
    login_url = f"https://{SCOPE}.parentstudentportal.com/mod.php/public/students/activitieslog.php?portal_students_id={student_id}"
    
    # Fetch the login page to get the CSRF token
    login_page = session.get(login_url)
    print(f"[DEBUG] Request URL: {login_url}")
    print(f"[DEBUG] Status Code: {login_page.status_code}")
    print(f"[DEBUG] Response Cookies: {login_page.cookies.get_dict()}")
    print(f"[DEBUG] Response Content: {login_page.text[:500]}")  # Print the first 500 chars of the response

    if login_page.status_code != 401:
        print(f"[DEBUG] Failed to fetch login page. Status Code: {login_page.status_code}")
        sys.exit(1)

    soup = BeautifulSoup(login_page.text, 'html.parser')
    csrf_token = soup.find('meta', attrs={'name': 'csrf-token'})['content']
    print(f"[DEBUG] Extracted CSRF Token: {csrf_token}")

    # Step 2: Log in
    print("[DEBUG] Attempting to log in...")
    login_payload = {
        '_login': username,
        '_password': password,
        '_scope': SCOPE,
        '__csrf_token__': csrf_token,
        'lform': '1'
    }

    login_headers = {
        'User-Agent': USER_AGENT,
        'Content-Type': 'application/x-www-form-urlencoded',
        'Origin': f'https://{SCOPE}.parentstudentportal.com',
        'Referer': login_url
    }

    print(f"[DEBUG] Login Payload: {login_payload}")
    print(f"[DEBUG] Login Headers: {login_headers}")
    
    # Log in and maintain session cookies
    login_response = session.post(login_url, data=login_payload, headers=login_headers)

    print(f"[DEBUG] Status Code: {login_response.status_code}")
    print(f"[DEBUG] Response Cookies: {session.cookies.get_dict()}")  # Cookies after login
    print(f"[DEBUG] Response Content: {login_response.text[:500]}")  # Print the first 500 chars of the response

    if login_response.status_code != 200:
        print(f"[DEBUG] Login request failed. Status Code: {login_response.status_code}")
        sys.exit(1)

    soup = BeautifulSoup(login_response.text, 'html.parser')
    csrf_token = soup.find('meta', attrs={'name': 'csrf-token'})['content']
    print(f"[DEBUG] Extracted CSRF Token: {csrf_token}")


    print("[DEBUG] Extracting PRINT_LPS from the select dropdown...")
    select_element = soup.find('select', {'name': 'printlps[]'})

    if not select_element:
        print("[DEBUG] Could not find the select element for PRINT_LPS.")
        sys.exit(1)

    # Find the current Learning Period (LP)
    selected_option = select_element.find('option', selected=True)
    if selected_option:
        PRINT_LPS = selected_option['value']
        print(f"[DEBUG] Found selected PRINT_LPS value: {PRINT_LPS}")
    else:
        print("[DEBUG] No selected PRINT_LPS found. Exiting.")
        sys.exit(1)

    # Step 3: Call the API to get student learning log data
    print(f"[DEBUG] Fetching {REPORT_TITLE} data...")
    api_url = f'https://{SCOPE}.parentstudentportal.com/mod.php/public/students/activitieslog.php?action[RenderLearningLog]&schoolyear={SCHOOL_YEAR}&logtype=checkgrid&report_title={REPORT_TITLE}&report_title_override=&printlps%5B%5D={PRINT_LPS}&options%5Bshow_signature_line%5D=1&students_id={student_id}&staff_id=&lform=1'

    api_headers = {
        'User-Agent': USER_AGENT,
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'X-Requested-With': 'XMLHttpRequest',
        'Referer': login_url
    }

    print(f"[DEBUG] API URL: {api_url}")
    print(f"[DEBUG] API Headers: {api_headers}")
    
    api_response = session.get(api_url, headers=api_headers)

    print(f"[DEBUG] Status Code: {api_response.status_code}")
    print(f"[DEBUG] Response Cookies: {session.cookies.get_dict()}")  # Cookies after API call
    print(f"[DEBUG] Response Content: {api_response.text[:500]}")  # Print the first 500 chars of the response

    if api_response.status_code != 200:
        print(f"[DEBUG] Failed to fetch learning log data. Status Code: {api_response.status_code}")
        sys.exit(1)

    # Step 4: Parse the JSON response and extract HTML
    print("[DEBUG] Parsing learning log JSON response...")

    # Parse the JSON response
    response_json = api_response.json()

    # Extract HTML from the 'html' key
    if 'returnJSON' in response_json and 'html' in response_json['returnJSON']:
        html_content = response_json['returnJSON']['html']
        print(f"[DEBUG] Extracted HTML content (truncated): {html_content[:500]}")  # Print first 500 characters of the HTML
    else:
        print("[DEBUG] Failed to find 'html' key in the response JSON.")
        sys.exit(1)

    # Step 5: Parse the extracted HTML using BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')
    unchecked_checkboxes = soup.find_all('input', {'class': 'al-gridcheck', 'value': '1'})

    unchecked_dates = []
    for checkbox in unchecked_checkboxes:
        print(f"[DEBUG] Checkbox: {checkbox.attrs}")
        if 'checked' not in checkbox.attrs:
            date = checkbox['name'].split('[')[1].split(']')[0]
            unchecked_dates.append(date)
            print(f"[DEBUG] Found unchecked checkbox for date: {date}")

    if not unchecked_dates:
        print("[DEBUG] No unchecked checkboxes found. Exiting script.")
        sys.exit(0)

    print(f"[DEBUG] Found {len(unchecked_dates)} unchecked checkboxes.")

    # Step 6: Call the API to check the unchecked dates
    for date in unchecked_dates:
        print(f"[DEBUG] Attempting to mark {date} as checked...")
        
        save_payload = {
            'action[Save]': '',
            'schoolyear': SCHOOL_YEAR,
            'logtype': 'checkgrid',
            'report_title': REPORT_TITLE,
            'report_title_override': '',
            'printlps[0]': PRINT_LPS,
            'options[show_signature_line]': '1',
            'students_id': student_id,
            'staff_id': '',
            'lform': '1',
            f'assignment[{date}]': '1',
            '__csrf_token__': csrf_token
        }

        save_headers = {
            'User-Agent': USER_AGENT,
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'X-Requested-With': 'XMLHttpRequest',
            'Referer': api_url
        }

        print(f"[DEBUG] Save Payload: {save_payload}")
        print(f"[DEBUG] Save Headers: {save_headers}")
        
        save_response = session.post(login_url, data=save_payload, headers=save_headers)

        print(f"[DEBUG] Status Code: {save_response.status_code}")
        print(f"[DEBUG] Response Cookies: {session.cookies.get_dict()}")  # Cookies after save request
        print(f"[DEBUG] Response Content: {save_response.text[:500]}")  # Print the first 500 chars of the response

        if save_response.status_code == 200:
            print(f"[DEBUG] Successfully marked {date} as checked.")
        else:
            print(f"[DEBUG] Failed to mark {date} as checked. Status Code: {save_response.status_code}")

    print("[DEBUG] Script execution completed.")

if __name__ == "__main__":
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Script to interact with the Student Learning Log.')
    parser.add_argument('username', type=str, help='Your username')
    parser.add_argument('password', type=str, help='Your password')
    parser.add_argument('student_id', type=str, help='Your student ID')
    
    args = parser.parse_args()

    # Execute the main function with provided credentials
    main(args.username, args.password, args.student_id)
