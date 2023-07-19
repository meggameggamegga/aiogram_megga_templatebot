"""
Добавить проверку, для продуктов в админ панели, если их нет вывести добавить

"""
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command, state


from aiogram_megga_templatebot.filters.admin import AdminCheck

from aiogram_megga_templatebot.keyboards.inline_category import *
from aiogram_megga_templatebot.keyboards.reply_keyboard import menu_keyboard, admin_keyboard_menu, admin_add
from aiogram_megga_templatebot.main import dp,bot
from aiogram_megga_templatebot.services.sql import DataBase
from aiogram_megga_templatebot.states.states import  AdminState

db = DataBase('my_shop.db')

@dp.message_handler(AdminCheck,text='Выйти в меню',state='*')
@dp.message_handler(AdminCheck,Command('admin_panel'))
async def admin_start(message:types.Message,state:FSMContext):
    current_state = await state.get_state()
    if current_state:
        await state.reset_state()
    await message.answer('Ты попал в админ-панель.Выбери что нужно сделать',reply_markup=admin_keyboard_menu())

@dp.message_handler(AdminCheck,text='Выйти с админ панели',state='*')
async def admin_exit(message:types.Message,state:FSMContext):
    current_state = await state.get_state()
    if current_state:
        await state.reset_state()
    await message.answer('Выход с админ панели',reply_markup=menu_keyboard())

@dp.message_handler(AdminCheck,text='📝Редактирование категорий')
async def edit_categories(message:types.Message):
    categories = db.get_all_categories()
    for category in categories:
        cat_id = category[0]
        name = category[1]
        count_products = len(db.get_products(cat_id))
        await message.answer(f'Продуктов в категории: {count_products}\n'
                             f'Категория ID: {cat_id}\n'
                             f'Имя продукта: {name}\n',reply_markup=admin_category_edit(cat_id,name))#reply_markup#добавить к
    await message.answer('По кнопке ниже вы можете добавить категорию', reply_markup=admin_add(True))

#Редкатирование продуктов
@dp.message_handler(AdminCheck,text='📋Редактирование продуктов')
async def edit_products(message:types.Message):
    categories = db.get_all_categories()
    await message.answer(f'По какой категории вывести продукты?',reply_markup=show_products(categories))#reply_markup#добавить продукт
    await message.answer('По кнопке ниже вы можете добавить продукты', reply_markup=admin_add())

@dp.callback_query_handler(admin_cb.filter(action='choose_category'))
async def show_product(call:types.CallbackQuery,callback_data:dict):
    await call.answer()
    category_id = callback_data.get('cat_id')
    products = db.get_products(category_id)
    print(products)
    await call.message.delete()
    for product in products:
        prod_id = product[0]
        name = product[1]
        desc = product[2]
        price = product[3]
        cat_id = product[4]
        await call.message.answer(f'Категория товара: {prod_id}\n'
                                  f'Имя: {name}\n'
                                  f'Описание: {desc}\n'

                                  f'Цена: {price}\n',reply_markup=admin_products_edit(cat_id=cat_id,prod_id=prod_id))#reply_markup изменить продукты
#Удаление продукта
@dp.callback_query_handler(admin_prod_cb.filter(action='delete_product'))
async def delete_product(call:types.CallbackQuery,callback_data:dict):
    cat_id = callback_data.get('cat_id')
    prod_id = callback_data.get('prod_id')
    db.delete_product(prod_id,cat_id)
    db.delete_basket_product(prod_id,cat_id)
    await call.message.edit_text('Товар успешно удален')
    #Удалить эти продукты в корзине

#Изменение имени
@dp.callback_query_handler(admin_prod_cb.filter(action='edit_product_name'))
async def edit_product_name(call:types.CallbackQuery,callback_data:dict,state:FSMContext):
    await call.answer()
    category_id = callback_data.get('cat_id')
    prod_id = callback_data.get('prod_id')
    async with state.proxy() as data:
        data['category_id'] = category_id
        data['prod_id'] = prod_id
    await call.message.answer('Введите новое имя товара')
    await AdminState.edit_name_prod.set()

#Сохранение измененного имени
@dp.message_handler(state=AdminState.edit_name_prod,content_types=types.ContentTypes.TEXT)
async def edit_product_name_set(message:types.Message,state:FSMContext):
    async with state.proxy() as data:
        category_id = data['category_id']
        prod_id = data['prod_id']
    db.edit_product_name(prod_id,category_id,str(message.text))
    await message.answer('Имя товара успешно изменено')
    await state.reset_state()

#Изменение цены
@dp.callback_query_handler(admin_prod_cb.filter(action='edit_product_price'))
async def edit_product_price(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    await call.answer()
    category_id = callback_data.get('cat_id')
    prod_id = callback_data.get('prod_id')
    async with state.proxy() as data:
        data['category_id'] = category_id
        data['prod_id'] = prod_id
    await call.message.answer('Введите новое цену товара')
    await AdminState.edit_price_prod.set()


# Сохранение измененного цены
@dp.message_handler(state=AdminState.edit_price_prod, content_types=types.ContentTypes.TEXT)
async def edit_product_price_set(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        category_id = data['category_id']
        prod_id = data['prod_id']
    db.edit_product_price(prod_id, category_id, int(message.text))
    await message.answer('Цена товара успешно изменено')
    await state.reset_state()


#Изменение id
@dp.callback_query_handler(admin_prod_cb.filter(action='edit_product_id'))
async def edit_product_id(call: types.CallbackQuery, callback_data: dict, state: FSMContext):
    await call.answer()
    category_id = callback_data.get('cat_id')
    prod_id = callback_data.get('prod_id')
    async with state.proxy() as data:
        data['category_id'] = category_id
        data['prod_id'] = prod_id
    await call.message.answer('Введите новое позицию товара\n'
                              '<u>ВАЖНО!</u>\n'
                              '<b>Когда вы меняете позицию товара, используйте временно не существующий номер позиции для текущих замен.</b>\n')
    await AdminState.edit_id_prod.set()


# Сохранение измененного id
@dp.message_handler(state=AdminState.edit_id_prod, content_types=types.ContentTypes.TEXT)
async def edit_product_id_set(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        category_id = data['category_id']
        prod_id = data['prod_id']
    db.edit_product_id(prod_id, category_id, int(message.text))
    await message.answer('ID товара успешно изменено')
    await state.reset_state()


#Удаление категории
@dp.callback_query_handler(AdminCheck,admin_cb.filter(action='delete_category'))
async def delete_category(call:types.CallbackQuery,callback_data:dict):
    await call.answer()
    cat_id = callback_data.get('cat_id')
    name = callback_data.get('name')
    db.delete_category(cat_id,name)
    await call.message.edit_text('Категория удалена\n'
                                 'Продукты все еще остались.')

#Ввод имени изменения категории
@dp.callback_query_handler(AdminCheck,admin_cb.filter(action='edit_category_name'))
async def edit_category_name(call:types.CallbackQuery,callback_data:dict,state:FSMContext):
    await call.answer()
    cat_id = callback_data.get('cat_id')
    name = callback_data.get('name')
    async with state.proxy() as data:
        data['cat_id'] = cat_id
        data['name'] = name
    await call.message.answer('Введи имя категории')
    await AdminState.edit_name.set()

#Изменение имени категории
@dp.message_handler(AdminCheck,state=AdminState.edit_name)
async def edit_category_name_save(message:types.Message,state:FSMContext):
    async with state.proxy() as data:
        name = data.get('name')
        cat_id = data.get('cat_id')
    db.edit_name_category(message.text,cat_id,name)
    await message.answer('Имя категории изменено')
    await state.reset_state()



#Ввод имени изменения ID категории
@dp.callback_query_handler(AdminCheck,admin_cb.filter(action='edit_category_id'))
async def edit_category_id(call:types.CallbackQuery,callback_data:dict,state:FSMContext):
    await call.answer()
    cat_id = callback_data.get('cat_id')
    name = callback_data.get('name')
    async with state.proxy() as data:
        data['cat_id'] = cat_id
        data['name'] = name
    await call.message.answer('Введи ID ')
    await AdminState.edit_id.set()

#Изменение ID категории
@dp.message_handler(AdminCheck,state=AdminState.edit_id)
async def edit_category_id_save(message:types.Message,state:FSMContext):
    async with state.proxy() as data:
        name = data.get('name')
        cat_id = data.get('cat_id')
    try:
        db.edit_id_category(int(message.text),cat_id,name)
        await message.answer('ID категории изменено')
        await state.reset_state()
    except Exception as e:
        await message.answer('Кажется данный ID уже существует или вы ввели не правильно\n'
                             'Введите снова:')


@dp.message_handler(AdminCheck, text='Добавить продукт')
async def add_new_product(message: types.Message):
    categories = db.get_all_categories()
    text = "Список категорий:\n\n"

    for category in categories:
        category_id = category[0]
        category_name = category[1]
        text += f"ID категории: {category_id}\n"
        text += f"Имя категории: {category_name}\n\n"

    await message.answer(f'{text}\n'
                         f'Дважды добавить одну и ту же категорию нельзя.\n'
                         f'Перед тем как добавить,проверьте существует ли категория в списке.\n\n'
                         f'<b>Если все верно, введите имя продукта:</b>')
    await AdminState.add_product_name.set()


@dp.message_handler(AdminCheck,state=AdminState.add_product_name)
async def add_new_product_name(message: types.Message,state:FSMContext):
    async with state.proxy() as data:
        data['name'] = message.text
    await message.answer('Введите описание товара')
    await AdminState.add_product_desc.set()

@dp.message_handler(AdminCheck,state=AdminState.add_product_desc)
async def add_new_product_desc(message: types.Message,state:FSMContext):
    async with state.proxy() as data:
        data['desc'] = message.text
    await message.answer('Введите цену товара')
    await AdminState.add_product_price.set()

@dp.message_handler(AdminCheck,state=AdminState.add_product_price)
async def add_new_product_price(message: types.Message,state:FSMContext):
    async with state.proxy() as data:
        data['price'] = int(message.text)
    await message.answer('Введите категорию товара')
    await AdminState.add_product_category.set()

@dp.message_handler(AdminCheck, state=AdminState.add_product_category)
async def add_new_product_category(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        name = data.get('name')
        desc = data.get('desc')
        price = data.get('price')
    category_id = int(message.text)
    await message.answer(f'Имя товара: {name}\n'
                         f'Описание: {desc}\n'
                         f'Цена: {price}\n'
                         f'Категория: {category_id}\n')
    db.add_product(name,desc,price,category_id)
    await message.answer('Сохранено')
    await state.reset_state()


