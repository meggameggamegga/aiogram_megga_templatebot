import typing

from aiogram import types
from aiogram.dispatcher.filters import BoundFilter


class AdminCheck(BoundFilter):
    key = 'is_admin'

    def __init__(self, admin_id:int):
        self.admin_id = admin_id

    def check(self, message: types.Message) -> bool:
        return message.from_user.id == self.admin_id