"""The main Chat app."""

# Importing necessary modules from reflex and webui.components
import reflex as rx
from webui.components import chat, navbar


# Define the main page layout and components
def index() -> rx.Component:
    # Adjust the layout to accommodate the fixed navbar
    return rx.vstack(
        navbar(),  # Navbar remains here but won't take up space in the flow
        chat.chat(),
        chat.action_bar(),
        padding_top="50px",  # Add padding at the top equal to the navbar's height
        background_color=rx.color("mauve", 1),
        color=rx.color("mauve", 12),
        min_height="100vh",
        align_items="stretch",
        spacing="0",
    )


# Initialize the app with a theme and accent color
app = rx.App(
    theme=rx.theme(
        appearance="dark",  # Adjust appearance to 'dark' as originally intended
        has_background=True,
        radius="large",
        accent_color="violet",  # Setting the accent color to 'violet' as in the original attempt
    ),
)

app.add_page(index)
