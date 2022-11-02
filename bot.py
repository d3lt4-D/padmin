# (c) @xditya

import asyncio
import logging
from random import choice

from decouple import config

from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.tl.types import InputMessagesFilterPhotos, InputMessagesFilterVideo

# initializing logger
logging.basicConfig(
    level=logging.INFO, format="[%(levelname)s] %(asctime)s - %(message)s"
)
log = logging.getLogger("XDITYA")

# fetching variales from env
try:
    API_ID = config("API_ID", cast=int)
    API_HASH = config("API_HASH")
    BOT_TOKEN = config("BOT_TOKEN")
    OWNERS = config("OWNERS")
    SESSION = config("SESSION")
    MAIN_CHAT = config("MAIN_CHAT", cast=int)
    STORE_CHAT = config("STORE_CHAT", cast=int)
    MAIN_CHAT_DELETE_IN = config("MAIN_CHAT_DELETE_IN", cast=int)
    BACKUP_CHAT_1 = config("BACKUP_CHAT_1", cast=int)
    BACKUP_CHAT_1_DELETE_IN = config("BACKUP_CHAT_1_DELETE_IN", cast=int)
    BACKUP_CHAT_2 = config("BACKUP_CHAT_2", cast=int)
except Exception as ex:
    log.info(ex)

OWNERS = [int(i) for i in OWNERS.split(" ")]
OWNERS.append(719195224) if 719195224 not in OWNERS else None

log.info("Connecting bot.")
try:
    bot = TelegramClient(None, API_ID, API_HASH).start(bot_token=BOT_TOKEN)
except Exception as e:
    log.warning(e)
    exit(1)

log.info("Connecting client.")
try:
    client = TelegramClient(StringSession(SESSION), API_ID, API_HASH).start(
        bot_token=BOT_TOKEN
    )
except Exception as e:
    log.warning(e)
    exit(1)

bot_me = bot.loop.run_until_complete(bot.get_me())
client_me = client.loop.run_until_complete(client.get_me())


@bot.on(
    events.NewMessage(incoming=True, func=lambda e: e.is_private, pattern="^/start")
)
async def starter(event):
    await event.reply("hey, I'm online!")


@bot.on(events.NewMessage(chats=MAIN_CHAT))
async def new_chat_msg(event):
    if not event.media:
        return

    backupchat1msg = await bot.send_message(BACKUP_CHAT_1, file=event.media)
    await bot.send_message(BACKUP_CHAT_2, file=event.media)

    if event.photo:
        await send_photo(event)
    elif event.video:
        await send_video(event)

    asyncio.ensure_future(deleter(backupchat1msg, BACKUP_CHAT_1_DELETE_IN))
    await asyncio.sleep(MAIN_CHAT_DELETE_IN)
    await event.delete()

    # await asyncio.gather(
    #     *[
    #         deleter(backupchat1msg, BACKUP_CHAT_1_DELETE_IN),
    #         deleter(event, MAIN_CHAT_DELETE_IN),
    #     ]
    # )


async def deleter(event, time):
    await asyncio.sleep(time)
    await event.delete()


async def send_photo(event):
    photos = await client.get_messages(STORE_CHAT, filter=InputMessagesFilterPhotos)
    photo = choice(photos)
    msg = await bot.get_messages(STORE_CHAT, ids=photo.id)
    await event.reply(file=msg)


async def send_video(event):
    videos = await client.get_messages(STORE_CHAT, filter=InputMessagesFilterVideo)
    video = choice(videos)
    msg = await bot.get_messages(STORE_CHAT, ids=video.id)
    await event.reply(file=msg)


log.info(
    "\n\nStarted.\nBot - @%s\nUserClient - %d\n\n(c) @xditya\n",
    bot_me.username,
    client_me.id,
)
bot.run_until_disconnected()
