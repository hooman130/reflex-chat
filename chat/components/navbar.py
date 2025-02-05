import reflex as rx
from chat.state import State


def sidebar_chat(chat: str) -> rx.Component:
    """A sidebar chat item.

    Args:
        chat: The chat item.
    """
    return rx.drawer.close(
        rx.hstack(
            rx.button(
                chat,
                on_click=lambda: State.set_chat(chat),
                width="80%",
                variant="surface",
            ),
            rx.button(
                rx.icon(
                    tag="trash",
                    on_click=State.delete_chat,
                    stroke_width=1,
                ),
                width="20%",
                variant="surface",
                color_scheme="red",
            ),
            width="100%",
        )
    )


def settings_sidebar():
    return rx.drawer(
        rx.drawer_overlay(
            rx.drawer_content(
                rx.drawer_close_button(),
                rx.drawer_header(rx.heading("Settings")),
                rx.drawer_body(
                    rx.vstack(
                        rx.hstack(
                            rx.text("Model:"),
                            rx.select(
                                options=["gpt-4o", "gpt-3.5", "o1-preview"],
                                value=State.model_name,
                                on_change=State.set_model_name,
                            ),
                        ),
                        rx.hstack(
                            rx.text("Temperature: "),
                            rx.slider(
                                value=State.temperature,
                                on_change_end=State.set_temperature,
                                min_=0.0,
                                max_=1.0,
                                step=0.1,
                            ),
                            rx.text(State.temperature),
                        ),
                    )
                ),
            )
        ),
        placement="right",
        is_open=State.show_settings_sidebar,
        on_close=State.close_settings_sidebar,
    )


def sidebar(trigger) -> rx.Component:
    """The sidebar component."""
    return rx.drawer.root(
        rx.drawer.trigger(trigger),
        rx.drawer.overlay(),
        rx.drawer.portal(
            rx.drawer.content(
                rx.vstack(
                    rx.heading("Chats", color=rx.color("mauve", 11)),
                    rx.divider(),
                    rx.foreach(State.chat_titles, lambda chat: sidebar_chat(chat)),
                    align_items="stretch",
                    width="100%",
                ),
                top="auto",
                right="auto",
                height="100%",
                width="20em",
                padding="2em",
                background_color=rx.color("mauve", 2),
                outline="none",
            )
        ),
        direction="left",
    )


def modal(trigger) -> rx.Component:
    """A modal to create a new chat."""
    return rx.dialog.root(
        rx.dialog.trigger(trigger),
        rx.dialog.content(
            rx.hstack(
                rx.input(
                    placeholder="Type something...",
                    on_blur=State.set_new_chat_name,
                    width=["15em", "20em", "30em", "30em", "30em", "30em"],
                ),
                rx.dialog.close(
                    rx.button(
                        "Create chat",
                        on_click=State.create_chat,
                    ),
                ),
                background_color=rx.color("mauve", 1),
                spacing="2",
                width="100%",
            ),
        ),
    )


def navbar():
    return rx.box(
        rx.hstack(
            rx.hstack(
                rx.avatar(fallback="RC", variant="solid"),
                rx.heading("Reflex Chat"),
                rx.desktop_only(
                    rx.badge(
                        State.current_chat,
                        rx.tooltip(
                            rx.icon("info", size=14),
                            content="The current selected chat.",
                        ),
                        variant="soft",
                    )
                ),
                align_items="center",
            ),
            rx.hstack(
                modal(rx.button("+ New chat")),
                sidebar(
                    rx.button(
                        rx.icon(
                            tag="messages-square",
                            color=rx.color("mauve", 12),
                        ),
                        background_color=rx.color("mauve", 6),
                    )
                ),
                rx.desktop_only(
                    rx.button(
                        rx.icon(
                            tag="sliders-horizontal",
                            color=rx.color("mauve", 12),
                        ),
                        background_color=rx.color("mauve", 6),
                        on_click=State.toggle_settings_sidebar,
                    )
                ),
                align_items="center",
            ),
            justify_content="space-between",
            align_items="center",
        ),
        backdrop_filter="auto",
        backdrop_blur="lg",
        padding="12px",
        border_bottom=f"1px solid {rx.color('mauve', 3)}",
        background_color=rx.color("mauve", 2),
        position="sticky",
        top="0",
        z_index="100",
        align_items="center",
    )
