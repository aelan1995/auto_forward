from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from fake_useragent import UserAgent
import time
import requests
import pyperclip  # To copy text to clipboard



class ClioAutomator:
    def __init__(self, driver_path, email, password):
        self.driver_path = driver_path
        self.email = email
        self.password = password
        self.driver = self.driver_path
    def login(self):
        try:
            self.driver.get("https://app.clio.com")
            time.sleep(15)
            self._enter_email()
            time.sleep(15)
            self._enter_password()
            time.sleep(15)
            data = self._fetch_data_from_api()
            if data:
                for item in data.get('data', []):
                    if item['display_number'] == '00003-Punzalan':
                       self._navigate_to_page_and_interact(item['id'], item['display_number'])
        finally:
            # Close the driver after a short delay to see the result
            self.driver.implicitly_wait(10)
            self.driver.quit()

    def _enter_email(self):
        # Wait for the email input to be clickable and enter the email
        email_input = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.ID, "email"))
        )
        email_input.send_keys(self.email)

        # Click the "Next" button
        next_button = self.driver.find_element(By.ID, "next")
        next_button.click()

    def _enter_password(self):
        # Wait for the password input to be clickable and enter the password
        password_input = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.ID, "password"))
        )
        password_input.send_keys(self.password)

        # Click the "Submit" button
        submit_button = self.driver.find_element(By.ID, "signin")
        submit_button.click()

    def _fetch_data_from_api(self):
        # Extract cookies from the Selenium session
        cookies = self.driver.get_cookies()
        session = requests.Session()
        for cookie in cookies:
            session.cookies.set(cookie['name'], cookie['value'])

        # Make an API request using the session with the extracted cookies
        api_url = "https://app.clio.com/api/v4/matters"  # Replace with the actual API endpoint
        response = session.get(api_url)

        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

    def _navigate_to_page_and_interact(self, matter_id, display_number_id):
        matter_url = f"https://app.clio.com/nc/#/matters/{matter_id}/communications"
        self.driver.get(matter_url)

        # Wait for the "New" button to be clickable and click it
        new_button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'New')]"))
        )
        new_button.click()

        # Wait for the "Copy matter Maildrop address" option to be clickable and click it
        copy_maildrop_option = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//a[contains(., 'Copy matter Maildrop address')]"))
        )
        copy_maildrop_option.click()

        # The copied address should now be in the clipboard
        time.sleep(1)  # Wait a moment to ensure the clipboard has the data
        data = [{
            "display_number":display_number_id,
            "maildrop_address":pyperclip.paste()
        }]

        # Save the copied address to a notepad file
        return pyperclip.paste()



# Usage
if __name__ == "__main__":
    options = Options()
    user_agent = UserAgent().random
    options.add_argument(f"user-agent={user_agent}")

    driver_path = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    email = 'allanboiebiaspunzalan@gmail.com'
    password = 'Palusutero@1995'

    clio_login_automator = ClioAutomator(driver_path, email, password)
    clio_login_automator.login()
