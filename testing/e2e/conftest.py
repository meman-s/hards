import pytest
from pathlib import Path
from playwright.sync_api import Page, sync_playwright


@pytest.fixture(scope="session")
def form_url() -> str:
    path = Path(__file__).resolve().parent / "test_form.html"
    return path.as_uri()


@pytest.fixture(scope="function")
def page() -> Page:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        pg = context.new_page()
        yield pg
        context.close()
        browser.close()
