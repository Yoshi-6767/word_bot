import asyncio
import random
import json
import os
from datetime import date
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, BufferedInputFile

TOKEN = os.getenv("BOT_TOKEN")

bot = Bot(token=TOKEN)
dp = Dispatcher()

FILE = "words.json"
words = {}
mode = {}
current_word = {}

hangman_state = {}

PHRASES_FILE = "phrases.json"
phrases = {}

LEARNED_FILE = "learned.json"
learned = {}

STATS_FILE = "stats.json"
stats = {}

ACHIEVEMENTS_FILE = "achievements.json"
achievements = {}

CORRECT_PHRASES = [
    "Джонни Инглиш гордится тобой! 🎩",
    "Шпионская работа! Чисто. 🕶️",
    "Есть! Цель поражена. 🎯",
    "Британский акцент одобряет. ☕",
    "Ты в ударе! Не останавливайся. 🔥",
    "Хладнокровно. Профессионально. 🧊",
    "Точно в цель, агент. 🎯",
    "Я бы дал тебе орден, но пока только +1 к интеллекту. 🏅",
]

WRONG_PHRASES = [
    "Мимо, агент. Правильно: {correct}",
    "Провал миссии. Запомни: {correct}",
    "Не то. Но Джонни тоже иногда падает в кусты. Правильно: {correct}",
    "Хм. Это было смело. Но неправильно. Правильно: {correct}",
    "Даже у Бонда бывают осечки. Правильно: {correct}",
    "Твой ответ ушёл в архив неудач. Правильно: {correct}",
    "Не угадал. Шпионская школа недовольна. Правильно: {correct}",
    "Ошибка. Но это тоже опыт. Правильно: {correct}",
]

ALL_ACHIEVEMENTS = {
    "first_blood": {"name": "🌱 Первая кровь", "desc": "Первое слово выучено", "need": 1, "type": "learned"},
    "sniper": {"name": "🎯 Снайпер", "desc": "5 слов выучено", "need": 5, "type": "learned"},
    "agent_010": {"name": "🥉 Агент 010", "desc": "10 слов выучено", "need": 10, "type": "learned"},
    "agent_025": {"name": "🥈 Агент 025", "desc": "25 слов выучено", "need": 25, "type": "learned"},
    "agent_050": {"name": "🥇 Агент 050", "desc": "50 слов выучено", "need": 50, "type": "learned"},
    "agent_100": {"name": "🏆 Агент 100", "desc": "100 слов выучено", "need": 100, "type": "learned"},
    "super_spy": {"name": "💎 Супершпион", "desc": "250 слов выучено", "need": 250, "type": "learned"},
    "legend": {"name": "👑 Легенда разведки", "desc": "500 слов выучено", "need": 500, "type": "learned"},
    "three_days": {"name": "🔥 Три дня в строю", "desc": "3 дня подряд", "need": 3, "type": "streak"},
    "week_warrior": {"name": "⚡ Неделя без пропусков", "desc": "7 дней подряд", "need": 7, "type": "streak"},
    "month_machine": {"name": "💪 Месяц дисциплины", "desc": "30 дней подряд", "need": 30, "type": "streak"},
    "long_word": {"name": "📏 Длинномер", "desc": "Слово из 10+ букв в базе", "need": 10, "type": "long_word"},
    "phrase_master": {"name": "🗣️ Мастер диалога", "desc": "10 фраз добавлено", "need": 10, "type": "phrases"},
    "orator": {"name": "🎭 Оратор", "desc": "50 фраз добавлено", "need": 50, "type": "phrases"},
    "night_owl": {"name": "🌙 Полуночник", "desc": "Тренировка после 00:00", "need": 1, "type": "night"},
    "perfectionist": {"name": "🎯 Перфекционист", "desc": "10 правильных подряд", "need": 10, "type": "perfect"},
    "reverse_master": {"name": "🔄 Мастер реверса", "desc": "10 правильных ответов в режиме «наоборот»", "need": 10, "type": "reverse"},
    "hangman_winner": {"name": "🪢 Палач", "desc": "Выиграть в Виселицу", "need": 1, "type": "hangman"},
}

if os.path.exists(STATS_FILE):
    with open(STATS_FILE, "r", encoding="utf-8") as f:
        stats = json.load(f)
    stats = {int(k): v for k, v in stats.items()}

if os.path.exists(ACHIEVEMENTS_FILE):
    with open(ACHIEVEMENTS_FILE, "r", encoding="utf-8") as f:
        achievements = json.load(f)
    achievements = {int(k): v for k, v in achievements.items()}

def save_stats():
    with open(STATS_FILE, "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)

def save_achievements():
    with open(ACHIEVEMENTS_FILE, "w", encoding="utf-8") as f:
        json.dump(achievements, f, ensure_ascii=False, indent=2)

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

async def check_achievements(message: types.Message, user_id: int, hangman_win: bool = False):
    unlocked = achievements.get(user_id, [])
    learned_count = len(learned.get(user_id, {}))
    phrases_count = len(phrases.get(user_id, {}))
    streak = stats.get(user_id, {}).get("streak", 0)
    perfect = stats.get(user_id, {}).get("perfect", 0)
    reverse = stats.get(user_id, {}).get("reverse", 0)
    new_achievements = []

    for key, ach in ALL_ACHIEVEMENTS.items():
        if key in unlocked:
            continue

        value = 0
        if ach["type"] == "learned":
            value = learned_count
        elif ach["type"] == "phrases":
            value = phrases_count
        elif ach["type"] == "streak":
            value = streak
        elif ach["type"] == "long_word":
            if words.get(user_id):
                longest = max(words[user_id].keys(), key=len)
                value = len(longest)
        elif ach["type"] == "night":
            value = 1
        elif ach["type"] == "perfect":
            value = perfect
        elif ach["type"] == "reverse":
            value = reverse
        elif ach["type"] == "hangman":
            value = 1 if hangman_win else 0

        if value >= ach["need"]:
            unlocked.append(key)
            new_achievements.append(ach)

    if new_achievements:
        achievements[user_id] = unlocked
        save_achievements()
        for ach in new_achievements:
            await message.answer(
                f"🏆 ДОСТИЖЕНИЕ РАЗБЛОКИРОВАНО!\n"
                f"{ach['name']}\n"
                f"{ach['desc']}"
            )

# Главное меню
def get_main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📚 Слова", callback_data="sub_words")],
        [InlineKeyboardButton(text="📝 Фразы", callback_data="sub_phrases")],
        [InlineKeyboardButton(text="🏆 Прогресс", callback_data="sub_progress")],
        [InlineKeyboardButton(text="🎮 Игры", callback_data="sub_games")]
    ])

# Подменю "Слова"
def get_words_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📚 Добавить", callback_data="menu_add")],
        [InlineKeyboardButton(text="🔥 Тренировать", callback_data="menu_train")],
        [InlineKeyboardButton(text="🔄 Наоборот", callback_data="menu_reverse")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_main")]
    ])

# Подменю "Фразы"
def get_phrases_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 Добавить", callback_data="menu_addphrase")],
        [InlineKeyboardButton(text="🎯 Тренировать", callback_data="menu_trainphrase")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_main")]
    ])

# Подменю "Прогресс"
def get_progress_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🧠 Выученное", callback_data="menu_learned")],
        [InlineKeyboardButton(text="🏆 Достижения", callback_data="menu_achievements")],
        [InlineKeyboardButton(text="📊 Статистика", callback_data="menu_stats")],
        [InlineKeyboardButton(text="📤 Экспорт", callback_data="menu_export")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_main")]
    ])

# Подменю "Игры"
def get_games_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🪢 Виселица", callback_data="menu_hangman")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data="back_main")]
    ])

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer(
        "Йоу, чувак. Я твой тренажёр слов.\n"
        "Выбирай раздел:",
        reply_markup=get_main_menu()
    )

@dp.message(Command("menu"))
async def menu(message: types.Message):
    await message.answer("Меню:", reply_markup=get_main_menu())

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
    await check_achievements(message, user_id)

@dp.message(Command("learned"))
async def learned_list(message: types.Message):
    user_id = message.from_user.id
    if user_id not in learned or not learned[user_id]:
        await message.answer("Ты пока ничего не выучил.")
        return
    text = "\n".join([f"{k} → {v}" for k, v in learned[user_id].items()])
    await message.answer(f"Выученные слова:\n{text}")

@dp.message(Command("export"))
async def export(message: types.Message):
    user_id = message.from_user.id
    if user_id not in words or not words[user_id]:
        await message.answer("У тебя пока нет слов для экспорта.")
        return
    text = "МОИ СЛОВА\n\n"
    for k, v in words[user_id].items():
        text += f"{k} - {v}\n"
    if user_id in phrases and phrases[user_id]:
        text += "\n\nМОИ ФРАЗЫ\n\n"
        for k, v in phrases[user_id].items():
            text += f"{k} - {v}\n"
    await message.answer_document(
        BufferedInputFile(text.encode("utf-8"), filename="my_words.txt"),
        caption="📤 Твой экспорт"
    )

@dp.callback_query()
async def handle_callback(call: types.CallbackQuery):
    user_id = call.from_user.id
    data = call.data

    if data == "sub_words":
        await call.message.edit_text("📚 Раздел «Слова»:", reply_markup=get_words_menu())

    elif data == "sub_phrases":
        await call.message.edit_text("📝 Раздел «Фразы»:", reply_markup=get_phrases_menu())

    elif data == "sub_progress":
        await call.message.edit_text("🏆 Раздел «Прогресс»:", reply_markup=get_progress_menu())

    elif data == "sub_games":
        await call.message.edit_text("🎮 Раздел «Игры»:", reply_markup=get_games_menu())

    elif data == "back_main":
        await call.message.edit_text("Главное меню:", reply_markup=get_main_menu())

    elif data == "menu_add":
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

    elif data == "menu_reverse":
        if user_id not in words or not words[user_id]:
            await call.message.answer("У тебя пока нет слов. Сначала добавь через /add.")
        else:
            mode[user_id] = "reverse"
            await call.message.answer("Режим «наоборот». Я кидаю русское слово, ты — английский перевод.")

    elif data == "menu_hangman":
        if user_id not in words or not words[user_id]:
            await call.message.answer("У тебя пока нет слов для игры. Сначала добавь через /add.")
        else:
            word = random.choice(list(words[user_id].keys()))
            hangman_state[user_id] = {"word": word, "guessed": [], "errors": 0}
            display = " ".join(["_" if c not in " " else " " for c in word])
            await call.message.answer(
                f"🪢 Виселица\n\n"
                f"Слово: {display}\n"
                f"Ошибок: 0/6\n\n"
                f"Угадывай буквы по одной."
            )
            mode[user_id] = "hangman"

    elif data == "menu_learned":
        if user_id not in learned or not learned[user_id]:
            await call.message.answer("Ты пока ничего не выучил.")
        else:
            text = "\n".join([f"{k} → {v}" for k, v in learned[user_id].items()])
            await call.message.answer(f"Выученные слова:\n{text}")

    elif data == "menu_achievements":
        unlocked = achievements.get(user_id, [])
        if not unlocked:
            await call.message.answer("🏆 У тебя пока нет достижений. Учи слова — и они появятся!")
        else:
            text = "🏆 Твои достижения:\n\n"
            for key in unlocked:
                ach = ALL_ACHIEVEMENTS.get(key)
                if ach:
                    text += f"✅ {ach['name']} — {ach['desc']}\n"
            await call.message.answer(text)

    elif data == "menu_export":
        if user_id not in words or not words[user_id]:
            await call.message.answer("У тебя пока нет слов для экспорта.")
        else:
            text = "МОИ СЛОВА\n\n"
            for k, v in words[user_id].items():
                text += f"{k} - {v}\n"
            if user_id in phrases and phrases[user_id]:
                text += "\n\nМОИ ФРАЗЫ\n\n"
                for k, v in phrases[user_id].items():
                    text += f"{k} - {v}\n"
            await call.message.answer_document(
                BufferedInputFile(text.encode("utf-8"), filename="my_words.txt"),
                caption="📤 Твой экспорт"
            )

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
            await check_achievements(message, user_id)
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
                user_stats = stats.get(user_id, {})
                perfect = user_stats.get("perfect", 0) + 1
                user_stats["perfect"] = perfect
                stats[user_id] = user_stats
                save_stats()

                phrase = random.choice(CORRECT_PHRASES)
                if perfect == 3:
                    phrase += "\n🔥 Три подряд! Ты разогрелся."
                elif perfect == 5:
                    phrase += "\n🏆 Пять подряд! Ты машина, агент."
                elif perfect == 10:
                    phrase += "\n👑 Десять! Ты не человек, ты легенда."

                await message.answer(phrase)
                await check_achievements(message, user_id)
            else:
                user_stats = stats.get(user_id, {})
                user_stats["perfect"] = 0
                stats[user_id] = user_stats
                save_stats()

                phrase = random.choice(WRONG_PHRASES).format(correct=correct)
                await message.answer(phrase)

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
                user_stats = stats.get(user_id, {})
                perfect = user_stats.get("perfect", 0) + 1
                user_stats["perfect"] = perfect
                stats[user_id] = user_stats
                save_stats()

                phrase = random.choice(CORRECT_PHRASES)
                if perfect == 3:
                    phrase += "\n🔥 Три подряд! Ты разогрелся."
                elif perfect == 5:
                    phrase += "\n🏆 Пять подряд! Ты машина, агент."
                elif perfect == 10:
                    phrase += "\n👑 Десять! Ты не человек, ты легенда."

                await message.answer(phrase)
                await check_achievements(message, user_id)
            else:
                user_stats = stats.get(user_id, {})
                user_stats["perfect"] = 0
                stats[user_id] = user_stats
                save_stats()

                phrase = random.choice(WRONG_PHRASES).format(correct=correct)
                await message.answer(phrase)

            available = [w for w in phrases[user_id].keys() if w != eng]
            if not available:
                await message.answer("Ты прошёл все фразы! Добавь новые через /addphrase.")
                del current_word[user_id]
            else:
                new_eng = random.choice(available)
                current_word[user_id] = new_eng
                await message.answer(f"Переведи: {new_eng}")

    elif mode.get(user_id) == "reverse":
        if user_id not in current_word:
            eng = random.choice(list(words[user_id].keys()))
            correct = words[user_id][eng]
            current_word[user_id] = correct
            await message.answer(f"Переведи на английский: {correct}")
        else:
            correct_eng = current_word[user_id]
            rus = None
            for k, v in words[user_id].items():
                if v == correct_eng:
                    rus = k
                    break
            if text.lower() == rus.lower():
                user_stats = stats.get(user_id, {})
                reverse = user_stats.get("reverse", 0) + 1
                user_stats["reverse"] = reverse
                stats[user_id] = user_stats
                save_stats()

                await message.answer(random.choice(CORRECT_PHRASES))
                await check_achievements(message, user_id)
            else:
                await message.answer(f"Не то. Правильно: {rus}")

            available = [w for w in words[user_id].keys() if words[user_id][w] != correct_eng]
            if not available:
                await message.answer("Ты прошёл все слова! Добавь новые через /add.")
                del current_word[user_id]
            else:
                new_eng = random.choice(available)
                current_word[user_id] = words[user_id][new_eng]
                await message.answer(f"Переведи на английский: {words[user_id][new_eng]}")

    elif mode.get(user_id) == "hangman":
        state = hangman_state.get(user_id)
        if not state:
            await message.answer("Начни игру заново через меню.")
            return
        if len(text) != 1 or not text.isalpha():
            await message.answer("Отправь одну букву.")
            return
        letter = text.lower()
        word = state["word"]
        if letter in state["guessed"]:
            await message.answer("Эту букву уже называл.")
            return
        state["guessed"].append(letter)
        if letter not in word:
            state["errors"] += 1
        display = " ".join([c if c in state["guessed"] else "_" for c in word])
        if all(c in state["guessed"] for c in word):
            await message.answer(f"🎉 Ты угадал! Слово: {word}")
            del hangman_state[user_id]
            mode[user_id] = None
            await check_achievements(message, user_id, hangman_win=True)
        elif state["errors"] >= 6:
            await message.answer(f"💀 Ты проиграл. Слово было: {word}")
            del hangman_state[user_id]
            mode[user_id] = None
        else:
            await message.answer(
                f"Слово: {display}\n"
                f"Ошибок: {state['errors']}/6"
            )

if __name__ == "__main__":
    asyncio.run(dp.start_polling(bot))
