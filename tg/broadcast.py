import os
import time

from pyrogram import Client, types
from pyrogram.errors import (PeerIdInvalid, FloodWait, UserIsBlocked, BadRequest,
                             InputUserDeactivated)
from db import repository as db_filters
# TODO add filter admin and command send and filter msg is force reply (line 18)


# in the admin want to send message for everyone
def get_message_for_subscribe(_, msg: types.Message):
    if msg.command:
        if msg.command[0] == 'send':
            msg.reply(text='אנא שלח את המידע אותו תרצה להעביר למנויים',
                      reply_markup=types.ForceReply(selective=True,
                                                    placeholder='אנא שלח את המידע..'))
    elif isinstance(msg.reply_to_message.reply_markup, types.ForceReply):
        msg.reply(reply_to_message_id=msg.id, text='לשלוח את ההודעה?',
                  reply_markup=types.InlineKeyboardMarkup(
                      [[
                          types.InlineKeyboardButton(text="כן", callback_data='send_broadcast'),
                          types.InlineKeyboardButton(text="לא", callback_data='un_send_broadcast')
                      ]]))


def send_message(c: Client, query: types.CallbackQuery):
    tg_id = query.from_user.id
    msg_id = query.message.id
    reply_msg_id = query.message.reply_to_message.id
    if query.data == 'un_send_broadcast':
        c.send_message(chat_id=tg_id, text='ההודעה לא תישלח למנויים')
        c.delete_messages(chat_id=tg_id, message_ids=msg_id)

    elif query.data == 'un_send_broadcast':

        log_file = open('logger.txt', 'a+')
        users = [i.tg_id for i in db_filters.get_active_tg_users()]
        sent = 0
        failed = 0

        c.send_message(chat_id=tg_id, text=f"**📣 starting broadcast to:** "
                                           f"`{len(users)} users`\nPlease Wait...")
        progress = c.send_message(chat_id=tg_id, text=f'**Message Sent To:** `{sent} users`')

        for tg_id in users:

            try:
                c.copy_message(chat_id=int(tg_id), from_chat_id=tg_id,
                               message_id=reply_msg_id)
                sent += 1

                c.edit_message_text(chat_id=tg_id, message_id=progress.id,
                                    text=f'**Message Sent To:** `{sent}` users')

                log_file.write(f"sent to {tg_id} \n")
                time.sleep(.05)  # 20 messages per second (Limit: 30 messages per second)

            except FloodWait as e:
                print(e)
                time.sleep(e.value)

            except InputUserDeactivated:
                db_filters.set_tg_user_active(tg_id=tg_id, active=False)
                log_file.write(f"user {tg_id} is Deactivated\n")
                failed += 1
                continue

            except UserIsBlocked:
                db_filters.set_tg_user_active(tg_id=tg_id, active=False)
                log_file.write(f"user {tg_id} Blocked your bot\n")
                failed += 1
                continue

            except PeerIdInvalid:
                db_filters.set_tg_user_active(tg_id=tg_id, active=False)
                log_file.write(f"user {tg_id} IdInvalid\n")
                failed += 1
                continue

            except BadRequest as e:
                db_filters.set_tg_user_active(tg_id=tg_id, active=False)
                log_file.write(f"BadRequest: {e} :{tg_id}")
                failed += 1
                continue

        c.delete_messages(chat_id=tg_id, message_ids=msg_id)

        text_done = f"📣 Broadcast Completed\n\n🔸 **Total Users in db:** " \
                    f"{len(users)}\n\n🔹 Message sent to: {sent} users\n" \
                    f"🔹 Failed to sent: {failed} users"

        log_file.write('\n\n' + text_done + '\n')

        c.send_message(chat_id=tg_id, text=text_done)

        log_file.close()
        try:
            c.send_document(chat_id=tg_id, document='logger.txt')
        except Exception as e:
            c.send_message(chat_id=tg_id, text=str(e))
        finally:
            os.remove('logger.txt')
