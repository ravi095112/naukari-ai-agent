from pathlib import Path
from playwright.sync_api import sync_playwright

BASE_DIR = Path(__file__).resolve().parent.parent
BROWSER_DATA = BASE_DIR / "data" / "naukri-browser"

RESUME_FILE = BASE_DIR / "Ravi_Kumar_Updated_Resume.docx"
PROFILE_URL = "https://www.naukri.com/mnjuser/profile"
SCREENSHOT = BASE_DIR / "logs" / "resume-network-capture.png"


def main():
    print()
    print("========================================")
    print("NAUKRI RESUME UPLOAD NETWORK CAPTURE")
    print("========================================")
    print()

    if not RESUME_FILE.exists():
        raise FileNotFoundError(
            f"Resume not found:\n{RESUME_FILE}"
        )

    playwright = sync_playwright().start()

    context = playwright.chromium.launch_persistent_context(
        user_data_dir=str(BROWSER_DATA),
        headless=False,
        viewport={"width": 1440, "height": 900},
    )

    page = context.pages[0] if context.pages else context.new_page()

    requests = []
    responses = []

    def on_request(request):
        # Capture POST/PUT/PATCH requests and anything
        # related to resume/upload/parser/profile.
        url = request.url.lower()

        interesting = (
                request.method in ["POST", "PUT", "PATCH"]
                or any(
            keyword in url
            for keyword in [
                "resume",
                "upload",
                "parser",
                "profile",
                "attach",
                "cv",
            ]
        )
        )

        if interesting:
            item = {
                "method": request.method,
                "url": request.url,
                "resource_type": request.resource_type,
            }

            requests.append(item)

            print()
            print(">>> REQUEST")
            print(f"METHOD : {request.method}")
            print(f"TYPE   : {request.resource_type}")
            print(f"URL    : {request.url}")

            try:
                post_data = request.post_data

                if post_data:
                    print(
                        f"POST DATA PRESENT: "
                        f"{len(post_data)} characters"
                    )
            except Exception:
                pass

    def on_response(response):
        url = response.url.lower()

        interesting = (
                response.request.method in ["POST", "PUT", "PATCH"]
                or any(
            keyword in url
            for keyword in [
                "resume",
                "upload",
                "parser",
                "profile",
                "attach",
                "cv",
            ]
        )
        )

        if interesting:
            item = {
                "status": response.status,
                "url": response.url,
                "method": response.request.method,
            }

            responses.append(item)

            print()
            print("<<< RESPONSE")
            print(f"STATUS : {response.status}")
            print(f"METHOD : {response.request.method}")
            print(f"URL    : {response.url}")

            # Try to read a small response body.
            try:
                body = response.text()

                if body:
                    print(
                        f"BODY ({min(len(body), 2000)} chars):"
                    )
                    print(body[:2000])
            except Exception as e:
                print(
                    f"Could not read response body: {e}"
                )

    page.on("request", on_request)
    page.on("response", on_response)

    try:
        # --------------------------------------------------
        # Open profile
        # --------------------------------------------------

        print("Opening Naukri profile...")

        page.goto(
            PROFILE_URL,
            wait_until="domcontentloaded",
            timeout=60000,
        )

        page.wait_for_timeout(5000)

        print(f"Title: {page.title()}")
        print(f"URL  : {page.url}")

        # --------------------------------------------------
        # Open resume update UI
        # --------------------------------------------------

        updates = page.get_by_text(
            "Update",
            exact=True,
        )

        profile_update = None

        for i in range(updates.count()):
            candidate = updates.nth(i)

            try:
                if candidate.is_visible():
                    profile_update = candidate
                    break
            except Exception:
                pass

        if profile_update is None:
            raise RuntimeError(
                "Profile Update control not found."
            )

        print()
        print("Clicking profile Update...")
        profile_update.click()

        page.wait_for_timeout(1500)

        # --------------------------------------------------
        # Update resume button
        # --------------------------------------------------

        update_resume = page.locator(
            'input[type="button"][value="Update resume"]'
        )

        if update_resume.count() != 1:
            raise RuntimeError(
                "Update resume button not found."
            )

        print(
            "Update resume button found."
        )

        # --------------------------------------------------
        # Clear previous captured network activity
        # --------------------------------------------------

        requests.clear()
        responses.clear()

        print()
        print("========================================")
        print("SELECTING RESUME")
        print("========================================")
        print()

        print(
            "The file will be selected through "
            "the verified Naukri file chooser."
        )

        print()
        print(f"FILE: {RESUME_FILE}")

        # --------------------------------------------------
        # File chooser
        # --------------------------------------------------

        with page.expect_file_chooser(
                timeout=5000
        ) as chooser_info:

            update_resume.click()

        chooser = chooser_info.value

        print()
        print(
            f"Chooser element: "
            f"{chooser.element.get_attribute('id')}"
        )

        # --------------------------------------------------
        # Select actual master resume
        # --------------------------------------------------

        chooser.set_files(
            str(RESUME_FILE)
        )

        print()
        print("FILE SELECTED.")
        print()
        print(
            "Waiting for Naukri's JavaScript/network "
            "processing..."
        )

        # Give React/Naukri enough time to process.
        page.wait_for_timeout(5000)

        # --------------------------------------------------
        # Final network summary
        # --------------------------------------------------

        print()
        print("========================================")
        print("NETWORK SUMMARY")
        print("========================================")

        print()
        print(
            f"Requests captured: "
            f"{len(requests)}"
        )

        for i, item in enumerate(requests, 1):
            print()
            print(
                f"REQUEST {i}"
            )
            print(
                f"  {item['method']} "
                f"{item['resource_type']}"
            )
            print(
                f"  {item['url']}"
            )

        print()
        print(
            f"Responses captured: "
            f"{len(responses)}"
        )

        for i, item in enumerate(responses, 1):
            print()
            print(
                f"RESPONSE {i}"
            )
            print(
                f"  STATUS: {item['status']}"
            )
            print(
                f"  {item['method']}"
            )
            print(
                f"  {item['url']}"
            )

        # --------------------------------------------------
        # Inspect result container
        # --------------------------------------------------

        print()
        print("========================================")
        print("RESUME PARSER RESULT")
        print("========================================")

        result = page.locator(
            "#results_resumeParser"
        )

        if result.count():
            try:
                print(
                    result.inner_text()
                )
            except Exception:
                print(
                    result.evaluate(
                        "(e) => e.outerHTML"
                    )[:5000]
                )

        # --------------------------------------------------
        # Inspect visible controls
        # --------------------------------------------------

        print()
        print("========================================")
        print("VISIBLE CONTROLS AFTER PROCESSING")
        print("========================================")

        controls = page.locator(
            "button:visible, "
            "a:visible, "
            "input:visible"
        )

        for i in range(controls.count()):
            try:
                element = controls.nth(i)

                tag = element.evaluate(
                    "(e) => e.tagName"
                )

                text = ""

                try:
                    text = element.inner_text().strip()
                except Exception:
                    pass

                value = element.get_attribute(
                    "value"
                )

                element_id = element.get_attribute(
                    "id"
                )

                element_class = element.get_attribute(
                    "class"
                )

                if text or value or element_id:
                    print(
                        f"[{i}] "
                        f"tag={tag} "
                        f"id={element_id} "
                        f"value={value} "
                        f"text={text[:150]} "
                        f"class={element_class}"
                    )

            except Exception:
                pass

        # --------------------------------------------------
        # Screenshot
        # --------------------------------------------------

        SCREENSHOT.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        page.screenshot(
            path=str(SCREENSHOT),
            full_page=True,
        )

        print()
        print("========================================")
        print("SAFE STOP")
        print("========================================")
        print()
        print(
            "The approved master resume was selected "
            "for diagnostic purposes."
        )
        print()
        print(
            "No explicit Save/Submit/Update action "
            "was clicked after file selection."
        )
        print()
        print(
            "If Naukri uploads immediately on selection, "
            "the network capture will show it."
        )
        print()
        print(
            f"Screenshot: {SCREENSHOT}"
        )
        print()
        print(
            "Press ENTER to close the browser."
        )

        input()

    finally:
        context.close()
        playwright.stop()


if __name__ == "__main__":
    main()

