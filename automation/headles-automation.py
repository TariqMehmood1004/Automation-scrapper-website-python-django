import logging
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException

# ---------------------------
# LOGGING CONFIG
# ---------------------------
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

# ---------------------------
# HEADLESS CONFIG
# ---------------------------
chrome_options = Options()
chrome_options.add_argument("--headless=new")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")

driver = webdriver.Chrome(options=chrome_options)
wait = WebDriverWait(driver, 30)

# ---------------------------
# HELPERS
# ---------------------------
def safe_send_keys(locator, value):
    for _ in range(3):
        try:
            el = wait.until(EC.presence_of_element_located(locator))
            driver.execute_script("arguments[0].scrollIntoView(true);", el)
            time.sleep(0.3)
            el.clear()
            el.send_keys(value)
            return
        except StaleElementReferenceException:
            time.sleep(1)
    logger.error(f"Failed to input field: {locator}")

def remove_overlay():
    try:
        overlay = driver.find_element(By.ID, "giveaway-popup-overlay")
        driver.execute_script("arguments[0].remove();", overlay)
        logger.info("Popup overlay removed")
    except:
        pass

def js_click(locator):
    el = wait.until(EC.presence_of_element_located(locator))
    driver.execute_script("arguments[0].scrollIntoView(true);", el)
    time.sleep(0.5)
    driver.execute_script("arguments[0].click();", el)

# ---------------------------
# FLOW START
# ---------------------------
try:
    logger.info("Opening product page")
    driver.get("https://luxury-drip.com/product/jacket-147/")

    # Select variation
    try:
        size = wait.until(EC.presence_of_element_located((By.NAME, "attribute_pa_size")))
        size.send_keys("L")
        logger.info("Selected size: L")
    except:
        logger.warning("Size selection skipped")

    # Remove popup if exists
    remove_overlay()

    # Add to cart
    logger.info("Adding product to cart")
    js_click((By.CSS_SELECTOR, "button.single_add_to_cart_button"))

    time.sleep(2)

    # Checkout
    logger.info("Navigating to checkout")
    js_click((By.CSS_SELECTOR, "a.checkout"))

    # Wait for checkout load
    wait.until(EC.presence_of_element_located((By.ID, "billing_first_name")))
    wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
    time.sleep(3)

    logger.info("Filling billing details")

    # Billing
    safe_send_keys((By.ID, "billing_first_name"), "Tariq")
    safe_send_keys((By.ID, "billing_last_name"), "Mehmood")
    safe_send_keys((By.ID, "billing_address_1"), "Multan")
    safe_send_keys((By.ID, "billing_city"), "Multan")
    safe_send_keys((By.ID, "billing_phone"), "03264848000")
    safe_send_keys((By.ID, "billing_email"), "abc.123@gmail.com")

    # Country
    country_el = wait.until(EC.presence_of_element_located((By.ID, "billing_country")))
    Select(country_el).select_by_visible_text("Pakistan")

    # State
    state_el = wait.until(EC.presence_of_element_located((By.ID, "billing_state")))
    Select(state_el).select_by_visible_text("Punjab")

    # Postcode
    safe_send_keys((By.ID, "billing_postcode"), "60600")

    time.sleep(4)

    # Place order
    logger.info("Placing order")
    js_click((By.ID, "place_order"))

    time.sleep(5)

    logger.info(f"Final URL: {driver.current_url}")

except TimeoutException as e:
    logger.error("Timeout occurred", exc_info=True)

except Exception as e:
    logger.error("Unexpected error occurred", exc_info=True)

finally:
    driver.quit()
    logger.info("Browser closed")