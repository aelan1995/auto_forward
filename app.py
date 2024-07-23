from flask import Flask, request, jsonify
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from fake_useragent import UserAgent
from webdriver_manager.chrome import ChromeDriverManager
import time
import requests
import pyperclip  # To copy text to clipboard
import json
import os

app = Flask(__name__)

class ClioAutomator:
    def __init__(self, email, password):
        self.email = email
        self.password = password
        self.driver = self._init_driver()

    def _init_driver(self):
        options = Options()
        options.add_argument("--headless")  # Run Chrome in headless mode
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        user_agent = UserAgent().random
        options.add_argument(f"user-agent={user_agent}")
        chrome_service = Service(ChromeDriverManager().install())
        return webdriver.Chrome(service=chrome_service, options=options)

    def login(self, label_name):
        try:
            self.driver.get("https://app.clio.com")
            time.sleep(5)
            self._enter_email()
            time.sleep(10)
            self._enter_password()
            time.sleep(15)
            data = self._fetch_data_from_api()
            if data:
                for item in data.get('data', []):
                    if item.get('display_number') == label_name:
                        copied_address = self._navigate_to_page_and_interact(item.get('id'), item.get('display_number'))
                        return copied_address
        except Exception as e:
            print(f"Error during login: {e}")
            return str(e)
        finally:
            self.driver.quit()

    def _enter_email(self):
        email_input = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.ID, "email"))
        )
        if email_input:
            email_input.send_keys(self.email)
            next_button = self.driver.find_element(By.ID, "next")
            if next_button:
                next_button.click()
            else:
                raise ValueError("Next button not found")
        else:
            raise ValueError("Email input element not found")

    def _enter_password(self):
        password_input = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.ID, "password"))
        )
        if password_input:
            password_input.send_keys(self.password)
            submit_button = self.driver.find_element(By.ID, "signin")
            if submit_button:
                submit_button.click()
            else:
                raise ValueError("Submit button not found")
        else:
            raise ValueError("Password input element not found")

    def _fetch_data_from_api(self):
        cookies = self.driver.get_cookies()
        session = requests.Session()
        for cookie in cookies:
            session.cookies.set(cookie['name'], cookie['value'])
        api_url = "https://app.clio.com/api/v4/matters"
        response = session.get(api_url)
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()

    def _navigate_to_page_and_interact(self, matter_id, display_number_id):
        if not matter_id or not display_number_id:
            raise ValueError("Invalid matter ID or display number ID")
        matter_url = f"https://app.clio.com/nc/#/matters/{matter_id}/communications"
        self.driver.get(matter_url)
        new_button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'New')]"))
        )
        if new_button:
            new_button.click()
            copy_maildrop_option = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//a[contains(., 'Copy matter Maildrop address')]"))
            )
            if copy_maildrop_option:
                copy_maildrop_option.click()
                time.sleep(1)
                return pyperclip.paste()
            else:
                raise ValueError("Copy Maildrop address option not found")
        else:
            raise ValueError("New button not found")


@app.route('/login', methods=['POST'])
def login():
    data = request.json
    if not data:
        return jsonify({"error": "No data received"}), 400

    label_name = data.get('label_name')
    if not label_name:
        return jsonify({"error": "Label name is required"}), 400

    # Load email and password from environment variables
    email = 'allanboiebiaspunzalan@gmail.com'
    password = 'Palusutero@1995'

    if not email or not password:
        return jsonify({"error": "Email or password not set in environment variables"}), 500

    copied_address = ClioAutomator(email, password).login(label_name)
    if not copied_address:
        return jsonify({"error": "Failed to retrieve copied address"}), 500

    return jsonify({"copied_address": copied_address})


# Test route for request.json
@app.route('/test-json', methods=['POST'])
def test_json():
    data = request.json
    if not data:
        return jsonify({"error": "No data received"}), 400
    return jsonify({"received_data": data})


if __name__ == "__main__":
    app.run(debug=True)
