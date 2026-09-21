from pathlib import Path
from playwright.sync_api import sync_playwright


BASE_DIR = Path(__file__).resolve().parent.parent
BROWSER_DATA = BASE_DIR / "data" / "naukri-browser"

PROFILE_URL = "https://www.naukri.com/mnjuser/profile"


def main():

    print("========================================")
    print("Naukri Resume UI Discovery")
    print("READ-ONLY MODE")
    print("========================================")

    with sync_playwright() as p:

        context = p.chromium.launch_persistent_context(
            user_data_dir=str(BROWSER_DATA),
            headless=False,
            viewport={
                "width": 1440,
                "height": 900,
            },
        )

        page = (
            context.pages[0]
            if context.pages
            else context.new_page()
        )

        print("\nOpening Naukri profile...")

        page.goto(
            PROFILE_URL,
            wait_until="domcontentloaded",
            timeout=60000,
        )

        page.wait_for_timeout(5000)

        print("\nCurrent URL:")
        print(page.url)

        print("\nPage title:")
        print(page.title())

        # --------------------------------------------------
        # Look for likely resume-related elements
        # --------------------------------------------------

        print("\n========================================")
        print("RESUME ELEMENT DISCOVERY")
        print("========================================")

        selectors = [
            "#lazyResumeHead",
            "#lazyResume",
            "[class*='resume']",
            "[id*='resume']",
            "[class*='Resume']",
            "[id*='Resume']",
        ]

        found = set()

        for selector in selectors:

            try:
                count = page.locator(selector).count()

                if count > 0:

                    print(
                        f"\nSelector: {selector}"
                    )

                    print(
                        f"Matches : {count}"
                    )

                    found.add(selector)

            except Exception as exc:

                print(
                    f"\nSelector error: "
                    f"{selector}"
                )

                print(exc)

        # --------------------------------------------------
        # Search visible text for resume references
        # --------------------------------------------------

        print("\n========================================")
        print("VISIBLE RESUME TEXT")
        print("========================================")

        resume_text_patterns = [
            "resume",
            "upload",
            "update resume",
            "download resume",
            "view resume",
        ]

        body_text = page.locator(
            "body"
        ).inner_text()

        body_lines = [
            line.strip()
            for line in body_text.splitlines()
            if line.strip()
        ]

        matched_lines = []

        for line in body_lines:

            lower_line = line.lower()

            if any(
                    pattern in lower_line
                    for pattern in resume_text_patterns
            ):
                matched_lines.append(line)

        if matched_lines:

            for line in matched_lines[:50]:
                print(f"- {line}")

        else:

            print(
                "No obvious resume text found."
            )

        # --------------------------------------------------
        # Inspect buttons and links
        # --------------------------------------------------

        print("\n========================================")
        print("RESUME-RELATED BUTTONS / LINKS")
        print("========================================")

        elements = page.locator(
            "button, a, input"
        )

        matches = 0

        for i in range(elements.count()):

            element = elements.nth(i)

            try:

                text = (
                    element.inner_text(
                        timeout=500
                    ).strip()
                )

            except Exception:
                text = ""

            try:

                aria = (
                        element.get_attribute(
                            "aria-label"
                        )
                        or ""
                ).strip()

            except Exception:
                aria = ""

            try:

                title = (
                        element.get_attribute(
                            "title"
                        )
                        or ""
                ).strip()

            except Exception:
                title = ""

            try:

                placeholder = (
                        element.get_attribute(
                            "placeholder"
                        )
                        or ""
                ).strip()

            except Exception:
                placeholder = ""

            combined = " ".join(
                [
                    text,
                    aria,
                    title,
                    placeholder,
                ]
            ).lower()

            if any(
                    keyword in combined
                    for keyword in [
                        "resume",
                        "upload",
                        "update",
                        "attach",
                    ]
            ):

                matches += 1

                print(
                    f"\nElement #{i}"
                )

                print(
                    f"Tag         : "
                    f"{element.evaluate('(e) => e.tagName')}"
                )

                print(
                    f"Text        : {text}"
                )

                print(
                    f"Aria-label  : {aria}"
                )

                print(
                    f"Title       : {title}"
                )

                print(
                    f"Placeholder : {placeholder}"
                )

                try:

                    print(
                        f"Class       : "
                        f"{element.get_attribute('class')}"
                    )

                    print(
                        f"ID          : "
                        f"{element.get_attribute('id')}"
                    )

                    print(
                        f"Name        : "
                        f"{element.get_attribute('name')}"
                    )

                except Exception:
                    pass

        if matches == 0:

            print(
                "No resume-related controls "
                "were detected."
            )

        # --------------------------------------------------
        # File inputs
        # --------------------------------------------------

        print("\n========================================")
        print("FILE INPUT DISCOVERY")
        print("========================================")

        file_inputs = page.locator(
            "input[type='file']"
        )

        file_count = file_inputs.count()

        print(
            f"File input count: {file_count}"
        )

        for i in range(file_count):

            element = file_inputs.nth(i)

            print(
                f"\nFile input #{i}"
            )

            print(
                f"ID      : "
                f"{element.get_attribute('id')}"
            )

            print(
                f"Name    : "
                f"{element.get_attribute('name')}"
            )

            print(
                f"Class   : "
                f"{element.get_attribute('class')}"
            )

            print(
                f"Accept  : "
                f"{element.get_attribute('accept')}"
            )

        # --------------------------------------------------
        # Save screenshot for inspection
        # --------------------------------------------------

        screenshot_path = (
                BASE_DIR
                / "logs"
                / "resume-discovery.png"
        )

        screenshot_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        page.screenshot(
            path=str(screenshot_path),
            full_page=True,
        )

        print("\n========================================")
        print("DISCOVERY COMPLETE")
        print("========================================")

        print(
            f"\nScreenshot saved:"
            f"\n{screenshot_path}"
        )

        print(
            "\nIMPORTANT:"
        )

        print(
            "No upload button was clicked."
        )

        print(
            "No resume was changed."
        )

        print(
            "No Naukri profile data was modified."
        )

        context.close()


if __name__ == "__main__":
    main()
