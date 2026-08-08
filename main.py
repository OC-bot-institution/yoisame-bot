import discord
import os
from dotenv import load_dotenv
from extract_phrase import extract_phrase
from special_reply import init,special_reply_exact,special_reply_contains,special_reply_endswith,special_reply_ordered,mention_reply

from discord.ext import commands
import asyncio
import random
import json
from pathlib import Path

#初期設定
#==============================
REPLY_PROBABILITY = 0.1
#らいな雑談、くらうどーむ雑談、らいな雑談2、創作雑談、くらうどーむメモ、一般
ACTIVE_CHANNELS = {1456597613926154452,1468960224730943560,1526572399833911296,1438885241170428068,1533682775448883260,1534055479049981974}
#==============================



load_dotenv()
api_key = os.getenv("API_KEY")

bot_status = "awake"

# インテントの生成
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)

# discordと接続した時に呼ばれる
@bot.event
async def on_ready():
    await bot.tree.sync()

    #bot.loop.create_task(console_loop())

    print(f"ログインしました: {bot.user}")


# メッセージを受信した時に呼ばれる
@bot.event
async def on_message(message):
    if message.author.bot:
        return
    if bot_status == "sleep":
        return
    


    init(message)
    if bot.user in message.mentions:
        await mention_reply(message)

    if message.channel.id not in ACTIVE_CHANNELS:
        #反応確率：30%
        if random.random() >= REPLY_PROBABILITY:
            return
    
    if await special_reply_exact(message):
        return
    if await special_reply_contains(message):
        return
    if await special_reply_endswith(message):
        return
    if await special_reply_ordered(message):
        return

        
    await bot.process_commands(message)

@bot.tree.command(
    name="sleep",
    description="30分寝ます"
)
async def sleep(interaction: discord.Interaction):

    global bot_status

    bot_status = "sleep"

    await interaction.response.send_message(
        "30分だけ寝ますおやすみ！！！！！"
    )

    await asyncio.sleep(1800)

    bot_status = "awake"


# クライアントの実行
bot.run(api_key)