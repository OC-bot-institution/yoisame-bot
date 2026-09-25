import discord
import os
from dotenv import load_dotenv

from discord.ext import commands
import asyncio
import random
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from bot_common.special_reply import (
    get_user_name,
    special_reply_exact,
    special_reply_contains,
    special_reply_endswith,
    special_reply_ordered,
    mention_reply,
)

from bot_common.util import (
    load_common_json,
    load_json
)

from bot_common.change_icon import change_icon

#初期設定
#==============================

# 基本の反応確率
REPLY_PROBABILITY = 0.1


JST = ZoneInfo("Asia/Tokyo")
icon_task = None


# アクティブチャンネル
channels = load_common_json("channels.json")
ACTIVE_CHANNELS = {
    int(channel_id)
    for channel_id in channels
}

# API
load_dotenv()
api_key = os.getenv("API_KEY")

bot_status = "awake"



# 読み込み
phrases = load_json("phrases.json")
keywords = load_common_json("keywords.json")
names = load_common_json("users.json")

exact = phrases["exact"]
contains = phrases["contains"]
endswith = phrases["endswith"]
ordered = phrases["ordered"]
mentions = phrases["mention"]


# インテントの生成
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)
#==============================






# discordと接続した時に呼ばれる
@bot.event
async def on_ready():
    global icon_task
    await bot.tree.sync()

    if icon_task is None or icon_task.done():
        icon_task = asyncio.create_task(
            change_icon(bot,"icons")
        )

    print(f"ログインしました: {bot.user}")


# メッセージを受信した時に呼ばれる
@bot.event
async def on_message(message):
    if message.author.bot:
        return
    if bot_status == "sleep":
        return

    user_name = get_user_name(message,names)

    if bot.user in message.mentions and bot.user.mention in message.content:
        await mention_reply(message, mentions, user_name)
        return

    if message.channel.id not in ACTIVE_CHANNELS:
        # 確率で反応しない
        if random.random() >= REPLY_PROBABILITY:
            return

    if await special_reply_exact(message,exact,keywords,user_name):
        return
    if await special_reply_contains(message,contains,keywords,user_name):
        return
    if await special_reply_endswith(message,endswith,keywords,user_name):
        return
    if await special_reply_ordered(message,ordered,keywords,user_name):
        return

        
    await bot.process_commands(message)

@bot.tree.command(
    name="sleep",
    description="しばらく反応しなくなります"
)
async def sleep(
    interaction: discord.Interaction,
    minutes: int
):
    global bot_status

    if bot_status=="sleep":
        await interaction.response.send_message("ｽﾔｧ...")
        return
    
    bot_status = "sleep"
    await interaction.response.send_message(
        f"{minutes}分だけ寝ます。おやすみ！！！！！"
    )
    await asyncio.sleep(minutes * 60)
    bot_status = "awake"


@bot.tree.command(
    name="awake",
    description="反応するようになります"
)
async def awake(interaction: discord.Interaction,):
    global bot_status
    bot_status = "awake"
    await interaction.response.send_message(f"おはらいな☆")

# クライアントの実行
bot.run(api_key)