import smtplib                                      # Импортируем библиотеку по работе с SMTP
import mimetypes  
import os

# Добавляем необходимые подклассы - MIME-типы
from email.mime.multipart import MIMEMultipart      # Многокомпонентный объект
from email.mime.text import MIMEText                # Текст/HTML
from email import encoders                                # Импортируем энкодер
from email.mime.base import MIMEBase                      # Общий тип
from email.mime.text import MIMEText                      # Текст/HTML

def sendemg():
  
  addr_from = os.getenv('ADDR_FROM')                      # Адресат
  addr_to   = os.getenv('ADDR_TO')                   # Получатель
  password  = os.getenv('PASSWORD')                                  # Пароль

  msg = MIMEMultipart()                               # Создаем сообщение
  msg['From']    = addr_from                          # Адресат
  msg['To']      = addr_to                            # Получатель
  msg['Subject'] = 'ЗАЯВКА НА ВЪЕЗД ЕМГ.docx'                   # Тема сообщения

  body = ""
  msg.attach(MIMEText(body, 'plain'))                 # Добавляем в сообщение текст
  filepath="ЗАЯВКА НА ВЪЕЗД ЕМГ.docx"                   # Имя файла в абсолютном или относительном формате
  filename = os.path.basename(filepath)                     # Только имя файла

  if os.path.isfile(filepath):                              # Если файл существует
    ctype, encoding = mimetypes.guess_type(filepath)        # Определяем тип файла на основе его расширения
    if ctype is None or encoding is not None:               # Если тип файла не определяется
        ctype = 'application/octet-stream'                  # Будем использовать общий тип
    maintype, subtype = ctype.split('/', 1)                 # Получаем тип и подтип
    if maintype == 'text':                                  # Если текстовый файл
        with open(filepath) as fp:                          # Открываем файл для чтения
            file = MIMEText(fp.read(), _subtype=subtype)    # Используем тип MIMEText
            fp.close()                                      # После использования файл обязательно нужно закрыть
    else:                                                   # Неизвестный тип файла
        with open(filepath, 'rb') as fp:
            file = MIMEBase(maintype, subtype)              # Используем общий MIME-тип
            file.set_payload(fp.read())                     # Добавляем содержимое общего типа (полезную нагрузку)
            fp.close()
        encoders.encode_base64(file)                        # Содержимое должно кодироваться как Base64
    file.add_header('Content-Disposition', 'attachment', filename=filename) # Добавляем заголовки
    msg.attach(file)


  server = smtplib.SMTP_SSL('smtp.mail.ru', 465)   # Создаем объект SMTP
  server.login(addr_from, password)                   # Получаем доступ
  server.send_message(msg)                            # Отправляем сообщение
  server.quit()                                       # Выходим

if __name__ == "__main__":
  sendslk()
