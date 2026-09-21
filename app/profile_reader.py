from naukri_profile import (
    open_profile,
    read_resume_headline,
    read_key_skills,
    close_resume_headline_editor,
)


def read_profile():
    playwright, context, page = open_profile()

    try:
        headline = read_resume_headline(page)
        skills = read_key_skills(page)

        return {
            "resume_headline": headline,
            "key_skills": skills,
        }

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