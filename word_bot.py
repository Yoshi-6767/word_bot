import asyncio
import random
import json
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()

FILE = "words.json"
words = {}
mode = {}
current_word = {}

LEARNED_FILE = "learned.json"
learned = {}

if os.path.exists(LEARNED_FILE):
    with open(LEARNED_FILE, "r", encoding="utf-8") as f:
        learned = json.load(f)
    learned = {int(k): v for k, v in learned.items()}

if os.path.exists(FILE):
    with open(FILE, "r", encoding="utf-8") as f:
        words = json.load(f)
    words = {int(k): v for k, v in words.items()}

def save():
    with open(FILE, "w", encoding="utf-8") as f:
        json.dump(words, f, ensure_ascii=False, indent=2)

def save_learned():
    with open(LEARNED_FILE, "w", encoding="utf-8") as f:
        json.dump(learned, f, ensure_ascii=False, indent=2)

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer(
        "Йоу, чувак. Я твой тренажёр слов.\n"
        "Напиши /add, чтобы добавить слова.\n"
        "Напиши /train, чтобы тренить.\n"
        "Напиши /learn слово, чтобы перенести его в выученные.\n"
        "Напиши /learned, чтобы посмотреть выученные слова."
    )

@dp.message(Command("add"))
async def add(message: types.Message):
    user_id = message.from_user.id
    mode[user_id] = "add"
    await message.answer("Кидай слова в формате: английское - русское. По одному в строке.")

@dp.message(Command("train"))
async def train(message: types.Message):
    user_id = message.from_user.id
    if user_id not in words or not words[user_id]:
        await message.answer("У тебя пока нет слов. Сначала добавь через /add.")
        return
    mode[user_id] = "train"
    await message.answer("Погнали. Я буду кидать слово на английском, ты — перевод.")

@dp.message(Command("learn"))
async def learn(message: types.Message):
    user_id = message.from_user.id
    word = message.text.replace("/learn", "").strip().lower()
    if user_id not in words or word not in words[user_id]:
        await message.answer("Такого слова нет в базе.")
        return
    learned.setdefault(user_id, {})[word] = words[user_id][word]
    del words[user_id][word]
    save()
    save_learned()
    await message.answer(f"Выучил: {word} → {learned[user_id][word]}")

@dp.message(Command("learned"))
async def learned_list(message: types.Message):
    user_id = message.from_user.id
    if user_id not in learned or not learned[user_id]:
        await message.answer("Ты пока нихуя не выучил.")
        return
    text = "\n".join([f"{k} → {v}" for k, v in learned[user_id].items()])
    await message.answer(f"Выученные слова:\n{text}")

@dp.message()
async def handle(message: types.Message):
    user_id = message.from_user.id
    text = message.text.strip()

    if mode.get(user_id) == "add":
        if " - " in text:
            eng, rus = text.split(" - ", 1)
            words.setdefault(user_id, {})[eng.strip().lower()] = rus.strip()
            save()
            await message.answer(f"Записал: {eng} → {rus}")
        else:
            await message.answer("Не понял. Формат: слово - перевод")

    elif mode.get(user_id) == "train":
        if user_id not in current_word:
            eng = random.choice(list(words[user_id].keys()))
            current_word[user_id] = eng
            await message.answer(f"Переведи: {eng}")
        else:
            eng = current_word[user_id]
            correct = words[user_id][eng]
            if text.lower() == correct.lower():
                await message.answer("Верно! Дабл ю! 🔥")
            else:
                await message.answer(f"Не то. Правильно: {correct}")

            available = [w for w in words[user_id].keys() if w != eng]
            if not available:
                await message.answer("Ты прошёл все слова! Добавь новые через /add.")
                del current_word[user_id]
            else:
                new_eng = random.choice(available)
                current_word[user_id] = new_eng
                await message.answer(f"Переведи: {new_eng}")

if __name__ == "__main__":
    asyncio.run(dp.start_polling(bot))
