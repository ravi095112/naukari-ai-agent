from pathlib import Path

from naukri_profile import open_profile


BASE_DIR = Path(__file__).resolve().parent.parent
LOG_DIR = BASE_DIR / "logs"


def open_key_skills_editor(page):
    section = page.locator("#lazyKeySkills")

    if section.count() == 0:
        raise RuntimeError("Key Skills section not found")

    section.locator(
        ".widgetHead .edit.icon"
    ).first.click()

    page.wait_for_timeout(1000)

    page.locator(
        "#keySkillSugg"
    ).wait_for(
        state="visible",
        timeout=5000
    )


def enter_skill(page, skill_name):
    skill_input = page.locator(
        "#keySkillSugg"
    )

    skill_input.click()

    value = skill_input.evaluate(
        """
        (element, skillName) => {

            const setter =
                Object.getOwnPropertyDescriptor(
                    HTMLInputElement.prototype,
                    "value"
                ).set;

            setter.call(
                element,
                skillName
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
                        key: "ArrowDown"
                    }
                )
            );

            element.dispatchEvent(
                new KeyboardEvent(
                    "keyup",
                    {
                        bubbles: true,
                        key: "ArrowDown"
                    }
                )
            );

            return element.value;
        }
        """,
        skill_name
    )

    print(
        "Input value:",
        repr(value)
    )

    page.wait_for_timeout(2500)


def inspect_suggestion(page, skill_name):
    suggestion_box = page.locator(
        "#sugDrp_keySkillSugg"
    )

    print(
        "\nSuggestion box visible:",
        suggestion_box.is_visible()
    )

    suggestions = suggestion_box.locator(
        "li.sugTouple"
    )

    print(
        "Suggestion count:",
        suggestions.count()
    )

    exact = None

    for i in range(
        suggestions.count()
    ):

        item = suggestions.nth(i)

        text = item.inner_text().strip()

        print(
            f"{i}: {text}"
        )

        if text.lower() == skill_name.lower():
            exact = item

    if exact is None:
        raise RuntimeError(
            f"Exact suggestion not found: {skill_name}"
        )

    return exact


def inspect_event_handlers(page, element):
    """
    Inspect what browser-level event information is
    available for the selected DOM element.
    """

    return element.evaluate(
        """
        (el) => {

            const events = {};

            for (
                const key of Object.keys(el)
            ) {
                if (
                    key.startsWith("__react")
                    || key.startsWith("__vue")
                    || key.startsWith("on")
                ) {
                    events[key] =
                        String(el[key]);
                }
            }

            return {
                tag: el.tagName,
                id: el.id,
                className: el.className,
                attributes:
                    Array.from(el.attributes)
                        .map(a => ({
                            name: a.name,
                            value: a.value
                        })),
                reactKeys:
                    Object.keys(el)
                        .filter(
                            key =>
                                key.startsWith(
                                    "__react"
                                )
                        ),
                events
            };
        }
        """
    )


def install_event_monitor(page):
    """
    Install browser-side event monitoring before
    the suggestion is clicked.
    """

    page.evaluate(
        """
        () => {

            window.__naukriEvents = [];

            const events = [
                "mousedown",
                "mouseup",
                "click",
                "pointerdown",
                "pointerup",
                "touchstart",
                "touchend"
            ];

            events.forEach(
                eventName => {

                    document.addEventListener(
                        eventName,
                        event => {

                            const target =
                                event.target;

                            window.__naukriEvents.push({
                                type: event.type,
                                tag:
                                    target?.tagName,
                                id:
                                    target?.id,
                                className:
                                    target?.className,
                                text:
                                    target?.innerText,
                                title:
                                    target?.getAttribute(
                                        "title"
                                    ),
                                time:
                                    Date.now()
                            });

                        },
                        true
                    );

                }
            );
        }
        """
    )


def get_events(page):
    return page.evaluate(
        "() => window.__naukriEvents || []"
    )


def get_editor_chips(page):

    chips = page.locator(
        "div.sWrap div.chipsContainer div.chip"
    )

    result = []

    for i in range(
        chips.count()
    ):

        title = chips.nth(i).get_attribute(
            "title"
        )

        if title:
            result.append(title)

    return result


def main():

    playwright, context, page = open_profile()

    try:

        print(
            "\n========== OPENING EDITOR ==========\n"
        )

        open_key_skills_editor(page)

        print(
            "Editor opened."
        )

        install_event_monitor(page)

        skill_name = "Docker"

        print(
            f"\n========== ENTERING {skill_name} ==========\n"
        )

        enter_skill(
            page,
            skill_name
        )

        exact = inspect_suggestion(
            page,
            skill_name
        )

        print(
            "\n========== SUGGESTION DETAILS ==========\n"
        )

        print(
            exact.evaluate(
                "(el) => el.outerHTML"
            )
        )

        print(
            "\n========== REACT / EVENT INSPECTION ==========\n"
        )

        button = exact.locator(
            ".Sbtn"
        )

        details = inspect_event_handlers(
            page,
            button
        )

        print(
            details
        )

        print(
            "\n========== CLICKING SUGGESTION ==========\n"
        )

        button.click()

        page.wait_for_timeout(1000)

        print(
            "Input after click:",
            repr(
                page.locator(
                    "#keySkillSugg"
                ).input_value()
            )
        )

        print(
            "\n========== EVENTS CAPTURED ==========\n"
        )

        events = get_events(page)

        for event in events:
            print(event)

        print(
            "\n========== EDITOR CHIPS ==========\n"
        )

        chips = get_editor_chips(page)

        print(
            "Chip count:",
            len(chips)
        )

        for chip in chips:
            print(
                f"- {chip}"
            )

        print(
            "\n========== PAGE JAVASCRIPT ==========\n"
        )

        print(
            "React root candidates:"
        )

        roots = page.locator(
            "[data-reactroot]"
        )

        print(
            "data-reactroot count:",
            roots.count()
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