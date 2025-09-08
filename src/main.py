
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import (
    Message,
)

from src.core.config import BOT_TOKEN
from src.service.service import get_or_create_user_service, set_stats_service

dp = Dispatcher()


@dp.message(Command("start"))
async def cmd_start(m: Message):
    user = await get_or_create_user_service(m.from_user.id, m.from_user.first_name)
    if not user:
        await m.answer("Не удалось создать профиль. Попробуй ещё раз.")
        return
    await m.answer(
        "Привет! Я inline-бот дуэлей.\n\n"
        "Напиши в любом чате: <code>@AdventureeeeBot</code> и отправь карточку.\n"
        "Любой может нажать «Принять вызов», и я сразу покажу результат боя.\n\n"
        "Можешь обновить статы через личку командами:\n"
        "<code>/setstats STR AGI INT</code> — задать статы\n"
        "<code>/profile</code> — мой профиль",
        parse_mode=ParseMode.HTML,
    )


@dp.message(Command("profile"))
async def cmd_profile(m: Message):
    user = await get_or_create_user_service(m.from_user.id, m.from_user.first_name)
    if not user:
        await m.answer("Не удалось получить профиль. Попробуй ещё раз.")
        return

    await m.answer(
        f"<b>{user.name}</b>\n"
        f"STR <code>{user.STR}</code> AGI <code>{user.AGI}</code> INT <code>{user.INT}</code> HP <code>{user.HP}</code>\n"
        f"POINT <code>{user.POINT}</code>  FREE POINT <code>{user.FREE_POINT}</code>",
        parse_mode=ParseMode.HTML,
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
            i=i,
        )
        if not result:
            await m.answer("Не удалось обновить stats. Попробуй ещё раз.")
            return

        user = await get_or_create_user_service(m.from_user.id, m.from_user.first_name)
        await m.reply("✅ Обновлено.\n"
                      f"*{user.name}* → STR <code>{user.STR}</code> AGI <code>{user.AGI}</code> INT <code>{user.INT}</code>",
                      parse_mode=ParseMode.HTML)
    except ValueError:
        await m.reply("Все значения должны быть целыми.", parse_mode=ParseMode.HTML)


#УШЕЛ В ТУАЛЕТ ЩА БУДУ


'''
# =========================
# INLINE: "via @bot"
# =========================
@dp.inline_query()
async def inline_duel(query: InlineQuery):
    """
    Пользователь пишет: @YourBot <текст>
    Мы показываем карточку «Вызвать на дуэль».
    В саму карточку кладём кнопку «Принять вызов».
    В callback_data передаём id вызывающего (чтобы в момент принятия знать «кто вызвал»).
    """
    challenger = query.from_user
    get_or_create_user(challenger)  # чтобы были статы по умолчанию

    opponent_hint = (query.query or "").strip() or "кого-нибудь"
    result_id = str(uuid.uuid4())

    # Кнопка «Принять вызов» — нажимает любой желающий
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Принять вызов", callback_data=f"accept:{challenger.id}")]
    ])

    msg_text = f"⚔️ {challenger.full_name} вызывает на дуэль *{opponent_hint}*!"
    item = InlineQueryResultArticle(
        id=result_id,
        title="Вызвать на дуэль",
        description=f"Бросить вызов «{opponent_hint}»",
        input_message_content=InputTextMessageContent(msg_text, parse_mode="Markdown"),
        reply_markup=kb
    )

    # cache_time=1 — чтобы изменения placeholder сразу подтягивались
    await query.answer([item], cache_time=1, is_personal=False)

# =========================
# CALLBACK: принятие вызова
# =========================
@dp.callback_query(F.data.startswith("accept:"))
async def on_accept(cq: CallbackQuery, bot: Bot):
    """
    Пользователь B жмёт «Принять вызов».
    В data храним id инициатора (A). Сражаем A vs B.
    Сообщение было отправлено в чат «via @YourBot», поэтому это inline-сообщение:
    редактируем текст через inline_message_id.
    """
    try:
        _, challenger_id_str = cq.data.split(":")
        challenger_id = int(challenger_id_str)
    except Exception:
        await cq.answer("Некорректные данные кнопки.", show_alert=True)
        return

    # Инициатор дуэли (A)
    challenger_user = types.User(id=challenger_id, is_bot=False, first_name=f"user_{challenger_id}")
    A = get_or_create_user(challenger_user)

    # Принявший дуэль (B) — тот, кто нажал кнопку
    B = get_or_create_user(cq.from_user)

    # Запрещаем принимать свой же вызов
    if A.user_id == B.user_id:
        await cq.answer("Нельзя принять собственный вызов 😅", show_alert=True)
        return

    # Проводим бой
    winner, battle = fight_with_log(A, B, rng=random)

    # Формируем итоговый текст (сохраним «via @bot» — оно останется, мы просто редактируем)
    result_text = (
        f"⚔️ {A.name} вызвал на дуэль *кого-то*.\n\n"  # исходный заголовок можно переписать на свой вкус
        + fmt_log(battle)
    )

    # Редактируем inline-сообщение.
    # В callback из inline-сообщения TELEGRAM присылает inline_message_id.
    if cq.inline_message_id:
        try:
            await bot.edit_message_text(
                inline_message_id=cq.inline_message_id,
                text=result_text,
                parse_mode="Markdown"
            )
        except Exception:
            # Если по каким-то причинам редактировать нельзя, просто ответим алертом.
            await cq.answer("Не удалось отредактировать сообщение.", show_alert=True)
            return
    else:
        # На случай, если кнопка пришла из обычного сообщения (редкий сценарий)
        try:
            await bot.edit_message_text(
                chat_id=cq.message.chat.id,
                message_id=cq.message.message_id,
                text=result_text,
                parse_mode="Markdown"
            )
        except Exception:
            await cq.answer("Не удалось обновить сообщение.", show_alert=True)
            return

    await cq.answer("Дуэль завершена!")
'''


# =========================
# ЗАПУСК
# =========================
async def main():
    bot = Bot(BOT_TOKEN)
    await dp.start_polling(bot)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
