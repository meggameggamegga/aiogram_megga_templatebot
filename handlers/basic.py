from aiogram import types
from aiogram.dispatcher.filters import Command

from main import bot,dp





@dp.message_handler(Command('start'))
async def start_cmnd(message:types.Message):
    pass