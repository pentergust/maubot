"""Главный файл бота.

Здесь определены функции для запуска бота и регистрации всех обработчиков.
"""

import sys
from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import Bot, Dispatcher
from aiogram.types import (
    CallbackQuery,
    ChatMemberUpdated,
    ChosenInlineResult,
    ErrorEvent,
    InlineQuery,
    Message,
    Update,
)
from aiogram.utils.token import TokenValidationError
from loguru import logger

from mau.session import TelegramSessionManager
from maubot.config import config, default
from maubot.handlers import ROUTERS

# Константы
# =========

sm = TelegramSessionManager()
dp = Dispatcher(sm=sm)


# Настраиваем формат отображения логов loguru
# Обратите внимание что в проекте помимо loguru используется logging
LOG_FORMAT = (
    "<light-black>{time:YYYY MM.DD HH:mm:ss.SSS}</> "
    "{file}:{function} "
    "<lvl>{message}</>"
)

# Middleware
# ==========


@dp.message.middleware()  # type: ignore
@dp.inline_query.middleware()  # type: ignore
@dp.callback_query.middleware()  # type: ignore
@dp.chat_member.middleware()  # type: ignore
@dp.chosen_inline_result.middleware()  # type: ignore
async def game_middleware(
    handler: Callable[[Update, dict[str, Any]], Awaitable[Any]],
    event: Update,
    data: dict[str, Any],
) -> Callable[[Update, dict[str, Any]], Awaitable[Any]]:
    """Предоставляет экземпляр игры в обработчики сообщений."""
    if isinstance(event, Message | ChatMemberUpdated):
        game = sm.games.get(str(event.chat.id))
    elif isinstance(event, CallbackQuery):
        if event.message is None:
            chat_id = sm.user_to_chat.get(str(event.from_user.id))
            game = None if chat_id is None else sm.games.get(chat_id)
        else:
            game = sm.games.get(event.message.chat.id)
    elif isinstance(event, InlineQuery | ChosenInlineResult):
        chat_id = sm.user_to_chat.get(str(event.from_user.id))
        game = None if chat_id is None else sm.games.get(chat_id)
    else:
        raise ValueError("Unknown update type")

    data["game"] = game
    data["player"] = (
        None
        if game is None or event.from_user is None
        else game.get_player(str(event.from_user.id))
    )
    return await handler(event, data)


# TODO: Вот тут было бы неплохо обработать глобальные ошибки и не повторяться
@dp.errors()
async def catch_errors(event: ErrorEvent) -> None:
    """Простой обработчик для ошибок."""
    logger.warning(event)
    logger.exception(event.exception)

    if event.update.callback_query:
        message = event.update.callback_query.message
    elif event.update.message:
        message = event.update.message
    else:
        message = None

    if message is not None:
        await message.answer(
            text=(
                "❌ <b>Что-то явно пошло не по плану...</b>\n\n"
                f"{event.exception}"
            )
        )


# Главная функция запуска бота
# ============================


async def main() -> None:
    """Запускает бота.

    Настраивает журнал действий.
    Загружает все необходимые обработчики.
    После запускает обработку событий бота.
    """
    logger.remove()
    logger.add(sys.stdout, format=LOG_FORMAT)

    logger.info("Setup bot ...")
    try:
        bot = Bot(
            token=config.telegram_token.get_secret_value(), default=default
        )
        sm.bot = bot
    except TokenValidationError as e:
        logger.error(e)
        logger.info("Check your bot token in .env file.")
        sys.exit(1)

    logger.info("Load handlers ...")
    for router in ROUTERS:
        dp.include_router(router)
        logger.debug("Include router {}", router.name)

    logger.success("Start polling!")
    await dp.start_polling(bot)
