"""Инициализация всех роутеров.

Весь функционал бота был поделён на различные обработчики для
большей гибкости.
"""

from maubot.handlers import user

# Список всех работающих роутеров
# Роутеры из этого списка будут включены в диспетчер бота
ROUTERS = (
    # Основная информация о пользователе
    user.router,
)

__all__ = ("ROUTERS",)
