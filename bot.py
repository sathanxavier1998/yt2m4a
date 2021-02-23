from pyrogram import Client, filters
import youtube_dl
from youtube_search import YoutubeSearch

import os
from config import Config

bot = Client(
    'yt2m4a',
    bot_token = Config.BOT_TOKEN,
    api_id = Config.API_ID,
    api_hash = Config.API_HASH
)

## Extra Fns -------------------------------

# Convert hh:mm:ss to seconds
def time_to_seconds(time):
    stringt = str(time)
    return sum(int(x) * 60 ** i for i, x in enumerate(reversed(stringt.split(':'))))


## Commands --------------------------------
@bot.on_message(filters.command(['start']))
def start(client, message):
    message.reply_text('👋 Hi. \nI can get you audio from youtube.🎶\n\nJust send me a keyword and I\'ll send you the audio from the first youtube link that I find.')

@bot.on_message(filters.command(['a']))
def a(client, message):
    query = ''
    for i in message.command[1:]:
        query += ' ' + str(i)
    print(query)
    m = message.reply('🔎 Fetching the song...')
    ydl_opts = {"format": "bestaudio[ext=m4a]"}
    try:
        results = YoutubeSearch(query, max_results=1).to_dict()
        link = f"https://youtube.com{results[0]['url_suffix']}"
        print(results)
        title = results[0]["title"]
        thumbnail = results[0]["thumbnails"][0]
        duration = results[0]["duration"]
        views = results[0]["views"]
        # if time_to_seconds(duration) >= 1800:  # duration limit
        #     m.edit("Exceeded 30mins cap")
        #     return
    except Exception as e:
        m.edit(
            "✖️ Found Nothing. Sorry.\n\nTry another keywork or maybe spell it properly."
        )
        print(str(e))
        return
    m.edit("⏬ Downloading.")
    try:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(link, download=False)
            audio_file = ydl.prepare_filename(info_dict)
            ydl.process_info(info_dict)
        rep = f'🎧 Title: `{title}`\n⏳ Duration: `{duration}`\n👁‍🗨 Views: `{views}`'
        secmul, dur, dur_arr = 1, 0, duration.split(':')
        for i in range(len(dur_arr)-1, -1, -1):
            dur += (int(dur_arr[i]) * secmul)
            secmul *= 60
        message.reply_audio(audio_file, caption=rep, parse_mode='md', title=title, duration=dur)
        m.delete()
    except Exception as e:
        m.edit('❌ Error')
        print(e)
        # os.rename(audio_file, "audio.webm")
    # command = 'ffmpeg -i "'+ audio_file + '" -vn "' + audio_file[:-4] + '.m4a"'
    # m.edit("Converting...")
    # p = subprocess.Popen(command, stdout=subprocess.PIPE, shell=False)
    # p.wait()

    try:
        os.remove(audio_file)
        # os.remove(audio_file[:-4] + '.m4a')
    except Exception as e:
        print(e)

bot.run()
