"""Все использованные сообщения в боте, доступные в общем доступе.

Разные обработчики могут получить доступ к данным сообщениям.
Здесь представлены как статические сообщения, так и динамические.
"""

from datetime import datetime

from mau import exceptions
from mau.game import UnoGame
from maubot.config import config

# Когда пользователь пишет сообщение /help
# Немного рассказывает про бота и как им пользоваться
HELP_MESSAGE = (
    "🍰 <b>Три простых шага чтобы начать веселье</b>!\n\n"
    "1. Добавьте бота в вашу группу.\n"
    "2. В группе создайте комнату через /game или зайдите в неё через /join.\n"
    "3. Как только все собрались, начинайте игру при помощи /start!\n"
    "4. Введите <code>@mili_maubot</code> в чате или жмякните на кнопку хода.\n"
    "Здесь все ваши карты, а ещё кнопки чтобы взять карты и "
    "проверить текущее состояние игры.\n"
    "<b>Серые</b> карты вы пока не можете разыграть.\n"
    "Нажмите на один из стикеров карты, чтобы разыграть её.\n\n"
    "🌳 Игроки могут подключиться в любое время.\n"
    "Если не хотите чтобы вам помешали, закройте комнату через /close.\n"
    "Чтобы покинуть игру используйте /leave.\n"
    "Если игрок долго думает. его можно пропустить командой /skip.\n"
    "☕ О прочих командах можно узнать в <b>меню</b>.\n"
)

# Рассказывает об авторстве проекта и новостном канале
# Просто как минутка рекламы
STATUS_MESSAGE = (
    "🌟 <b>Информация о боте</b>:\n\n"
    "🃏 <b>Maubot</b> - Telegram бот с открытым исходным кодом, позволяющий "
    "пользователям играть в Uno с друзьями в групповых чатах.\n"
    "Исходный код проекта доступен в "
    "<a href='https://codeberg.org/salormoont/maubot'>Codeberg</a>, а также в"
    "<a href='https://github.com/pentergust/maubot'>Github</a>.\n"
    "🍓 Мы будем очень рады ваше <b>поддержке</b> в развитие бота.\n\n"
    "Узнать о всех будущих планах вы можете в Telegram канале "
    "<a href='https://t.me/mili_qlaster'>Salorhard</a>."
)

# Игровые комнаты ------------------------------------------------------

# Если в данном чате ещё не создано ни одной комнаты
NO_ROOM_MESSAGE = (
    "👀 В данном чате ещё <b>нет игровой комнаты</b>.\n"
    "🍰 Вы можете <b>создайте новую</b> при помощи команды /game."
)

NO_JOIN_MESSAGE = (
    "🍓 Для начала надо <b>зайти в комнату</b>.\n"
    "🍰 Сделать это можно командой /join.\n"
    "🔑 Если комната <b>закрыта</b> дождитесь окончания игры."
)


# Когда недостаточно игроков для продолжения/начала игры
NOT_ENOUGH_PLAYERS = (
    f"🌳 <b>Недостаточно игроков</b> (минимум {config.min_players}) для "
    "игры.\n"
    "Если игра ещё <b>не началась</b> воспользуйтесь командой "
    "/join чтобы зайти в комнату.\n"
    "🍰 Или создайте новую комнату при помощи /game."
)


def get_closed_room_message(game: UnoGame) -> str:
    """Когда пользователь пытается подключиться в закрытую комнату."""
    return (
        "🔒 К сожалению данная комната <b>закрыта</b>.\n"
        f"Вы можете попросить {game.owner.name} открыть"
        "комнату или дождаться окончания игра."
    )


# Вспомогательные функции
# =======================


def plural_form(n: int, v: tuple[str, str, str]) -> str:
    """Возвращает склонённое значение в зависимости от числа.

    Возвращает склонённое слово: "для одного", "для двух",
    "для пяти" значений.
    """
    return v[2 if (4 < n % 100 < 20) else (2, 0, 1, 1, 1, 2)[min(n % 10, 5)]]  # noqa: PLR2004


def get_str_timedelta(seconds: int) -> str:
    """Возвращает строковое представление времени из количества секунд.

    Модификатор времени автоматически склоняется в зависимости от времени.
    """
    m, s = divmod(seconds, 60)
    if m == 0:
        return f"{s} {plural_form(m, ('секунду', 'секунды', 'секунд'))}"
    if s == 0:
        return f"{m} {plural_form(m, ('минуту', 'минуты', 'минут'))}"
    return (
        f"{m} {plural_form(m, ('минуту', 'минуты', 'минут'))} и "
        f"{s} {plural_form(m, ('секунду', 'секунды', 'секунд'))}"
    )


# Динамические сообщения
#  =====================


def get_room_rules(game: UnoGame) -> str:
    """Получает включенные игровые правила для текущей комнаты.

    Отображает список правил и общее количество включенных правил.
    Если ничего не выбрано, то вернёт пустую строку.
    """
    rule_list = ""
    active_rules = 0
    for rule in game.rules:
        if rule.status:
            active_rules += 1
            rule_list += f"\n- {rule.name}"

    if active_rules == 0:
        return ""
    return f"🔥 Выбранные правила {active_rules}:{rule_list}"


def get_all_room_players(game: UnoGame) -> str:
    """Собирает список участников игры без описания карт и текущего игрока.

    Используется в комнате до начала игры, поскольку тут не нужно знать
    кто начал игру, сколько у кого карт и так далее.

    Если игроков в комнате ещё нет, вернёт милое сообщение что в комнате
    ещё пусто.
    """
    if len(game.players) == 0:
        return "✨ В комнате пока никого нету.\n"
    players_list = f"✨ всего игроков {len(game.players)}:\n"
    for player in game.players:
        players_list += f"- {player.name}\n"
    return players_list


def get_new_game_message(game: UnoGame) -> str:
    """Сообщение о начале новой игры в комнате.

    Показывает кто первым ходит, полный список игроков и выбранные
    режимы игры.
    """
    return (
        "🌳 Да начнётся <b>Новая игра!</b>!\n"
        f"✨ И первым у нас ходит {game.player.name}\n"
        "/rules чтобы изменить игровые правила.\n"
        "/close чтобы закрыть комнату от посторонних.\n\n"
        f"{get_all_room_players(game)}\n"
        f"{get_room_rules(game)}"
    )


def get_room_status(game: UnoGame) -> str:
    """Отображает статус текущей комнаты.

    Используется и при создании новой комнаты.
    Показывает список игроков и полезные команды.

    Если игра уже началась, то добавляется самая разна полезная
    информация о текущем состоянии игры.
    Как минимум список игроков, выбранные режимы, количество карт и так
    далее.
    """
    if not game.started:
        return (
            f"☕ Новая <b>Игровая комната</b>!\n"
            f"🪄 <b>Создатель</b>: {game.owner.name}\n\n"
            f"{get_all_room_players(game)}\n"
            "⚙️ Игровые <b>правила</b> позволяют сделать игру более весёлой.\n"
            "- /rules настройки игровых правил комнаты\n"
            "- /join чтобы присоединиться к игре ✨\n"
            "- /start для начала веселья!🍰"
        )

    if game.rules.single_shotgun.status:
        shotgun_stats = f"🔫 <b>Револьвер</b>: {game.shotgun_current} / 8"
    else:
        shotgun_stats = ""

    now = datetime.now()
    game_delta = get_str_timedelta(int((now - game.game_start).total_seconds()))
    turn_delta = get_str_timedelta(int((now - game.turn_start).total_seconds()))
    return (
        f"☕ <b>Игровая комната</b> {game.owner.name}:\n"
        f"🃏 <b>Последняя карта</b>: {game.deck.top}\n"
        f"🦝 <b>Сейчас ход</b> {game.player.name} "
        f"(прошло {turn_delta})\n\n"
        f"{get_room_players(game)}\n"
        f"{get_room_rules(game)}\n"
        f"⏳ <b>Игра идёт</b> {game_delta}\n"
        f"📦 <b>карт</b> в колоде: {len(game.deck.cards)} доступно / "
        f"{len(game.deck.used_cards)} использовано.\n{shotgun_stats}"
    )


def get_error_message(exc: Exception) -> str:
    """Возвращает сообщение об ошибке."""
    if isinstance(exc, exceptions.NoGameInChatError):
        return NO_ROOM_MESSAGE

    if isinstance(exc, exceptions.LobbyClosedError):
        return (
            "🔒 К сожалению данная комната <b>закрыта</b>.\n"
            "Вы можете попросить владельца комнаты открыть"
            "комнату или дождаться окончания игра."
        )

    if isinstance(exc, exceptions.NotEnoughPlayersError):
        return NOT_ENOUGH_PLAYERS

    return f"👀 Что-то пошло не по плану...\n\n{exc}"


def end_game_message(game: UnoGame) -> str:
    """Сообщение об окончании игры.

    Отображает список победителей текущей комнаты и проигравших.
    Ну и полезные команды, если будет нужно создать новую игру.
    """
    res = "✨ <b>Игра завершилась</b>!\n"
    for i, winner in enumerate(game.winners):
        res += f"{i + 1}. {winner.name}\n"
    res += "\n👀 Проигравшие:\n"
    for i, loser in enumerate(game.losers):
        res += f"{i + 1}. {loser.name}\n"

    res += "\n🍰 /game - чтобы создать новую комнату!"
    return res


def get_room_players(game: UnoGame) -> str:
    """Собирает список игроков для текущей комнаты.

    Отображает порядок хода, список всех игроков.
    Активного игрока помечает жирным шрифтом.
    Также указывает количество карт и выстрелов из револьвера.
    """
    reverse_sim = "🔺" if game.reverse else "🔻"
    players_list = f"✨ Игроки ({len(game.players)}{reverse_sim}):\n"
    for i, player in enumerate(game.players):
        if game.rules.shotgun.status:
            shotgun_stat = f" {player.shotgun_current} / 8 🔫"
        else:
            shotgun_stat = ""

        if i == game.current_player:
            players_list += (
                f"- <b>{player.name}</b> 🃏{len(player.hand)} {shotgun_stat}\n"
            )
        else:
            players_list += (
                f"- {player.name} 🃏{len(player.hand)} {shotgun_stat}\n"
            )
    return players_list
