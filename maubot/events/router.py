"""Маршрутизация событий от движка."""

from mau.events import Event, GameEvents
from maubot import keyboards, messages
from maubot.config import sm
from maubot.events.journal import EventRouter, MessageJournal
from maubot.messages import plural_form

er = EventRouter()


# Обработчик сессий
# =================


@er.handler(event=GameEvents.SESSION_START)
async def start_session(event: Event, journal: MessageJournal) -> None:
    """Отправляет лобби, когда начинается новая сессия в чате."""
    lobby_message = (
        f"{messages.get_room_status(event.game)}\n\n"
        f"🔥 {event.player.name}, Начинает новую игру!"
    )
    await journal.send_lobby(
        message=lobby_message,
        reply_markup=keyboards.get_room_markup(event.game),
    )


# Обработка событий игры
# ======================


@er.handler(event=GameEvents.GAME_JOIN)
async def join_player(event: Event, journal: MessageJournal) -> None:
    """Оповещает что пользователь зашёл в игру."""
    if event.game.started:
        journal.add(f"🍰 Добро пожаловать в игру, {event.player.name}!")
        await journal.send()
    else:
        lobby_message = (
            f"{messages.get_room_status(event.game)}\n\n"
            f"👋 {event.player.name}, добро пожаловать в комнату!"
        )
        await journal.send_lobby(
            message=lobby_message,
            reply_markup=keyboards.get_room_markup(event.game),
        )


@er.handler(event=GameEvents.GAME_LEAVE)
async def leave_player(event: Event, journal: MessageJournal) -> None:
    """Оповещает что пользователь зашёл в игру."""
    # Это может бывать выход из игры до её начала
    if event.data == "win":
        journal.add(f"👑 {event.player.name} победил(а)!\n")
    else:
        journal.add(f"👋 {event.player.name} покидает игру!\n")

    if not event.game.started:
        journal.set_markup(None)

    await journal.send()


@er.handler(event=GameEvents.GAME_UNO)
async def say_uno(event: Event, journal: MessageJournal) -> None:
    """Оповещает что пользователь зашёл в игру."""
    journal.add("🌟 UNO!\n")
    await journal.send()


@er.handler(event=GameEvents.GAME_TAKE)
async def player_take_cards(event: Event, journal: MessageJournal) -> None:
    """Оповещает что пользователь взял N карт."""
    if journal.room_message is not None:
        journal.add(
            f"🃏 Беру {event.data} "
            f"{plural_form(int(event.data), ('карту', 'карты', 'карт'))}"
        )
        await journal.send()


@er.handler(event=GameEvents.GAME_ROTATE)
async def rotate_cards(event: Event, journal: MessageJournal) -> None:
    """Оповещает что пользователь зашёл в игру."""
    journal.add("🌀 Обмениваемся ручками")
    journal.add(messages.get_room_players(event.game))
    await journal.send()


@er.handler(event=GameEvents.GAME_SELECT_COLOR)
async def select_card_color(event: Event, journal: MessageJournal) -> None:
    """Оповещает что пользователь зашёл в игру."""
    journal.add(f"🎨 Я выбираю.. {event.data}!")
    await journal.send()


@er.handler(event=GameEvents.GAME_START)
async def start_game(event: Event, journal: MessageJournal) -> None:
    """Оповещает что пользователь зашёл в игру."""
    await journal.send_card(event.game.deck.top)
    await journal.send_message(messages.get_new_game_message(event.game))


@er.handler(event=GameEvents.GAME_END)
async def end_game(event: Event, journal: MessageJournal) -> None:
    """Оповещает что пользователь зашёл в игру."""
    journal.add(messages.end_game_message(event.game))
    journal.set_markup(None)
    sm.remove(event.game.room_id)
    await journal.send()


@er.handler(event=GameEvents.GAME_SELECT_PLAYER)
async def twist_hand(event: Event, journal: MessageJournal) -> None:
    """Оповещает что пользователь зашёл в игру."""
    other_player = event.game.get_player(event.data)
    if other_player is None:
        journal.add("🍺 Куда подевался второй игрок?")
    else:
        journal.add(
            f"🤝 {event.player.name} ({len(other_player.hand)} карт) "
            f"и {other_player.name} ({len(event.player.hand)} карт) "
            "обменялись руками.\n"
        )
    await journal.send()


@er.handler(event=GameEvents.GAME_BLUFF)
async def player_bluffing(event: Event, journal: MessageJournal) -> None:
    """Оповещает что пользователь зашёл в игру."""
    bluff_flag, take_counter = event.data.split(";")
    bluff_player = event.game.bluff_player
    if bluff_player is not None and bluff_flag == "true":
        journal.add(
            "🔎 <b>Замечен блеф</b>!\n"
            f"{bluff_player.name} получает "
            f"{take_counter} карт."
        )
    else:
        if bluff_player is None:
            bluff_header = "🎩 <b>Никто не блефовал</b>!\n"
        else:
            bluff_header = f"🎩 {bluff_player.name} <b>Честный игрок</b>!\n"

        journal.add(
            f"{bluff_header}{event.player.name} получает {take_counter} карт.\n"
        )

    await journal.send()


@er.handler(event=GameEvents.GAME_STATE)
async def set_game_state(event: Event, journal: MessageJournal) -> None:
    """Изменение игрового состояния."""
    if event.data == "shotgun" and (
        event.game.rules.shotgun.status
        or event.game.rules.single_shotgun.status
    ):
        current = (
            event.game.shotgun_current
            if event.game.rules.single_shotgun.status
            else event.player.shotgun_current
        )
        journal.add(
            f"🍷 беру {event.game.take_counter} карт.\n"
            "💼 У нас для Вас есть <b>деловое предложение</b>!\n\n"
            f"Вы можете <b>взять свои карты</b> "
            "или же попробовать <b>выстрелить из револьвера</b>.\n"
            "Если вам повезёт, то карты будет брать уже следующий игрок.\n"
            f"🔫 Из револьвера стреляли {current} / 8 раз\n."
        )
        journal.set_markup(keyboards.SHOTGUN_KEYBOARD)

    elif event.data == "twist_hand":
        journal.add(f"✨ {event.player.name} Задумывается c кем обменяться.")
        journal.set_markup(keyboards.select_player_markup(event.game))

    elif event.data == "choose_color":
        journal.add(f"✨ {event.player.name} Задумывается о выборе цвета..")
        journal.set_markup(keyboards.SELECT_COLOR)

    await journal.send()


@er.handler(event=GameEvents.GAME_TURN)
async def next_turn(event: Event, journal: MessageJournal) -> None:
    """Оповещает что пользователь зашёл в игру."""
    await journal.clear()
    journal.add(f"\n🍰 <b>ход</b>: {event.game.player.name}")
    await journal.send()
