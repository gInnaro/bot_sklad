from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ParseMode
from aiogram.utils.executor import start_webhook
from docxtpl import DocxTemplate
import asyncio
import os
import time
import SendEidos
import SendSmart
import logging
from datetime import datetime

async def time():
    dt = datetime.now()
    print(dt)

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


async def on_shutdown(dispatcher):
    await bot.delete_webhook()

patheidos = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'ЗАЯВКА НА ВЪЕЗД НА склад.docx')
doceidos = DocxTemplate("Eidos.docx")
pathsmart = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'ЗАЯВКА НА ВЪЕЗД СМАРТЛАЙФКЕА.docx')
docsmart = DocxTemplate("Smart.docx")
record_dict = {};

class Form(StatesGroup):
    brand_t = State()  # Will be represented in storage as 'Form:name'
    number_t = State()  # Will be represented in storage as 'Form:age'
    arrivaldate_t = State()  # Will be represented in storage as 'Form:gender

# Функция, обрабатывающая команду /start
# Команда start

@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    await bot.send_message(message.chat.id, "Чтобы сделать пропуск, нужна марка автомобиля, гос.номер, и дата вьезда. \nМарка автомобиля с большой буквы.\nГос.номер нужно писать формате, А 111 АА. \nА дата вьезда, это дата вьезда автомобиля, и писать ее нужно формате ДД.ММ.ГГГГ. \nЧтобы сделать пропуск нужно отправить в чат /pass. \nЧтобы сделать на Эйдос-Медицина то /sendeidos, а на Смартлайфкея /sendsmart.")

#Блок ЭЙДОС-МЕДИЦИНА
    
@dp.message_handler(commands=["sendeidos"])
#Сохранием файл
async def sendeidos(message: types.Message):
    if os.path.isfile(patheidos) == True:
        os.remove(patheidos)
    else:
        print("Файла нет, идем дальше")
    context = {'Brand' : brand_t, 'Number' : number_t, 'ArrivalDate' : arrivaldate_t}
    doceidos.render(context)
    doceidos.save("ЗАЯВКА НА ВЪЕЗД НА склад.docx")
    print('                   Эйдос-Медицина: ')
    print('Марка: ' + brand_t + '\nГос.номер: ' + number_t + '\nДата вьезда: ' + arrivaldate_t)
    await bot.send_message(message.chat.id, 'Пропуск отправляется, нужно чуточку подождать ')
    time.sleep(2)
    SendEidos.checkem()
    await bot.send_message(message.chat.id, 'Пропуск отправлен. \nЧтобы сделать новый пропуск, отправь /pass')
    print('                   Пропуск отправлен ')
    
#Блок СМАРТЛАЙФКЕЯ
@dp.message_handler(commands=["sendsmart"])
#Сохранием файл
async def sendsmart(message: types.Message):
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
    await bot.send_message(message.chat.id, 'Пропуск отправляется, нужно чуточку подождать ')
    time.sleep(2)
    SendSmart.sendslk()
    await bot.send_message(message.chat.id, 'Пропуск отправлен. \nЧтобы сделать новый пропуск, отправь /pass ')
    print('                   Пропуск отправлен ')


# Функция, обрабатывающая команду /pass
# Команда pass

@dp.message_handler(commands=["pass"])
async def passn(message: types.Message):
    await Form.brand_t.set()
    await bot.send_message(message.chat.id, 'Марка Автомобиля? ');
    
@dp.message_handler(state=Form.brand_t)
async def brand(message): #получаем марку Автомобиля
    global brand_t;
    brand_t = message.text;
    print('Марка: ' + brand_t);
    await Form.next()
    await bot.send_message(message.chat.id, 'Номера Автомобиля? ')
    
@dp.message_handler(state=Form.number_t)        
async def number(message):
    global number_t; #получаем номер Автомобиля
    if message.text == 'Ошибка' or message.text == 'ошибка':
        await Form.brand_t.set()
        await bot.send_message(message.chat.id, 'Марка Автомобиля? ');
    else:
        number_t = message.text;
        print('Гос.номер: ' + number_t)
        await Form.next()
        await bot.send_message(message.chat.id, 'Какого числа должен заехать? ')

@dp.message_handler(state=Form.arrivaldate_t)        
async def arrivaldate(message):
    global arrivaldate_t; #получаем дату въезда
    if message.text == 'Ошибка' or message.text == 'ошибка':
        await Form.number_t.set()
        await bot.send_message(message.chat.id, 'Номера Автомобиля? ');
    else:
        arrivaldate_t = message.text;
        print('Дата вьезда: ' + arrivaldate_t)
        await Form.next()
        await bot.send_message(message.chat.id, 'Марка: ' + brand_t + '\nГос.номер: ' + number_t + '\nДата вьезда: ' + arrivaldate_t + '\nЧтобы сделать на Эйдос-Медицина то /sendeidos, а на Смартлайфкея /sendsmart.')

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    start_webhook(dp, skip_updates=True, webhook_path=WEBHOOK_PATH, on_startup=on_startup, on_shutdown=on_shutdown, host=WEBAPP_HOST, port=WEBAPP_PORT)
