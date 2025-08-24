from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import os
import time

def wait_until_input_enabled(driver, selector, timeout=20):
    element = WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
    )
    WebDriverWait(driver, timeout).until(
        lambda d: not element.get_attribute("disabled")
    )
    print(f"Input #{selector} is now enabled.")

def upload_with_retry(driver, input_selector, file_path, delete_prefix, max_retries=3, timeout=45):
    """
    Simplified upload with longer timeout and page reload on failure
    """
    for attempt in range(1, max_retries + 1):
        print(f"Attempt {attempt}/{max_retries}: uploading {os.path.basename(file_path)}...")

        try:
            # Find and upload file
            file_input = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, input_selector))
            )
            driver.execute_script("arguments[0].scrollIntoView({block:'center'});", file_input)
            time.sleep(1)
            file_input.send_keys(file_path)

            # Wait longer for upload completion
            WebDriverWait(driver, timeout).until(
                EC.visibility_of_element_located(
                    (By.CSS_SELECTOR, f"button.wcuf_delete_button[data-id^='{delete_prefix}']")
                )
            )
            print(f"✓ Upload complete for {os.path.basename(file_path)}")
            return True

        except Exception as e:
            print(f"Upload attempt {attempt} failed: {str(e)}")
            
            if attempt < max_retries:
                print("Will try page reload...")
                return "reload_needed"  # Signal that page reload is needed
                
    print(f"✗ Failed to upload {os.path.basename(file_path)} after {max_retries} attempts")
    return False

def reload_and_setup_page(driver, printType):
    """Reload the page and set it up again"""
    print("Reloading page and setting up options...")
    driver.get("https://www.printplaygames.com/product/poker-cards/")
    time.sleep(5)

    # Re-select dropdowns
    printings = {"Standard Gloss 285gsm: $3.46": "gloss",
                 "Plastic Paper 244gsm: $7.75": "plastic-paper-waterproof",
                 "Gloss Premium Black Corse 310gsm: $5.52": "gloss-premium-black-core",
                 "Heavy Gloss 350gsm: $5.06": "heavy-gloss-non-cored-350gsm"}
    
    Select(driver.find_element(By.ID, "pa_print")).select_by_value("print-double-sided")
    Select(driver.find_element(By.ID, "pa_paper-stock")).select_by_value(printings[printType])
    wait_until_input_enabled(driver, "input[id^='quantity_']")
    time.sleep(3)
    print("Page reloaded and configured.")

def automate_browser(output_sheets, output_sheets_backs, printType, username, password):
    if not os.path.exists(output_sheets):
        print(f"Output folder '{output_sheets}' does not exist.")
        return
    if not os.path.exists(output_sheets_backs):
        print(f"Output folder '{output_sheets_backs}' does not exist.")
        return

    print("Output folders found. Starting browser automation...")
    
    # Minimal Chrome options - only suppress the registration error
    options = Options()
    options.add_argument("--incognito")
    options.add_argument("--disable-logging")
    options.add_argument("--disable-gpu-logging")
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    
    driver = webdriver.Chrome(options=options)

    try:
        # Login
        driver.get("https://www.printplaygames.com/my-account/")
        username_input = driver.find_element(By.ID, "username")
        username_input.send_keys(username)
        time.sleep(2)
        password_input = driver.find_element(By.ID, "password")
        password_input.send_keys(password)
        time.sleep(2)
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button.woocommerce-form-login__submit"))
        ).click()
        
        # Load the page
        driver.get("https://www.printplaygames.com/product/poker-cards/")
        time.sleep(3)

        # Select dropdowns
        printings = {"Standard Gloss 285gsm: $3.46": "gloss",
                     "Plastic Paper 244gsm: $7.75": "plastic-paper-waterproof",
                     "Gloss Premium Black Corse 310gsm: $5.52": "gloss-premium-black-core",
                     "Heavy Gloss 350gsm: $5.06": "heavy-gloss-non-cored-350gsm"}
        
        Select(driver.find_element(By.ID, "pa_print")).select_by_value("print-double-sided")
        Select(driver.find_element(By.ID, "pa_paper-stock")).select_by_value(printings[printType])
        print("Selected print options.")
        wait_until_input_enabled(driver, "input[id^='quantity_']")
        time.sleep(5)

        # Count sheets
        folder_path = output_sheets
        sheet_count = sum(1 for file in os.listdir(folder_path) if file.lower().endswith(".jpg"))
        print(f"Number of .jpg files: {sheet_count}")

        for i in range(1, sheet_count + 1):
            front_path = os.path.abspath(os.path.join(output_sheets, f"Sheet{i}.jpg"))
            back_path = os.path.abspath(os.path.join(output_sheets_backs, f"Sheet{i}.jpg"))

            if not os.path.exists(front_path) or not os.path.exists(back_path):
                print(f"Missing Sheet {i} — skipping.")
                continue

            print(f"===== Uploading Sheet {i} =====")

            # Upload front with page reload on failure
            front_result = upload_with_retry(driver, "input[data-title^='File Upload FRONT']", front_path, "wcufuploadedfile_11-", timeout=60)
            
            if front_result == "reload_needed":
                reload_and_setup_page(driver, printType)
                # Retry front upload after reload
                front_result = upload_with_retry(driver, "input[data-title^='File Upload FRONT']", front_path, "wcufuploadedfile_11-", timeout=60)
            
            if not front_result:
                print(f"Skipping Sheet {i} - front upload failed after reload")
                continue

            time.sleep(3)

            # Upload back with page reload on failure
            back_result = upload_with_retry(driver, "input[data-title^='File Upload Back']", back_path, "wcufuploadedfile_77-", timeout=60)
            
            if back_result == "reload_needed":
                reload_and_setup_page(driver, printType)
                # Need to re-upload front since page was reloaded
                print("Re-uploading front after page reload...")
                front_result = upload_with_retry(driver, "input[data-title^='File Upload FRONT']", front_path, "wcufuploadedfile_11-", timeout=60)
                if not front_result:
                    print(f"Skipping Sheet {i} - front re-upload failed")
                    continue
                time.sleep(3)
                # Retry back upload
                back_result = upload_with_retry(driver, "input[data-title^='File Upload Back']", back_path, "wcufuploadedfile_77-", timeout=60)
            
            if not back_result:
                print(f"Skipping Sheet {i} - back upload failed after reload")
                continue

            time.sleep(3)
            
            # Add to cart
            try:
                WebDriverWait(driver, 30).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button.single_add_to_cart_button"))
                ).click()
                print(f"✓ Sheet {i} added to cart.")
                time.sleep(5)  # Wait a bit longer between sheets
            except Exception as e:
                print(f"Failed to add Sheet {i} to cart: {e}")

    finally:
        try:
            driver.get("https://www.printplaygames.com/cart/")
            time.sleep(10)
        finally:
            driver.quit()
            print("Browser closed.")

# Setup
script_dir = os.path.dirname(os.path.abspath(__file__))
output_sheets = os.path.join(script_dir, 'output_sheets')
output_sheets_backs = os.path.join(script_dir, 'output_sheets_backs')

#automate_browser(output_sheets, output_sheets_backs, "Standard Gloss 285gsm: $3.46", "Karmichael.realina@gmail.com", "CoolCat123!!")
