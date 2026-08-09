import discord
import os
from dotenv import load_dotenv
from extract_phrase import extract_phrase
from special_reply import init,special_reply_exact,special_reply_contains,special_reply_endswith,special_reply_ordered,mention_reply

from discord.ext import commands
import asyncio
import random
from util import load_json

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
#初期設定
#==============================
# アクティブでないチャンネルで発言する確率
REPLY_PROBABILITY = 0.1

# 毎日おはよう設定
TARGET_CHANNEL_IDS = [
    123456789012345678,
    234567890123456789,
    345678901234567890,
]
NORMAL_PROBABILITY = 0.12
NEBOU_PROBABILITY = 0.02
HAYAI_PROBABILITY = 0.02
JST = ZoneInfo("Asia/Tokyo")
#==============================
channels = load_json("channels.json")
ACTIVE_CHANNELS = {
    int(channel_id)
    for channel_id in channels
}
daily_message_task = None


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



# 決まった時間の固定メッセージ
# 時間も、基準の時間から±30分ぐらい前後してランダムに選びたい
async def daily_message():
    while True:
        now = datetime.now(JST)

        # 今日の07:00を基準にする
        base_time = now.replace(
            hour=7,
            minute=0,
            second=0,
            microsecond=0
        )

        status = "none"
        probability = random.random()

        # 寝坊
        if probability < NEBOU_PROBABILITY:
            offset = random.randint(180, 210)
            status = "nebou"

        # 早起き
        elif probability < NEBOU_PROBABILITY + HAYAI_PROBABILITY:
            offset = random.randint(-210, -180)
            status = "hayai"

        # 通常
        elif probability < (
            NEBOU_PROBABILITY
            + HAYAI_PROBABILITY
            + NORMAL_PROBABILITY
        ):
            offset = random.randint(-30, 30)
            status = "normal"

        # それ以外は送信しない
        else:
            offset = random.randint(-30, 30)
            status = "none"

        target = base_time + timedelta(minutes=offset)
        # すでに実行時刻を過ぎていたら明日の07:00を基準にする
        if target <= now:
            target += timedelta(days=1)

        # 次回実行まで待つ
        wait_seconds = (target - now).total_seconds()

        print(
            f"次回の定期メッセージ: "
            f"{target.strftime('%Y-%m-%d %H:%M:%S')}"
            f"status : {status}"
        )

        await asyncio.sleep(wait_seconds)

        # チャンネルをランダムに1つ選択
        channel_id = random.choice(TARGET_CHANNEL_IDS)
        channel = bot.get_channel(channel_id)

        if channel is None:
            print(f"チャンネルが見つかりません: {channel_id}")
            continue

        phrase = random.choice(
            ["おはらいな～！！","おはらいな！","おはらいな☀️"]
        )
        if status == "nebou":
            phrase += "......まだ眠いよ。。。"
        elif status == "hayai":
            phrase += "はやおきしてえらい！！"
        await channel.send(phrase)


# discordと接続した時に呼ばれる
@bot.event
async def on_ready():
    global daily_message_task
    await bot.tree.sync()

    if daily_message_task is None or daily_message_task.done():
        daily_message_task = asyncio.create_task(
            daily_message()
        )

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