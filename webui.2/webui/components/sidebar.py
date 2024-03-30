import reflex as rx

from webui import styles
from webui.state import State


def sidebar_chat(chat: str) -> rx.Component:
    """A sidebar chat item.

    Args:
        chat: The chat item.
    """
    # Assuming rx.Box and rx.HStack are similar constructs from Reflex for layout
    # Assuming rx.Icon is a way to include icons, which needs to be confirmed with Reflex documentation
    return rx.HStack(
        rx.Box(
            chat,
            on_click=lambda: State.set_chat(chat),
            style=styles.sidebar_style,
            color=styles.icon_color,
            flex="1",
        ),
        rx.Box(
            # Placeholder for adding an icon with an on_click event in Reflex
            rx.Icon(
                tag="delete",
                style=styles.icon_style,
                on_click=State.delete_chat,
            ),
            style=styles.sidebar_style,
        ),
        color=styles.text_light_color,
        cursor="pointer",
    )


def sidebar() -> rx.Component:
    """The sidebar component."""

    # Assuming rx.Drawer and related components as constructs in Reflex for drawer functionality
    # This is a placeholder code and needs to be confirmed and possibly adjusted per Reflex documentation
    return rx.VStack(
        rx.Drawer(
            rx.DrawerOverlay(
                rx.DrawerContent(
                    rx.DrawerHeader(
                        rx.HStack(
                            rx.Text("Chats"),
                            # Placeholder for an icon within a drawer header
                            rx.Icon(
                                tag="close",
                                on_click=State.toggle_drawer,
                                style=styles.icon_style,
                            ),
                        )
                    ),
                    rx.DrawerBody(
                        rx.VStack(
                            # Assuming rx.foreach is a way to render iterable components in Reflex
                            rx.foreach(
                                State.chat_titles, lambda chat: sidebar_chat(chat)
                            ),
                            align_items="stretch",
                        )
                    ),
                ),
            ),
            placement="left",
            is_open=State.drawer_open,
        ),
        height="80vh",  # Reduce sidebar height
        spacing="10px",  # Reduce spacing
    )
