import time
from pyrogram import Client, types
from pyrogram.errors import PeerIdInvalid, FloodWait, UserIsBlocked, BadRequest, InputUserDeactivated
from pyrogram.types import Message, ForceReply
from db import repository
from tg.callbacks import Broadcast


def prompt_for_broadcast_msg(_: Client, msg: Message):
    if msg.command:
        msg.reply(
            text='Reply to this message with the message you want to broadcast to your subscribers.',
            reply_markup=ForceReply(
                selective=True,
                placeholder='Announcement Message'
            ),
            quote=True
        )
    elif isinstance(msg.reply_to_message.reply_markup, types.ForceReply):
        print(msg.reply_to_message.reply_markup)
        lang_code = msg.reply_to_message.command[1] \
            if len(msg.reply_to_message.command) > 0 else ''
        subs_count = repository.get_tg_users_count(active=True, lang_code=lang_code or None)
        msg.reply(
            text=f'Are you sure you want to broadcast this message to {subs_count} subscribers?',
            reply_markup=types.InlineKeyboardMarkup(
                [
                    [
                        types.InlineKeyboardButton(
                            text="Yes",
                            callback_data=Broadcast(
                                send=True,
                                lang_code=lang_code
                            ).to_callback()
                        ),
                        types.InlineKeyboardButton(
                            text="No",
                            callback_data=Broadcast(
                                send=False,
                                lang_code=lang_code
                            ).to_callback()
                        )
                    ]
                ]
            ),
            quote=True
        )


def broadcast(c: Client, clb: types.CallbackQuery):
    bct = Broadcast.from_callback(clb.data)
    chat_id = clb.from_user.id
    msg_id = clb.message.id
    reply_msg_id = clb.message.reply_to_message.id
    if not bct.send:
        c.send_message(chat_id=chat_id, text='Broadcast cancelled.')
        c.delete_messages(chat_id=chat_id, message_ids=msg_id)
        return

    sent = 0
    failed = 0
    users = repository.get_tg_users(active=True, lang_code=bct.lang_code or None)
    clb.edit_message_text(text='Sending message to users...')
    for user in users:
        try:
            c.copy_message(
                chat_id=user.tg_id,
                from_chat_id=chat_id,
                message_id=reply_msg_id
            )
            sent += 1
            time.sleep(.05)  # 20 messages per second (Limit: 30 messages per second)

        except FloodWait as e:
            time.sleep(e.value)
        except (InputUserDeactivated, UserIsBlocked, PeerIdInvalid, BadRequest):
            repository.set_tg_user_active(tg_id=user.tg_id, active=False)
            failed += 1
            continue

    c.delete_messages(chat_id=chat_id, message_ids=msg_id)
    clb.edit_message_text(
        text=f'Successfully sent message to {sent} users.\nFailed to send message to {failed} users.'
    )
