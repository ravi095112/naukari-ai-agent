from pathlib import Path

from naukri_profile import open_profile


BASE_DIR = Path(__file__).resolve().parent.parent
LOG_DIR = BASE_DIR / "logs"


def main():
    playwright, context, page = open_profile()

    try:
        print("\n========== Opening Key Skills Editor ==========\n")

        section = page.locator("#lazyKeySkills")

        if section.count() == 0:
            raise RuntimeError(
                "Key Skills section not found"
            )

        section.locator(
            ".widgetHead .edit.icon"
        ).first.click()

        page.wait_for_timeout(1500)

        print(
            "Editor opened."
        )

        # Find likely editor containers
        print(
            "\n========== Inputs ==========\n"
        )

        inputs = page.locator(
            "#lazyKeySkills input"
        )

        print(
            "Input count:",
            inputs.count()
        )

        for i in range(inputs.count()):
            element = inputs.nth(i)

            print(
                f"\n--- Input {i} ---"
            )

            print(
                element.evaluate(
                    "(el) => el.outerHTML"
                )
            )

        # Print the complete Key Skills section
        print(
            "\n========== FULL KEY SKILLS HTML ==========\n"
        )

        html = section.evaluate(
            "(el) => el.outerHTML"
        )

        print(html)

        html_file = LOG_DIR / "keyskills-editor.html"

        html_file.write_text(
            html,
            encoding="utf-8"
        )

        print(
            "\nFull HTML saved to:"
        )

        print(html_file)

        print(
            "\n=========================================="
        )
        print(
            "NO INPUT"
        )
        print(
            "NO SELECTION"
        )
        print(
            "NO SAVE"
        )
        print(
            "==========================================\n"
        )

        input(
            "Press ENTER to close..."
        )

    finally:
        context.close()
        playwright.stop()


if __name__ == "__main__":
    main()