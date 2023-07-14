import re
from pywa import WhatsApp
from pywa.types import CallbackButton, SectionList, Section, SectionRow, CallbackSelection, Message
from data import api
from data.callbacks import BrowseType
from data.enums import BrowseType as BrowseTypeEnum
from data.strings import String as s
from wa.helpers import get_string as gs, Commands


def browse_menu(_: WhatsApp, clb: CallbackButton):
    """
    Browse menu
    """
    menu = [
        (BrowseTypeEnum.SHAS, s.SHAS, s.SHAS_CMD),
        (BrowseTypeEnum.SUBJECT, s.SUBJECTS, s.SUBJECTS_CMD),
        (BrowseTypeEnum.DATERANGE, s.DATE_RANGES, s.DATE_RANGES_CMD),
        (BrowseTypeEnum.LETTER, s.LETTERS, s.LETTERS_CMD),
    ]
    clb.reply_text(
        text=gs(mqc=clb, string=s.CHOOSE_BROWSE_TYPE),
        keyboard=SectionList(
            button_title=gs(s.CHOOSE_BROWSE_TYPE),
            sections=[
                Section(
                    title=gs(s.CHOOSE_BROWSE_TYPE),
                    rows=[
                        SectionRow(
                            title=gs(title),
                            description=gs(cmd),
                            callback_data=BrowseType(type=browse_type, id="").to_callback()
                        ) for browse_type, title, cmd in menu
                    ]
                )
            ]
        )
    )


def browse_help(_: WhatsApp, clb: CallbackSelection):
    """
    Browse help
    """
    msg_map = {
        BrowseTypeEnum.SHAS: s.SHAS_CMD,
        BrowseTypeEnum.SUBJECT: s.SUBJECTS_CMD,
        BrowseTypeEnum.DATERANGE: s.DATE_RANGES_CMD,
        BrowseTypeEnum.LETTER: s.LETTERS_CMD,
    }
    clb.reply_text(text=gs(msg_map[BrowseType.from_callback(clb.data).type]))


def browse_from_msg(_: WhatsApp, msg: Message):
    """
    Browse query
    """
    cmd = msg.text
    if cmd.startswith(tuple(f"!{c}" for c in Commands.SHAS)):
        masechtot = api.get_masechtot()
        name, page = (x.strip() for x in cmd.split(', '))
        name = re.sub(r'^!(%s)\s' % '|'.join(Commands.SHAS), '', name)
        masechet = next((m for m in masechtot if m.name == name), None)
        if masechet is None:
            msg.reply_text(text=", ".join((m.name for m in masechtot)))
            return
        if (masechet_page := next(filter(lambda p: p.name == page, api.get_masechet(masechet.id).pages), None)) is None:
            msg.reply_text(text=", ".join((p.name for p in api.get_masechet(masechet.id).pages)))
            return
        msg.reply_image(
            image=masechet_page.get_page_img(750, 1334),
            caption=masechet.name
        )
    elif cmd.startswith(('!נושא', '!sub')):
        subjects = api.get_subjects()
        subject = re.sub(r'^!(%s)\s' % '|'.join(Commands.SUBJECT), '', cmd)
        if (subject := next(filter(lambda s: s.name == subject, subjects), None)) is None:
            msg.reply_text(text=", ".join((s.name for s in subjects)))
            return
        raise NotImplementedError("TODO")
    else:
        raise NotImplementedError(f"Unknown browse command: {cmd}")