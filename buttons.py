from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

#кнопки
but_yes = InlineKeyboardButton('Да', callback_data='btn1')
but_no = InlineKeyboardButton('Нет', callback_data='btn2')
but_er = InlineKeyboardButton('Ошибка', callback_data='btn3')
but_em = InlineKeyboardButton('Эйдос-Медицина', callback_data='btn4')
but_slk = InlineKeyboardButton('Смартлайфкея', callback_data='btn5')
but_emg = InlineKeyboardButton('Эвотек', callback_data='btn6')

but_vopros = InlineKeyboardMarkup().add(but_yes, but_no, but_er)
but_send = InlineKeyboardMarkup().add(but_em, but_slk, but_emg)