from naukri_profile import PROFILE_URL


def open_key_skills_editor(page):
    section = page.locator("#lazyKeySkills")

    if section.count() == 0:
        raise RuntimeError("Key Skills section not found.")

    edit_button = section.locator(
        ".widgetHead .edit.icon"
    )

    if edit_button.count() == 0:
        raise RuntimeError("Key Skills edit button not found.")

    edit_button.click()

    input_box = page.locator(
        'input[name="suggestor"]#keySkillSugg:visible'
    )

    input_box.wait_for(
        state="visible",
        timeout=5000,
    )

    return input_box



def get_editor_chips(page):
    chips = page.locator(
        "div.sWrap div.chipsContainer div.chip:visible"
    )

    for _ in range(10):
        if chips.count() > 0:
            break

        page.wait_for_timeout(500)

    result = []

    for i in range(chips.count()):
        title = chips.nth(i).get_attribute("title")

        if title:
            result.append(title.strip())

    return result




def get_suggestions(page):
    suggestions = page.locator(
        "#sugDrp_keySkillSugg li.sugTouple"
    )

    result = []

    for i in range(suggestions.count()):
        text = suggestions.nth(i).inner_text().strip()

        if text:
            result.append(text)

    return result


def type_skill(page, skill_name):
    input_box = page.locator(
        'input[name="suggestor"]#keySkillSugg:visible'
    )

    input_box.wait_for(
        state="visible",
        timeout=5000,
    )

    page.evaluate(
        """
        () => {
            const input = document.querySelector(
                'input[name="suggestor"]#keySkillSugg'
            );

            if (!input) {
                throw new Error("Key Skills input not found.");
            }

            input.removeAttribute("maxlength");
            input.focus();
        }
        """
    )

    input_box.click()

    page.keyboard.press("Control+A")
    page.keyboard.press("Backspace")

    for char in skill_name:
        page.evaluate(
            """
            (char) => {
                const input = document.querySelector(
                    'input[name="suggestor"]#keySkillSugg'
                );

                if (!input) {
                    throw new Error("Key Skills input not found.");
                }

                const setter =
                    Object.getOwnPropertyDescriptor(
                        HTMLInputElement.prototype,
                        "value"
                    ).set;

                setter.call(
                    input,
                    input.value + char
                );

                input.dispatchEvent(
                    new Event(
                        "input",
                        { bubbles: true }
                    )
                );

                input.dispatchEvent(
                    new Event(
                        "change",
                        { bubbles: true }
                    )
                );

                input.dispatchEvent(
                    new KeyboardEvent(
                        "keyup",
                        {
                            bubbles: true,
                            key: char
                        }
                    )
                );
            }
            """,
            char,
        )

        page.wait_for_timeout(300)

    page.wait_for_timeout(2000)


def has_exact_suggestion(page, skill_name):
    type_skill(page, skill_name)

    target = skill_name.strip().lower()

    suggestions = get_suggestions(page)

    print(
        f"\nNaukri suggestions for '{skill_name}':"
    )

    if not suggestions:
        print("  - None")
        return False

    for suggestion in suggestions:
        print(f"  - {suggestion}")

        if suggestion.strip().lower() == target:
            return True

    return False



def remove_skill(page, skill_name):
    """
    Remove one exact skill from the open editor.

    Naukri may keep a stale/hidden React chip in the DOM,
    so only visible chips are considered.
    """

    print(f"Removing: {skill_name}")

    target = skill_name.strip().lower()

    chips = page.locator(
        "div.sWrap div.chipsContainer div.chip:visible"
    )

    initial_count = chips.count()

    for i in range(initial_count):
        chip = chips.nth(i)

        title = chip.get_attribute("title")

        if not title:
            continue

        if title.strip().lower() != target:
            continue

        close_button = chip.locator(".close")

        if close_button.count() == 0:
            raise RuntimeError(
                f"Remove button not found for "
                f"'{skill_name}'."
            )

        close_button.click()

        # Wait until the visible target chip disappears.
        for _ in range(20):
            page.wait_for_timeout(500)

            current_chips = page.locator(
                "div.sWrap div.chipsContainer div.chip:visible"
            )

            found_target = False

            for j in range(current_chips.count()):
                current_chip = current_chips.nth(j)

                current_title = (
                    current_chip.get_attribute("title")
                )

                if (
                    current_title
                    and current_title.strip().lower()
                    == target
                ):
                    found_target = True
                    break

            if not found_target:
                print(
                    f"Removed successfully: "
                    f"{skill_name}"
                )
                return

        raise RuntimeError(
            f"Skill '{skill_name}' was not removed "
            "from the visible editor."
        )

    raise RuntimeError(
        f"Skill '{skill_name}' was not found."
    )




def select_exact_suggestion(page, skill_name):
    """
    Select an exact Naukri suggestion.
    """

    target = skill_name.strip().lower()

    suggestions = page.locator(
        "#sugDrp_keySkillSugg li.sugTouple"
    )

    count = suggestions.count()

    if count == 0:
        raise RuntimeError(
            f"No suggestions found for skill: "
            f"{skill_name}"
        )

    for i in range(count):
        suggestion = suggestions.nth(i)

        text = suggestion.inner_text().strip()

        if text.lower() != target:
            continue

        suggestion.click()

        page.wait_for_timeout(500)

        chips = get_editor_chips(page)

        if not any(
            value.strip().lower() == target
            for value in chips
        ):
            raise RuntimeError(
                f"'{skill_name}' was not added "
                "to editor."
            )

        print(
            f"Added to editor successfully: "
            f"{skill_name}"
        )

        return

    raise RuntimeError(
        f"Exact Naukri suggestion "
        f"'{skill_name}' was not found."
    )


def click_save(page):
    print("Saving Key Skills...")

    save_button = page.get_by_text(
        "Save",
        exact=True,
    ).last

    save_button.wait_for(
        state="visible",
        timeout=5000,
    )

    save_button.click()

    page.wait_for_timeout(2500)


def read_saved_skills(page):
    page.wait_for_timeout(1000)

    section = page.locator("#lazyKeySkills")

    if section.count() == 0:
        raise RuntimeError(
            "Key Skills section not found after save."
        )

    chips = section.locator(
        ".widgetCont .chip"
    )

    result = []

    for i in range(chips.count()):
        title = chips.nth(i).get_attribute("title")

        if title:
            result.append(title.strip())

    return result


def apply_replacement(
    page,
    remove_skill_name,
    add_skill,
):
    """
    Safely replace one Naukri Key Skill.

    The new skill is verified against Naukri's
    actual suggestion list BEFORE the old skill
    is removed.
    """

    print(
        "\n========== APPLYING APPROVED REPLACEMENT ==========\n"
    )

    print(f"REMOVE : {remove_skill_name}")
    print(f"ADD    : {add_skill}")

    # --------------------------------------------------
    # 1. Open editor
    # --------------------------------------------------

    open_key_skills_editor(page)

    initial_skills = get_editor_chips(page)

    print(
        f"\nInitial editor skills: "
        f"{len(initial_skills)}"
    )

    remove_target = remove_skill_name.strip().lower()
    add_target = add_skill.strip().lower()

    normalized_initial = {
        skill.strip().lower()
        for skill in initial_skills
    }

    if remove_target not in normalized_initial:
        raise RuntimeError(
            f"Cannot remove '{remove_skill_name}'. "
            "It is not currently present."
        )

    if add_target in normalized_initial:
        raise RuntimeError(
            f"Cannot add '{add_skill}'. "
            "It is already present."
        )

    if len(initial_skills) != 23:
        raise RuntimeError(
            f"Expected 23 initial skills, "
            f"found {len(initial_skills)}."
        )

    # --------------------------------------------------
    # 2. Verify ADD skill BEFORE removing anything
    # --------------------------------------------------

    print(
        f"\nChecking whether Naukri supports: "
        f"{add_skill}"
    )

    if not has_exact_suggestion(
        page,
        add_skill,
    ):
        print(
            f"\nNaukri does not provide an exact "
            f"suggestion for '{add_skill}'."
        )

        raise RuntimeError(
            f"Skill '{add_skill}' is not available "
            "as an exact Naukri suggestion. "
            "No profile change was saved."
        )

    print(
        f"Exact Naukri suggestion confirmed: "
        f"{add_skill}"
    )

    # --------------------------------------------------
    # 3. Remove old skill
    # --------------------------------------------------

    remove_skill(
        page,
        remove_skill_name,
    )

    # IMPORTANT:
    # React may update the DOM asynchronously.
    # Poll until exactly 22 skills are visible.

    # --------------------------------------------------
    # 3b. Verify the OLD skill is actually gone
    # --------------------------------------------------

    after_remove = []

    for _ in range(20):
        after_remove = get_editor_chips(page)

        normalized_after_remove = {
            skill.strip().lower()
            for skill in after_remove
        }

        if remove_target not in normalized_after_remove:
            break

        page.wait_for_timeout(500)

    print(
        f"Skills visible after removal check: "
        f"{len(after_remove)}"
    )

    if remove_target in {
        skill.strip().lower()
        for skill in after_remove
    }:
        raise RuntimeError(
            f"Removed skill '{remove_skill_name}' "
            "is still present in the editor."
        )

    print(
        f"Confirmed old skill is gone: "
        f"{remove_skill_name}"
    )

    # --------------------------------------------------
    # 4. Type new skill
    # --------------------------------------------------

    type_skill(
        page,
        add_skill,
    )

    # --------------------------------------------------
    # 5. Select exact suggestion
    # --------------------------------------------------

    select_exact_suggestion(
        page,
        add_skill,
    )

    after_add = []

    for _ in range(20):
        after_add = get_editor_chips(page)

        if len(after_add) == 23:
            break

        page.wait_for_timeout(500)

    print(
        f"Skills after addition: "
        f"{len(after_add)}"
    )

    if len(after_add) != 23:
        raise RuntimeError(
            f"Expected 23 skills after addition, "
            f"found {len(after_add)}."
        )

    normalized_after_add = {
        skill.strip().lower()
        for skill in after_add
    }

    if remove_target in normalized_after_add:
        raise RuntimeError(
            f"Removed skill '{remove_skill_name}' "
            "is still present."
        )

    if add_target not in normalized_after_add:
        raise RuntimeError(
            f"Added skill '{add_skill}' "
            "is not present."
        )

    # --------------------------------------------------
    # 6. Save
    # --------------------------------------------------

    click_save(page)

    # --------------------------------------------------
    # 7. Reload
    # --------------------------------------------------

    print(
        "\nReloading profile to verify persistence..."
    )

    page.goto(
        PROFILE_URL,
        wait_until="domcontentloaded",
        timeout=60000,
    )

    page.wait_for_timeout(5000)

    final_skills = read_saved_skills(page)

    print(
        f"Final saved skills: "
        f"{len(final_skills)}"
    )

    # --------------------------------------------------
    # 8. Final verification
    # --------------------------------------------------

    normalized_final = {
        skill.strip().lower()
        for skill in final_skills
    }

    if len(final_skills) != 23:
        raise RuntimeError(
            f"Final profile should contain "
            f"23 skills. Found {len(final_skills)}."
        )

    if remove_target in normalized_final:
        raise RuntimeError(
            f"Removed skill '{remove_skill_name}' "
            "is still present after reload."
        )

    if add_target not in normalized_final:
        raise RuntimeError(
            f"Added skill '{add_skill}' "
            "is missing after reload."
        )

    print(
        "\n============================================"
    )

    print(
        "Replacement persisted successfully."
    )

    print(
        f"Removed : {remove_skill_name}"
    )

    print(
        f"Added   : {add_skill}"
    )

    print(
        "Verified: after page reload"
    )

    print(
        "============================================\n"
    )

    return final_skills
