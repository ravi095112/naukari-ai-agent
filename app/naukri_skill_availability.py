from naukri_profile import open_profile


def get_naukri_skill_suggestions(page, skill_name):
    input_box = page.locator(
        'input[name="suggestor"]#keySkillSugg:visible'
    )

    input_box.wait_for(
        state="visible",
        timeout=5000,
    )

    input_box.click()

    input_box.press("Control+A")
    input_box.press("Backspace")

    page.wait_for_timeout(300)

    input_box.type(
    	skill_name,
	delay=120,
    )

    page.wait_for_timeout(3500)

    suggestions = page.locator(
        "#sugDrp_keySkillSugg li.sugTouple"
    )

    result = []

    for i in range(suggestions.count()):
        text = suggestions.nth(i).inner_text().strip()

        if text:
            result.append(text)

    return result


def check_candidate_skills(candidate_skills):
    playwright, context, page = open_profile()

    try:
        section = page.locator("#lazyKeySkills")

        edit_button = section.locator(
            ".widgetHead .edit.icon"
        )

        edit_button.click()

        page.locator(
            'input[name="suggestor"]#keySkillSugg:visible'
        ).wait_for(
            state="visible",
            timeout=5000,
        )

        supported = {}
        unsupported = {}

        for skill in candidate_skills:

            print(
                f"\nChecking Naukri availability: {skill}"
            )

            suggestions = get_naukri_skill_suggestions(
                page,
                skill,
            )

            exact = any(
                suggestion.strip().lower()
                == skill.strip().lower()
                for suggestion in suggestions
            )

            if exact:
                supported[skill] = suggestions
                print("  SUPPORTED")
            else:
                unsupported[skill] = suggestions
                print("  NOT SUPPORTED")
                print(
                    f"  Suggestions: {suggestions}"
                )

        return supported, unsupported

    finally:
        context.close()
        playwright.stop()


if __name__ == "__main__":

    candidates = [
        "REST API",
        "GenAI",
    ]

    supported, unsupported = check_candidate_skills(
        candidates
    )

    print(
        "\n========== Naukri Skill Availability ==========\n"
    )

    print("Supported:")

    for skill in supported:
        print(f"- {skill}")

    print("\nUnsupported:")

    for skill in unsupported:
        print(f"- {skill}")