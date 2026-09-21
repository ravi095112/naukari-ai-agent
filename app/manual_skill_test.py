from pathlib import Path
from playwright.sync_api import sync_playwright

BASE_DIR = Path(__file__).resolve().parent.parent
BROWSER_DATA = BASE_DIR / "data" / "naukri-browser"
PROFILE_URL = "https://www.naukri.com/mnjuser/profile"

with sync_playwright() as p:
    context = p.chromium.launch_persistent_context(
        user_data_dir=str(BROWSER_DATA),
        headless=False,
        viewport={"width": 1440, "height": 900},
    )

    page = context.pages[0] if context.pages else context.new_page()

    print("\nOpening Naukri profile...")
    page.goto(PROFILE_URL, wait_until="domcontentloaded", timeout=60000)
    page.wait_for_timeout(5000)

    section = page.locator("#lazyKeySkills")
    section.scroll_into_view_if_needed()

    print("Clicking Key Skills edit...")
    section.locator(".widgetHead .edit.icon").click()

    input_box = page.locator(
        'input[name="suggestor"]#keySkillSugg:visible'
    )
    input_box.wait_for(state="visible", timeout=5000)

    print("\n========== REACT EVENT TEST ==========")

    # Remove the suspicious maxlength.
    page.evaluate("""
        () => {
            const input = document.querySelector(
                'input[name="suggestor"]#keySkillSugg'
            );

            if (input) {
                input.removeAttribute("maxlength");
                input.focus();
            }
        }
    """)

    print("maxlength:",
          input_box.get_attribute("maxlength"))

    # Clear.
    input_box.click()
    page.keyboard.press("Control+A")
    page.keyboard.press("Backspace")

    print("\nEntering Docker character by character...")

    for char in "Docker":
        # Set the value using the native HTMLInputElement setter.
        page.evaluate(
            """
            (char) => {
                const input = document.querySelector(
                    'input[name="suggestor"]#keySkillSugg'
                );

                const setter = Object.getOwnPropertyDescriptor(
                    HTMLInputElement.prototype,
                    "value"
                ).set;

                setter.call(input, input.value + char);

                input.dispatchEvent(
                    new Event("input", { bubbles: true })
                );

                input.dispatchEvent(
                    new Event("change", { bubbles: true })
                );

                input.dispatchEvent(
                    new KeyboardEvent("keyup", {
                        bubbles: true,
                        key: char
                    })
                );
            }
            """,
            char,
        )

        page.wait_for_timeout(700)

        print(
            f"Typed: {char} | Current value:",
            repr(input_box.input_value())
        )

    print("\nWaiting for autocomplete...")
    page.wait_for_timeout(5000)

    print("\nFinal value:")
    print(repr(input_box.input_value()))

    suggestions = page.locator(
        "#sugDrp_keySkillSugg li.sugTouple:visible"
    )

    print("\nSuggestion count:", suggestions.count())

    for i in range(min(suggestions.count(), 10)):
        print(
            f"{i + 1}.",
            suggestions.nth(i).inner_text().strip()
        )

    # Also inspect the suggestion container itself.
    dropdown = page.locator("#sugDrp_keySkillSugg")

    print("\nDropdown count:", dropdown.count())

    if dropdown.count():
        print(
            "Dropdown visible:",
            dropdown.is_visible()
        )

        print(
            "Dropdown text:",
            repr(dropdown.inner_text())
        )

        print(
            "Dropdown HTML:",
            (dropdown.inner_html())[:3000]
        )

    print("\n========== END TEST ==========")
    print("Do NOT click Save.")

    input("\nPress ENTER to close...")

    context.close()