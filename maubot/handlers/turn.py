"""Обрабатывает действия игрока во время хода.

Это касается обработки Inline query и при помощи него результатов.
"""

import re

from aiogram import Bot, F, Router
from aiogram.types import CallbackQuery, ChosenInlineResult, InlineQuery
from loguru import logger

from maubot import keyboards, messages
from maubot.stickers import from_str
from maubot.uno.card import BaseCard, CardColor, TakeCard, TakeFourCard
from maubot.uno.enums import GameState
from maubot.uno.game import UnoGame
from maubot.uno.player import Player
from maubot.uno.session import SessionManager

router = Router(name="Turn")

# Дополнительные функции
# ======================

def take_card(player: Player) -> str | None:
    """Действие при взятии карты пользователем."""
    logger.info("{} take cards", player)
    take_counter = player.game.take_counter
    player.take_cards()
    if len(player.game.deck.cards) == 0:
        return "🃏 В колоде не осталось карт для игрока.\n"

    # Если пользователь выбрал взять карты, то он пропускает свой ход
    if (isinstance(player.game.deck.top, (TakeCard, TakeFourCard))
        and take_counter
    ):
        player.game.next_turn()
    else:
        player.game.state = GameState.NEXT
    return None

def call_bluff(player: Player) -> str:
    """Проверка на честность предыдущего игрока."""
    logger.info("{} call bluff", player)
    bluff_player = player.game.bluff_player
    if bluff_player.bluffing:
        status_message = (
            "🔎 <b>Замечен блеф</b>!\n"
            f"{bluff_player.user.first_name} получает "
            f"{player.game.take_counter} карт.\n"
        )
        bluff_player.take_cards()
        if len(player.game.deck.cards) == 0:
            status_message += "🃏 В колоде не осталось свободных карт.\n"
    else:
        player.game.take_counter += 2
        status_message = (
            f"🎩 {bluff_player.user.first_name} <b>Честный игрок</b>!\n"
            f"{player.user.first_name} получает "
            f"{player.game.take_counter} карт.\n"
        )
        player.take_cards()
        if len(player.game.deck.cards) == 0:
            status_message += "🃏 В колоде не осталось свободных карт.\n"

    player.game.next_turn()
    return status_message

def play_card(player: Player, card: BaseCard) -> str:
    """Разыгрывает выброшенную карту."""
    logger.info("Push {} from {}", card, player.user.id)
    player.hand.remove(card)
    player.game.process_turn(card)
    status_message = ""

    if len(player.hand) == 1:
        status_message += "🌟 UNO!\n"

    if (player.game.rules.random_color
        or player.game.rules.choose_random_color
        or player.game.rules.auto_choose_color
    ):
        status_message += f"🎨 Я выбираю цвет.. {player.game.deck.top.color}\n"

    if (player.game.rules.rotate_cards
        and player.game.deck.top.cost == 0
        and len(player.hand) > 0
    ):
        status_message += (
            "🤝 Все игроки обменялись картами по кругу.\n"
            f"{messages.get_room_players(player.game)}\n"
        )

    if len(player.hand) == 0:
        status_message += f"👑 {player.user.first_name} победил(а)!\n"
        player.game.remove_player(player.user.id)

        if not player.game.started:
            status_message += messages.end_game_message(player.game)
    return status_message


# Обработчики
# ===========

@router.inline_query()
async def inline_handler(query: InlineQuery, game: UnoGame | None):
    """Обработчик inline запросов к бот."""
    if game is None:
        result = keyboards.NO_GAME_QUERY
    else:
        result = keyboards.get_hand_query(game.get_player(query.from_user.id))

    await query.answer(result, cache_time=1, is_personal=True)

@router.chosen_inline_result()
async def process_card_handler(result: ChosenInlineResult,
    game: UnoGame | None,
    player: Player | None,
    bot: Bot,
    sm: SessionManager
):
    """Обрабатывает все выбранные события от бота."""
    logger.info("Process result {} in game {}", result, game)
    # Пропускаем если нам передали не действительные значения игрока и игры
    # Нам не нужно повторно отправлять сообщения если это статус игры
    if (player is None
        or game is None
        or result.result_id in ("status", "nogame")
        or re.match(r"status:\d", result.result_id)
    ):
        return

    status_message = ""
    markup = None

    if result.result_id == "pass":
        game.next_turn()

    elif result.result_id == "take":
        if game.rules.take_until_cover and game.take_counter == 0:
            game.take_counter = game.deck.count_until_cover()
            status_message += f"🍷 беру {game.take_counter} карт.\n"
        if not game.rules.shotgun and not game.rules.single_shotgun:
            status_message += take_card(player) or ""
        elif game.take_counter <= 2 or game.state == GameState.SHOTGUN:
            status_message += take_card(player) or ""
        else:
            current = (
                game.shotgun_current if game.rules.single_shotgun
                else player.shotgun_current
            )

            status_message = (
                "🍷 У нас для Вас есть <b>деловое предложение</b>!\n\n"
                f"Вы можете <b>взять {game.take_counter} карт</b> "
                "или же <b>выстрелить из револьвера</b>.\n"
                "Если вам повезёт, то карты будет брать уже следующий игрок.\n"
                f"🔫 Из револьвера стреляли {current} / 8 раз\n."
            )
            markup = keyboards.SHOTGUN_REPLY

    elif result.result_id == "bluff":
        status_message = call_bluff(player)

    change_color = re.match(r"color:([0-3])", result.result_id)
    if change_color is not None:
        game.choose_color(CardColor(int(change_color.groups()[0])))

    select_player = re.match(r"select_player:(\d)", result.result_id)
    if select_player is not None:
        other_player = game.players[int(select_player.groups()[0])]
        if game.state == GameState.TWIST_HAND:
            player_hand = len(player.hand)
            other_hand = len(other_player.hand)
            status_message += (
                f"🤝 {player.user.first_name} ({player_hand} карт)"
                f"и {other_player.user.first_name} ({other_hand} карт)"
                "обменялись руками.\n"
            )
            player.twist_hand(other_player)
        else:
            status_message += "🍻 Что-то пошло не так, но мы не знаем что."


    card = from_str(result.result_id)
    if card is not None:
        status_message += play_card(player, card)

    if game.started:
        status_message  += (
            f"🍰 <b>Следующий ходит</b>: {game.player.user.mention_html()}"
        )
        if markup is None:
            markup = keyboards.TURN_MARKUP
    else:
        sm.remove(player.game.chat_id)

    if game.state == GameState.SHOTGUN:
        logger.warning("Game state now is {}", game.state)
        status_message += "\n🔑 Сейчас игра немного поломанная.\n"
    elif game.state != GameState.NEXT:
        logger.info("Skip send status message")
        return

    await bot.send_message(player.game.chat_id,
        text=status_message,
        reply_markup=markup
    )


# Обработчики для кнопок
# ======================

@router.callback_query(F.data.regexp(r"color:([0-3])").as_("color"))
async def choose_color_call( # noqa
    query: CallbackQuery,
    game: UnoGame | None,
    player: Player | None,
    color: re.Match[str],
    sm: SessionManager,
    bot: Bot
):
    """Выбирает цвет по нажатию на кнопку."""
    # Игнорируем нажатие на кнопку если это требуется
    if (game is None
        or player is None
        or game.state != GameState.CHOOSE_COLOR
        or game.player != player
    ):
        return await query.answer("👀 Вы не играете или сейчас не ваш ход.")

    color = CardColor(int(color.groups()[0]))
    game.choose_color(color)

    status_message = f"🎨 Я выбираю цвет.. {color}\n"
    if len(player.hand) == 1:
        status_message += "🌟 UNO!\n"

    if len(player.hand) == 0:
        status_message += f"👑 {player.user.first_name} победил(а)!\n"
        player.game.remove_player(player.user.id)

        if not player.game.started:
            status_message += messages.end_game_message(game)

    if game.started:
        status_message += (
            f"🍰 <b>Следующий ходит</b>: {game.player.user.mention_html()}"
        )
        markup = keyboards.TURN_MARKUP
    else:
        sm.remove(player.game.chat_id)
        markup = None

    await bot.send_message(player.game.chat_id,
        text=status_message,
        reply_markup=markup
    )
    return await query.answer(f"🎨 Вы выбрали {color}.")
