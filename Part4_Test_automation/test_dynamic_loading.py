import pytest
from playwright.sync_api import sync_playwright, expect

BASE_URL = "https://the-internet.herokuapp.com"

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
    yield page
    page.close()


# ─── TC-DL-01 ─────────────────────────────────────────────────────────────────
def test_dynamic_loading_main_page_loads(page):
    page.goto(f"{BASE_URL}/dynamic_loading")

    expect(page.locator("h3")).to_have_text("Dynamically Loaded Page Elements")
    expect(page.locator("a[href='/dynamic_loading/1']")).to_be_visible()
    expect(page.locator("a[href='/dynamic_loading/2']")).to_be_visible()


# ─── TC-DL-02 ─────────────────────────────────────────────────────────────────
def test_example1_page_loads_correctly(page):
    page.goto(f"{BASE_URL}/dynamic_loading/1")

    expect(page.locator("#content h4").first).to_have_text("Example 1: Element on page that is hidden")


# ─── TC-DL-03 ─────────────────────────────────────────────────────────────────
def test_example1_element_hidden_before_start(page):
    page.goto(f"{BASE_URL}/dynamic_loading/1")

    hidden_element = page.locator("#finish")
    expect(hidden_element).to_be_hidden()


# ─── TC-DL-04 ─────────────────────────────────────────────────────────────────
def test_example1_loading_bar_appears_after_click(page):
    page.goto(f"{BASE_URL}/dynamic_loading/1")

    page.click("button")
    expect(page.locator("#loading")).to_be_visible()


# ─── TC-DL-05 ─────────────────────────────────────────────────────────────────
def test_example1_element_visible_after_loading(page):
    page.goto(f"{BASE_URL}/dynamic_loading/1")

    page.click("button")
    finish_element = page.locator("#finish h4")
    expect(finish_element).to_be_visible(timeout=10000)
    expect(finish_element).to_have_text("Hello World!")


# ─── TC-DL-06 ─────────────────────────────────────────────────────────────────
def test_example1_loading_bar_disappears_after_finish(page):
    page.goto(f"{BASE_URL}/dynamic_loading/1")

    page.click("button")
    expect(page.locator("#finish h4")).to_be_visible(timeout=10000)
    expect(page.locator("#loading")).to_be_hidden()


# ─── TC-DL-07 ─────────────────────────────────────────────────────────────────
def test_example2_page_loads_correctly(page):
    page.goto(f"{BASE_URL}/dynamic_loading/2")

    expect(page.locator("h4")).to_have_text("Example 2: Element rendered after the fact")
    expect(page.locator("button")).to_be_visible()
    expect(page.locator("button")).to_have_text("Start")


# ─── TC-DL-08 ─────────────────────────────────────────────────────────────────
def test_example2_element_not_in_dom_before_start(page):
    page.goto(f"{BASE_URL}/dynamic_loading/2")

    expect(page.locator("#finish")).to_have_count(0)


# ─── TC-DL-09 ─────────────────────────────────────────────────────────────────
def test_example2_element_added_to_dom_after_loading(page):
    page.goto(f"{BASE_URL}/dynamic_loading/2")

    page.click("button")
    finish_element = page.locator("#finish h4")
    expect(finish_element).to_be_visible(timeout=10000)
    expect(finish_element).to_have_text("Hello World!")


# ─── TC-DL-10 ─────────────────────────────────────────────────────────────────
def test_example2_loading_bar_disappears_after_finish(page):
    page.goto(f"{BASE_URL}/dynamic_loading/2")

    page.click("button")
    expect(page.locator("#finish h4")).to_be_visible(timeout=10000)
    expect(page.locator("#loading")).to_be_hidden()


# ─── TC-DL-11 ─────────────────────────────────────────────────────────────────
def test_example1_vs_example2_same_end_result(page):
    results = []

    for example_num in [1, 2]:
        page.goto(f"{BASE_URL}/dynamic_loading/{example_num}")
        page.click("button")
        finish = page.locator("#finish h4")
        expect(finish).to_be_visible(timeout=10000)
        results.append(finish.inner_text())

    assert results[0] == results[1] == "Hello World!"