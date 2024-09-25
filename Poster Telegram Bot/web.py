from telethon import types, utils
from telethon.tl.types import Channel

from keyboards import *
from texts import *


async def ensure_connected(user_client):
    if not user_client.is_connected():
        await user_client.connect()
    if not await user_client.is_user_authorized():
        print("Пользователь не вошел в систему. Начинаем процесс входа.")
        await user_client.start()
    return True


async def get_all_channels(client):
    channels = []
    async for dialog in client.iter_dialogs():
        if isinstance(dialog.entity, Channel):
            channels.append(dialog.entity)
    return channels


async def add_new_channel(msg, bot_client, user_client, user_id):
    await ensure_connected(user_client)
    if msg.fwd_from and isinstance(msg.fwd_from.from_id, types.PeerChannel):
        channel_id_from_forward = msg.fwd_from.from_id.channel_id  # ID канала
        original_channel_name = "Unknown"

        # Пытаемся получить информацию о канале с помощью бота
        try:
            sender_info = await bot_client.get_entity(types.PeerChannel(channel_id=channel_id_from_forward))
            original_channel_name = utils.get_display_name(sender_info) if sender_info else "Unknown"
        except:
            pass

        # Если не удалось получить имя, пытаемся использовать клиента пользователя
        if original_channel_name == "Unknown":
            try:
                sender_info = await user_client.get_entity(types.PeerChannel(channel_id=channel_id_from_forward))
                original_channel_name = utils.get_display_name(sender_info) if sender_info else "Unknown"
            except:
                pass

        # Если все еще не удалось, ищем канал среди подписок клиента пользователя
        if original_channel_name == "Unknown":
            dialogs = await user_client.get_dialogs()
            for dialog in dialogs:
                if dialog.is_channel and dialog.entity.id == channel_id_from_forward:
                    original_channel_name = dialog.name
                    break

            if original_channel_name == "Unknown":
                await bot_client.send_message(user_id, MESSAGES['channel_private_error'], buttons=await generate_back_keyboard())
                return None, None, None

        return channel_id_from_forward, original_channel_name, user_id
    else:
        await bot_client.send_message(user_id, MESSAGES['reply_is_not_from_channel'], buttons=await generate_back_keyboard())
        return None, None, None



async def can_bot_post(bot_client, channel_id):
    try:
        message = await bot_client.send_message(channel_id, MESSAGES['autoposting_message_to_channel'])
        await bot_client.delete_messages(channel_id, message)
        return True
    except Exception as e:
        return False