"""Все использованные сообщения в боте, доступные в общем доступе.

Разные обработчики могут получить доступ к данным сообщениям.
"""

from maubot.config import config

# Когда пользователь пишет сообщение /help
HELP_MESSAGE = (
    "🍰 <b>Три простых шага чтобы начать</b>:\n"
    "1. Добавьте бота в группу.\n"
    "2. В группе начните новую игру через /game или подключитесь через /join.\n"
    "3. Если вас двое и больше, начинайте игру при помощи /start!\n"
    "4. Введите <code>@mili_maubot</code> в чате или жмякните на "
    "<code>via @mili_maubot</code>.\n"
    "Здесь все ваши карты, а ещё кнопки чтобы взять карты и посмотреть или "
    "проверить текущее состояние игры.\n"
    "<b>Серые</b> карты вы пока не можете разыграть.\n"
    "Нажмите на один из стикеров, чтобы разыграть его.\n\n"
    "Игроки могут подключиться в любое время.\n"
    "Чтобы покинуть игру используйте /leave.\n"
    "Если игрок долго думает. его можно пропустить командой /skip.\n"
    "☕ О прочих командах можно узнать в <b>меню</b>.\n"
)

# Рассказывает об авторстве проекта и новостном канале
STATUS_MESSAGE = (
    "🌟 <b>Информация о боте</b>:\n\n"
    "<b>Maubot</b> - Telegram бот с открытым исходным кодом, предоставляющий "
    "пользователям играть в Uno в групповых чатах.\n"
    "Исходный код проекта доступен в "
    "<a href='https://codeberg.org/pentergust/maubot'>Codeberg</a>.\n"
    "Мы будем очень рады если вы внесёте свой вклад в развитие бота. 🍓\n\n"
    "Узнать о всех новостях проекта вы можете в Telegram канале "
    "<a href='https://t.me/mili_qlaster'>Salorhard</a>."
)


# Игровые комнаты
# ===============

# Если в данном чате ещё не создано ни одной комнаты
NO_ROOM_MESSAGE = (
    "👀 В данном чате <b>нет игровой комнаты</b>.\n"
    "Создайте новую при помощи команды /game."
)

# Когда недостаточно игроков для продолжения игры
NOT_ENOUGH_PLAYERS = (
    f"🍰 <b>Недостаточно игроков<b> (минимум {config.min_players}) для "
    "начала игры.\n"
    "Воспользуйтесь командой /join чтобы присоединиться к игре."
)

