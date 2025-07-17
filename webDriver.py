from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import os
import time

def wait_until_input_enabled(driver, selector, timeout=30):
    element = WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
    )
    WebDriverWait(driver, timeout).until(
        lambda d: not element.get_attribute("disabled")
    )
    print(f"✅ Input #{selector} is now enabled.")

def automate_browser(output_sheets, output_sheets_backs, username, password):
    if not os.path.exists(output_sheets):
        print(f"❌ Output folder '{output_sheets}' does not exist.")
        return
    if not os.path.exists(output_sheets_backs):
        print(f"❌ Output folder '{output_sheets_backs}' does not exist.")
        return

    print("✅ Output folders found. Starting browser automation...")
    # Chrome options
    options = Options()
    options.add_argument("--incognito")
    driver = webdriver.Chrome(options=options)

    #login
    driver.get("https://www.printplaygames.com/my-account/")
    username_input = driver.find_element(By.ID, "username")
    username_input.send_keys(username)  # Replace with your username
    time.sleep(2)
    password_input = driver.find_element(By.ID, "password")
    password_input.send_keys(password)  # Replace with your password
    time.sleep(2)
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "button.woocommerce-form-login__submit"))
    ).click()
    # Load the page
    driver.get("https://www.printplaygames.com/product/poker-cards/")
    time.sleep(3)

    # Select dropdowns
    Select(driver.find_element(By.ID, "pa_print")).select_by_value("print-double-sided")
    Select(driver.find_element(By.ID, "pa_paper-stock")).select_by_value("gloss")
    print("✅ Selected print options.")
    wait_until_input_enabled(driver, "input[id^='quantity_']")
    time.sleep(5)

    #find how many sheets to upload
    folder_path = output_sheets  # Replace with your folder name
    sheet_count = sum(1 for file in os.listdir(folder_path) if file.lower().endswith(".jpg"))
    print(f"Number of .jpg files: {sheet_count}")

    try:
        for i in range(1, sheet_count + 1):

            # Wait for upload fields
            front_path = os.path.join(output_sheets, f'Sheet{i}.jpg')
            back_path = os.path.join(output_sheets_backs, f'Sheet{i}.jpg')

            if not os.path.exists(front_path) or not os.path.exists(back_path):
                print(f"❌ Missing Sheet {i}: {front_path} or {back_path}")
                continue

            print(f"📤 Uploading Sheet {i}...")

            # Upload front
            print("⏳ Waiting for Front upload input...")
            front_input = WebDriverWait(driver, 60).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[data-title^='File Upload FRONT']"))
            )
            front_input.send_keys(front_path)        
            wait_until_input_enabled(driver, "input[id^='quantity_']")
            print("Front upload Done.")
            time.sleep(2)


            # Upload back
            print("⏳ Waiting for back upload input...")
            back_input = WebDriverWait(driver, 60).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[data-title^='File Upload Back']"))
            )
            back_input.send_keys(back_path)        
            print("Back upload Done.")
            wait_until_input_enabled(driver, "input[id^='quantity_']")
            time.sleep(2)
            
            # Add to cart
            driver.find_element(By.CSS_SELECTOR, "button.single_add_to_cart_button").click()
            print(f"✅ Sheet {i} added to cart.")
            time.sleep(5)
    finally:
        if driver:
            try:
                driver.get("https://www.printplaygames.com/cart/")
                #input("Press Enter to continue to checkout...")
                time.sleep(10)
            finally:
                driver.quit()
                print("🛑 Browser closed.")
    
# Setup
script_dir = os.path.dirname(os.path.abspath(__file__))
output_sheets = os.path.join(script_dir, 'output_sheets')
output_sheets_backs = os.path.join(output_sheets, 'output_sheets_backs')

#automate_browser(output_sheets, output_sheets_backs, "Karmichael.realina@gmail.com", "CoolCat123!!")
