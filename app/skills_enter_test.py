from naukri_profile import open_profile


def open_key_skills_editor(page):
    section = page.locator("#lazyKeySkills")

    if section.count() == 0:
        raise RuntimeError("Key Skills section not found")

    section.locator(".widgetHead .edit.icon").first.click()

    page.wait_for_timeout(1000)

    page.locator("#keySkillSugg").wait_for(
        state="visible",
        timeout=5000
    )


def get_editor_chips(page):

    chips = page.locator(
        "div.sWrap div.chipsContainer div.chip"
    )

    result = []

    for i in range(chips.count()):

        title = chips.nth(i).get_attribute(
            "title"
        )

        if title:
            result.append(title)

    return result


def search_skill(page, skill_name):

    skill_input = page.locator(
        "#keySkillSugg"
    )

    skill_input.click()

    skill_input.evaluate(
        """
        (element, value) => {

            const setter =
                Object.getOwnPropertyDescriptor(
                    HTMLInputElement.prototype,
                    "value"
                ).set;

            setter.call(
                element,
                value
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
                        cancelable: true,
                        key: "d",
                        code: "KeyD",
                        keyCode: 68,
                        which: 68
                    }
                )
            );

            element.dispatchEvent(
                new KeyboardEvent(
                    "keyup",
                    {
                        bubbles: true,
                        cancelable: true,
                        key: "d",
                        code: "KeyD",
                        keyCode: 68,
                        which: 68
                    }
                )
            );
        }
        """,
        skill_name
    )

    page.wait_for_timeout(2500)


def main():

    playwright, context, page = open_profile()

    try:

        print(
            "\n========== OPENING EDITOR ==========\n"
        )

        open_key_skills_editor(page)

        before = get_editor_chips(page)

        print(
            "Initial chips:",
            len(before)
        )

        print(
            "\n========== SEARCHING DOCKER ==========\n"
        )

        search_skill(
            page,
            "Docker"
        )

        suggestion = page.locator(
            'li.sugTouple[data-id="55888"]'
        )

        if suggestion.count() == 0:

            raise RuntimeError(
                "Docker suggestion not found"
            )

        print(
            "\nDocker suggestion found."
        )

        print(
            suggestion.evaluate(
                "(el) => el.outerHTML"
            )
        )

        print(
            "\n========== DISPATCHING EVENTS ON LI ==========\n"
        )

        suggestion.dispatch_event(
            "pointerdown"
        )

        suggestion.dispatch_event(
            "mousedown"
        )

        page.wait_for_timeout(200)

        suggestion.dispatch_event(
            "pointerup"
        )

        suggestion.dispatch_event(
            "mouseup"
        )

        suggestion.dispatch_event(
            "click"
        )

        page.wait_for_timeout(1500)

        after = get_editor_chips(page)

        print(
            "\n========== RESULT ==========\n"
        )

        print(
            "Before:",
            len(before)
        )

        print(
            "After:",
            len(after)
        )

        print(
            "Docker added:",
            "Docker" in after
        )

        print(
            "\nCurrent chips:"
        )

        for chip in after:
            print(
                "-",
                chip
            )

        print(
            "\nNO SAVE ACTION PERFORMED."
        )

        input(
            "\nPress ENTER to close..."
        )

    finally:

        context.close()
        playwright.stop()


if __name__ == "__main__":
    main()