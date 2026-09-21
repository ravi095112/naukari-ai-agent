from naukri_profile import open_profile


REMOVE_SKILL = "SQLite"
ADD_SKILL = "Docker"


def open_key_skills_editor(page):
    section = page.locator("#lazyKeySkills")

    if section.count() == 0:
        raise RuntimeError("Key Skills section not found")

    section.locator(
        ".widgetHead .edit.icon"
    ).first.click()

    page.wait_for_timeout(1000)

    page.locator(
        "#keySkillSugg"
    ).wait_for(
        state="visible",
        timeout=5000
    )


def get_editor_chips(page):
    chips = page.locator(
        "div.sWrap div.chipsContainer div.chip"
    )

    result = []

    for i in range(chips.count()):
        title = chips.nth(i).get_attribute("title")

        if title:
            result.append(title.strip())

    return result


def remove_skill(page, skill_name):
    chips = page.locator(
        "div.sWrap div.chipsContainer div.chip"
    )

    for i in range(chips.count()):
        chip = chips.nth(i)

        title = chip.get_attribute("title")

        if title and title.strip().lower() == skill_name.lower():

            print(f"Found skill to remove: {title}")

            print("Chip HTML:")
            print(
                chip.evaluate(
                    "(el) => el.outerHTML"
                )
            )

            remove_button = chip.locator(
                ".close"
            )

            if remove_button.count() == 0:
                raise RuntimeError(
                    f"Remove button not found for {skill_name}"
                )

            print("Removing using selector: .close")

            remove_button.first.click()

            page.wait_for_timeout(700)

            return

    raise RuntimeError(
        f"Skill not found: {skill_name}"
    )


def enter_skill(page, skill_name):
    skill_input = page.locator(
        "#keySkillSugg"
    )

    skill_input.click()

    skill_input.evaluate(
        """
        (element, skillName) => {

            const setter =
                Object.getOwnPropertyDescriptor(
                    HTMLInputElement.prototype,
                    "value"
                ).set;

            setter.call(
                element,
                skillName
            );

            element.dispatchEvent(
                new Event(
                    "input",
                    { bubbles: true }
                )
            );

            element.dispatchEvent(
                new Event(
                    "change",
                    { bubbles: true }
                )
            );

            element.dispatchEvent(
                new KeyboardEvent(
                    "keydown",
                    {
                        bubbles: true,
                        key: "ArrowDown"
                    }
                )
            );

            element.dispatchEvent(
                new KeyboardEvent(
                    "keyup",
                    {
                        bubbles: true,
                        key: "ArrowDown"
                    }
                )
            );
        }
        """,
        skill_name
    )

    page.wait_for_timeout(2500)


def select_exact_suggestion(page, skill_name):
    suggestion_box = page.locator(
        "#sugDrp_keySkillSugg"
    )

    suggestions = suggestion_box.locator(
        "li.sugTouple"
    )

    print(
        f"Suggestion count: {suggestions.count()}"
    )

    for i in range(suggestions.count()):

        item = suggestions.nth(i)

        text = item.inner_text().strip()

        print(
            f"{i}: {text}"
        )

        if text.lower() == skill_name.lower():

            print(
                f"Selecting exact suggestion: {text}"
            )

            item.locator(
                ".Sbtn"
            ).click()

            page.wait_for_timeout(1000)

            return

    raise RuntimeError(
        f"Exact suggestion not found: {skill_name}"
    )


def click_save(page):

    save_button = page.get_by_role(
        "button",
        name="Save",
        exact=True
    )

    if save_button.count() == 0:
        raise RuntimeError(
            "Save button not found"
        )

    print(
        "Clicking Save..."
    )

    save_button.click()

    page.wait_for_timeout(3000)


def read_saved_skills(page):

    page.reload(
        wait_until="domcontentloaded",
        timeout=60000
    )

    page.wait_for_timeout(5000)

    chips = page.locator(
        "#lazyKeySkills .widgetCont .chip"
    )

    result = []

    for i in range(chips.count()):

        title = chips.nth(i).get_attribute(
            "title"
        )

        if title:
            result.append(title.strip())

    return result


def main():

    print(
        "\n========== KEY SKILL REPLACEMENT TEST ==========\n"
    )

    playwright, context, page = open_profile()

    try:

        print(
            "========== OPENING EDITOR ==========\n"
        )

        open_key_skills_editor(page)

        initial = get_editor_chips(page)

        print(
            f"Initial chip count: {len(initial)}"
        )

        for skill in initial:
            print(f"- {skill}")

        if len(initial) != 23:
            raise RuntimeError(
                f"Expected 23 skills, found {len(initial)}"
            )

        if REMOVE_SKILL not in initial:
            raise RuntimeError(
                f"{REMOVE_SKILL} is not present"
            )

        if ADD_SKILL in initial:
            raise RuntimeError(
                f"{ADD_SKILL} is already present"
            )

        print(
            f"\n========== REMOVING {REMOVE_SKILL} ==========\n"
        )

        remove_skill(
            page,
            REMOVE_SKILL
        )

        after_remove = get_editor_chips(page)

        print(
            f"After removal: {len(after_remove)}"
        )

        if REMOVE_SKILL in after_remove:
            raise RuntimeError(
                f"{REMOVE_SKILL} was not removed"
            )

        print(
            f"\n========== ADDING {ADD_SKILL} ==========\n"
        )

        enter_skill(
            page,
            ADD_SKILL
        )

        select_exact_suggestion(
            page,
            ADD_SKILL
        )

        after_add = get_editor_chips(page)

        print(
            f"\nAfter addition: {len(after_add)}"
        )

        for skill in after_add:
            print(f"- {skill}")

        if ADD_SKILL not in after_add:
            raise RuntimeError(
                f"{ADD_SKILL} was not added"
            )

        if REMOVE_SKILL in after_add:
            raise RuntimeError(
                f"{REMOVE_SKILL} is still present"
            )

        if len(after_add) != 23:
            raise RuntimeError(
                f"Expected 23 skills, found {len(after_add)}"
            )

        print(
            "\n========== SAVING ==========\n"
        )

        click_save(page)

        print(
            "Save clicked."
        )

        print(
            "\n========== VERIFYING SAVED PROFILE ==========\n"
        )

        saved_skills = read_saved_skills(page)

        print(
            f"Saved chip count: {len(saved_skills)}"
        )

        for skill in saved_skills:
            print(f"- {skill}")

        docker_saved = ADD_SKILL in saved_skills
        sqlite_saved = REMOVE_SKILL in saved_skills

        print(
            f"\nDocker saved: {docker_saved}"
        )

        print(
            f"SQLite still saved: {sqlite_saved}"
        )

        if not docker_saved:
            raise RuntimeError(
                "Docker was not persisted"
            )

        if sqlite_saved:
            raise RuntimeError(
                "SQLite was not removed"
            )

        if len(saved_skills) != 23:
            raise RuntimeError(
                f"Expected 23 saved skills, found {len(saved_skills)}"
            )

        print(
            "\n========== SUCCESS ==========\n"
        )

        print(
            "SQLite -> Docker replacement persisted successfully."
        )

        input(
            "\nPress ENTER to close..."
        )

    finally:

        context.close()
        playwright.stop()


if __name__ == "__main__":
    main()