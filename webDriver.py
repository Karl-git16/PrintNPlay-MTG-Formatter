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

def wait_for_upload_complete(driver, prefix, timeout=20):
    # prefix examples: "wcufuploadedfile_11-" (front), "wcufuploadedfile_77-" (back)
    WebDriverWait(driver, timeout).until(
        EC.visibility_of_element_located(
            (By.CSS_SELECTOR, f"button.wcuf_delete_button[data-id^='{prefix}']")
        )
    )
def upload_with_retry(driver, input_selector, file_path, delete_prefix, max_retries=3, timeout=20):
    """
    Uploads a file and waits for the site's delete button to confirm completion.
    Retries if upload fails to complete within `timeout`.
    """
    for attempt in range(1, max_retries + 1):
        print(f"Attempt {attempt}: uploading {os.path.basename(file_path)}...")

        # Scroll into view & upload
        file_input = WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, input_selector))
        )
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", file_input)
        file_input.send_keys(file_path)

        try:
            # Wait for delete button to appear
            WebDriverWait(driver, timeout).until(
                EC.visibility_of_element_located(
                    (By.CSS_SELECTOR, f"button.wcuf_delete_button[data-id^='{delete_prefix}']")
                )
            )
            print(f"Upload complete for {os.path.basename(file_path)}.")
            return True  # success
        except:
            print(f"Upload timeout for {os.path.basename(file_path)}. Retrying...")

            # Try deleting partially uploaded file
            try:
                delete_button = driver.find_element(By.CSS_SELECTOR, f"button.wcuf_delete_button[data-id^='{delete_prefix}']")
                driver.execute_script("arguments[0].click();", delete_button)
                print("Deleted failed upload.")
                time.sleep(2)
            except:
                print("No delete button found — skipping delete step.")

    print(f"Failed to upload {os.path.basename(file_path)} after {max_retries} attempts.")
    return False

def automate_browser(output_sheets, output_sheets_backs, printType, username, password):
    if not os.path.exists(output_sheets):
        print(f"Output folder '{output_sheets}' does not exist.")
        return
    if not os.path.exists(output_sheets_backs):
        print(f"Output folder '{output_sheets_backs}' does not exist.")
        return

    print("Output folders found. Starting browser automation...")
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
    printings = {"Standard Gloss 285gsm: $3.46": "gloss",
                 "Plastic Paper 244gsm: $7.75": "plastic-paper-waterproof",
                 "Gloss Premium Black Corse 310gsm: $5.52": "gloss-premium-black-core",
                 "Heavy Gloss 350gsm: $5.06": "heavy-gloss-non-cored-350gsm"}
    
    Select(driver.find_element(By.ID, "pa_print")).select_by_value("print-double-sided")
    Select(driver.find_element(By.ID, "pa_paper-stock")).select_by_value(printings[printType])
    print("Selected print options.")
    wait_until_input_enabled(driver, "input[id^='quantity_']")
    time.sleep(5)

    #find how many sheets to upload
    folder_path = output_sheets  # Replace with your folder name
    sheet_count = sum(1 for file in os.listdir(folder_path) if file.lower().endswith(".jpg"))
    print(f"Number of .jpg files: {sheet_count}")

    try:
        for i in range(1, sheet_count + 1):

            front_path = os.path.abspath(os.path.join(output_sheets, f"Sheet{i}.jpg"))
            back_path  = os.path.abspath(os.path.join(output_sheets_backs, f"Sheet{i}.jpg"))

            if not os.path.exists(front_path) or not os.path.exists(back_path):
                print(f"Missing Sheet {i} — skipping.")
                continue

            print(f"===== Uploading Sheet {i} =====")

            if not upload_with_retry(driver, "input[data-title^='File Upload FRONT']", front_path, "wcufuploadedfile_11-"):
                continue  # skip this sheet if front fails

            if not upload_with_retry(driver, "input[data-title^='File Upload Back']", back_path, "wcufuploadedfile_77-"):
                continue  # skip this sheet if back fails

            # Add to cart
            WebDriverWait(driver, 30).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button.single_add_to_cart_button"))
            ).click()
            print(f"Sheet {i} added to cart.")
    finally:
        if driver:
            try:
                driver.get("https://www.printplaygames.com/cart/")
                #input("Press Enter to continue to checkout...")
                time.sleep(10)
            finally:
                driver.quit()
                print("Browser closed.")
    
# Setup
script_dir = os.path.dirname(os.path.abspath(__file__))
output_sheets = os.path.join(script_dir, 'output_sheets')
output_sheets_backs = os.path.join(script_dir, 'output_sheets_backs')

#automate_browser(output_sheets, output_sheets_backs, "Karmichael.realina@gmail.com", "CoolCat123!!")
