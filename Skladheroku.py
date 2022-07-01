from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, ReplyKeyboardMarkup
from aiogram.utils.executor import start_webhook
from docxtpl import DocxTemplate
import asyncio
import os
import time
import SendEidos
import SendSmart
import logging
import datetime
import requests


storage = MemoryStorage()
TOKEN = os.getenv('BOT_TOKEN')
bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage = MemoryStorage())

HEROKU_APP_NAME = os.getenv('HEROKU_APP_NAME')

# webhook settings
WEBHOOK_HOST = f'https://{HEROKU_APP_NAME}.herokuapp.com'
WEBHOOK_PATH = f'/webhook/{TOKEN}'
WEBHOOK_URL = f'{WEBHOOK_HOST}{WEBHOOK_PATH}'

# webserver settings
WEBAPP_HOST = '0.0.0.0'
WEBAPP_PORT = os.getenv('PORT', default=8000)

async def on_startup(dispatcher):
    await bot.set_webhook(WEBHOOK_URL, drop_pending_updates=True)
    
    
patheidos = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'ЗАЯВКА НА ВЪЕЗД НА склад.docx')
doceidos = DocxTemplate("Eidos.docx")
pathsmart = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'ЗАЯВКА НА ВЪЕЗД СМАРТЛАЙФКЕА.docx')
docsmart = DocxTemplate("Smart.docx")

#keybords
but_yes = InlineKeyboardButton('Да', callback_data='btn1')
but_no = InlineKeyboardButton('Нет', callback_data='btn2')
but_er = InlineKeyboardButton('Ошибка', callback_data='btn3')
but_em = InlineKeyboardButton('Эйдос-Медицина', callback_data='btn4')
but_slk = InlineKeyboardButton('Смартлайфкея', callback_data='btn5')

but_vopros = InlineKeyboardMarkup().add(but_yes, but_no, but_er)
but_send = InlineKeyboardMarkup().add(but_em, but_slk)

class Form(StatesGroup):
    brand_t = State()  # Will be represented in storage as 'Form:brand_t'
    number_t = State()  # Will be represented in storage as 'Form:number_t'
    button_t = State()  # Will be represented in storage as 'Form:button_t'
    arrivaldate_t = State()  # Will be represented in storage as 'Form:arrivaldate_t'

# Функция, обрабатывающая команду /start
# Команда start

@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    await bot.send_message(message.chat.id, '''
Чтобы сделать пропуск, нужна марка автомобиля, гос.номер, и дата вьезда. 
Марка автомобиля с большой буквы.
Гос.номер нужно писать формате, А 111 АА. 
А дата вьезда, это дата вьезда автомобиля, и писать ее нужно формате ДД.ММ.ГГГГ. 
Чтобы сделать пропуск нужно отправить в чат /pass. 
Чтобы сделать на Эйдос-Медицина то /sendeidos, а на Смартлайфкея /sendsmart.''')

# Функция, обрабатывающая команду /pass
# Команда pass

@dp.message_handler(commands=["pass"])
async def passn(message: types.Message):
    await Form.brand_t.set()
    global msg_id
    msg_id = await bot.send_message(message.chat.id, 'Марка Автомобиля? ')
    
@dp.message_handler(state=Form.brand_t)
async def brand(message): #получаем марку Автомобиля
    global brand_t;
    brand_t = message.text;
    msg_id = msg_id.message_id
    await bot.delete_message(chat_id=message.chat.id, message_id=int(msg_id + 1))
    await bot.edit_message_text(chat_id=message.chat.id, message_id=msg_id.message_id, text = f'Марка Автомобиля: \n{brand_t}')
    print('Марка: ' + brand_t);
    global msg_idn
    msg_idn = await bot.send_message(message.chat.id, 'Номера Автомобиля? ')
    
@dp.message_handler(state=Form.number_t)        
async def number(message):
    global number_t; #получаем номер Автомобиля
    if message.text == 'Ошибка' or message.text == 'ошибка':
        await Form.brand_t.set()
        global msg_id
        msg_id = await bot.send_message(message.chat.id, 'Марка Автомобиля? ');
        await bot.delete_message(chat_id=message.chat.id, message_id=msg_id.message_id - 1)
        await bot.delete_message(chat_id=message.chat.id, message_id=msg_idn.message_id)
    else:
        number_t = message.text;
        await bot.delete_message(chat_id=message.chat.id, message_id=msg_idn.message_id + 1)
        await bot.edit_message_text(chat_id=message.chat.id, message_id=msg_idn.message_id, text = f'Номера Автомобиля: \n{number_t}')
        print('Гос.номер: ' + number_t)
        await Form.next()
        dt_now = datetime.datetime.now()
        dt = dt_now.strftime("%d.%m.%Y")
        await bot.send_message(message.chat.id, 'Сегодня должен заехать? \nСегодняшняя дата: ' +  dt, reply_markup=but_vopros)

@dp.callback_query_handler(lambda c: c.data.startswith('btn'), state=Form.button_t) 
async def button_t(callback_query: types.CallbackQuery, state: FSMContext):
    global arrivaldate_t; #получаем дату въезда
    code = callback_query.data[-1]
    if code.isdigit():
        code = int(code)
    if code == 1:
        dt_now = datetime.datetime.now()
        dt = dt_now.strftime("%d.%m.%Y")
        arrivaldate_t = dt
        print('Дата вьезда: ' + arrivaldate_t)
        await state.reset_state(with_data=False)
        await bot.send_message(callback_query.message.chat.id, f'''
Марка: {brand_t}
Гос.номер: {number_t}
Дата вьезда: {arrivaldate_t}
Чтобы сделать на Эйдос-Медицина то /sendeidos, а на Смартлайфкея /sendsmart.''', reply_markup=but_send)
    elif code == 2:
        await Form.next()
        global msg_idd
        msg_idd = await bot.send_message(callback_query.message.chat.id, 'А какого числа должен заехать? ')
    elif code == 3:
        await Form.number_t.set()
        global msg_idn
        msg_idn = await bot.send_message(callback_query.message.chat.id, 'Номера Автомобиля? ');
        await bot.delete_message(chat_id=callback_query.message.chat.id, message_id=msg_idn.message_id - 2)
    await callback_query.message.edit_reply_markup()

@dp.message_handler(state=Form.arrivaldate_t)
async def arrivaldate(message, state: FSMContext):
    global arrivaldate_t; #получаем дату въезда
    arrivaldate_t = message.text;
    dt_now = datetime.datetime.now()
    dt = dt_now.strftime("%d.%m.%Y")
    if arrivaldate_t != dt:
        await bot.delete_message(chat_id=message.chat.id, message_id=msg_idd.message_id + 1)
    await bot.edit_message_text(chat_id=message.chat.id, message_id=msg_idd.message_id, text = f'Заехать должен: \n{arrivaldate_t}')
    print('Дата вьезда: ' + arrivaldate_t)
    await state.reset_state(with_data=False)
    await bot.send_message(message.chat.id, f'''
Марка: {brand_t}
Гос.номер: {number_t}
Дата вьезда: {arrivaldate_t}
Чтобы сделать на Эйдос-Медицина то /sendeidos, а на Смартлайфкея /sendsmart.''', reply_markup=but_send)
    
@dp.callback_query_handler(lambda c: c.data.startswith('btn')) 
async def send(callback_query: types.CallbackQuery, state: FSMContext):
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
        context = {'Brand' : brand_t, 'Number' : number_t, 'ArrivalDate' : arrivaldate_t}
        doceidos.render(context)
        doceidos.save("ЗАЯВКА НА ВЪЕЗД НА склад.docx")
        print('                   Эйдос-Медицина: ')
        print('Марка: ' + brand_t + '\nГос.номер: ' + number_t + '\nДата вьезда: ' + arrivaldate_t)
        await bot.send_message(callback_query.message.chat.id, 'Пропуск отправляется от Эйдос-Медицины, нужно чуточку подождать ')
        time.sleep(2)
        SendEidos.checkem()
        await bot.send_message(callback_query.message.chat.id, 'Пропуск отправлен. \nЧтобы сделать новый пропуск, отправь /pass \nЕсли я не отвечаю на ваше сообщение откройте сайт снизу и я вам сразу отвечу. \nhttps://bot-sklad.herokuapp.com/')
        print('                   Пропуск отправлен ')
    elif code == 5:
        #Блок Смартлайфкея
        await callback_query.message.edit_reply_markup()
        if os.path.isfile(pathsmart) == True:
            os.remove(pathsmart)
        else:
            print("Файла нет, идем дальше")
        context = {'Brand' : brand_t, 'Number' : number_t, 'ArrivalDate' : arrivaldate_t}
        print(context)
        docsmart.render(context)
        docsmart.save("ЗАЯВКА НА ВЪЕЗД СМАРТЛАЙФКЕА.docx")
        print('                   Смартлайфкеа: ')
        print('Марка: ' + brand_t + '\nГос.номер: ' + number_t + '\nДата вьезда: ' + arrivaldate_t)
        await bot.send_message(callback_query.message.chat.id, 'Пропуск отправляется от Смартлайфкея, нужно чуточку подождать ')
        time.sleep(2)
        SendSmart.sendslk()
        await bot.send_message(callback_query.message.chat.id, 'Пропуск отправлен. \nЧтобы сделать новый пропуск, отправь /pass \nЕсли я не отвечаю на ваше сообщение откройте сайт снизу и я вам сразу отвечу. \nhttps://bot-sklad.herokuapp.com/')
        print('                   Пропуск отправлен ')
    
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    start_webhook(dp, skip_updates=True, webhook_path=WEBHOOK_PATH, on_startup=on_startup, host=WEBAPP_HOST, port=WEBAPP_PORT)
