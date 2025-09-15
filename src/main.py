import uuid

from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.types import (
    Message, InlineQuery, InlineQueryResultCachedPhoto, InputMediaPhoto,
    InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, BotCommand, FSInputFile
)

from src.core.config import BOT_TOKEN, ADMIN_ID
from src.service.service import (get_or_create_user_service, set_stats_service, resset_stats_service, add_stats_service,
                                 compare_units_service, add_statistics_service)
from src.utils.utils import make_profile_card, update_stats, start_challenger, get_winner
from src.models.models import Messages


dp = Dispatcher()


@dp.message(Command("start"))
async def cmd_start(m: Message):
    user = await get_or_create_user_service(m.from_user.id, m.from_user.first_name)
    if not user:
        await m.answer(Messages.CREATE_ERROR.value)
        return
    photo = FSInputFile("./images/start.png")
    caption = Messages.SEND_HELLO.value
    await m.answer_photo(photo=photo, caption=caption)


@dp.message(Command("info"))
async def info(m: Message):
    photo = FSInputFile("./images/info.png")
    caption = Messages.SEND_INFO.value
    await m.answer_photo(photo=photo, caption=caption)


@dp.message(Command("profile"))
async def cmd_profile(m: Message):
    user = await get_or_create_user_service(m.from_user.id, m.from_user.first_name)
    if not user:
        await m.answer(Messages.GET_ERROR.value)
        return

    photo = FSInputFile("./images/profile.png")
    caption = make_profile_card(user)
    await m.answer_photo(photo=photo, caption=caption)


@dp.message(Command("set"))
async def cmd_setstats(m: Message):
    user = await get_or_create_user_service(m.from_user.id, m.from_user.first_name)
    if not user:
        await m.answer(Messages.GET_ERROR.value)
        return
    list_stats = m.text.split()

    if len(list_stats) not in (2, 3, 4):
        await m.answer(Messages.HINT.value)
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
            await m.answer(Messages.SET_ERROR.value)
            return

        user = await get_or_create_user_service(m.from_user.id, m.from_user.first_name)
        photo = FSInputFile("./images/set.png")
        caption = update_stats(user)
        await m.answer_photo(photo=photo, caption=caption)
    except ValueError:
        await m.answer(Messages.WARNING.value)

#УШЕЛ В ТУАЛЕТ ЩА БУДУ


@dp.message(Command("reset"))
async def cmd_setstats(m: Message):
    result = await resset_stats_service(user_id=m.from_user.id)
    if result:
        photo = FSInputFile("./images/reset.png")
        caption = Messages.SUCCESSFUL.value
        await m.answer_photo(photo=photo, caption=caption)
        return
    await m.answer(Messages.RESET_ERROR.value)


@dp.inline_query()
async def inline_duel(query: InlineQuery):
    challenger = query.from_user
    challenger_user = await get_or_create_user_service(user_id=challenger.id, user_name=challenger.first_name)
    if not challenger_user:
        return

    result_id = str(uuid.uuid4())
    message_text = start_challenger(challenger_user)

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⚔️ Принять вызов", callback_data=f"accept:{challenger.id}")]
        ]
    )

    item = InlineQueryResultCachedPhoto(
        id=result_id,
        photo_file_id="AgACAgIAAxkBAAIBiGjDI6l2NBpyj5RGzrYS0FTONyG7AAKR_TEbv_YZSk6EVmZhlkkRAQADAgADeQADNgQ",
        caption=message_text,
        reply_markup=kb
    )

    await query.answer([item], cache_time=1, is_personal=False)


@dp.callback_query(F.data.startswith("accept:"))
async def on_accept(cq: CallbackQuery, bot: Bot):
    try:
        _, challenger_id_str = cq.data.split(":")
        challenger_id = int(challenger_id_str)
    except Exception:
        await cq.answer("❌ Некорректные данные кнопки.", show_alert=True)
        return

    # Инициатор (A)
    challenger_user = types.User(id=challenger_id, is_bot=False, first_name=f"user_{challenger_id}")
    challenger_user = await get_or_create_user_service(challenger_user.id, challenger_user.first_name)

    # Принявший (B)
    accept_user = await get_or_create_user_service(cq.from_user.id, cq.from_user.first_name)
    if not accept_user:
        await cq.answer("❌ Не удалось создать профиль. Попробуй ещё раз.", show_alert=True)
        return

    if challenger_user.user_id == accept_user.user_id:
        await cq.answer("❌ Нельзя принять собственный вызов 😅", show_alert=True)
        return

    # Бой
    winner, loser, flag = compare_units_service(a=challenger_user, b=accept_user, clamp=5)

    if not flag:
        # НИЧЬЯ
        media_file_id = 'AgACAgIAAxkBAAIBjGjGy05SM9rdXmhOeLliOKZA4ie3AAIU-jEb4vc4StkgPmIHjlvNAQADAgADeQADNgQ'
        caption = Messages.DRAW.value
        result_winner = await add_statistics_service(user_id=winner.user_id, lose=1)
        result_loser = await add_statistics_service(user_id=loser.user_id, lose=1)
        if not result_winner and not result_loser:
            await cq.answer("❌ Не удалось сразиться. Попробуй ещё раз.", show_alert=True)
            return
    else:
        # ПОБЕДА
        media_file_id = 'AgACAgIAAxkBAAIBimjDI7RmGXszPiMsoCelYBknhFgYAAKT_TEbv_YZSsmSOiuRmoC9AQADAgADeQADNgQ'
        caption = get_winner(winner)
        # Пробуем выдать награду
        ok, point = await add_stats_service(winner.user_id)
        if not ok:
            caption += "\n\n💀💀💀Очки не были начислены."
        caption += f"\n\n✨Очки начислены: {point}"
        result_winner = await add_statistics_service(user_id=winner.user_id, win=1)
        result_loser = await add_statistics_service(user_id=loser.user_id, lose=1)
        if not result_winner and not result_loser:
            await cq.answer("❌ Не удалось сразиться. Попробуй ещё раз.", show_alert=True)
            return

    # Меняем media (картинку + подпись) тем же сообщением
    media = InputMediaPhoto(media=media_file_id, caption=caption)

    try:
        if cq.inline_message_id:
            # сообщение отправлено через inline (без chat_id)
            await bot.edit_message_media(
                inline_message_id=cq.inline_message_id,
                media=media,
                reply_markup=None  # можно убрать кнопки; или оставить свою
            )

        else:
            # обычное сообщение в чате
            await bot.edit_message_media(
                chat_id=cq.message.chat.id,
                message_id=cq.message.message_id,
                media=media,
                reply_markup=None
            )

    except Exception:
        await cq.answer("❌ Не удалось изменить картинку.", show_alert=True)
        return

    await cq.answer()


@dp.message(F.photo)
async def get_file_id(m: Message):
    if m.from_user.id == ADMIN_ID:
        file_id = m.photo[-1].file_id
        await m.answer(f"📎 file_id: `{file_id}`")
    return


async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="Запуск бота"),
        BotCommand(command="info", description="Информация"),
        BotCommand(command="profile", description="Мой профиль"),
        BotCommand(command="set", description="Задать STR AGI INT"),
        BotCommand(command="reset", description="Сбросить характеристики"),
    ]
    await bot.set_my_commands(commands)


async def main():
    bot = Bot(BOT_TOKEN)
    await set_commands(bot)
    await dp.start_polling(bot)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
