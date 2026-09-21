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

    page.goto(
        PROFILE_URL,
        wait_until="domcontentloaded",
        timeout=60000,
    )

    page.wait_for_timeout(5000)

    section = page.locator("#lazyKeySkills")

    edit_button = section.locator(
        ".widgetHead .edit.icon"
    )

    edit_button.click()

    input_box = page.locator(
        'input[name="suggestor"]#keySkillSugg:visible'
    )

    input_box.wait_for(
        state="visible",
        timeout=5000,
    )

    print("\nKey Skills editor opened.")

    input_box.fill("GenAI")

    print("Typed: GenAI")

    # Give Naukri time to call its suggestion API
    page.wait_for_timeout(3000)

    print("\n========== SUGGESTION INSPECTION ==========\n")

    # Check our previous selector
    selector = "#sugDrp_keySkillSugg li.sugTouple"

    suggestions = page.locator(selector)

    print(f"Selector: {selector}")
    print(f"Count  : {suggestions.count()}")

    for i in range(suggestions.count()):
        item = suggestions.nth(i)

        print(f"\nSuggestion #{i + 1}")
        print("Text :", item.inner_text())
        print("HTML :", item.evaluate("(el) => el.outerHTML"))

    # Inspect the entire suggestion container
    dropdown = page.locator("#sugDrp_keySkillSugg")

    print("\n========== DROPDOWN ==========\n")

    print(
        f"Dropdown count: {dropdown.count()}"
    )

    if dropdown.count():
        print(
            dropdown.first.evaluate(
                "(el) => el.outerHTML"
            )
        )

    # Inspect elements containing GenAI
    print("\n========== GENAI ELEMENTS ==========\n")

    genai_elements = page.get_by_text(
        "GenAI",
        exact=False,
    )

    print(
        f"Elements containing GenAI: "
        f"{genai_elements.count()}"
    )

    for i in range(
        min(genai_elements.count(), 20)
    ):
        element = genai_elements.nth(i)

        try:
            print(
                f"\nElement #{i + 1}:"
            )
            print(
                element.evaluate(
                    "(el) => el.outerHTML"
                )
            )
        except Exception:
            pass

    print(
        "\nBrowser will remain open."
    )

    input(
        "\nPress ENTER to close..."
    )

    context.close()