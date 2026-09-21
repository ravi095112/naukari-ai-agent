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


def enter_skill(page, skill_name):

    skill_input = page.locator("#keySkillSugg")

    skill_input.click()

    skill_input.evaluate(
        """
        (element, value) => {

            const setter =
                Object.getOwnPropertyDescriptor(
                    HTMLInputElement.prototype,
                    "value"
                ).set;

            setter.call(element, value);

            element.dispatchEvent(
                new Event("input", { bubbles: true })
            );

            element.dispatchEvent(
                new Event("change", { bubbles: true })
            );

            element.dispatchEvent(
                new KeyboardEvent("keydown", {
                    bubbles: true,
                    cancelable: true,
                    key: "d",
                    code: "KeyD",
                    keyCode: 68,
                    which: 68
                })
            );

            element.dispatchEvent(
                new KeyboardEvent("keyup", {
                    bubbles: true,
                    cancelable: true,
                    key: "d",
                    code: "KeyD",
                    keyCode: 68,
                    which: 68
                })
            );
        }
        """,
        skill_name
    )

    page.wait_for_timeout(2500)


def main():

    playwright, context, page = open_profile()

    try:

        open_key_skills_editor(page)

        print("\nKey Skills editor opened.")

        requests = []

        def on_request(request):

            url = request.url

            if (
                "naukri.com" in url
                and (
                    request.method != "GET"
                    or "suggest" in url.lower()
                    or "skill" in url.lower()
                    or "taxonomy" in url.lower()
                )
            ):

                requests.append({
                    "method": request.method,
                    "url": url
                })

        page.on("request", on_request)

        print("\nSearching Docker...")

        enter_skill(
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
            "\nDocker suggestion is visible."
        )

        print(
            "Now click Docker manually with your mouse."
        )

        print(
            "DO NOT click Save."
        )

        input(
            "\nPress ENTER after you have clicked Docker..."
        )

        print(
            "\n========== REQUESTS AFTER SELECTION ==========\n"
        )

        for request in requests:

            print(
                request["method"],
                request["url"]
            )

        print(
            "\n========== FINAL CHIP CHECK ==========\n"
        )

        chips = page.locator(
            "div.sWrap div.chipsContainer div.chip"
        )

        print(
            "Chip count:",
            chips.count()
        )

        for i in range(chips.count()):

            print(
                "-",
                chips.nth(i).get_attribute("title")
            )

        input(
            "\nPress ENTER to close..."
        )

    finally:

        context.close()
        playwright.stop()


if __name__ == "__main__":
    main()