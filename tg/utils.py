from pyrogram import Client
from pyrogram.types import InlineKeyboardButton, CallbackQuery, InlineKeyboardMarkup
from data import api


def get_offset(current_offset: int, total: int, increase: int = 5) -> int:
    """
    Get the offset for thr next query results.

    Args:
        current_offset: The current offset.
        total: The total number of results.
        increase: The number of results to increase. (default: 5)
    Returns:
        The offset for the next query results.
    """
    if current_offset + increase > total:
        return total - current_offset
    return current_offset + increase
