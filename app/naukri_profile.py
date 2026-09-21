import os
from pathlib import Path
from playwright.sync_api import sync_playwright


BASE_DIR = Path(__file__).resolve().parent.parent
BROWSER_DATA = BASE_DIR / "data" / "naukri-browser"

PROFILE_URL = "https://www.naukri.com/mnjuser/profile"


def open_profile():
    playwright = sync_playwright().start()

    storage_state = os.getenv("NAUKRI_STORAGE_STATE")

    if storage_state:
        browser = playwright.chromium.launch(
            headless=True,
        )

        context = browser.new_context(
            storage_state=storage_state,
            viewport={"width": 1440, "height": 900},
        )
    else:
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

    return playwright, context, page


def read_resume_headline(page):
    section = page.locator("#lazyResumeHead")

    section.wait_for(
        state="visible",
        timeout=15000,
    )

    headline = section.locator(".prefill")

    headline.wait_for(
        state="visible",
        timeout=10000,
    )

    return headline.inner_text().strip()


def read_key_skills(page):
    section = page.locator("#lazyKeySkills")

    if section.count() == 0:
        raise RuntimeError("Key skills section not found")

    skills = section.locator(
        ".widgetCont .chip"
    )

    result = []

    for i in range(skills.count()):
        skill = skills.nth(i).get_attribute("title")

        if skill:
            result.append(skill.strip())

    return result


def open_resume_headline_editor(page):
    section = page.locator("#lazyResumeHead")

    if section.count() == 0:
        raise RuntimeError("Resume headline section not found")

    edit_button = section.locator(
        ".widgetHead .edit.icon"
    )

    if edit_button.count() == 0:
        raise RuntimeError(
            "Resume headline edit button not found"
        )

    edit_button.click()

    textarea = page.locator(
        'textarea[name="resumeHeadline"]:visible'
    )

    textarea.wait_for(
        state="visible",
        timeout=5000,
    )

    return textarea


def close_resume_headline_editor(page):
    page.get_by_text(
        "Cancel",
        exact=True
    ).last.click()


if __name__ == "__main__":

    playwright, context, page = open_profile()

    try:

        # -----------------------------------------
        # Resume headline
        # -----------------------------------------

        headline = read_resume_headline(page)

        print("\nCURRENT RESUME HEADLINE")
        print("=" * 70)
        print(headline)
        print("=" * 70)

        # -----------------------------------------
        # Key skills
        # -----------------------------------------

        skills = read_key_skills(page)

        print("\nCURRENT KEY SKILLS")
        print("=" * 70)

        for index, skill in enumerate(skills, start=1):
            print(f"{index:02d}. {skill}")

        print("=" * 70)

        # -----------------------------------------
        # Test headline editor
        # -----------------------------------------

        textarea = open_resume_headline_editor(page)

        print("\nEDITOR VALUE")
        print("=" * 70)
        print(textarea.input_value())
        print("=" * 70)

        close_resume_headline_editor(page)

        print("\nHeadline editor closed WITHOUT saving.")

    finally:
        context.close()
        playwright.stop()