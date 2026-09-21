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

        page.wait_for_timeout(1000)

        # --------------------------------------------------
        # Find the editor globally
        # --------------------------------------------------

        print(
            "\n========== GLOBAL EDITOR SEARCH ==========\n"
        )

        skill_input = page.locator(
            "#keySkillSugg"
        )

        print(
            "keySkillSugg count:",
            skill_input.count()
        )

        if skill_input.count() == 0:
            raise RuntimeError(
                "keySkillSugg was not found globally"
            )

        print(
            "Input visible:",
            skill_input.is_visible()
        )

        print(
            "\nInput HTML:"
        )

        print(
            skill_input.evaluate(
                "(el) => el.outerHTML"
            )
        )

        # --------------------------------------------------
        # Find parent hierarchy
        # --------------------------------------------------

        print(
            "\n========== PARENT HIERARCHY ==========\n"
        )

        parent_html = skill_input.evaluate(
            """(el) => {
                let result = [];
                let current = el;

                for (let i = 0; i < 8 && current; i++) {
                    result.push({
                        level: i,
                        tag: current.tagName,
                        id: current.id,
                        className: current.className,
                        html: current.outerHTML.substring(0, 3000)
                    });

                    current = current.parentElement;
                }

                return result;
            }"""
        )

        for item in parent_html:
            print(
                f"\n========== LEVEL {item['level']} =========="
            )

            print(
                f"TAG       : {item['tag']}"
            )

            print(
                f"ID        : {item['id']}"
            )

            print(
                f"CLASS     : {item['className']}"
            )

            print(
                item["html"]
            )

        # --------------------------------------------------
        # Find Save buttons globally
        # --------------------------------------------------

        print(
            "\n========== SAVE BUTTONS ==========\n"
        )

        save_buttons = page.get_by_text(
            "Save",
            exact=True
        )

        print(
            "Save button count:",
            save_buttons.count()
        )

        for i in range(save_buttons.count()):
            button = save_buttons.nth(i)

            print(
                f"\n--- Save {i} ---"
            )

            print(
                "Visible:",
                button.is_visible()
            )

            print(
                button.evaluate(
                    "(el) => el.outerHTML"
                )
            )

        # --------------------------------------------------
        # Find editor-like containers
        # --------------------------------------------------

        print(
            "\n========== POSSIBLE EDITOR CONTAINERS ==========\n"
        )

        containers = page.locator(
            "div"
        ).filter(
            has=page.locator("#keySkillSugg")
        )

        print(
            "Containers containing input:",
            containers.count()
        )

        for i in range(
            min(containers.count(), 10)
        ):
            container = containers.nth(i)

            try:
                print(
                    f"\n--- Container {i} ---"
                )

                print(
                    container.evaluate(
                        "(el) => el.outerHTML"
                    )[:5000]
                )

            except Exception:
                pass

        # --------------------------------------------------
        # Screenshot
        # --------------------------------------------------

        screenshot = LOG_DIR / "keyskills-portal.png"

        page.screenshot(
            path=str(screenshot),
            full_page=True
        )

        print(
            "\nScreenshot saved:"
        )

        print(screenshot)

        print(
            "\n=========================================="
        )

        print(
            "NO SKILL SELECTED"
        )

        print(
            "NO SAVE CLICKED"
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