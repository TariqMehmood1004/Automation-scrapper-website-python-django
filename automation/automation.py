from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.common.by import By
from selenium import webdriver
import logging
import time


# ---------------------------
# LOGGING CONFIG
# ---------------------------
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)


driver = webdriver.Chrome()
wait = WebDriverWait(driver, 20)


def safe_send_keys(locator, value):
    for _ in range(3):
        try:
            el = wait.until(EC.element_to_be_clickable(locator))
            el.clear()
            el.send_keys(value)
            return
        except StaleElementReferenceException:
            time.sleep(1)


# ---------------------------
# GLOBAL OVERLAY REMOVAL
# ---------------------------
def remove_overlays():
    try:
        driver.execute_script("""
            let selectors = [
                '#giveaway-popup-overlay',
                '.pum-overlay',
                '.pum-container',
                '.modal',
                '.modal-backdrop',
                '.popup-overlay',
                '.newsletter-popup',
                '[class*="overlay"]',
                '[id*="overlay"]'
            ];

            selectors.forEach(sel => {
                document.querySelectorAll(sel).forEach(el => el.remove());
            });

            document.body.classList.remove('modal-open');
            document.body.style.overflow = 'auto';
        """)
        logger.info("Overlays removed (global handler)")
    except Exception:
        pass


def handle_page_state():
    # Call multiple times to defeat delayed injections
    for _ in range(3):
        remove_overlays()
        time.sleep(1)


# ---------------------------
# OPEN PRODUCT
# ---------------------------
driver.get("https://luxury-drip.com/product/jacket-147/")
handle_page_state()


# ---------------------------
# SELECT VARIATION
# ---------------------------
try:
    size = wait.until(EC.presence_of_element_located((By.NAME, "attribute_pa_size")))
    size.send_keys("L")
except:
    pass

handle_page_state()


# ---------------------------
# ADD TO CART
# ---------------------------
wait.until(EC.element_to_be_clickable(
    (By.CSS_SELECTOR, "button.single_add_to_cart_button"))
).click()

time.sleep(2)
handle_page_state()


# ---------------------------
# CHECKOUT
# ---------------------------
checkout_btn = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "a.checkout")))
driver.execute_script("arguments[0].click();", checkout_btn)

wait.until(EC.presence_of_element_located((By.ID, "billing_first_name")))
time.sleep(3)

handle_page_state()


# ---------------------------
# BILLING
# ---------------------------
safe_send_keys((By.ID, "billing_first_name"), "Tariq")
safe_send_keys((By.ID, "billing_last_name"), "Mehmood")
safe_send_keys((By.ID, "billing_address_1"), "Multan")
safe_send_keys((By.ID, "billing_city"), "Multan")
safe_send_keys((By.ID, "billing_state"), "Punjab")
safe_send_keys((By.ID, "billing_phone"), "03264848000")
safe_send_keys((By.ID, "billing_email"), "abc.123@gmail.com")

handle_page_state()


# Country
country_el = wait.until(EC.presence_of_element_located((By.ID, "billing_country")))
Select(country_el).select_by_visible_text("Pakistan")

state_el = wait.until(EC.presence_of_element_located((By.ID, "billing_state")))
Select(state_el).select_by_visible_text("Punjab")

safe_send_keys((By.ID, "billing_postcode"), "60600")

time.sleep(4)
handle_page_state()


# ---------------------------
# PLACE ORDER
# ---------------------------
place_order = wait.until(EC.element_to_be_clickable((By.ID, "place_order")))
driver.execute_script("arguments[0].scrollIntoView(true);", place_order)
time.sleep(1)

handle_page_state()

driver.execute_script("arguments[0].click();", place_order)

time.sleep(5)
print("Final URL:", driver.current_url)

input("Press ENTER to close browser...")
driver.quit()