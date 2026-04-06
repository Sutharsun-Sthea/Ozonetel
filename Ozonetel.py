from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException
from datetime import datetime
import time
import os
from dotenv import load_dotenv

# ---------------- LOAD ENV ---------------- #
load_dotenv()

USERNAME = os.getenv("OZONETEL_USERNAME")
PASSWORD = os.getenv("OZONETEL_PASSWORD")

if not USERNAME or not PASSWORD:
    raise ValueError("❌ OZONETEL_USERNAME or OZONETEL_PASSWORD not set in .env")

# ---------------- CONFIG ---------------- #
LOGIN_URL = "https://cloudagent.ozonetel.com/give"
CALL_DETAILS_URL = "https://cloudagent.ozonetel.com/reports/call-details"
IVR_URL = "https://cloudagent.ozonetel.com/reports/ivr-feedback"
AGENT_LOGIN_URL = "https://cloudagent.ozonetel.com/reports/agent-login-details"
DOWNLOADED_REPORTS_URL = "https://cloudagent.ozonetel.com/reports/downloaded_reports"
# ---------------------------------------- #

driver = webdriver.Chrome()
driver.maximize_window()
wait = WebDriverWait(driver, 30)

# ---------------- LOGIN ---------------- #
driver.get(LOGIN_URL)

try:
    wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//span[normalize-space()='Login']")
        )
    ).click()
except:
    pass

wait.until(
    EC.presence_of_element_located(
        (By.XPATH, "//input[@placeholder='Enter User Name']")
    )
).send_keys(USERNAME)

wait.until(
    EC.presence_of_element_located(
        (By.XPATH, "//input[@placeholder='Enter Password']")
    )
).send_keys(PASSWORD)

wait.until(
    EC.element_to_be_clickable(
        (By.XPATH, "//button[normalize-space()='Login']")
    )
).click()

print("✅ Logged in")
time.sleep(8)

# ---------------- COMMON FUNCTIONS ---------------- #
def switch_to_iframe():
    driver.switch_to.default_content()
    iframes = driver.find_elements(By.TAG_NAME, "iframe")
    if iframes:
        driver.switch_to.frame(iframes[0])


def click_generate():
    generate_btn = wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//button[normalize-space()='Generate']")
        )
    )
    driver.execute_script("arguments[0].click();", generate_btn)
    print("✅ Generate clicked")
    time.sleep(20)


def click_download_csv():
    arrow_svg = wait.until(
        EC.presence_of_element_located(
            (By.XPATH,
             "//span[normalize-space()='Yesterday']/following::*[name()='svg'][2]")
        )
    )
    driver.execute_script("""
        arguments[0].closest('div').scrollIntoView({block:'center'});
        arguments[0].closest('div').click();
    """, arrow_svg)

    csv_option = wait.until(
        EC.presence_of_element_located(
            (By.XPATH,
             "//*[contains(@class,'MuiMenu') or contains(@class,'MuiPopover')]//*[contains(text(),'CSV')]")
        )
    )
    driver.execute_script("arguments[0].click();", csv_option)
    print("✅ CSV clicked")
    time.sleep(15)

# ---------------- CALL DETAILS ---------------- #
driver.get(CALL_DETAILS_URL)
time.sleep(5)
switch_to_iframe()

click_generate()
click_download_csv()

detailed_btn = wait.until(
    EC.presence_of_element_located(
        (By.XPATH, "//*[normalize-space()='Detailed View']")
    )
)
driver.execute_script("arguments[0].click();", detailed_btn)
print("✅ Detailed View clicked")
time.sleep(8)

click_generate()
click_download_csv()
print("✅ Call Details reports done")

# ---------------- IVR FEEDBACK ---------------- #
driver.get(IVR_URL)
time.sleep(5)
switch_to_iframe()

try:
    click_generate()
except:
    print("ℹ️ Generate not present for IVR")

click_download_csv()
print("✅ IVR Feedback report done")

# ---------------- AGENT LOGIN DETAILS ---------------- #
driver.get(AGENT_LOGIN_URL)
time.sleep(5)
switch_to_iframe()

try:
    click_generate()
except:
    print("ℹ️ Generate not present for Agent Login")

click_download_csv()
time.sleep(10)
click_download_csv()
print("✅ Agent Login Details CSV downloaded twice")

# ---------------- DOWNLOADED REPORTS ---------------- #
driver.get(DOWNLOADED_REPORTS_URL)

CSV_XPATH = "//label[contains(normalize-space(), 'CSV')]"

csv_labels = wait.until(
    EC.visibility_of_all_elements_located((By.XPATH, CSV_XPATH))
)

print(f"✅ Found {len(csv_labels)} CSV label(s)")

for i in range(len(csv_labels)):
    try:
        csvs = driver.find_elements(By.XPATH, CSV_XPATH)
        csv_label = csvs[i]

        driver.execute_script(
            "arguments[0].scrollIntoView({block:'center'});",
            csv_label
        )

        wait.until(EC.element_to_be_clickable(csv_label))
        driver.execute_script("arguments[0].click();", csv_label)
        print(f"✅ Clicked CSV #{i + 1}")

        time.sleep(2)

    except StaleElementReferenceException:
        print(f"🔁 Retrying CSV #{i + 1}")
        time.sleep(1)

print("✅ All CSV downloads completed")
driver.quit()