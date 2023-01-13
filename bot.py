from aiogram.dispatcher import FSMContext
from aiogram import Bot, Dispatcher, executor
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram import types
from functions_app.steam_funck import *
import logging
import configparser
from keyboard import *
import functions_app.main_func as main_func
import db
import sys_const

config = configparser.ConfigParser()
config.read(sys_const.settings, encoding="utf-8")
token = config["bot"]["token"]
telephone = config["bot"]["telephone"]
percent = float(config['bot']['percent'])
min_replenishment = float(config['bot']['min_replenishment'])
max_replenishment = float(config['bot']['max_replenishment'])
bot = Bot(token=token)
dp = Dispatcher(bot, storage=MemoryStorage())
logging.basicConfig(level=logging.INFO)

class Steam(StatesGroup):
    waiting_for_rulle = State()
    waiting_for_login = State()
    waiting_for_rub = State()
    waiting_for_pay = State()
    waiting_for_save = State()

@dp.message_handler(commands='start')
async def start_message(message : types.Message):
    if data_baz.chek(id=message.from_user.id, param='rulle') is None:
        data_baz.register_new_user(message.from_user.id)
    await message.answer("Привет, я бот-пополнения стим\nПока что это только бета верcия.",
     reply_markup=generator_keyboards(menu_keyboards))
    
@dp.message_handler(text ='💳Пополнить баланс')
async def pay_steam(message : types.Message):
    if data_baz.chek(id=message.from_user.id, param='rulle')[0] == 0:
        await message.answer('Продолжая вы подтверждате правила пользования ботом: \n1.Пополнение только RU акаунтов \n2.Вы до этого уже пополняли аккаунт\n3.Логин введенный вами, введен корректно', reply_markup=generator_keyboards('✅'))
        await Steam.waiting_for_rulle.set()
    else:
        if data_baz.chek(id=message.from_user.id, param='login_steam')[0] != 0:
            keyboard = [data_baz.chek(id=message.from_user.id, param='login_steam')[0]]
            await message.answer("Введите логин steam:", reply_markup=generator_keyboards(keyboard))
        else:
            await message.answer("Введите логин steam:", reply_markup=types.ReplyKeyboardRemove())
        await Steam.waiting_for_login.set()

@dp.message_handler(state=Steam.waiting_for_rulle)
async def rulle(message: types.Message, state: FSMContext):
    if message.text == '✅':
        data_baz.update_rulle(message.from_user.id)
        await message.answer("Введите логин steam:", reply_markup=types.ReplyKeyboardRemove())
        await Steam.next()
    else:
        await message.answer('Для продолжения пользования ботом примите соглашение!')

@dp.message_handler(state=Steam.waiting_for_login)
async def login(message: types.Message, state: FSMContext):
        login = message.text
        inquiry = check_steam(login)
        await state.update_data(login = login)
        match inquiry:
            case True:
                await message.answer(f'⚠️Такого логина не существует!', reply_markup=types.ReplyKeyboardRemove())
            case False:
                await message.answer(f'Введите сколько рублей вы хотите перевести (сумма полученная вами будет МЕНЬШЕ из-за конвертации):\
                    \nМинимально {min_replenishment} рублей, максимум - {max_replenishment}!\n', reply_markup=generator_keyboards(['Отмена']))
                await Steam.next()
            case 'no_info':
                await message.answer(f'Нет связи со STEAM, не удалось проверить корректность логина, будьте внимательнее! \nВведите сколько рублей вы хотите перевести \
                    (сумма полученная вами будет МЕНЬШЕ из-за конвертации):\nМинимально {min_replenishment} рублей, максимум - {max_replenishment}!\n', reply_markup=generator_keyboards(['Отмена']))
                await Steam.next()
        
@dp.message_handler(state=Steam.waiting_for_rub)
async def rub(message: types.Message, state: FSMContext):
    if message.text == 'Отмена':
        await message.answer(f'Меню:', reply_markup=generator_keyboards(menu_keyboards))
        await state.finish()
    else:
        try:
            rub_people = float(message.text)
        except ValueError:
            await message.answer('⚠️Введите корректное число!')
        else:   
            if min_replenishment <= rub_people and rub_people  <= max_replenishment:
                billId = main_func.generator_billId()   
                await state.update_data(rub = message.text)
                await state.update_data(billId = billId)
                await state.update_data(id_user = message.from_user.id)
                rub = float(message.text)
                price_withcomision = rub + (rub * percent)
                link = f'https://oplata.qiwi.com/create?publicKey={main_func.publick_key}&amount={price_withcomision}&billId={billId}'
                msg = await message.answer(f'Ваш счёт с учетом комиссии сервиса {price_withcomision}руб.:', reply_markup=payment_process(link))
                await state.update_data(msg = msg)
                await Steam.next()   
            else:
                await message.answer(f'⚠️Сумма должна быть не меньше {min_replenishment} и не больше {max_replenishment} рублей!')
        
@dp.callback_query_handler(text="btn2", state=Steam.waiting_for_pay)
@dp.callback_query_handler(text="btn3", state=Steam.waiting_for_pay)
async def pay_steam_good(callback: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    billId = user_data['billId']
    msg = user_data['msg']
    if callback.data == 'btn3':
        await msg.edit_text('Операция отменена!')
        await msg.answer("Меню:", reply_markup=generator_keyboards(menu_keyboards))
        await state.finish()
    elif callback.data == 'btn2':
        status = main_func.check_P2P(main_func.secret_key, billId)
        if status in ['WAITING', 'REJECTED', 'EXPIRED'] or status == None:
            await callback.message.answer('Платеж не прошёл!')
        elif status == 'PAID':
            await msg.edit_text('Платеж принят!')
            rub = float(user_data['rub'])
            loginsteam = user_data['login']
            msg = await callback.message.answer("Считаю ваши денюжки...")
            money = round((main_func.curse(main_func.token, '643' , '398')) * rub, 2)
            main_func.convert_to_tenge(main_func.token, money, telephone)
            await msg.edit_text("Начинаю отправку в steam...")
            main_func.start_steam(loginsteam, str(money))
            await msg.edit_text("✅Готово")
            id = str(user_data['id_user'])
            login = user_data['login']
            data_baz.sum_update(id, user_data['rub'])
            if data_baz.chek(id=id, param='login_steam')[0] != login:
                await callback.message.answer('Запомнить логин для дальнейщих платежей ?', reply_markup=save_selection())
                await Steam.next()
            else:
                await callback.message.answer('Приятной игры!', reply_markup=generator_keyboards(menu_keyboards))
                await state.finish()

@dp.callback_query_handler(text="Yes_Save", state=Steam.waiting_for_save)
@dp.callback_query_handler(text="NO_Save", state=Steam.waiting_for_save)
async def save_login_steam(callback: types.CallbackQuery, state: FSMContext):
    if callback.data == 'Yes_Save':
        user_data = await state.get_data()
        id = user_data['id_user']
        login = user_data['login']
        data_baz.update_login(id=id, login=login)
        await callback.message.answer('Логин запомнил!', reply_markup=generator_keyboards(menu_keyboards))
        await state.finish()
    if callback.data == 'NO_Save':
        await callback.message.answer('Хорошо, приятной игры!', reply_markup=generator_keyboards(menu_keyboards))
        await state.finish()

if __name__ == '__main__':
    data_baz = db.DataBase()
    executor.start_polling(dp)