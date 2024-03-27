import reflex as rx  # Importing the reflex library for UI components

from webui.components import loading_icon  # Importing a loading icon component
from webui.state import (
    QA,
    State,
)  # Importing QA class and State for managing application state

# Style dictionary for message components
message_style = dict(
    display="inline-block",  # Ensuring messages are inline and block-level elements
    padding="1em",  # Adding padding around the text for better readability
    border_radius="8px",  # Rounding the corners for a softer look
    max_width=[
        "30em",
        "30em",
        "50em",
        "50em",
        "50em",
        "50em",
    ],  # Responsive max-width settings
)


def message(qa: QA) -> rx.Component:
    """A single question/answer message with a copy icon.

    Args:
        qa: The question/answer pair.

    Returns:
        A component displaying the question/answer pair with a copy icon.
    """
    # Creating a box component for the question part with a copy icon on the right
    question_box = rx.radix.box(
        rx.hstack(
            rx.radix.text(
                qa.question,  # Displaying the question text
                background_color=rx.color(
                    "mauve", 4
                ),  # Setting a light mauve background for the question
                color=rx.color("mauve", 12),  # Dark mauve text color for contrast
                **message_style,  # Applying the predefined style
            ),
            rx.icon_button(
                "copy",
                size="1",
                on_click=rx.set_clipboard(qa.question),
                tooltip="Copy question",
            ),  # Adding a copy button
            spacing="1",
        ),
        text_align="right",  # Aligning the question to the right
        margin_top="1em",  # Adding a top margin for spacing between messages
        justify_content="flex-end",  # Ensuring the content is aligned to the right
    )
    # Creating a box component for the answer part with a copy icon on the left
    answer_box = rx.radix.box(
        rx.hstack(
            rx.icon_button(
                "copy",
                size="1",
                on_click=rx.set_clipboard(qa.answer),
                tooltip="Copy answer",
            ),  # Adding a copy button
            rx.markdown(
                qa.answer,  # Displaying the answer text
                background_color=rx.color(
                    "accent", 4
                ),  # Setting a light accent color background for the answer
                color=rx.color("accent", 12),  # Dark accent text color for readability
                **message_style,  # Applying the predefined style
            ),
            spacing="1",
        ),
        text_align="left",  # Aligning the answer to the left
        padding_top="1em",  # Adding top padding for spacing within the answer box
    )
    # Combining question and answer boxes into a single component, with conditional alignment
    return rx.radix.box(
        rx.radix.box(
            question_box,
            width="100%",
            display="flex",
            justify_content="flex-end",  # Aligning question box to the right
        ),
        rx.radix.box(
            answer_box,
            width="100%",
            display="flex",
            justify_content="flex-start",  # Aligning answer box to the left
        ),
        direction="column",  # Stacking question and answer vertically
    )


def chat() -> rx.Component:
    """List all the messages in a single conversation."""
    # Creating a vertical stack of message components for each chat
    return rx.radix.vstack(
        rx.radix.box(
            rx.foreach(State.chats[State.current_chat], message),
            width="100%",  # Iterating over chat messages
        ),
        py="8",  # Vertical padding
        flex="1",  # Flex grow to fill available space
        width="100%",  # Full width
        max_width="60em",  # Maximum width for better readability on large screens
        padding_x="4px",  # Horizontal padding for slight spacing
        align_self="center",  # Centering the chat vertically
        overflow="hidden",  # Hiding overflow
        padding_bottom="5em",  # Bottom padding to avoid overlap with the action bar
    )


def action_bar() -> rx.Component:
    """The action bar to send a new message."""
    # Creating a form for sending new messages
    form = rx.chakra.form(
        rx.chakra.form_control(
            rx.hstack(
                rx.radix.text_field.root(
                    rx.radix.text_field.input(
                        placeholder="Type something...",  # Placeholder text
                        id="question",  # Input field ID
                        width=[
                            "15em",
                            "20em",
                            "30em",
                            "30em",
                            "30em",
                            "30em",
                        ],  # Responsive width settings
                    ),
                    rx.radix.text_field.slot(
                        rx.tooltip(
                            rx.icon("info", size=18),  # Info icon for tooltip
                            content="Enter a question to get a response.",  # Tooltip text
                        )
                    ),
                ),
                rx.button(
                    rx.cond(
                        State.processing,  # Conditional rendering based on processing state
                        loading_icon(height="1em"),  # Show loading icon if processing
                        rx.text("Send"),  # Show "Send" text if not processing
                    ),
                    type="submit",  # Button type for form submission
                ),
                align_items="center",  # Aligning items in the horizontal stack
            ),
            is_disabled=State.processing,  # Disabling form control while processing
        ),
        on_submit=State.process_question,  # Handling form submission
        reset_on_submit=True,  # Resetting form after submission
    )
    # Adding a disclaimer text below the form
    disclaimer_text = rx.text(
        "ReflexGPT may return factually incorrect or misleading responses. Use discretion.",
        text_align="center",  # Centering the text
        font_size=".75em",  # Smaller font size for the disclaimer
        color=rx.color("mauve", 10),  # Setting the text color
    )
    # Combining form and disclaimer into a vertical stack and making it sticky at the bottom
    return rx.center(
        rx.vstack(
            form, disclaimer_text, align_items="center"
        ),  # Vertical stack of form and disclaimer
        position="sticky",  # Making the action bar sticky
        bottom="0",  # Positioning at the bottom
        left="0",  # Aligning to the left
        padding_y="16px",  # Vertical padding
        backdrop_filter="auto",  # Enabling backdrop filter
        backdrop_blur="lg",  # Applying a large blur effect
        border_top=f"1px solid {rx.color('mauve', 3)}",  # Top border for separation
        background_color=rx.color("mauve", 2),  # Background color
        align_items="stretch",  # Stretching items to fill the available space
        width="100%",  # Full width
    )
