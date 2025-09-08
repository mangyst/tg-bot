import random
import uuid

from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.enums import ParseMode
from aiogram.types import (
    Message, InlineQuery, InlineQueryResultArticle, InputTextMessageContent,
    InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
)

from src.core.config import BOT_TOKEN
from src.service.service import get_or_create_user_service, set_stats_service, resset_stats_service, fight_with_log_service, add_stats_service


dp = Dispatcher()


@dp.message(Command("start"))
async def cmd_start(m: Message):
    user = await get_or_create_user_service(m.from_user.id, m.from_user.first_name)
    if not user:
        await m.answer("❎ Не удалось создать профиль. Попробуй ещё раз.")
        return
    await m.answer(
        "Привет! Я inline-бот дуэлей.\n\n"
        "Напиши в любом чате: <code>@AdventureeeeBot</code> и отправь карточку.\n"
        "Любой может нажать «Принять вызов», и я сразу покажу результат боя.\n\n"
        "Можешь обновить статы через личку командами:\n"
        "<code>/setstats STR AGI INT</code> — задать характеристики\n"
        "<code>/profile</code> — мой профиль\n"
        "<code>/resetstats</code> - сбросить характеристики",
        parse_mode=ParseMode.HTML
    )


@dp.message(Command("profile"))
async def cmd_profile(m: Message):
    user = await get_or_create_user_service(m.from_user.id, m.from_user.first_name)
    if not user:
        await m.answer("❎ Не удалось получить профиль. Попробуй ещё раз.")
        return

    await m.answer(
        f"<b>{user.name}</b>\n"
        f"STR <code>{user.STR}</code> AGI <code>{user.AGI}</code> INT <code>{user.INT}</code> HP <code>{user.HP}</code>\n"
        f"POINT <code>{user.POINT}</code>  FREE POINT <code>{user.FREE_POINT}</code>",
        parse_mode=ParseMode.HTML
    )


@dp.message(Command("setstats"))
async def cmd_setstats(m: Message):
    user = await get_or_create_user_service(m.from_user.id, m.from_user.first_name)
    list_stats = m.text.split()

    if len(list_stats) not in (2, 3, 4):
        await m.reply("Использование: `/setstats STR AGI INT`", parse_mode=ParseMode.HTML)
        return

    try:
        if len(list_stats) == 2:
            s = int(list_stats[-1])
            a = 0
            i = 0
        elif len(list_stats) == 3:
            s, a = map(int, list_stats[1:])
            i = 0
        else:
            s, a, i = map(int, list_stats[1:])

        result = await set_stats_service(
            user_id=user.user_id,
            user_name=user.name,
            s=s,
            a=a,
            i=i
        )
        if not result:
            await m.answer("❎ Не удалось обновить характеристики. Попробуй ещё раз.")
            return

        user = await get_or_create_user_service(m.from_user.id, m.from_user.first_name)
        await m.reply("✅ Обновлено.\n"
                      f"*{user.name}* → STR <code>{user.STR}</code> AGI <code>{user.AGI}</code> INT <code>{user.INT}</code>",
                      parse_mode=ParseMode.HTML)
    except ValueError:
        await m.reply("Все значения должны быть целыми.", parse_mode=ParseMode.HTML)


#УШЕЛ В ТУАЛЕТ ЩА БУДУ

@dp.message(Command("resetstats"))
async def cmd_setstats(m: Message):
    result = await resset_stats_service(user_id=m.from_user.id)
    if result:
        await m.reply("✅ Характеристики сброшены.", parse_mode=ParseMode.HTML)
        return
    await m.reply("❎ Не удалось сбросить характеристики.  Попробуй ещё раз.", parse_mode=ParseMode.HTML)
    return


@dp.inline_query()
async def inline_duel(query: InlineQuery):
    text = (query.query or "").strip().lower()
    if text != "дуэль":
        return

    challenger = query.from_user
    challenger_user = await get_or_create_user_service(user_id=challenger.id, user_name=challenger.first_name)
    if not challenger_user:
        return

    result_id = str(uuid.uuid4())
    message_text = f"⚔️ {challenger.full_name} бросил вызов чату!"

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Принять вызов", callback_data=f"accept:{challenger.id}")]
        ]
    )

    item = InlineQueryResultArticle(
        id=result_id,
        title="Вызвать на дуэль",
        description="Отправить вызов чату",
        input_message_content=InputTextMessageContent(
            message_text=message_text,
            parse_mode="Markdown"
        ),
        reply_markup=kb
    )

    await query.answer([item], cache_time=1, is_personal=False)


@dp.callback_query(F.data.startswith("accept:"))
async def on_accept(cq: CallbackQuery, bot: Bot):
    try:
        _, challenger_id_str = cq.data.split(":")
        challenger_id = int(challenger_id_str)
    except Exception:
        await cq.answer("Некорректные данные кнопки.", show_alert=True)
        return

    # Инициатор дуэли (A)
    challenger_user = types.User(id=challenger_id, is_bot=False, first_name=f"user_{challenger_id}")
    challenger_user = await get_or_create_user_service(user_id=challenger_user.id, user_name=challenger_user.first_name)

    # Принявший дуэль (B) — тот, кто нажал кнопку
    accept_user = await get_or_create_user_service(user_id=cq.from_user.id, user_name=cq.from_user.first_name)
    if not accept_user:
        await cq.answer("❎ Не удалось сбросить характеристики.  Попробуй ещё раз.", show_alert=True)

    # Запрещаем принимать свой же вызов
    if challenger_user.user_id == accept_user.user_id:
        await cq.answer("Нельзя принять собственный вызов 😅", show_alert=True)
        return

    # Проводим бой
    winner = fight_with_log_service(challenger_user, accept_user, rng=random)
    if not winner:
        result_text = (
            f"⚔️ Исход боя ничья я в АХУЕ как так вышло"
        )
        if cq.inline_message_id:
            try:
                await bot.edit_message_text(
                    inline_message_id=cq.inline_message_id,
                    text=result_text,
                    parse_mode="Markdown"
                )
            except Exception:
                await cq.answer("❎ Не удалось отредактировать сообщение.", show_alert=True)
                return
        else:
            try:
                await bot.edit_message_text(
                    chat_id=cq.message.chat.id,
                    message_id=cq.message.message_id,
                    text=result_text,
                    parse_mode="Markdown"
                )
            except Exception:
                await cq.answer("❎ Не удалось обновить сообщение.", show_alert=True)
                return
    else:
        result_text = (
            f"⚔️ {winner.name} победил"
        )
        result = await add_stats_service(winner.user_id)
        if result:
            if cq.inline_message_id:
                try:
                    await bot.edit_message_text(
                        inline_message_id=cq.inline_message_id,
                        text=result_text,
                        parse_mode="Markdown"
                    )
                except Exception:
                    await cq.answer("❎ Не удалось отредактировать сообщение.", show_alert=True)
                    return
            else:
                try:
                    await bot.edit_message_text(
                        chat_id=cq.message.chat.id,
                        message_id=cq.message.message_id,
                        text=result_text,
                        parse_mode="Markdown"
                    )
                except Exception:
                    await cq.answer("❎ Не удалось обновить сообщение.", show_alert=True)
                    return
        else:
            result_text = (
                f"⚔️ {winner.name} победил\n"
                f"но балы не получил"
            )
            try:
                await bot.edit_message_text(
                    inline_message_id=cq.inline_message_id,
                    text=result_text,
                    parse_mode="Markdown"
                )
            except Exception:
                await cq.answer("❎ Не удалось отредактировать сообщение.", show_alert=True)
                return


async def main():
    bot = Bot(BOT_TOKEN)
    await dp.start_polling(bot)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
