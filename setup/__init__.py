"""Setup helpers for remote browser scenarios.

These are regular async functions that scenarios call in their setup phase.
"""
from setup.navigate import navigate_to_url
from setup.cookies import set_cookies, clear_cookies
from setup.interact import click_element, fill_input, select_option
from setup.load_html import load_html_content

__all__ = [
    "navigate_to_url",
    "set_cookies",
    "clear_cookies",
    "click_element",
    "fill_input",
    "select_option",
    "load_html_content",
]
