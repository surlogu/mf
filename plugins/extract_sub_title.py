# Copyright (C) 2020 by surlogu@Github, < https://github.com/surlogu>.
#
# This file is part of < https://github.com/surlogu/AsEnDL > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/surlogu/AsEnDL/blob/master/LICENSE >
#
# All rights reserved.

import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

import os
import subprocess
import time

# the secret configuration specific things
if bool(os.environ.get("WEBHOOK", False)):
    from sample_config import Config
else:
    from config import Config

# the Strings used for this "thing"
from translation import Translation

import pyrogram

#from helper_funcs.chat_base import TRChatBase
from helper_funcs.display_progress import progress_for_pyrogram


async def extractsubtitle(video_file, output_directory):
    out_put_file_name = output_directory + str(round(time.time())) + ".srt"
    command_to_execute = [
        "ffmpeg",
        "-i ", "\"" + video_file + "\"",
        # "-map 0:2",
        # https://superuser.com/a/927507
        out_put_file_name
    ]
    logger.info(command_to_execute)
    p = subprocess.Popen(command_to_execute, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    if not p.returncode and os.path.lexists(video_file):
        return out_put_file_name
    else:
        return None

@pyrogram.Client.on_message(pyrogram.Filters.command(["extractsubtitle"]))
async def extract_sub_title(bot, update):
    #TRChatBase(update.from_user.id, update.text, "extract_sub_title")
    if update.from_user.id not in Config.AUTH_USERS:
        await bot.send_message(
            chat_id=update.chat.id,
            text=Translation.NOT_AUTH_USER_TEXT,
            reply_to_message_id=update.message_id
        )
        return
    download_location = Config.DOWNLOAD_LOCATION + "/" + str(update.from_user.id) + ".srt"
    if update.reply_to_message is not None:
        text = update.reply_to_message.text
        if text is not None and text.startswith("http"):
            a = await bot.send_message(
                chat_id=update.chat.id,
                text=Translation.UPLOAD_START,
                reply_to_message_id=update.message_id
            )
            sub_title_file_name = extractsubtitle(text, download_location)
            await bot.send_document(
                chat_id=update.chat.id,
                document=sub_title_file_name,
                # thumb=thumb_image_path,
                # caption=description,
                # reply_markup=reply_markup,
                reply_to_message_id=update.reply_to_message.message_id
            )
            os.remove(sub_title_file_name)
            await bot.edit_message_text(
                text=Translation.AFTER_SUCCESSFUL_UPLOAD_MSG,
                chat_id=update.chat.id,
                message_id=a.message_id,
                disable_web_page_preview=True
            )
        else:
            await bot.send_message(
                chat_id=update.chat.id,
                text=Translation.REPLY_TO_DOC_OR_LINK_FOR_RARX_SRT,
                reply_to_message_id=update.message_id
            )
    else:
        await bot.send_message(
            chat_id=update.chat.id,
            text=Translation.REPLY_TO_DOC_OR_LINK_FOR_RARX_SRT,
            reply_to_message_id=update.message_id
        )
