import reflex as rx
from webui.state import State


def create_button_with_icon(
    icon_tag,
    on_click,
    tooltip=None,
    color_scheme="surface",
    icon_color="mauve",
    width="100%",
):
    """Helper function to create a button with an icon."""
    icon_element = rx.icon(
        tag=icon_tag, on_click=on_click, stroke_width=1, color=rx.color(icon_color, 12)
    )
    if tooltip:
        icon_element = rx.tooltip(icon_element, content=tooltip)
    return rx.button(
        icon_element, width=width, variant="surface", color_scheme=color_scheme
    )


def create_sidebar_chat_item(chat: str) -> rx.Component:
    """Refactored sidebar chat item with clearer structure."""
    return rx.drawer.close(
        rx.hstack(
            rx.button(
                chat,
                on_click=lambda: State.set_chat(chat),
                width="80%",
                variant="surface",
            ),
            create_button_with_icon(
                "trash", State.delete_chat, color_scheme="red", width="20%"
            ),
            width="100%",
        )
    )


def sidebar(trigger) -> rx.Component:
    """The sidebar component with minor adjustments for clarity."""
    return rx.drawer.root(
        rx.drawer.trigger(trigger),
        rx.drawer.overlay(),
        rx.drawer.portal(
            rx.drawer.content(
                rx.vstack(
                    rx.heading("Chats", color=rx.color("mauve", 11)),
                    rx.divider(),
                    rx.foreach(State.chat_titles, create_sidebar_chat_item),
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


def create_modal_content():
    """Separate function for modal content creation for better readability."""
    return rx.hstack(
        rx.input(
            placeholder="Type something...",
            on_blur=State.set_new_chat_name,
            width=["15em", "20em", "30em", "30em", "30em", "30em"],
        ),
        rx.dialog.close(rx.button("Create chat", on_click=State.create_chat)),
        background_color=rx.color("mauve", 1),
        spacing="2",
        width="100%",
    )


def modal(trigger) -> rx.Component:
    """A modal to create a new chat with refactored content creation."""
    return rx.dialog.root(
        rx.dialog.trigger(trigger),
        rx.dialog.content(create_modal_content()),
    )


def create_filebar_content() -> rx.Component:
    """Function to create content for the filebar drawer for knowledge base management."""
    color = "rgb(98, 90, 246)"
    upload = rx.vstack(
        rx.upload(
            rx.text("Drag and drop files here or click to select files"),
            id="upload1",
            multiple=True,
        ),
        rx.vstack(rx.foreach(rx.selected_files("upload1"), rx.text)),
        rx.cond(
            State.uploading,
            rx.button("Uploading...", disabled=True),
            rx.button(
                "Upload",
                on_click=State.handle_upload(
                    rx.upload_files(
                        upload_id="upload1",
                        on_upload_progress=State.handle_upload_progress,
                    )
                ),
                style={"margin-bottom": "1rem"},
            ),
        ),
        border=f"1px dotted {color}",
        padding="2em",
    )

    knowledge_base_list = rx.box(
        rx.foreach(
            State.knowledge_bases,  # Placeholder for a state variable listing knowledge bases
            lambda kb: rx.text(kb, padding="0.5rem"),
        ),
        style={"overflow-y": "auto", "max-height": "20em"},
        align="stretch",
        width="100%",
        height="100%",
        background_color=rx.color("sky", 3),
    )

    return rx.vstack(
        rx.heading("Knowledge Base", color=rx.color("mauve", 11)),
        rx.divider(),
        upload,
        rx.progress(value=State.progress, max=100),
        rx.divider(),
        rx.heading("Current Files:", color=rx.color("mauve", 10), size="1"),
        knowledge_base_list,
        width="100%",
    )


def create_sliderbar_content():
    """Separate function for sliderbar content creation for better readability."""

    return rx.vstack(
        rx.heading("Model Parameters", color=rx.color("mauve", 11)),
        rx.divider(),
        rx.text("Model"),
        rx.select(
            State.models_list,
            value=State.model,
            on_change=State.handle_model_change,
        ),
        create_model_param_slider("Temperature", "temperature", 0, 1, 0.01),
        create_model_param_slider("Max Tokens", "max_tokens", 100, 4000, 10),
        align_items="stretch",
        width="100%",
    )


def create_model_param_slider(label, param_name, min_val, max_val, step):
    """Helper function to create a slider for model parameters."""
    return rx.vstack(
        rx.text(label),
        rx.heading(State.model_params[param_name], size="1"),
        rx.slider(
            value=[State.model_params[param_name]],
            name=param_name,
            min=min_val,
            max=max_val,
            step=step,
            on_change=lambda value: State.update_model_params(param_name, value),
        ),
    )


def sliderbar(trigger) -> rx.Component:
    """The sliderbar component with refactored content creation."""
    return rx.drawer.root(
        rx.drawer.trigger(trigger),
        rx.drawer.overlay(),
        rx.drawer.portal(
            rx.drawer.content(
                create_sliderbar_content(),
                top="auto",
                left="auto",
                height="100%",
                width="20em",
                padding="2em",
                background_color=rx.color("mauve", 2),
                outline="none",
            )
        ),
        direction="right",
    )


def filebar(trigger) -> rx.Component:
    """The sliderbar component with refactored content creation."""
    return rx.drawer.root(
        rx.drawer.trigger(trigger),
        rx.drawer.overlay(),
        rx.drawer.portal(
            rx.drawer.content(
                create_filebar_content(),
                top="auto",
                left="auto",
                height="100%",
                width="20em",
                padding="2em",
                background_color=rx.color("mauve", 2),
                outline="none",
            )
        ),
        direction="right",
    )


# @rx.memo
def navbar():
    """Refactored navbar with minor adjustments for consistency."""
    return rx.hstack(
        rx.box(
            rx.hstack(
                create_navbar_left_section(),
                create_navbar_right_section(),
                justify_content="space-between",
                align_items="center",
            ),
            backdrop_filter="auto",
            backdrop_blur="lg",
            padding="12px",
            border_bottom=f"1px solid {rx.color('mauve', 3)}",
            background_color=rx.color("mauve", 2),
            position="fixed",  # Changed from 'sticky' to 'fixed'
            top="0",
            left="0",
            right="0",  # Ensure it spans the full width
            z_index="100",
            align_items="center",
        ),
        height="50px",
        spacing="9",
        width="100%",  # Ensure full width
    )


def create_navbar_left_section():
    """Helper function to create the left section of the navbar."""
    return rx.hstack(
        rx.avatar(fallback="RC", variant="solid"),
        rx.heading("Reflex Chat"),
        rx.desktop_only(
            rx.badge(
                State.current_chat,
                rx.tooltip(
                    rx.icon("info", size=14), content="The current selected chat."
                ),
                variant="soft",
            )
        ),
        align_items="center",
    )


def create_navbar_right_section():
    """Helper function to create the right section of the navbar."""
    return rx.hstack(
        modal(rx.button("+ New chat")),
        filebar(
            rx.button(
                rx.icon(tag="book_text", color=rx.color("mauve", 12)),
                background_color=rx.color("mauve", 6),
            )
        ),
        sidebar(
            rx.button(
                rx.icon(tag="messages-square", color=rx.color("mauve", 12)),
                background_color=rx.color("mauve", 6),
            )
        ),
        rx.desktop_only(
            sliderbar(
                rx.button(
                    rx.icon(tag="sliders-horizontal", color=rx.color("mauve", 12)),
                    background_color=rx.color("mauve", 6),
                )
            )
        ),
        align_items="center",
    )
