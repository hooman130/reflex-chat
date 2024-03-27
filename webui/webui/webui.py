"""The main Chat app."""

# Importing necessary modules from reflex and webui.components
import reflex as rx
from webui.components import chat, navbar


# Define the main page layout and components
def index() -> rx.Component:
    """
    This function defines the main page layout using a vertical stack layout.
    It includes the navbar, chat window, and action bar with specific styling.
    """
    # Creating a vertical stack layout with navbar, chat window, and action bar
    return rx.vstack(
        navbar(),  # Adds the navigation bar at the top
        chat.chat(),  # Adds the main chat window
        chat.action_bar(),  # Adds the chat action bar at the bottom
        background_color=rx.color("mauve", 1),  # Sets the background color
        color=rx.color("mauve", 12),  # Sets the text color
        min_height="100vh",  # Ensures the layout fills the whole viewport height
        align_items="stretch",  # Stretches items to fill the container
        spacing="0",  # Sets the spacing between items to 0
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
