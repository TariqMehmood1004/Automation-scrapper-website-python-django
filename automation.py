from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException
import time
from selenium.webdriver.support.ui import Select

driver = webdriver.Chrome()
wait = WebDriverWait(driver, 30)

def safe_send_keys(locator, value):
    for _ in range(3):
        try:
            el = wait.until(EC.element_to_be_clickable(locator))
            el.clear()
            el.send_keys(value)
            return
        except StaleElementReferenceException:
            time.sleep(1)

# Open product
driver.get("https://luxury-drip.com/product/jacket-147/")

# Select variation
try:
    size = wait.until(EC.presence_of_element_located((By.NAME, "attribute_pa_size")))
    size.send_keys("L")
except:
    pass

# Add to cart
wait.until(EC.element_to_be_clickable(
    (By.CSS_SELECTOR, "button.single_add_to_cart_button"))
).click()

time.sleep(2)

# Click checkout
checkout_btn = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "a.checkout")))
driver.execute_script("arguments[0].click();", checkout_btn)

# Wait checkout load completely
wait.until(EC.presence_of_element_located((By.ID, "billing_first_name")))
time.sleep(3)  # IMPORTANT for Woo AJAX

# ---------------------------
# BILLING (SAFE INPUT)
# ---------------------------
safe_send_keys((By.ID, "billing_first_name"), "Tariq")
safe_send_keys((By.ID, "billing_last_name"), "Mehmood")
safe_send_keys((By.ID, "billing_address_1"), "Multan")
safe_send_keys((By.ID, "billing_city"), "Multan")
safe_send_keys((By.ID, "billing_state"), "Punjab")
safe_send_keys((By.ID, "billing_phone"), "03264848000")
safe_send_keys((By.ID, "billing_email"), "test@gmail.com")

# Country
# country = wait.until(EC.element_to_be_clickable((By.ID, "billing_country")))
# country.send_keys("Pakistan")

# Wait for country dropdown
country_el = wait.until(EC.presence_of_element_located((By.ID, "billing_country")))

# Use Select for standard <select>
select_country = Select(country_el)
select_country.select_by_visible_text("Pakistan")  # Exact text as in dropdown

state_el = wait.until(EC.presence_of_element_located((By.ID, "billing_state")))

# Use Select for standard <select>
select_state = Select(state_el)
select_state.select_by_visible_text("Punjab")  # Exact text as in dropdown

# billing_postcode
safe_send_keys((By.ID, "billing_postcode"), "60600")

# Wait for WooCommerce AJAX refresh
time.sleep(4)

# ---------------------------
# PLACE ORDER
# ---------------------------
place_order = wait.until(EC.element_to_be_clickable((By.ID, "place_order")))
driver.execute_script("arguments[0].scrollIntoView(true);", place_order)
time.sleep(1)
driver.execute_script("arguments[0].click();", place_order)

# Wait for redirect
time.sleep(5)
print("Final URL:", driver.current_url)

input("Press ENTER to close browser...")  # prevents auto close
driver.quit()