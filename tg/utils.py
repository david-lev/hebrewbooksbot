from pyrogram import Client
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, CallbackQuery


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


def start(_: Client, msg_or_callback: Message | CallbackQuery):
    kwargs = {
        'text': (
            "ברוכים הבאים לבוט היברו בוקס!\n"
            "הבוט מאפשר לכם לחפש ספרים באתר hebrewbooks.org ולקרוא אותם בטלגרם.\n"
        ),
        'reply_markup': InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("חיפוש", switch_inline_query_current_chat="")],
                [InlineKeyboardButton("חיפוש בצ'אט אחר", switch_inline_query="")],
                [InlineKeyboardButton("עיון", callback_data="browse_menu")],
                [InlineKeyboardButton("לאתר", url="https://hebrewbooks.org")]
            ]
        )
    }
    if isinstance(msg_or_callback, Message):
        msg_or_callback.reply_text(**kwargs)
    else:
        msg_or_callback.edit_message_text(**kwargs)
