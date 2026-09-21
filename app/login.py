from pathlib import Path
from playwright.sync_api import sync_playwright

BASE_DIR = Path(__file__).resolve().parent.parent
BROWSER_DATA = BASE_DIR / "data" / "naukri-browser"

with sync_playwright() as p:
    context = p.chromium.launch_persistent_context(
        user_data_dir=str(BROWSER_DATA),
        headless=False,
        viewport={"width": 1440, "height": 900},
    )

    page = context.pages[0] if context.pages else context.new_page()

    page.goto("https://www.naukri.com/", wait_until="domcontentloaded")

    print("\nBrowser opened.")
    print("Log in to Naukri manually.")
    print("Complete OTP/CAPTCHA manually if requested.")
    print("After you reach your logged-in Naukri homepage, return here.")
    input("\nPress ENTER after login is complete...")

    print("\nCurrent URL:")
    print(page.url)

    context.close()