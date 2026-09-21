import json
from pathlib import Path
from playwright.sync_api import sync_playwright


BASE_DIR = Path(__file__).resolve().parent.parent
STATE_FILE = BASE_DIR / "data" / "naukri-storage-state.json"

PROFILE_URL = "https://www.naukri.com/mnjuser/profile"


with sync_playwright() as playwright:

    browser = playwright.chromium.launch(
        headless=True
    )

    context = browser.new_context(
        storage_state=str(STATE_FILE),
        viewport={"width": 1440, "height": 900},
    )

    page = context.new_page()

    page.goto(
        PROFILE_URL,
        wait_until="domcontentloaded",
        timeout=60000,
    )

    page.wait_for_timeout(5000)

    print("URL:", page.url)
    print("TITLE:", page.title())

    headline = page.locator("#lazyResumeHead")

    print(
        "Resume headline section:",
        headline.count()
    )

    skills = page.locator("#lazyKeySkills")

    print(
        "Key skills section:",
        skills.count()
    )

    if "mnjuser/profile" not in page.url:
        raise RuntimeError(
            "Storage state is not authenticated."
        )

    if headline.count() == 0:
        raise RuntimeError(
            "Authenticated page loaded, but "
            "resume headline section was not found."
        )

    if skills.count() == 0:
        raise RuntimeError(
            "Authenticated page loaded, but "
            "key skills section was not found."
        )

    print()
    print("STORAGE STATE TEST PASSED")

    context.close()
    browser.close()
