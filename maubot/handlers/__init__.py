"""Инициализация всех роутеров.

Весь функционал бота был поделён на различные обработчики для
большей гибкости.
"""

from maubot.handlers import player, session, simple_commands, turn, user

# Список всех работающих роутеров
# Роутеры из этого списка будут включены в диспетчер бота
ROUTERS = (
    # Основная информация о пользователе
    user.router,
    simple_commands.router,
    session.router,
    player.router,
    turn.router
)

__all__ = ("ROUTERS",)
