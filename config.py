import logging
import os
from docxtpl import DocxTemplate


logging.basicConfig(level=logging.INFO)

TOKEN = 'Ваш ТОКЕН'
BOT_VERSION = 0.1

#Документы
patheidos = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'ЗАЯВКА НА ВЪЕЗД НА склад.docx')
doceidos = DocxTemplate("Eidos.docx")
pathsmart = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'ЗАЯВКА НА ВЪЕЗД СМАРТЛАЙФКЕА.docx')
docsmart = DocxTemplate("Smart.docx")
pathemg = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'ЗАЯВКА НА ВЪЕЗД ЕМГ.docx')
docemg = DocxTemplate("Emg.docx")

