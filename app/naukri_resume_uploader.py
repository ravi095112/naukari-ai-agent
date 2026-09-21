from pathlib import Path
from datetime import datetime, timezone
import json

from playwright.sync_api import sync_playwright


BASE_DIR = Path(__file__).resolve().parent.parent

BROWSER_DATA = BASE_DIR / "data" / "naukri-browser"

RESUME_FILE = BASE_DIR / "Ravi_Kumar_Updated_Resume.docx"

RESUME_DATA_DIR = BASE_DIR / "data" / "resume"
ANALYSIS_FILE = RESUME_DATA_DIR / "resume_change_analysis.json"

LOG_DIR = BASE_DIR / "logs"
AUDIT_FILE = LOG_DIR / "resume_upload_audit.jsonl"

PROFILE_URL = "https://www.naukri.com/mnjuser/profile"


def load_approved_analysis():
    if not ANALYSIS_FILE.exists():
        raise FileNotFoundError(
            f"Resume analysis not found:\n"
            f"{ANALYSIS_FILE}\n\n"
            "Run resume analysis first."
        )

    with ANALYSIS_FILE.open(
            "r",
            encoding="utf-8",
    ) as f:
        return json.load(f)


def verify_approval(analysis):
    """
    Validate whether a resume upload is actually required and approved.

    Returns:
        True  -> approved upload may proceed
        False -> safe no-op / blocked
    """

    changed = analysis.get("changed", False)
    meaningful_change_count = analysis.get("meaningful_change_count", 0)
    approval_status = analysis.get("approval_status", "NOT_REQUIRED")
    naukri_upload_approved = analysis.get("naukri_upload_approved", False)

    # Normal no-op: resume has not changed.
    if not changed or meaningful_change_count == 0:
        print()
        print("========================================")
        print("NO RESUME UPDATE REQUIRED")
        print("========================================")
        print()
        print("Resume is unchanged.")
        print("No Naukri upload will be performed.")
        return False

    # Change exists but user has not approved it.
    if approval_status != "APPROVED":
        print()
        print("========================================")
        print("UPLOAD BLOCKED")
        print("========================================")
        print()
        print(f"Approval status: {approval_status}")
        print("Resume changes require explicit approval.")
        return False

    # Approval exists but upload permission is missing.
    if not naukri_upload_approved:
        print()
        print("========================================")
        print("UPLOAD BLOCKED")
        print("========================================")
        print()
        print("Naukri upload approval is not enabled.")
        return False

    print()
    print("Approval verified.")
    print("Proceeding with approved resume upload...")
    return True



def write_audit(event):
    LOG_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    record = {
        "timestamp": datetime.now(
            timezone.utc
        ).isoformat(),
        **event,
    }

    with AUDIT_FILE.open(
            "a",
            encoding="utf-8",
    ) as f:
        f.write(
            json.dumps(
                record,
                ensure_ascii=False,
            )
            + "\n"
        )


def get_visible_resume_text(page):
    section = page.locator(
        "#lazyResumeHead"
    )

    if section.count() == 0:
        raise RuntimeError(
            "Resume section #lazyResumeHead not found."
        )

    return section.inner_text().strip()


def main():

    print("========================================")
    print("Naukri Resume Uploader - Step 7")
    print("APPROVED UPLOAD MODE")
    print("========================================")

    # --------------------------------------------------
    # Validate local resume
    # --------------------------------------------------

    if not RESUME_FILE.exists():
        raise FileNotFoundError(
            f"Master resume not found:\n"
            f"{RESUME_FILE}"
        )

    print("\nMaster resume:")
    print(RESUME_FILE)

    # --------------------------------------------------
    # Validate approval
    # --------------------------------------------------

    analysis = load_approved_analysis()

    print("\nChecking approval gate...")

    if not verify_approval(analysis):
        return

    print("Meaningful change: CONFIRMED")
    print("Approval status    : APPROVED")
    print("Naukri upload      : APPROVED")

    # --------------------------------------------------
    # Open Naukri
    # --------------------------------------------------

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

        print(
            f"Current URL:\n{page.url}"
        )

        # --------------------------------------------------
        # Read current resume
        # --------------------------------------------------

        before_text = get_visible_resume_text(
            page
        )

        print("\nCurrent resume section:")
        print("----------------------------------------")
        print(before_text)
        print("----------------------------------------")

        # --------------------------------------------------
        # Locate controls
        # --------------------------------------------------

        update_control = page.get_by_text(
            "Update",
            exact=True,
        )

        if update_control.count() == 0:
            raise RuntimeError(
                "Naukri Update control was not found."
            )

        file_input = page.locator(
            "#attachCV"
        )

        if file_input.count() == 0:
            raise RuntimeError(
                "Naukri resume file input #attachCV "
                "was not found."
            )

        # --------------------------------------------------
        # Open resume update UI
        # --------------------------------------------------

        print("\nOpening resume update UI...")

        update_control.first.click()

        page.wait_for_timeout(1000)

        upload_option = page.get_by_text(
            "Yes, upload new",
            exact=True,
        )

        if upload_option.count() == 0:
            raise RuntimeError(
                "Naukri 'Yes, upload new' option "
                "was not found."
            )

        print(
            "Upload option found."
        )

        # --------------------------------------------------
        # Select local resume
        # --------------------------------------------------

        print(
            "\nSelecting master resume..."
        )

        file_input.set_input_files(
            str(RESUME_FILE)
        )

        page.wait_for_timeout(2000)

        print(
            "Resume file selected successfully."
        )

        # --------------------------------------------------
        # IMPORTANT:
        # Do not guess a Save button.
        #
        # Inspect visible controls after file selection.
        # --------------------------------------------------

        print("\n========================================")
        print("POST-UPLOAD UI INSPECTION")
        print("========================================")

        buttons = page.locator(
            "button, a"
        )

        for i in range(
                min(buttons.count(), 150)
        ):

            element = buttons.nth(i)

            try:
                text = (
                    element.inner_text(
                        timeout=300
                    ).strip()
                )
            except Exception:
                text = ""

            if text:
                lowered = text.lower()

                if any(
                        word in lowered
                        for word in [
                            "save",
                            "upload",
                            "update",
                            "submit",
                            "confirm",
                        ]
                ):
                    print(
                        f"Control #{i}: {text}"
                    )

        print("\n========================================")
        print("UPLOAD FILE SELECTED")
        print("========================================")

        print(
            "\nThe file has been selected in Naukri."
        )

        print(
            "The script will NOT guess or click "
            "a final Save/Submit control."
        )

        print(
            "\nThis run stops here intentionally."
        )

        print(
            "No final upload submission was performed."
        )

        # --------------------------------------------------
        # Audit the safe stage
        # --------------------------------------------------

        write_audit({
            "event": "resume_upload_file_selected",
            "status": "PENDING_FINAL_SUBMISSION",
            "resume_file": RESUME_FILE.name,
            "analysis_file": str(
                ANALYSIS_FILE
            ),
        })

        print(
            f"\nAudit written to:\n{AUDIT_FILE}"
        )

        context.close()


if __name__ == "__main__":
    main()