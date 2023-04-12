from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils import executor
import os
import time
import SendEidos, SendSmart, SendEmg
from config import TOKEN, patheidos, doceidos, pathsmart, docsmart, pathemg, docemg
from buttons import but_vopros, but_send
from db import BotDB
import datetime

storage = MemoryStorage()
bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage = MemoryStorage())
BotDB = BotDB('database.db')

class Form(StatesGroup):
    brand_t = State()
    number_t = State()
    button_t = State()
    arrivaldate_t = State()

# Функция, обрабатывающая команду /start
# Команда start

@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    await bot.send_message(message.chat.id, "Чтобы сделать пропуск, нужна марка автомобиля, гос.номер, и дата вьезда. \nМарка автомобиля с большой буквы.\nГос.номер нужно писать формате, А 111 АА. \nА дата вьезда, это дата вьезда автомобиля, и писать ее нужно формате ДД.ММ.ГГГГ. \nЧтобы сделать пропуск нужно отправить в чат /pass. \nЧтобы сделать на Эйдос-Медицина то /sendeidos, а на Смартлайфкея /sendsmart.")


@dp.message_handler(commands=["pass"])
async def passn(message: types.Message):
    BotDB.check_username(message.from_user.id)
    await Form.brand_t.set()
    await bot.send_message(message.chat.id, 'Марка Автомобиля? ');


@dp.message_handler(state=Form.brand_t)
async def brand(message):  # получаем марку Автомобиля
    brand_t = message.text
    BotDB.edit_brand(message.from_user.id, brand_t)
    await Form.next()
    await bot.send_message(message.chat.id, 'Номера Автомобиля? ')

@dp.message_handler(state=Form.number_t)
async def number(message):
    if message.text == 'Ошибка' or message.text == 'ошибка':
        await Form.brand_t.set()
        await bot.send_message(message.chat.id, 'Марка Автомобиля? ');
    else:
        number_t = message.text
        BotDB.edit_number(message.from_user.id, number_t)
        await Form.next()
        dt_now = datetime.datetime.now()
        dt = dt_now.strftime("%d.%m.%Y")
        await bot.send_message(message.chat.id, 'Сегодня должен заехать? \nСегодняшняя дата: ' +  dt, reply_markup=but_vopros)

@dp.callback_query_handler(lambda c: c.data.startswith('btn'), state=Form.button_t)
async def button_t(callback_query: types.CallbackQuery, state: FSMContext):
    code = callback_query.data[-1]
    if code.isdigit():
        code = int(code)
    if code == 1:
        dt_now = datetime.datetime.now()
        dt = dt_now.strftime("%d.%m.%Y")
        arrivaldate_t = dt
        BotDB.edit_arrivaldate(callback_query.from_user.id, arrivaldate_t)
        await state.reset_state(with_data=False)
        datas = BotDB.sends_data(callback_query.from_user.id)
        username, brand_data, number_data, date_data = [data for data in datas]
        await bot.send_message(callback_query.message.chat.id, 'Марка: ' + brand_data + '\nГос.номер: ' + number_data + '\nДата вьезда: ' + date_data + '\nОт какой организации сделать пропуск? ', reply_markup=but_send)
    elif code == 2:
        await Form.next()
        await bot.send_message(callback_query.message.chat.id, 'А какого числа должен заехать? ')
    elif code == 3:
        await Form.number_t.set()
        await bot.send_message(callback_query.message.chat.id, 'Номера Автомобиля? ')
    await callback_query.message.edit_reply_markup()

@dp.message_handler(state=Form.arrivaldate_t)
async def arrivaldate(message, state: FSMContext):
    arrivaldate_t = message.text
    BotDB.edit_arrivaldate(message.from_user.id, arrivaldate_t)
    datas = BotDB.sends_data(message.from_user.id)
    username, brand_data, number_data, date_data = [data for data in datas]
    await state.reset_state(with_data=False)
    await bot.send_message(message.chat.id, 'Марка: ' + brand_data + '\nГос.номер: ' + number_data + '\nДата вьезда: ' + date_data + '\nОт какой организации сделать пропуск? ', reply_markup=but_send)

@dp.callback_query_handler(lambda c: c.data.startswith('btn'))
async def send(callback_query: types.CallbackQuery, state: FSMContext):
    datas = BotDB.sends_data(callback_query.from_user.id)
    username, brand_data, number_data, date_data = [data for data in datas]
    context = {'Brand': brand_data, 'Number': number_data, 'ArrivalDate': date_data}
    code = callback_query.data[-1]
    if code.isdigit():
        code = int(code)
    if code == 4:
        #Блок Эйдос-Медицины
        await callback_query.message.edit_reply_markup()
        if os.path.isfile(patheidos) == True:
            os.remove(patheidos)
        else:
            print("Файла нет, идем дальше")
        doceidos.render(context)
        doceidos.save("ЗАЯВКА НА ВЪЕЗД НА склад.docx")
        print('                   Эйдос-Медицина: ')
        print('Марка: ' + brand_data + '\nГос.номер: ' + number_data + '\nДата вьезда: ' + date_data)
        await bot.send_message(callback_query.message.chat.id, 'Пропуск отправляется от Эйдос-Медицины, нужно чуточку подождать ')
        time.sleep(2)
        SendEidos.checkem()
        await bot.send_message(callback_query.message.chat.id, 'Пропуск отправлен. \nЧтобы сделать новый пропуск, отправь /pass')
        print('                   Пропуск отправлен ')
    elif code == 5:
        #Блок Смартлайфкея
        await callback_query.message.edit_reply_markup()
        if os.path.isfile(pathsmart) == True:
            os.remove(pathsmart)
        else:
            print("Файла нет, идем дальше")
        docsmart.render(context)
        docsmart.save("ЗАЯВКА НА ВЪЕЗД СМАРТЛАЙФКЕА.docx")
        print('                   Смартлайфкеа: ')
        print('Марка: ' + brand_data + '\nГос.номер: ' + number_data + '\nДата вьезда: ' + date_data)
        await bot.send_message(callback_query.message.chat.id, 'Пропуск отправляется от Смартлайфкея, нужно чуточку подождать ')
        time.sleep(2)
        SendSmart.sendslk()
        await bot.send_message(callback_query.message.chat.id, 'Пропуск отправлен. \nЧтобы сделать новый пропуск, отправь /pass')
        print('                   Пропуск отправлен ')
    elif code == 6:
        #Блок Эвотек
        await callback_query.message.edit_reply_markup()
        if os.path.isfile(pathemg) == True:
            os.remove(pathemg)
        else:
            print("Файла нет, идем дальше")
        print(context)
        docemg.render(context)
        docemg.save("ЗАЯВКА НА ВЪЕЗД ЕМГ.docx")
        print('                   Эвотек: ')
        print('Марка: ' + brand_data + '\nГос.номер: ' + number_data + '\nДата вьезда: ' + date_data)
        await bot.send_message(callback_query.message.chat.id, 'Пропуск отправляется от Эвотек нужно чуточку подождать ')
        time.sleep(2)
        SendEmg.sendemg()
        await bot.send_message(callback_query.message.chat.id, 'Пропуск отправлен. \nЧтобы сделать новый пропуск, отправь /pass')
        print('                   Пропуск отправлен ')


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
