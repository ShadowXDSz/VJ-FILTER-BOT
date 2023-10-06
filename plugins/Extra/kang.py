import hashlib
import os
import math
import urllib.request as urllib

from io import BytesIO
from PIL import Image
from pyrogram import Client

import telegram
import logging
import json

from typing import Optional, List
from telegram import ParseMode, InlineKeyboardMarkup, InlineKeyboardButton
from telegram import TelegramError
from telegram import Update, Bot
from telegram.ext import CommandHandler, run_async, Updater, Handler, InlineQueryHandler
from telegram.utils.helpers import escape_markdown

from telegram import Message, Chat, MessageEntity, InlineQueryResultArticle
from os import path
from telegram import ParseMode
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger()

def getConfig(name: str):
    return os.environ[name]

try:
    BOT_TOKEN = getConfig('BOT_TOKEN')
except KeyError as e:
    LOGGER.error("BOT_TOKEN env variables missing! Exiting now")
    exit(1)

updater = telegram.ext.Updater(token=BOT_TOKEN)
bot = updater.bot
dispatcher = updater.dispatcher

START_TEXT = """
Hey! I'm {}, and I'm a bot which allows you to create a sticker pack from other stickers, images and documents!
I only have a few commands so I don't have a help menu or anything like that.
You can also check out the source code for the bot [here](https://github.com/breakdowns/kang-stickerbot)
""".format(dispatcher.bot.first_name)

@run_async
def starts(bot: Bot, update: Update):
    if update.effective_chat.type == "private":
        update.effective_message.reply_text(START_TEXT, parse_mode=ParseMode.MARKDOWN)


@run_async
def kang(bot: Bot, update: Update, args: List[str]):
    msg = update.effective_message
    user = update.effective_user
    packnum = 0
    packname = "a" + str(user.id) + "_by_"+bot.username
    packname_found = 0
    max_stickers = 120
    while packname_found == 0:
        try:
            stickerset = bot.get_sticker_set(packname)
            if len(stickerset.stickers) >= max_stickers:
                    packnum += 1
                    packname = "a" + str(packnum) + "_" + str(user.id) + "_by_"+bot.username
            else:
                packname_found = 1
        except TelegramError as e:
            if e.message == "Stickerset_invalid":
                packname_found = 1
    if msg.reply_to_message:
        if msg.reply_to_message.sticker:
            file_id = msg.reply_to_message.sticker.file_id
        elif msg.reply_to_message.photo:
            file_id = msg.reply_to_message.photo[-1].file_id
        elif msg.reply_to_message.document:
            file_id = msg.reply_to_message.document.file_id
        else:
            msg.reply_text("Yea, I can't kang that.")
        kang_file = bot.get_file(file_id)
        kang_file.download('kangsticker.png')
        if args:
            sticker_emoji = str(args[0])
        elif msg.reply_to_message.sticker and msg.reply_to_message.sticker.emoji:
            sticker_emoji = msg.reply_to_message.sticker.emoji
        else:
            sticker_emoji = "🤔"
        kangsticker = "kangsticker.png"
        try:
            im = Image.open(kangsticker)
            if (im.width and im.height) < 512:
                size1 = im.width
                size2 = im.height
                if im.width > im.height:
                    scale = 512/size1
                    size1new = 512
                    size2new = size2 * scale
                else:
                    scale = 512/size2
                    size1new = size1 * scale
                    size2new = 512
                size1new = math.floor(size1new)
                size2new = math.floor(size2new)
                sizenew = (size1new, size2new)
                im = im.resize(sizenew)
            else:
                maxsize = (512, 512)
                im.thumbnail(maxsize)
            if not msg.reply_to_message.sticker:
                im.save(kangsticker, "PNG")
            bot.add_sticker_to_set(user_id=user.id, name=packna
