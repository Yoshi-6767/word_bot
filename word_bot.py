import asyncio
import random
import json
import os
from datetime import date
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()

FILE = "words.json"
words = {}
mode = {}
current_word = {}

PHRASES_FILE = "phrases.json"
phrases = {}

LEARNED_FILE = "learned.json"
learned = {}

STATS_FILE = "stats.json"
stats = {}

if os.path.exists(STATS_FILE):
    with open(STATS_FILE, "r", encoding="utf-8") as f:
        stats = json.load(f)
    stats = {int(k): v for k, v in stats.items()}

def save_stats():
    with open(STATS_FILE, "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)

if os.path.exists(LEARNED_FILE):
    with open(LEARNED_FILE, "r", encoding="utf-8") as f:
        learned = json.load(f)
    learned = {int(k): v for k, v in learned.items()}

if os.path.exists(PHRASES_FILE):
    with open(PHRASES_FILE, "r", encoding="utf-8") as f:
        phrases = json.load(f)
    phrases = {int(k): v for k, v in phrases.items()}

if os.path.exists(FILE):
    with open(FILE, "r", encoding="utf-8") as f:
        words = json.load(f)
    words = {int(k): v for k, v in words.items()}

def save():
    with open(FILE, "w", encoding="utf-8") as f:
        json.dump(words, f, ensure_ascii=False, indent=2)

def save_phrases():
    with open(PHRASES_FILE, "w", encoding="utf-8") as f:
        json.dump(phrases, f, ensure_ascii=False, indent=2)

def save_learned():
    with open(LEARNED_FILE, "w", encoding="utf-8") as f:
        json.dump(learned, f, ensure_ascii=False, indent=2)

def get_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📚 Добавить слова", callback_data="menu_add")],
        [InlineKeyboardButton(text="📝 Добавить фразы", callback_data="menu_addphrase")],
        [InlineKeyboardButton(text="🔥 Тренировать слова", callback_data="menu_train")],
        [InlineKeyboardButton(text="🎯 Тренировать фразы", callback_data="menu_trainphrase")],
        [InlineKeyboardButton(text="🧠 Выученное", callback_data="menu_learned")],
        [InlineKeyboardButton(text="📊 Статистика", callback_data="menu_stats")]
    ])

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer(
        "Йоу, чувак. Я твой тренажёр слов.\n"
        "Выбирай, что делаем:",
        reply_markup=get_menu()
    )

@dp.message(Command("menu"))
async def menu(message: types.Message):
    await message.answer("Меню:", reply_markup=get_menu())

@dp.message(Command("add"))
async def add(message: types.Message):
    user_id = message.from_user.id
    mode[user_id] = "add"
    await message.answer("Кидай слова в формате: английское - русское. По одному в строке.")

@dp.message(Command("addphrase"))
async def addphrase(message: types.Message):
    user_id = message.from_user.id
    mode[user_id] = "addphrase"
    await message.answer("Кидай фразы в формате: английская - русская. По одной в строке.")

@dp.message(Command("train"))
async def train(message: types.Message):
    user_id = message.from_user.id
    if user_id not in words or not words[user_id]:
        await message.answer("У тебя пока нет слов. Сначала добавь через /add.")
        return
    mode[user_id] = "train"
    await message.answer("Погнали. Я буду кидать слово на английском, ты — перевод.")

@dp.message(Command("trainphrase"))
async def trainphrase(message: types.Message):
    user_id = message.from_user.id
    if user_id not in phrases or not phrases[user_id]:
        await message.answer("У тебя пока нет фраз. Сначала добавь через /addphrase.")
        return
    mode[user_id] = "trainphrase"
    await message.answer("Погнали. Я буду кидать фразу на английском, ты — перевод.")

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
        await message.answer("Ты пока ничего не выучил.")
        return
    text = "\n".join([f"{k} → {v}" for k, v in learned[user_id].items()])
    await message.answer(f"Выученные слова:\n{text}")

@dp.callback_query()
async def handle_callback(call: types.CallbackQuery):
    user_id = call.from_user.id
    data = call.data

    if data == "menu_add":
        mode[user_id] = "add"
        await call.message.answer("Кидай слова в формате: английское - русское.")

    elif data == "menu_addphrase":
        mode[user_id] = "addphrase"
        await call.message.answer("Кидай фразы в формате: английская - русская.")

    elif data == "menu_train":
        if user_id not in words or not words[user_id]:
            await call.message.answer("У тебя пока нет слов. Сначала добавь через /add.")
        else:
            mode[user_id] = "train"
            await call.message.answer("Погнали. Я буду кидать слово на английском, ты — перевод.")

    elif data == "menu_trainphrase":
        if user_id not in phrases or not phrases[user_id]:
            await call.message.answer("У тебя пока нет фраз. Сначала добавь через /addphrase.")
        else:
            mode[user_id] = "trainphrase"
            await call.message.answer("Погнали. Я буду кидать фразу на английском, ты — перевод.")

    elif data == "menu_learned":
        if user_id not in learned or not learned[user_id]:
            await call.message.answer("Ты пока ничего не выучил.")
        else:
            text = "\n".join([f"{k} → {v}" for k, v in learned[user_id].items()])
            await call.message.answer(f"Выученные слова:\n{text}")

    elif data == "menu_stats":
        total = len(words.get(user_id, {}))
        learned_count = len(learned.get(user_id, {}))
        all_words = total + learned_count

        if all_words == 0:
            await call.message.answer("У тебя пока нет слов. Добавь через /add.")
            await call.answer()
            return

        percent = round(learned_count / all_words * 100)
        today = str(date.today())

        user_stats = stats.get(user_id, {})
        last_day = user_stats.get("last_day", "")
        streak = user_stats.get("streak", 0)

        if last_day != today:
            yesterday = str(date.fromordinal(date.today().toordinal() - 1))
            if last_day == yesterday:
                streak += 1
            else:
                streak = 1
            stats[user_id] = {"last_day": today, "streak": streak}
            save_stats()

        longest = ""
        if words.get(user_id):
            longest = max(words[user_id].keys(), key=len)

        await call.message.answer(
            f"📊 Твоя статистика:\n\n"
            f"📚 Слов в базе: {total}\n"
            f"🧠 Выучено: {learned_count}\n"
            f"📈 Прогресс: {percent}%\n"
            f"🔥 Серия дней: {streak}\n"
            f"🏆 Рекорд: {longest if longest else '—'}"
        )

    await call.answer()

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

    elif mode.get(user_id) == "addphrase":
        if " - " in text:
            eng, rus = text.split(" - ", 1)
            phrases.setdefault(user_id, {})[eng.strip().lower()] = rus.strip()
            save_phrases()
            await message.answer(f"Записал: {eng} → {rus}")
        else:
            await message.answer("Не понял. Формат: фраза - перевод")

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

    elif mode.get(user_id) == "trainphrase":
        if user_id not in current_word:
            eng = random.choice(list(phrases[user_id].keys()))
            current_word[user_id] = eng
            await message.answer(f"Переведи: {eng}")
        else:
            eng = current_word[user_id]
            correct = phrases[user_id][eng]
            if text.lower() == correct.lower():
                await message.answer("Верно! 🔥")
            else:
                await message.answer(f"Не то. Правильно: {correct}")

            available = [w for w in phrases[user_id].keys() if w != eng]
            if not available:
                await message.answer("Ты прошёл все фразы! Добавь новые через /addphrase.")
                del current_word[user_id]
            else:
                new_eng = random.choice(available)
                current_word[user_id] = new_eng
                await message.answer(f"Переведи: {new_eng}")

if __name__ == "__main__":
    asyncio.run(dp.start_polling(bot))
