from data import api
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, InlineQuery, InlineQueryResultArticle, CallbackQuery


async def start(_: Client, message: Message | CallbackQuery):
    kwargs = {
        "text": "Start",
        "reply_markup": InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("חיפוש", switch_inline_query_current_chat=""),
                    InlineKeyboardButton("עיון", callback_data="browse")
                ]
            ]
        )
    }
    if isinstance(message, Message):
        await message.reply(**kwargs)
    else:
        await message.edit_message_text(**kwargs)


def browse_menu(_: Client, query: CallbackQuery):
    query.edit_message_text(
        text="בחר סוג עיון",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("אותיות", callback_data="browse_letter"),
                    InlineKeyboardButton("תאריכים", callback_data="browse_daterange"),
                    InlineKeyboardButton("נושאים", callback_data="browse_subject"),
                    InlineKeyboardButton("חזור", callback_data="start_menu")
                ]
            ]
        )
    )


def browse(_: Client, query: CallbackQuery):
    _type = query.data.split("_")[-1]
    if _type == "letter":
        results = api.get_letters()
    elif _type == "daterange":
        results = api.get_date_ranges()
    else:
        results = api.get_subjects()
    query.edit_message_text(
        text="בחר",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text=f"{result.name} ({result.total})",
                        callback_data=f"browse_{_type}_{result.id}"
                    )
                ] for result in results
            ] + [[
                InlineKeyboardButton(text="חזור", callback_data="browse_menu")
            ]]
        )
    )


def browse_results(_: Client, query: CallbackQuery):
    browse_type, browse_id = query.data.split("_")[1:]
    results = api.browse(browse_type, browse_id, offset=1, limit=10)
    query.edit_message_text(
        text="בחר",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text=f"{result.title} | {result.author}",
                        callback_data=f"book_{result.id}"
                    )
                ] for result in results
            ] + [[
                InlineKeyboardButton(text="חזור", callback_data="browse_menu")
            ]]
        )
    )
