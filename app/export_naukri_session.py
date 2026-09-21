from pathlib import Path
from playwright.sync_api import sync_playwright


BASE_DIR = Path(__file__).resolve().parent.parent
BROWSER_DATA = BASE_DIR / "data" / "naukri-browser"
OUTPUT_FILE = BASE_DIR / "data" / "naukri-storage-state.json"

PROFILE_URL = "https://www.naukri.com/mnjuser/profile"


with sync_playwright() as playwright:

    context = playwright.chromium.launch_persistent_context(
        user_data_dir=str(BROWSER_DATA),
        headless=False,
        viewport={"width": 1440, "height": 900},
    )

    page = context.pages[0] if context.pages else context.new_page()

    page.goto(
        PROFILE_URL,
        wait_until="domcontentloaded",
        timeout=60000,
    )

    page.wait_for_timeout(5000)

    print("URL:", page.url)
    print("TITLE:", page.title())

    if "mnjuser/profile" not in page.url:
        raise RuntimeError(
            "Naukri profile page was not reached. "
            "Session may not be authenticated."
        )

    context.storage_state(
        path=str(OUTPUT_FILE)
    )

    print()
    print("Storage state exported:")
    print(OUTPUT_FILE)

    context.close()