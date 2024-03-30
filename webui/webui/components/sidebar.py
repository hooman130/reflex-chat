import reflex as rx
from webui import styles
from webui.state import State


def create_chat_box(chat: str) -> rx.Box:
    """Creates a chat box component.

    Args:
        chat: The chat item.

    Returns:
        A chat box component.
    """
    return rx.Box(
        chat,
        on_click=lambda: State.set_chat(chat),
        style=styles.sidebar_style,
        color=styles.icon_color,
        flex="1",
    )


def create_delete_icon() -> rx.Icon:
    """Creates a delete icon component.

    Returns:
        A delete icon component.
    """
    return rx.Icon(
        tag="delete",
        style=styles.icon_style,
        on_click=State.delete_chat,
    )


def sidebar_chat(chat: str) -> rx.Component:
    """A sidebar chat item.

    Args:
        chat: The chat item.

    Returns:
        A sidebar chat item component.
    """
    chat_box = create_chat_box(chat)
    delete_icon = create_delete_icon()

    return rx.HStack(
        chat_box,
        rx.Box(delete_icon, style=styles.sidebar_style),
        color=styles.text_light_color,
        cursor="pointer",
    )


def create_drawer_header() -> rx.DrawerHeader:
    """Creates a drawer header component.

    Returns:
        A drawer header component.
    """
    return rx.DrawerHeader(
        rx.HStack(
            rx.Text("Chats"),
            rx.Icon(tag="close", on_click=State.toggle_drawer, style=styles.icon_style),
        )
    )


def create_drawer_body() -> rx.DrawerBody:
    """Creates a drawer body component.

    Returns:
        A drawer body component.
    """
    chat_items = rx.foreach(State.chat_titles, sidebar_chat)
    return rx.DrawerBody(rx.VStack(chat_items, align_items="stretch"))


def sidebar() -> rx.Component:
    """The sidebar component.

    Returns:
        A sidebar component.
    """
    drawer_header = create_drawer_header()
    drawer_body = create_drawer_body()

    return rx.VStack(
        rx.Drawer(
            rx.DrawerOverlay(rx.DrawerContent(drawer_header, drawer_body)),
            placement="left",
            is_open=State.drawer_open,
        ),
        height="80vh",
        spacing="10px",
    )
