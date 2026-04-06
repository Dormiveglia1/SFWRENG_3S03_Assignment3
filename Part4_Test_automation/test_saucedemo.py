import pytest
from playwright.sync_api import sync_playwright, expect

BASE_URL = "https://www.saucedemo.com"

VALID_USER = "standard_user"
LOCKED_USER = "locked_out_user"
PASSWORD = "secret_sauce"

@pytest.fixture(scope="session")
def browser():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        yield browser
        browser.close()

@pytest.fixture(autouse=True)
def page(browser):
    context = browser.new_context()
    page = context.new_page()
    page.goto(BASE_URL)
    yield page
    context.close()

def login(page, username=VALID_USER, password=PASSWORD):
    page.fill("#user-name", username)
    page.fill("#password", password)
    page.click("#login-button")


# ══════════════════════════════════════════════════════════════
#  BRANCH 1 — Login
# ══════════════════════════════════════════════════════════════

# TC-SC-01
def test_login_page_elements_visible(page):
    expect(page.locator("#user-name")).to_be_visible()
    expect(page.locator("#password")).to_be_visible()
    expect(page.locator("#login-button")).to_be_visible()

# TC-SC-02
def test_successful_login(page):
    login(page)
    expect(page).to_have_url(f"{BASE_URL}/inventory.html")
    expect(page.locator(".title")).to_have_text("Products")

# TC-SC-03
def test_login_wrong_password(page):
    login(page, password="wrongpass")
    expect(page.locator("[data-test='error']")).to_be_visible()
    expect(page.locator("[data-test='error']")).to_contain_text("Username and password do not match")

# TC-SC-04
def test_login_empty_username(page):
    page.fill("#password", PASSWORD)
    page.click("#login-button")
    expect(page.locator("[data-test='error']")).to_contain_text("Username is required")

# TC-SC-05
def test_login_empty_password(page):
    page.fill("#user-name", VALID_USER)
    page.click("#login-button")
    expect(page.locator("[data-test='error']")).to_contain_text("Password is required")

# TC-SC-06
def test_login_locked_user(page):
    login(page, username=LOCKED_USER)
    expect(page.locator("[data-test='error']")).to_contain_text("Sorry, this user has been locked out")


# ══════════════════════════════════════════════════════════════
#  BRANCH 2 — Products page
# ══════════════════════════════════════════════════════════════

# TC-SC-07
def test_products_page_shows_items(page):
    login(page)
    items = page.locator(".inventory_item")
    expect(items).to_have_count(6)

# TC-SC-08
def test_sort_by_name_az(page):
    login(page)
    page.select_option(".product_sort_container", "az")
    names = page.locator(".inventory_item_name").all_text_contents()
    assert names == sorted(names)

# TC-SC-09
def test_sort_by_name_za(page):
    login(page)
    page.select_option(".product_sort_container", "za")
    names = page.locator(".inventory_item_name").all_text_contents()
    assert names == sorted(names, reverse=True)

# TC-SC-10
def test_sort_by_price_low_to_high(page):
    login(page)
    page.select_option(".product_sort_container", "lohi")
    prices = [
        float(p.replace("$", ""))
        for p in page.locator(".inventory_item_price").all_text_contents()
    ]
    assert prices == sorted(prices)

# TC-SC-11
def test_sort_by_price_high_to_low(page):
    login(page)
    page.select_option(".product_sort_container", "hilo")
    prices = [
        float(p.replace("$", ""))
        for p in page.locator(".inventory_item_price").all_text_contents()
    ]
    assert prices == sorted(prices, reverse=True)


# ══════════════════════════════════════════════════════════════
#  BRANCH 3 — Cart
# ══════════════════════════════════════════════════════════════

# TC-SC-12
def test_add_single_item_to_cart(page):
    login(page)
    page.locator(".btn_inventory").first.click()
    expect(page.locator(".shopping_cart_badge")).to_have_text("1")

# TC-SC-13
def test_add_multiple_items_to_cart(page):
    login(page)
    buttons = page.locator(".btn_inventory").all()
    buttons[0].click()
    buttons[1].click()
    expect(page.locator(".shopping_cart_badge")).to_have_text("2")

# TC-SC-14
def test_remove_item_from_products_page(page):
    login(page)
    page.locator(".btn_inventory").first.click()
    expect(page.locator(".shopping_cart_badge")).to_have_text("1")
    page.locator(".btn_inventory").first.click()
    expect(page.locator(".shopping_cart_badge")).to_have_count(0)

# TC-SC-15
def test_cart_page_shows_added_items(page):
    login(page)
    page.locator(".btn_inventory").first.click()
    page.click(".shopping_cart_link")
    expect(page).to_have_url(f"{BASE_URL}/cart.html")
    expect(page.locator(".cart_item")).to_have_count(1)

# TC-SC-16
def test_remove_item_from_cart_page(page):
    login(page)
    page.locator(".btn_inventory").first.click()
    page.click(".shopping_cart_link")
    page.locator(".cart_button").first.click()
    expect(page.locator(".cart_item")).to_have_count(0)
    expect(page.locator(".shopping_cart_badge")).to_have_count(0)

# TC-SC-17
def test_continue_shopping_from_cart(page):
    login(page)
    page.click(".shopping_cart_link")
    page.click("#continue-shopping")
    expect(page).to_have_url(f"{BASE_URL}/inventory.html")


# ══════════════════════════════════════════════════════════════
#  BRANCH 4 — Checkout
# ══════════════════════════════════════════════════════════════

# TC-SC-18
def test_checkout_step1_empty_fields_error(page):
    login(page)
    page.locator(".btn_inventory").first.click()
    page.click(".shopping_cart_link")
    page.click("#checkout")
    page.click("#continue")
    expect(page.locator("[data-test='error']")).to_contain_text("First Name is required")

# TC-SC-19
def test_checkout_step1_missing_last_name(page):
    login(page)
    page.locator(".btn_inventory").first.click()
    page.click(".shopping_cart_link")
    page.click("#checkout")
    page.fill("#first-name", "John")
    page.click("#continue")
    expect(page.locator("[data-test='error']")).to_contain_text("Last Name is required")

# TC-SC-20
def test_checkout_step1_missing_zip(page):
    login(page)
    page.locator(".btn_inventory").first.click()
    page.click(".shopping_cart_link")
    page.click("#checkout")
    page.fill("#first-name", "John")
    page.fill("#last-name", "Doe")
    page.click("#continue")
    expect(page.locator("[data-test='error']")).to_contain_text("Postal Code is required")

# TC-SC-21
def test_checkout_step2_overview_shows_correct_item(page):
    login(page)
    page.locator(".btn_inventory").first.click()
    item_name = page.locator(".inventory_item_name").first.inner_text()
    page.click(".shopping_cart_link")
    page.click("#checkout")
    page.fill("#first-name", "John")
    page.fill("#last-name", "Doe")
    page.fill("#postal-code", "12345")
    page.click("#continue")
    expect(page).to_have_url(f"{BASE_URL}/checkout-step-two.html")
    all_names = page.locator(".inventory_item_name").all_text_contents()
    assert item_name in all_names

# TC-SC-22
def test_checkout_step2_shows_total(page):
    login(page)
    page.locator(".btn_inventory").first.click()
    page.click(".shopping_cart_link")
    page.click("#checkout")
    page.fill("#first-name", "John")
    page.fill("#last-name", "Doe")
    page.fill("#postal-code", "12345")
    page.click("#continue")
    total_text = page.locator(".summary_total_label").inner_text()
    assert "Total:" in total_text

# TC-SC-23
def test_complete_full_purchase_journey(page):
    login(page)
    page.locator(".btn_inventory").first.click()
    page.click(".shopping_cart_link")
    page.click("#checkout")
    page.fill("#first-name", "John")
    page.fill("#last-name", "Doe")
    page.fill("#postal-code", "12345")
    page.click("#continue")
    page.click("#finish")
    expect(page).to_have_url(f"{BASE_URL}/checkout-complete.html")
    expect(page.locator(".complete-header")).to_have_text("Thank you for your order!")

# TC-SC-24
def test_cancel_checkout_returns_to_cart(page):
    login(page)
    page.locator(".btn_inventory").first.click()
    page.click(".shopping_cart_link")
    page.click("#checkout")
    page.fill("#first-name", "John")
    page.fill("#last-name", "Doe")
    page.fill("#postal-code", "12345")
    page.click("#continue")
    page.click("#cancel")
    expect(page).to_have_url(f"{BASE_URL}/inventory.html")