## Script: **Student Learning Log Interaction**

This script automates interactions with a student portal, specifically fetching the student's learning log, checking for unchecked assignments, and marking them as checked.

### Prerequisites
- **Python 3.x**
- **Requests library** (`pip install requests`)
- **BeautifulSoup library** for HTML parsing (`pip install beautifulsoup4`)

---

### 1. **Command-Line Arguments**

The script accepts the following required command-line arguments:

1. **username**: The portal username.
2. **password**: The portal password.
3. **student_id**: The student ID for which the script will fetch the learning log data.

### 2. **How to Run the Script**

To run the script, use the following syntax in your terminal:

```bash
./script_name.py <username> <password> <student_id>
```

#### Example:

```bash
./student_log_script.py john.doe@example.com securepassword123 12345678
```

Where:
- `john.doe@example.com` is the username.
- `securepassword123` is the password.
- `12345678` is the student ID.

### 3. **Functional Overview**

#### **Step-by-Step Process**

1. **Login Authentication**:  
   The script first logs into the portal using the provided username, password, and student ID. It retrieves a CSRF token from the login page and submits a POST request to authenticate.

2. **Retrieve Learning Log Period (`PRINT_LPS`)**:  
   After successful login, the script fetches the current Learning Period (LP) from the `<select>` dropdown in the HTML of the portal page. The selected option (`PRINT_LPS`) is extracted from the dropdown.

3. **Fetch Student Learning Log**:  
   The script constructs an API URL that queries the student's learning log data for the specified Learning Period (`PRINT_LPS`).

4. **Identify Unchecked Assignments**:  
   The script parses the returned HTML to find assignments that have not been marked as "checked." It looks for unchecked checkboxes in the form of `<input type="checkbox" ...>` elements.

5. **Mark Assignments as Checked**:  
   The script sends a POST request to the portal to mark any unchecked assignments as checked.

6. **Completion**:  
   Once the unchecked assignments are marked, the script prints success messages for each marked assignment.

---

### 4. **Expected Output**

As the script executes, it will print debugging information to the terminal:

1. **Fetching CSRF Token**:  
   The script will output the login URL and the extracted CSRF token.

2. **Login Status**:  
   The script will print the status of the login request.

3. **Learning Period (PRINT_LPS)**:  
   The script will extract and display the selected Learning Period.

4. **Assignment Checks**:  
   It will display all unchecked assignments and mark them as checked, printing success or failure messages for each.

Example terminal output:

```bash
[DEBUG] Fetching login page to extract CSRF token...
[DEBUG] Request URL: https://cweb.parentstudentportal.com/mod.php/public/students/activitieslog.php?portal_students_id=12345678
[DEBUG] Status Code: 200
[DEBUG] Extracted CSRF Token: abc123...
[DEBUG] Attempting to log in...
[DEBUG] Login request successful.
[DEBUG] Extracting PRINT_LPS from the select dropdown...
[DEBUG] Found selected PRINT_LPS value: 3023
[DEBUG] Fetching Student Learning Log data...
[DEBUG] Found unchecked checkbox for date: 20241004
[DEBUG] Marking 20241004 as checked...
[DEBUG] Successfully marked 20241004 as checked.
```

---

### 5. **Troubleshooting**

- **Login Failure**:  
   If the login fails (e.g., incorrect username or password), the script will exit with a message indicating the failure:
   ```bash
   [DEBUG] Login request failed. Status Code: 401
   ```

- **No Learning Period Found**:  
   If the script cannot find the `<select>` element or a selected option, it will print an error and exit:
   ```bash
   [DEBUG] Could not find the select element for PRINT_LPS.
   ```

- **No Unchecked Assignments**:  
   If no unchecked assignments are found, the script will print:
   ```bash
   [DEBUG] No unchecked checkboxes found. Exiting script.
   ```

---

### 6. **Modifying Script Configuration**

You can modify script behavior by adjusting these variables inside the script:

- `SCOPE`: The scope of the portal (e.g., 'cweb').
- `SCHOOL_YEAR`: The school year for which to fetch data (e.g., '2024 - 2025').
- `USER_AGENT`: The User-Agent string for HTTP requests.

For example, to change the school year to "2025 - 2026", modify the variable in the script:

```python
SCHOOL_YEAR = '2025 - 2026'
```

---

### 7. **Dependencies**

Ensure you have the following Python packages installed:

```bash
pip install requests beautifulsoup4
```
