from pyrogram import Client
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from data import api
from data.enums import BrowseType as BrowseTypeEnum
from tg import helpers
from tg.strings import String as s, get_string as gs
from tg.callbacks import BrowseNavigation, BrowseType, ShowBook


def browse_menu(_: Client, query: CallbackQuery):
    """
    Browse menu

    query.data format: "browse_menu"
    """
    query.edit_message_text(
        text=gs(mqc=query, string=s.CHOOSE_BROWSE_TYPE),
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text=gs(mqc=query, string=s.SUBJECTS),
                        callback_data=BrowseType(BrowseTypeEnum.SUBJECT).to_callback()
                    ),
                    InlineKeyboardButton(
                        text=gs(mqc=query, string=s.LETTERS),
                        callback_data=BrowseType(BrowseTypeEnum.LETTER).to_callback()
                    ),
                    InlineKeyboardButton(
                        text=gs(mqc=query, string=s.DATES),
                        callback_data=BrowseType(BrowseTypeEnum.DATERANGE).to_callback()
                    )
                ],
                [InlineKeyboardButton("🔙", callback_data="start")]
            ]
        )
    )


def browse_types(_: Client, clb: CallbackQuery):
    """
    Browse types
    """
    browse_type = BrowseType.from_callback(clb.data)
    if browse_type.type is BrowseTypeEnum.LETTER:
        results = api.get_letters()
    elif browse_type.type is BrowseTypeEnum.DATERANGE:
        results = api.get_date_ranges()
    elif browse_type.type is BrowseTypeEnum.SUBJECT:
        results = api.get_subjects()
    else:
        raise ValueError(f"Invalid browse type: {browse_type}")

    clb.edit_message_text(
        text=gs(mqc=clb, string=s.CHOOSE),
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text=f"{result.name} ({result.total})",
                        callback_data=BrowseNavigation(
                            type=browse_type.type,
                            id=result.id,
                            offset=1,
                            total=result.total
                        ).to_callback()
                    )
                ] for result in results
            ] + [[
                InlineKeyboardButton(text="🔙", callback_data="browse_menu")
            ]]
        )
    )


def browse_books_navigator(_: Client, clb: CallbackQuery):
    """
    Browse books navigator
    """
    browse_nav = BrowseNavigation.from_callback(clb.data)
    results, total = api.browse(
        browse_type=browse_nav.type,
        browse_id=browse_nav.id,
        offset=browse_nav.offset,
        limit=5
    )
    buttons = [
        [
            InlineKeyboardButton(
                text=f"{book.title} • {book.author}{f' • {book.year}' if book.year else ''}"
                     f"{f' • {book.city}' if book.city else ''}",
                callback_data=ShowBook(id=book.id).join_to_callback(browse_nav)
            )
        ] for book in (api.get_book(result.id) for result in results)
    ]
    next_offset = helpers.get_offset(browse_nav.offset, int(total), increase=5)

    next_previous_buttons = []
    if next_offset:
        next_previous_buttons.append(
            InlineKeyboardButton(
                text=gs(mqc=clb, string=s.NEXT),
                callback_data=BrowseNavigation(
                    type=browse_nav.type,
                    id=browse_nav.id,
                    offset=next_offset,
                    total=total
                ).to_callback()
            )
        )
    if (browse_nav.offset - 5) > 0:
        next_previous_buttons.append(
            InlineKeyboardButton(
                text=gs(mqc=clb, string=s.PREVIOUS),
                callback_data=BrowseNavigation(
                    type=browse_nav.type,
                    id=browse_nav.id,
                    offset=browse_nav.offset - 5,
                    total=total
                ).to_callback()
            )
        )
    if next_previous_buttons:
        buttons.append(next_previous_buttons)

    buttons.append(
        [
            InlineKeyboardButton(text="🔙", callback_data=BrowseType(browse_nav.type).to_callback())
        ]
    )

    clb.edit_message_text(
        text=gs(mqc=clb, string=s.CHOOSE),
        reply_markup=InlineKeyboardMarkup(
            buttons
        )
    )
