import pytest
from playwright.sync_api import sync_playwright, expect

BASE_URL = "https://the-internet.herokuapp.com/login"

@pytest.fixture(scope="session")
def browser_context():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        yield context
        browser.close()

@pytest.fixture(autouse=True)
def page(browser_context):
    page = browser_context.new_page()
    page.goto(BASE_URL)
    yield page
    page.close()


# ─── TC-AUTH-01 ───────────────────────────────────────────────────────────────
def test_page_loads_correctly(page):
    expect(page).to_have_title("The Internet")
    expect(page.locator("h2")).to_have_text("Login Page")
    expect(page.locator("#username")).to_be_visible()
    expect(page.locator("#password")).to_be_visible()
    expect(page.locator("button[type='submit']")).to_be_visible()


# ─── TC-AUTH-02 ───────────────────────────────────────────────────────────────
def test_successful_login(page):
    page.fill("#username", "tomsmith")
    page.fill("#password", "SuperSecretPassword!")
    page.click("button[type='submit']")

    expect(page).to_have_url("https://the-internet.herokuapp.com/secure")
    expect(page.locator(".flash.success")).to_be_visible()
    expect(page.locator(".flash.success")).to_contain_text("You logged into a secure area!")


# ─── TC-AUTH-03 ───────────────────────────────────────────────────────────────
def test_wrong_password(page):
    page.fill("#username", "tomsmith")
    page.fill("#password", "wrongpassword")
    page.click("button[type='submit']")

    expect(page).to_have_url(BASE_URL)
    expect(page.locator(".flash.error")).to_be_visible()
    expect(page.locator(".flash.error")).to_contain_text("Your password is invalid!")


# ─── TC-AUTH-04 ───────────────────────────────────────────────────────────────
def test_wrong_username(page):
    page.fill("#username", "invaliduser")
    page.fill("#password", "SuperSecretPassword!")
    page.click("button[type='submit']")

    expect(page).to_have_url(BASE_URL)
    expect(page.locator(".flash.error")).to_be_visible()
    expect(page.locator(".flash.error")).to_contain_text("Your username is invalid!")


# ─── TC-AUTH-05 ───────────────────────────────────────────────────────────────
def test_empty_username(page):
    page.fill("#password", "SuperSecretPassword!")
    page.click("button[type='submit']")

    expect(page).to_have_url(BASE_URL)
    expect(page.locator(".flash.error")).to_be_visible()
    expect(page.locator(".flash.error")).to_contain_text("Your username is invalid!")


# ─── TC-AUTH-06 ───────────────────────────────────────────────────────────────
def test_empty_password(page):
    page.fill("#username", "tomsmith")
    page.click("button[type='submit']")

    expect(page).to_have_url(BASE_URL)
    expect(page.locator(".flash.error")).to_be_visible()
    expect(page.locator(".flash.error")).to_contain_text("Your password is invalid!")


# ─── TC-AUTH-07 ───────────────────────────────────────────────────────────────
def test_both_fields_empty(page):
    page.click("button[type='submit']")

    expect(page).to_have_url(BASE_URL)
    expect(page.locator(".flash.error")).to_be_visible()


# ─── TC-AUTH-08 ───────────────────────────────────────────────────────────────
def test_logout_after_login(page):
    page.fill("#username", "tomsmith")
    page.fill("#password", "SuperSecretPassword!")
    page.click("button[type='submit']")

    expect(page).to_have_url("https://the-internet.herokuapp.com/secure")

    page.click("a[href='/logout']")

    expect(page).to_have_url(BASE_URL)
    expect(page.locator(".flash.success")).to_contain_text("You logged out of the secure area!")


# ─── TC-AUTH-09 ───────────────────────────────────────────────────────────────
def test_secure_page_redirects_when_not_logged_in(page):
    page.goto("https://the-internet.herokuapp.com/secure")
    expect(page).to_have_url(BASE_URL)