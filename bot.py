import asyncio, logging, os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from anthropic import AsyncAnthropic

TELEGRAM_TOKEN, CLAUDE_API_KEY = os.getenv("TELEGRAM_TOKEN"), os.getenv("CLAUDE_API_KEY")
logging.basicConfig(level=logging.INFO)
bot, dp, claude = Bot(token=TELEGRAM_TOKEN), Dispatcher(), AsyncAnthropic(api_key=CLAUDE_API_KEY)

SYSTEM_PROMPT = """Sen — Mobile Legends (MLBB) bo‘yicha o‘zbek murabbiyisan. O‘zbek tilida, yoshlarbop, gamer tilida (farm, gank, ult, meta, pro) javob ber. Adabiy va quruq so‘zlardan qoch. Geroy so‘rasa: Roli, Combo, Build, Counter va Pro maslahat ber."""

main_menu = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text="🦸‍♂️ Geroy o‘rganish"), KeyboardButton(text="🔥 Hozirgi Meta")],[KeyboardButton(text="🎮 Vaziyatli O‘yin (Test)"), KeyboardButton(text="💡 Pro Maslahatlar")],[KeyboardButton(text="⚔️ Counter-Pick (Kimga kim?)")]], resize_keyboard=True)
user_histories = {}

async def ask_claude(user_id, msg):
    if user_id not in user_histories: user_histories[user_id] = []
    user_histories[user_id].append({"role": "user", "content": msg})
    if len(user_histories[user_id]) > 10: user_histories[user_id] = user_histories[user_id][-10:]
    try:
        res = await claude.messages.create(model="claude-3-5-sonnet-20241022", max_tokens=1024, system=SYSTEM_PROMPT, messages=user_histories[user_id])
        reply = res.content[0].text
        user_histories[user_id].append({"role": "assistant", "content": reply})
        return reply
    except: return "⚠️ Ping ko‘tarilib ketdi 😅, birozdan keyin yozib ko‘r!"

@dp.message(CommandStart())
async def start(m: types.Message):
    user_histories[m.from_user.id] = []
    await m.answer(f"Salom, **{m.from_user.first_name}**! Men MLBB bo‘yicha murabbiyingman. Geroy nomini yoz!", reply_markup=main_menu, parse_mode="Markdown")

@dp.message()
async def all_msg(m: types.Message):
    await bot.send_chat_action(chat_id=m.chat.id, action="typing")
    await m.answer(await ask_claude(m.from_user.id, m.text), parse_mode="Markdown")

async def main(): await dp.start_polling(bot)
if __name__ == "__main__": asyncio.run(main())
