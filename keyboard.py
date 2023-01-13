from aiogram import types

def generator_keyboards(ListNameBTN, NumberColumns = 1):
    keyboards = types.ReplyKeyboardMarkup(row_width=NumberColumns, resize_keyboard=True)
    btn_names = [types.KeyboardButton(text=x) for x in ListNameBTN]
    keyboards.add(*btn_names)
    return keyboards

def payment_process(link):
    keyboard = types.InlineKeyboardMarkup()
    button1 = types.InlineKeyboardButton('Оплатить счёт', url=link)
    button2 = types.InlineKeyboardButton('Проверить оплату', callback_data='btn2')
    button3 = types.InlineKeyboardButton('Отмена', callback_data='btn3')
    keyboard.add(button1, button2, button3)
    return keyboard

def save_selection():
    keyboard = types.InlineKeyboardMarkup()
    button1 = types.InlineKeyboardButton('✅', callback_data='Yes_Save')
    button2 = types.InlineKeyboardButton('❌',callback_data='NO_Save')
    keyboard.add(button1, button2)
    return keyboard

menu_keyboards = ['💳Пополнить баланс']