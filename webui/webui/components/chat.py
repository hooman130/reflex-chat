import reflex as rx
from webui.components import loading_icon
from webui.state import QA, State

PRIMARY_COLOR = "#3b82f6"
SECONDARY_COLOR = "#64b5f6"
ACCENT_COLOR = "#ffbaba"

message_style = {
    "padding": "1em",
    "border_radius": "8px",
    "max_width": "100%",
    "@media (min-width: 768px)": {"max_width": "50em"},
    "display": "flex",
    "flex_direction": "column",
}


def create_message_box(
    text, background_color, text_color, align="left", hover_color=None
):
    style = {**message_style, "background_color": background_color, "color": text_color}
    if hover_color:
        style["transition"] = "background-color 0.2s ease-in-out"
        style["on_hover"] = {"background-color": hover_color}
    return rx.box(
        rx.text(text, **style),
        text_align=align,
        justify_content="flex-end" if align == "right" else "flex-start",
    )


def create_copy_button(content, tooltip):
    return rx.icon_button(
        "copy",
        size="1",
        on_click=lambda: State.set_clipboard(content),
        tooltip=tooltip,
        aria_label=tooltip,
    )


def create_delete_button(chat_name, index):
    return rx.icon(
        "trash-2",
        size=15,
        color="red",
        on_click=lambda: State.delete_message(chat_name, index),
        style={"cursor": "pointer"},
    )


def message(qa: QA, index: int, chat_name: str) -> rx.Component:
    question_box = create_message_box(
        qa.question, PRIMARY_COLOR, "white", align="right", hover_color=SECONDARY_COLOR
    )
    answer_box = create_message_box(
        qa.answer, rx.color("accent", 4), rx.color("accent", 12), align="left"
    )
    question_box.children.extend(
        [
            create_copy_button(qa.question, "Copy question"),
            create_delete_button(chat_name, index),
        ]
    )
    answer_box.children.append(create_copy_button(qa.answer, "Copy answer"))
    return rx.vstack(question_box, answer_box, direction="column")


def chat() -> rx.Component:
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
        padding_bottom="5em",
    )


def action_bar() -> rx.Component:
    send_button_text = rx.cond(State.streaming, rx.text("Stop"), rx.text("Send"))
    send_button_action = rx.cond(
        State.streaming, lambda: State.stop_streaming(), State.process_question
    )

    form = rx.chakra.form(
        rx.chakra.form_control(
            rx.hstack(
                rx.text_area(
                    # Existing attributes...
                ),
                rx.button(
                    send_button_text,
                    type="submit" if not State.streaming else "button",
                    on_click=send_button_action if State.streaming else None,
                ),
                # Existing attributes...
            ),
            is_disabled=State.processing,
        ),
        on_submit=State.process_question if not State.streaming else None,
        reset_on_submit=True,
    )
    disclaimer_text = rx.text(
        "ReflexGPT may return factually incorrect or misleading responses. Use discretion.",
        text_align="center",
        font_size=".75em",
        color=rx.color("mauve", 10),
    )
    return rx.center(
        rx.vstack(form, disclaimer_text, align_items="center"),
        position="sticky",
        bottom="0",
        left="0",
        padding_y="16px",
        backdrop_filter="auto",
        backdrop_blur="lg",
        border_top=f"1px solid {rx.color('mauve', 3)}",
        background_color=rx.color("mauve", 2),
        align_items="stretch",
        width="100%",
    )
