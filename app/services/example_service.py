"""
Example service to demonstrate separation of concerns.
Place all business logic here, keeping routes clean.
"""


def get_welcome_message(name: str = None) -> str:
    """Return a welcome message."""
    if name:
        return f"Welcome, {name}!"
    return "Welcome to the Flask App"


def get_about_info() -> dict:
    """Return about page information."""
    return {
        "title": "About",
        "description": "This is the about page of the Flask application.",
        "version": "1.0.0"
    }
