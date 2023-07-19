from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command, state
from yoomoney import Quickpay,Client
import string
import random
from aiogram_megga_templatebot import config

from aiogram_megga_templatebot.keyboards.inline_category import *
from aiogram_megga_templatebot.keyboards.reply_keyboard import menu_keyboard
from aiogram_megga_templatebot.main import dp,bot
from aiogram_megga_templatebot.services.sql import DataBase


db = DataBase('my_shop.db')



@dp.message_handler(Command('start'))
async def start_cmnd(message:types.Message):
    if not db.user_exist(message.from_user.id):
        db.add_user(user_id=message.from_user.id)
        await message.answer('Привет новый пользователь')
        await message.answer('Бот магазин аккаунтов\n'
                             'Нажми на кнопку ниже', reply_markup=menu_keyboard())  # reply_markup
    else:
        await message.answer('Бот,магазин аккаунтов\n'
                             'Нажми на кнопку ниже', reply_markup=menu_keyboard())  # reply_markup


@dp.message_handler(text='Категории📁')
async def category(message:types.Message):
    categories = db.get_all_categories()
    await message.answer('Выбери категорию',reply_markup=categories_keyboard(categories))

@dp.callback_query_handler(cat_cb.filter(action='categories'))
async def products(call: types.CallbackQuery, callback_data: dict):
    await call.answer()
    page = 0
    category_id = callback_data.get('cat_id')
    all_products = db.get_products(category_id)
    if len(all_products)>0:
        product = db.get_products(category_id)[page]
        await call.message.edit_text(f'Имя товара: {product[1]}\n'
                                 f'Описание товара: {product[2]}\n'
                                 f'Цена товара: {product[3]}', reply_markup=button_keyboard(page_index=page,
                                                                                                     cat_id=category_id,
                                                                                                     prod_id=product[0],
                                                                                            ))
    else:
        await call.message.delete()
        await call.message.answer('В данной категории нет товаров')

@dp.callback_query_handler(button_cb.filter(action='next'))
async def button_next(call:types.CallbackQuery,callback_data:dict):
    await call.answer()
    page = int(callback_data.get('page'))+1
    category_id = callback_data.get('cat_id')
    products = db.get_products(category_id)
    if page < len(products):
        product = products[page]
        await call.message.edit_text(f'Имя товара: {product[1]}\n'
                                     f'Описание товара: {product[2]}\n'
                                     f'Цена товара: {product[3]}', reply_markup=button_keyboard(page_index=page,
                                                                                                     cat_id=category_id,
                                                                                                     prod_id=product[0]))

    else:
        categories = db.get_all_categories()
        await call.message.edit_text('Выбери категорию', reply_markup=categories_keyboard(categories))


@dp.callback_query_handler(button_cb.filter(action='back'))
async def button_back(call: types.CallbackQuery, callback_data: dict):
    await call.answer()
    page = int(callback_data.get('page'))
    category_id = callback_data.get('cat_id')
    all_products = db.get_products(category_id)[page - 1]
    if page - 1 >= 0:
        await call.message.edit_text(f'Имя товара: {all_products[1]}\n'
                                     f'Описание товара: {all_products[2]}\n'
                                     f'Цена товара: {all_products[3]}', reply_markup=button_keyboard(page_index=page-1,
                                                                                                     cat_id=category_id,
                                                                                                     prod_id=all_products[0],
                                                                                                     ))
    else:
        categories = db.get_all_categories()
        await call.message.edit_text('Выбери категорию',reply_markup=categories_keyboard(categories))  # Назад кнопка

@dp.callback_query_handler(button_cb.filter(action='add_product'))
async def add_product(call:types.CallbackQuery,callback_data:dict):
    await call.answer()
    category_id = int(callback_data.get('cat_id'))
    prod_id = int(callback_data.get('prod_id'))
    user_product = db.check_basket_product(user_id=call.from_user.id,cat_id=category_id,prod_id=prod_id)
    if user_product:
        await call.message.answer('Данный товар уже добавлен в корзину')
    else:
        db.add_user_product(call.from_user.id,prod_id,category_id)
        await call.message.answer('Товар добавлен!')

@dp.message_handler(text='Корзина🛒')
async def basket(message:types.Message):
    user_basket = db.get_user_basket(message.from_user.id)
    if user_basket:
        for basket in user_basket:
            prod_id = basket[2]
            cat_id = basket[3]

            product = db.get_product(cat_id=cat_id,prod_id=prod_id)[0]
            if product:
                print(product)
                name = product[1]
                desc = product[2]
                price = product[3]
                await message.answer(f'Имя товара:{name}\n'
                                 f'Описание товара:{desc}\n'
                                 f'Цена товара:{price}\n',
                                 reply_markup=delete_keyboard(cat_id=cat_id,prod_id=prod_id)) #reply_markup - удалить товар с корзины
    else:
        await message.answer('Корзина пуста')#Вывести клаву мб

@dp.message_handler(text='Техподдержка📝')
async def support(message:types.Message):
    await message.answer(f'Обращаться к @meggameggamegga')#Тут через кончиг или settings бд взять саппорт id

@dp.callback_query_handler(del_cb.filter(action='delete'))
async def delete_product_basket(call:types.CallbackQuery,callback_data:dict):
    await call.answer()
    cat_id = callback_data.get('cat_id')
    prod_id = callback_data.get('prod_id')
    db.delete_product_basket(user_id=call.from_user.id,prod_id=prod_id,cat_id=cat_id)
    await call.message.edit_text('Товар удален с корзины')

@dp.message_handler(text='Оплатить 📦')
async def pay_basket(message:types.Message):
    baskets = db.get_user_basket(message.from_user.id)
    count_products = len(baskets)
    price_all = 0
    if not baskets:
        await message.answer('У вас еще нет товаров')
    else:
        for basket in baskets:
            prod_id = basket[2]
            cat_id = basket[3]
            user_products = db.get_product(cat_id,prod_id)
            print(user_products)
            for user_product in user_products:
                price_all+= int(user_product[2])
        # Создаем ссылку для оплаты
        label_user = ''.join(random.sample(string.ascii_letters + string.digits, 10))
        quickpay = Quickpay(
            receiver="410019014512803",
            quickpay_form="shop",
            targets="Sponsor this project",
            label=label_user,
            paymentType="SB",
            sum=price_all,
        )
        await message.answer(f'Кол-во товаров: {count_products}\n'
                             f'Сумма к оплате: {price_all}',reply_markup=paymen_keyboard(quickpay.base_url,label_user))

#Проверка оплаты
@dp.callback_query_handler(pay_cb.filter(action='check_payment'))
async def payment_method(call:types.CallbackQuery, callback_data:dict):
    print('Ворк')
    await call.answer(cache_time=2)
    user_label = callback_data.get('label')
    client = Client(config.ACCESS_TOKEN)
    try:
        history = client.operation_history(label=user_label)
        status_operation = history.operations[-1].status
        #Если найдет по лейблу оплата прошла
        if history and status_operation=='success':#
            await call.message.answer('Оплата успешно прошла')
            await call.message.answer('Выдача товаров')
    except Exception as e:
            await call.message.answer('Оплата еще в пути')









