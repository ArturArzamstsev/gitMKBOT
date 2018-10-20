# -*- coding: utf-8 -*-

import vk_api
import telebot
import configparser
import logging
import time

# Считываем настройки
config = configparser.ConfigParser()
config.read('settings.ini')
LOGIN = config.get('VK', 'LOGIN')
PASSWORD = config.get('VK', 'PASSWORD')
DOMAIN = config.get('VK', 'DOMAIN')
COUNT = config.get('VK', 'COUNT')
BOT_TOKEN = config.get('Telegram', 'BOT_TOKEN')
CHANNEL = config.get('Telegram', 'CHANNEL')


# Инициализируем телеграмм бота
bot = telebot.TeleBot(BOT_TOKEN)


# Получаем данные из vk.com
def get_data(domain_vk, count_vk):
    vk_session = vk_api.VkApi(LOGIN, PASSWORD)
    vk_session.auth()
    vk = vk_session.get_api()
    response = vk.wall.get(domain=domain_vk, count=count_vk)  # Используем метод wall.get из документации по API vk.com
    return response


# Проверяем данные по условиям перед отправкой
def check_posts_vk():
    response = get_data(DOMAIN, COUNT)
    response = reversed(response['items'])

    for post in response:

        # Читаем последний извесный id из файла
        id = config.get('Settings', 'LAST_ID')

        # Сравниваем id, пропускаем уже опубликованные
        if int(post['id']) <= int(id):
            continue

        # Записываем id в файл
        config.set('Settings', 'LAST_ID', str(post['id']))
        with open('settings.ini', "w") as config_file:
            config.write(config_file)


        print('------------------------------------------------------------------------------------------------')
        print(post)

        # Текст
        text = post['text']
        send_posts_text(text)

        # Проверяем есть ли что то прикрепленное к посту
        if 'attachments' in post:
            attach = post['attachments']
            for add in attach:
                if add['type'] == 'photo':
                    add = add['photo']
                    send_posts_img(add)

       
# Отправляем посты в телеграмм


# Текст
def send_posts_text(text):
    if text == '':
        print('no text')
    else:
        # В телеграмме есть ограничения на длину одного сообщения в 4091 символ, разбиваем длинные сообщения на части
        if len(text) >= 4091:
            text4091 = text[:4091]
            bot.send_message(CHANNEL, text4091)
            if len(text) >= 8182:
                text8182 = text[4091:8182]
                bot.send_message(CHANNEL, text8182)
                text12773 = text[8182:12773]
                bot.send_message(CHANNEL, text12773)
        else:
            bot.send_message(CHANNEL, text)


# Изображения
def send_posts_img(add):
    photka = add['sizes'][6]
    bot.send_photo(CHANNEL, photka['url'])

    logging.info('Image: ' + photka['url'])
if __name__ == '__main__':
    while True:
        check_posts_vk()
        # Пауза в 4 минуты перед повторной проверкой
        time.sleep(60 * 2)
    else:
        check_posts_vk()
        time.sleep(60 * 2)
