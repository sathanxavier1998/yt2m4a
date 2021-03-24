from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import youtube_dl
from youtube_search import YoutubeSearch
import requests

import os
from config import Config

bot = Client(
    'yt2m4a',
    bot_token = Config.BOT_TOKEN,
    api_id = Config.API_ID,
    api_hash = Config.API_HASH
)

## Extra Fns -------------------------------

# Check channel subscribed
def is_subscribed(bot, query):
    try:
        user = bot.get_chat_member(AUTH_CHANNEL, query.from_user.id)
    except UserNotParticipant:
        pass
    except Exception as e:
        logger.exception(e)
    else:
        if not user.status == 'kicked':
            return True
    return False

# Convert hh:mm:ss to seconds
def time_to_seconds(time):
    stringt = str(time)
    return sum(int(x) * 60 ** i for i, x in enumerate(reversed(stringt.split(':'))))


## Commands --------------------------------
@bot.on_message(filters.command(['start']))
def start(client, message):
    mention = f"Hello [{message.from_user.first_name}](tg://user?id={message.from_user.id})  my name is Hinata Hyuga ❣ \n\ni can download any video songs from youtube.  But now i only works for my owner's group.\n\n👉🏻 tap /help to know how to use me ❣️\n\nif you wanna add me to your group plz contact my owner 👇🏻"
    bot.send_photo(chat_id=message.chat.id, photo="https://raw.githubusercontent.com/sathanxavier1998/yt2m4a/main/welcome_photo.jpg", caption=mention, reply_to_message_id=message.message_id, reply_markup=InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("⚡Contact Owner⚡", url="https://t.me/sathan_of_telegram")]
             
        ]))

@bot.on_message(filters.command(['help']))
def help(client, message):
    text_msg="**How to Use me..?**\n\n 🔰 /song - **any song name**\n\n 🔰 /song - **any youtube link**\n\n 🔰 /mp3 - **to download songs in mp3 format**\n\n**⚠️ Note: I can only download songs under 10 minutes.\n\nIf you like this bot plz support out Telegram Channels 🦋⃟ 𝄟࿐**"
    bot.send_message(chat_id=message.chat.id, text=text_msg, reply_to_message_id=message.message_id,reply_markup=InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("[CT™] Channel", url="https://t.me/cinemaathattakam_chanel"),
            InlineKeyboardButton("[CT™] Series", url="https://t.me/cinemaathattakam_series"),
            InlineKeyboardButton("പാട്ടു പെട്ടി 🎶🎤", url="https://t.me/paattuppetti")],
            [InlineKeyboardButton("🦋MY DEV🦋", url="https://t.me/sathan_of_telegram")]
        ]))
    
@bot.on_message(filters.command(['song']))
def song(client, message):
    if Config.AUTH_CHANNEL and not is_subscribed(bot, message):
        message.reply(Config.INVITE_MSG)
        return
    query = ''
    for i in message.command[1:]:
        query += ' ' + str(i)
    print(query)
    m = message.reply('🔎 Fetching the song for you...')
    ydl_opts = {"format": "bestaudio[ext=m4a]"}
    try:
        results = []
        count = 0
        while len(results) == 0 and count < 6:
            if count>0:
                time.sleep(1)
            results = YoutubeSearch(query, max_results=1).to_dict()
            count += 1
        # results = YoutubeSearch(query, max_results=1).to_dict()
        try:
            link = f"https://youtube.com{results[0]['url_suffix']}"
            # print(results)
            title = results[0]["title"]
            thumbnail = results[0]["thumbnails"][0]
            duration = results[0]["duration"]

            ## UNCOMMENT THIS IF YOU WANT A LIMIT ON DURATION. CHANGE 1800 TO YOUR OWN PREFFERED DURATION AND EDIT THE MESSAGE (30 minutes cap) LIMIT IN SECONDS
            # if time_to_seconds(duration) >= 1800:  # duration limit
            #     m.edit("Exceeded 30mins cap")
            #     return

            views = results[0]["views"]
            thumb_name = f'thumb{message.message_id}.jpg'
            thumb = requests.get(thumbnail, allow_redirects=True)
            open(thumb_name, 'wb').write(thumb.content)

        except Exception as e:
            print(e)
            m.edit('Found nothing. Try changing the spelling a little.')
            return
    except Exception as e:
        m.edit(
            "✖️ Found Nothing. Sorry babe.\n\nTry another keyword or try to spell it properly."
        )
        print(str(e))
        return
    m.edit("Yeah I Got The Song 😎\n\n Let me download it for you ⏬.")
    try:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(link, download=False)
            audio_file = ydl.prepare_filename(info_dict)
            ydl.process_info(info_dict)
        rep = f'🎧 **Title**: [{title[:35]}]({link})\n⏳ **Duration**: `{duration}`\n👁‍🗨 **Views**: `{views}`'
        secmul, dur, dur_arr = 1, 0, duration.split(':')
        for i in range(len(dur_arr)-1, -1, -1):
            dur += (int(dur_arr[i]) * secmul)
            secmul *= 60
        message.reply_audio(audio_file, caption=rep, parse_mode='md',quote=False, title=title, duration=dur, thumb=thumb_name)
        m.delete()
    except Exception as e:
        m.edit('❌ Error')
        print(e)
    try:
        os.remove(audio_file)
        os.remove(thumb_name)
    except Exception as e:
        print(e)

bot.run()
