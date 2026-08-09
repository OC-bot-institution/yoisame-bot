import json
from pathlib import Path
import random
import asyncio
import re
from itertools import product
import unicodedata

from util import load_json
    
#フレーズ
phrases = load_json("phrases.json")
exact = phrases["exact"]
contains = phrases["contains"]
endswith = phrases["endswith"]
ordered = phrases["ordered"]
mention = phrases["mention"]

#ユーザー
names = load_json("users.json")
name = ""

#キーワード
keywords = load_json("keywords.json")

# 待ち時間設定
base = 0.8
per_char = 0.1


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFKC", text)
    text = text.lower()
    text = re.sub(r"[!！?？〜～ー\-…・、。,\.\s]", "", text)
    return text


def expand_keys(keys: list[str], keywords: dict) -> list[str]:
    expanded = []

    for key in keys:

        # &で始まるキーワードをすべて取得
        tokens = re.findall(r"&([^&]+)&", key)

        if not tokens:
            expanded.append(key)
            continue

        # 各トークンの候補一覧
        candidates = []
        for token in tokens:
            if token in keywords:
                candidates.append(keywords[token])
            else:
                # 定義されていないものはそのまま残す
                candidates.append([f"&{token}"])

        # 全組み合わせを生成
        for words in product(*candidates):
            result = key
            for token, word in zip(tokens, words):
                result = result.replace(f"&{token}&", word, 1)
            expanded.append(result)

    return expanded


def init(message):
    global name
    user_id = str(message.author.id)    
    if user_id in names:
        name = names[user_id]
    else:
        name = message.author.display_name


async def mention_reply(message):
    reply = random.choice(mention["replies"])
    reply = reply.replace("&user", name)

    await message.reply(
        reply,
        mention_author=False
    )
    return

#共通関数
async def special_reply(message, rules, judge):
    text = normalize(message.content)

    for rule in rules:

        if random.random() > rule["probability"]:
            continue
        keys = expand_keys(rule["keys"], keywords)
        if any(judge(text, normalize(key)) for key in keys):
            reply = random.choice(rule["replies"])
            wait = base + len(reply) * per_char + random.uniform(0, 1.2)
            reply = reply.replace("&user", name)
            async with message.channel.typing():
                await asyncio.sleep(wait)
            await message.reply(
                reply,
                mention_author=False
            )

            return True

    return False

#完全一致
async def special_reply_exact(message):
    return await special_reply(
        message,
        exact,
        lambda t, k: t == k
    )

#部分一致

async def special_reply_contains(message):
    return await special_reply(
        message,
        contains,
        lambda t, k: k in t
    )


async def special_reply_endswith(message):
    return await special_reply(
        message,
        endswith,
        lambda t, k: t.endswith(k)
    )


async def special_reply_ordered(message):
    return await special_reply(
        message,
        ordered,
        contains_in_order
    )


def contains_in_order(text: str, pattern: str) -> bool:
    if not pattern:
        return False
    index = 0
    for ch in text:
        if ch == pattern[index]:
            index += 1
            if index == len(pattern):
                return True
    return False

