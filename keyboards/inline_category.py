from aiogram.types import InlineKeyboardMarkup,InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData

from aiogram_megga_templatebot.services.sql import DataBase

#Имя кнопок








cb = CallbackData('btn','action')

cat_cb = CallbackData('btn','action','cat_id','name')

button_cb = CallbackData('btn','action','page','cat_id','prod_id')

del_cb = CallbackData('btn','action','cat_id','prod_id')

admin_cb = CallbackData('btn','action','cat_id','name')

admin_prod_cb = CallbackData('btn','action','cat_id','prod_id')

pay_cb = CallbackData('btn','action','label')

db = DataBase('my_shop.db')

def start_keyboard():
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(text='Категории',callback_data=cb.new(
        action='category'
    )))
    return keyboard

def categories_keyboard(catogories):
    keyboard = InlineKeyboardMarkup()
    for category in catogories:
        cat_id = category[0]
        name = category[1]
        keyboard.add(InlineKeyboardButton(text=name,callback_data=cat_cb.new(action='categories',cat_id=cat_id,name=name)))
    return keyboard

def button_keyboard(page_index,cat_id,prod_id):
    count_products = len(db.get_products(cat_id))-1
    if count_products != page_index:
        keyboard = InlineKeyboardMarkup()
        keyboard.row(
            InlineKeyboardButton(text='Назад',
                                 callback_data=button_cb.new(action='back', page=page_index, cat_id=cat_id,
                                                             prod_id=prod_id)),
            InlineKeyboardButton(text='Добавить товар',
                                              callback_data=button_cb.new(action='add_product', page=page_index,
                                                                          cat_id=cat_id, prod_id=prod_id)),
            InlineKeyboardButton(text='Вперед',
                                 callback_data=button_cb.new(action='next', page=page_index, cat_id=cat_id,
                                                             prod_id=prod_id))
        )
    else:
        keyboard = InlineKeyboardMarkup()
        keyboard.row(
            InlineKeyboardButton(text='Назад',
                                 callback_data=button_cb.new(action='back', page=page_index, cat_id=cat_id,
                                                             prod_id=prod_id)),
            InlineKeyboardButton(text='Добавить товар',
                                          callback_data=button_cb.new(action='add_product', page=page_index,
                                                                      cat_id=cat_id, prod_id=prod_id))
        )

    return keyboard

def delete_keyboard(cat_id,prod_id):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(text='Удалить товар',callback_data=del_cb.new(action='delete',cat_id=cat_id,prod_id=prod_id)))
    return keyboard


def admin_category_edit(cat_id,name):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton(text='➖Удалить',callback_data=admin_cb.new(action='delete_category',cat_id=cat_id,name=name)),
        InlineKeyboardButton(text='📝Изменить имя',callback_data=admin_cb.new(action='edit_category_name', cat_id=cat_id, name=name)),
        InlineKeyboardButton(text='📝Изменить id',callback_data=admin_cb.new(action='edit_category_id', cat_id=cat_id, name=name))
    )
    return keyboard

def show_products(categories):
    keyboard = InlineKeyboardMarkup()
    for category in categories:
        cat_id = category[0]
        name = category[1]
        keyboard.add(
            InlineKeyboardButton(text=f'Вывести все продукты категории {name}',
                                 callback_data=admin_cb.new(action='choose_category', cat_id=cat_id, name=name))
        )
    return keyboard

def admin_products_edit(cat_id,prod_id):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(
        InlineKeyboardButton(text='➖Удалить',callback_data=admin_prod_cb.new(action='delete_product',cat_id=cat_id,prod_id=prod_id)),
        InlineKeyboardButton(text='📝Изменить имя',callback_data=admin_prod_cb.new(action='edit_product_name', cat_id=cat_id,prod_id=prod_id)),
        InlineKeyboardButton(text='📝Изменить место',callback_data=admin_prod_cb.new(action='edit_product_id', cat_id=cat_id,prod_id=prod_id)),
        InlineKeyboardButton(text='📝Изменить цену',callback_data=admin_prod_cb.new(action='edit_product_price', cat_id=cat_id,
                                                             prod_id=prod_id))

    )
    return keyboard

def paymen_keyboard(url_pay,label):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(text='Оплатить?',url=url_pay))
    keyboard.add(InlineKeyboardButton(text='Проверить платеж',callback_data=pay_cb.new(action='check_payment',label=label)))
    return keyboard