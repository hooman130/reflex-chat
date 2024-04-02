import reflex as rx  # Importing the reflex library for UI components

from webui.components import loading_icon  # Importing a loading icon component
from webui.state import (
    QA,
    State,
)  # Importing QA class and State for managing application state

# Define a consistent color palette
PRIMARY_COLOR = "#3b82f6"  # No change, assuming it's already suitable
SECONDARY_COLOR = "#64b5f6"  # Lighter shade for hover effect
ACCENT_COLOR = "#ffbaba"  # Softer accent color for answers

# Update the message_style dictionary
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


def message(qa: QA, index: int, chat_name: str) -> rx.Component:
    """A single question/answer message with a copy icon.

    Args:
        qa: The question/answer pair.

    Returns:
        A component displaying the question/answer pair with a copy icon.
    """
    # Creating a box component for the question part with a copy icon on the right
    question_box = rx.box(
        rx.text(
            qa.question,
            background_color=PRIMARY_COLOR,
            color="white",
            **message_style,
            transition="background-color 0.2s ease-in-out",
            on_hover={
                "background-color": SECONDARY_COLOR,
            },
        ),  # Adding a copy button
        text_align="right",  # Aligning the question to the right
        margin_top="1em",  # Adding a top margin for spacing between messages
        justify_content="flex-end",  # Ensuring the content is aligned to the right
    )
    # Creating a box component for the answer part with a copy icon on the left
    answer_box = rx.box(
        rx.markdown(
            qa.answer,  # Displaying the answer text
            background_color=rx.color(
                "accent", 4
            ),  # Setting a light accent color background for the answer
            color=rx.color("accent", 12),  # Dark accent text color for readability
            **message_style,  # Applying the predefined style
        ),
        text_align="left",  # Aligning the answer to the left
        padding_top="1em",  # Adding top padding for spacing within the answer box
        justify_content="flex-start",  # Ensuring the content is aligned to the left
        children_align="flex-start",  # Aligning children to the start (left side
    )

    copy_button_answer = rx.icon_button(
        "copy",
        size="1",
        on_click=lambda: State.set_clipboard(qa.answer),
        tooltip="Copy answer",
    )

    copy_button_q = rx.icon_button(
        "copy",
        size="1",
        on_click=lambda: State.set_clipboard(qa.question),
        tooltip="Copy question",
    )  # Adding a copy button# Adding a copy button

    delete_button = rx.icon(
        "trash-2",  # Using the 'delete' icon from the Lucide Icons library
        size=15,  # Setting a small size for the icon
        color="red",  # Optional: setting the color of the icon
        on_click=lambda: State.delete_message(
            chat_name, index
        ),  # Pass the 'index' argument
        style={"cursor": "pointer"},  # Making the icon clickable
    )

    question_box.children.extend([copy_button_q, delete_button])
    answer_box.children.append(copy_button_answer)
    # Combining question and answer boxes into a single component, with conditional alignment
    return rx.box(
        rx.box(
            question_box,
            width="100%",
            display="flex",
            justify_content="flex-end",  # Aligning question box to the right
        ),
        rx.box(
            answer_box,
            width="100%",
            display="flex",
            justify_content="flex-start",  # Aligning answer box to the left
        ),
        direction="column",  # Stacking question and answer vertically
    )


def chat() -> rx.Component:
    """List all the messages in a single conversation."""
    # Adjust the top padding to ensure chat content starts below the navbar
    return rx.vstack(
        rx.box(
            rx.foreach(
                State.chats[State.current_chat],
                lambda qa, index: message(qa, index, State.current_chat),
            ),
            width="100%",
            overflow_y="auto",
        ),
        py="8",
        flex="1",
        width="100%",
        max_width="60em",
        padding_x="4px",
        align_self="center",
        overflow="hidden",
        padding_top="70px",  # Adjusted to add space at the top for the navbar
    )


def action_bar() -> rx.Component:
    """The action bar to send a new message."""
    # Creating a form for sending new messages
    form = rx.form(
        rx.hstack(
            rx.text_area(  # Corrected from rx.text_field.root to rx.input
                placeholder="Type something...",  # Placeholder text
                id="question",  # Input field ID
                required=True,
                width=[
                    "15em",
                    "20em",
                    "30em",
                    "30em",
                    "30em",
                    "30em",
                ],  # Full width input field
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
