import discord
import os
from dotenv import load_dotenv
from discord.ext import commands
import asyncio




load_dotenv()
api_key = os.getenv("API_KEY")



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

    bot.loop.create_task(console_loop())

    print(f"ログインしました: {bot.user}")


async def console_loop():
    await bot.wait_until_ready()

    while True:
        text = await asyncio.to_thread(input, ">>> ")

        try:
            channel_id, message = text.split(maxsplit=1)
            channel_id = int(channel_id)

            channel = bot.get_channel(channel_id)

            if channel is None:
                print("チャンネルが見つかりません")
                continue

            await channel.send(message)

        except Exception as e:
            print("エラー:", e)

# クライアントの実行
bot.run(api_key)