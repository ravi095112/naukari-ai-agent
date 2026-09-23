import os

from naukri_profile import (
    open_profile,
    read_resume_headline,
    read_key_skills,
    close_resume_headline_editor,
)


def ensure_profile_loaded(page):
    title = page.title() or ""

    if "Access Denied" in title:
        raise RuntimeError(
            "Naukri blocked this browser/session before the profile loaded. "
            "Run locally with a persistent, logged-in Chrome profile instead of CI."
        )

    page.wait_for_url("**/mnjuser/profile**", timeout=30000)
    page.wait_for_selector("#lazyResumeHead", timeout=30000)


def read_profile():
    playwright, context, page = open_profile()
    ensure_profile_loaded(page)
    try:
        ensure_profile_loaded(page)

        headline = read_resume_headline(page)
        skills = read_key_skills(page)

        return {
            "resume_headline": headline,
            "key_skills": skills,
        }

    except Exception:
        os.makedirs("logs", exist_ok=True)
        page.screenshot(path="logs/failure.png", full_page=True)

        with open("logs/failure.html", "w", encoding="utf-8") as f:
            f.write(page.content())

        print(f"\nFailure URL: {page.url}")
        print(f"Failure title: {page.title()}")
        print("Saved logs/failure.png and logs/failure.html")

        raise

    finally:
        context.close()
        playwright.stop()


if __name__ == "__main__":
    profile = read_profile()

    print("\n========== Naukri Profile ==========\n")

    print("Resume Headline:")
    print(profile["resume_headline"])

    print("\nKey Skills:")

    for skill in profile["key_skills"]:
        print(f"- {skill}")

    print("\n====================================")