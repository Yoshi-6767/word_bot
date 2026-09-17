import os
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

# Загрузка слов из файла
if os.path.exists(FILE):
    with open(FILE, "r", encoding="utf-8") as f:
        words = json.load(f)
    words = {int(k): v for k, v in words.items()}

# Сохранение слов в файл
def save():
    with open(FILE, "w", encoding="utf-8") as f:
        json.dump(words, f, ensure_ascii=False, indent=2)

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer(
        "Йоу, чувак. Я твой тренажёр слов.\n"
        "Напиши /add, чтобы добавить слова.\n"
        "Напиши /train, чтобы тренить."
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
                await message.answer("Верно! 🔥")
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
