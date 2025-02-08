"""Модели базы данных.

Модели используются для хранения в базе данных.
TortoiseORM предоставляет удобный API для управления базами данных.
После модели будут конвертироваться в pydantic схемы.

Данный файл содержит все доступные модели в одном месте для удобства.
Поскольку так будет куда удобнее, чем собирать модели по всему проекту.
"""

from enum import StrEnum

from tortoise import Model, fields


class UserModel(Model):
    """Пользователь уно."""

    id = fields.UUIDField(primary_key=True)
    username = fields.CharField(max_length=16, unique=True)
    name = fields.CharField(max_length=64)
    password_hash = fields.TextField()
    avatar_url = fields.TextField(default="")
    gems = fields.IntField(default=100)
    play_count = fields.IntField(default=0)
    win_count = fields.IntField(default=0)
    cards_count = fields.IntField(default=0)
    create_date = fields.DatetimeField(auto_now_add=True)
    supporter = fields.BooleanField(default=False)

    rooms = fields.ReverseRelation["RoomModel"]
    my_rooms = fields.ReverseRelation["RoomModel"]


class RoomState(StrEnum):
    """Все возможные состояния игровой комнаты."""

    idle = "idle"
    game = "game"
    ended = "ended"


class RoomModel(Model):
    """Игровая комната."""

    # Информация о комнате
    id = fields.UUIDField(primary_key=True)
    name = fields.CharField(max_length=64)
    create_time = fields.DatetimeField(auto_now_add=True)
    private = fields.BooleanField(default=False)
    room_password = fields.CharField(max_length=32, default="")

    # Участники
    owner: fields.ForeignKeyRelation[UserModel] = fields.ForeignKeyField(
        "models.UserModel", related_name="my_rooms"
    )
    players: fields.ManyToManyRelation[UserModel] = fields.ManyToManyField(
        "models.UserModel", related_name="rooms"
    )

    # Настройки комнаты
    gems = fields.IntField(default=50)
    max_players = fields.IntField(default=7)
    min_players = fields.IntField(default=2)

    # Статус комнаты
    status = fields.CharEnumField(RoomState, default=RoomState.idle)
    status_updates = fields.DatetimeField(auto_now_add=True)
