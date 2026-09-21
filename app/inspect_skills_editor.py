from pathlib import Path

from naukri_profile import open_profile


BASE_DIR = Path(__file__).resolve().parent.parent
LOG_DIR = BASE_DIR / "logs"


def main():

    playwright, context, page = open_profile()

    try:

        print("\nOpening Key Skills editor...")

        section = page.locator("#lazyKeySkills")

        if section.count() == 0:
            raise RuntimeError(
                "Key Skills section not found"
            )

        edit_button = section.locator(
            ".widgetHead .edit.icon"
        )

        print(
            f"Edit buttons found: {edit_button.count()}"
        )

        if edit_button.count() == 0:
            raise RuntimeError(
                "Key Skills edit button not found"
            )

        edit_button.first.click()

        page.wait_for_timeout(1500)

        screenshot = (
            LOG_DIR /
            "skills-editor.png"
        )

        page.screenshot(
            path=str(screenshot),
            full_page=True,
        )

        print(
            f"\nScreenshot saved to:\n"
            f"{screenshot}"
        )

        print(
            "\n========== Visible Inputs ==========\n"
        )

        inputs = page.locator(
            "input:visible, textarea:visible"
        )

        for i in range(inputs.count()):

            element = inputs.nth(i)

            print(
                f"[{i}] "
                f"tag={element.evaluate('(e) => e.tagName')} "
                f"name={element.get_attribute('name')} "
                f"class={element.get_attribute('class')} "
                f"placeholder={element.get_attribute('placeholder')}"
            )

        print(
            "\n========== Visible Buttons ==========\n"
        )

        buttons = page.locator(
            "button:visible"
        )

        for i in range(buttons.count()):

            button = buttons.nth(i)

            try:
                text = button.inner_text().strip()
            except Exception:
                text = ""

            print(
                f"[{i}] "
                f"text='{text}' "
                f"class={button.get_attribute('class')}"
            )

        print(
            "\n========== Editor HTML ==========\n"
        )

        print(
            section.inner_text()
        )

        print(
            "\nEditor inspection complete."
        )

        input(
            "\nPress ENTER to close without saving..."
        )

    finally:

        context.close()
        playwright.stop()


if __name__ == "__main__":
    main()
