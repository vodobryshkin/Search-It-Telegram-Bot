from collections import namedtuple
from re import findall, match
from time import strftime, localtime

import telebot
import wikipedia as wiki
from bs4 import BeautifulSoup as bs
from pycoingecko import CoinGeckoAPI
from pyowm import OWM
from pyowm.utils.config import get_default_config
from requests import get
from telebot import types
from translate import Translator

from config import *

bot = telebot.TeleBot(TELEGRAM_TOKEN, parse_mode='html')
cg = CoinGeckoAPI()
#
date = namedtuple('Date', ['day', 'month', 'year'])
db = {}
hideBoard = types.ReplyKeyboardRemove()
wiki.set_lang("ru")
number_tech = 0
number_com = 0
fl = ''
sl = ''
funcflag = False
excepts = [""]
lang = {
    'Арабский': 'ar',
    'Азербайджанский': 'az',
    'Белорусский': 'be',
    'Немецкий': 'de',
    'Английский': 'en',
    'Испанский': 'es',
    'Армянский': 'hy',
    'Итальянский': 'it',
    'Японский': 'ja',
    'Грузинский': 'ka',
    'Казахский': 'kk',
    'Польский': 'pl',
    'Португальский': 'pt',
    'Русский': 'ru',
    'Украинский': 'uk',
    'Китайский': 'zh-cn',
    'Французски': 'fr',
    'Узбекский': 'uz',
}


def parse_date(actual_date: str):
    try:
        real_date = match(r'^[0-9]{1,2}[ .][0-9]{1,2}[ .][0-9]{4}', actual_date).group()
    except TypeError:
        return 0
    except AttributeError:  # Обработка ошибки для .group()
        return 0
    else:
        now_day, now_month, now_year = strftime("%d %m %Y", localtime()).split()

        if '.' in real_date:
            real_date = real_date.split('.')
        else:
            real_date = real_date.split()

        new_date = date(real_date[0], real_date[1], real_date[2])

        if int(new_date.year) > int(now_year):
            return 0
        elif int(new_date.year) == int(now_year) and int(new_date.month) > int(now_month):
            return 0
        elif int(new_date.year) == int(now_year) and int(new_date.month) == int(now_month) and int(new_date.day) > int(
                now_day):
            return 0

        return new_date


def get_currency(actual_currency: str, date_to_parse: tuple):
    """
    Функция для парсинга курса ЦБ. Если данный курс уже парсился, то данные возьмутся из словаря db.
    :param actual_currency: Имя валюты.
    :param date_to_parse: Кортеж, который содержит дату для парсинга.
    :return: Текст с именем валюты и её курсом.
    """
    day, month, year = date_to_parse.day, date_to_parse.month, date_to_parse.year

    currency = db.get(f'{day} {month} {year} {actual_currency}', None)
    if currency:
        return f'Курс {currency[0]} на {day}.{month}.{year}: {currency[1]}'
    else:
        url = f'https://cbr.ru/scripts/XML_daily.asp?date_req={day}/{month}/{year}'

        request = get(url)
        soup = bs(request.text, 'lxml')

        for tag in soup.findAll('valute'):
            result = tag.get_text(strip=True)
            name_of_currency = ' '.join(findall(r'[а-яА-я]+', result))

            numbers = findall(r'[0-9]+', result)
            price = f'{numbers[-2]}.{numbers[-1]}'

            if actual_currency in name_of_currency:
                db[f'{day} {month} {year} {actual_currency}'] = (name_of_currency, price)
                return f'Курс {name_of_currency} на {day}.{month}.{year}: {price}₽'


# Вспомогательные части


def regular_markup():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn1 = types.KeyboardButton("/help")
    btn2 = types.KeyboardButton("/search")
    btn3 = types.KeyboardButton("/translate")
    btn4 = types.KeyboardButton("/currency")
    btn5 = types.KeyboardButton("/weather")
    btn6 = types.KeyboardButton("/tech_problem")
    btn7 = types.KeyboardButton("/commercial_ask")
    btn8 = types.KeyboardButton("/criptocurrency")
    markup.add(btn1, btn2, btn3, btn4, btn5, btn8, btn6, btn7)
    return markup


def wiki_markup(message):
    markup = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    wikilist = list(wiki.search(message, results=6))
    for i in wikilist:
        btn1 = types.KeyboardButton(i)
        markup.add(btn1)
    return markup


def translate_markup():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_az = types.KeyboardButton("🇦🇿 Азербайджанский")
    btn_ar = types.KeyboardButton("🇸🇦 Арабский")
    btn_be = types.KeyboardButton("🇧🇾 Белорусский")
    btn_de = types.KeyboardButton("🇩🇪 Немецкий")
    btn_en = types.KeyboardButton("🇬🇧 Английский")
    btn_es = types.KeyboardButton("🇪🇸 Испанский")
    btn_hy = types.KeyboardButton("🇦🇲 Армянский")
    btn_it = types.KeyboardButton("🇮🇹 Итальянский")
    btn_ja = types.KeyboardButton("🇯🇵 Японский")
    btn_kk = types.KeyboardButton("🇰🇿 Казахский")
    btn_pl = types.KeyboardButton("🇵🇱 Польский")
    btn_pt = types.KeyboardButton("🇵🇹 Португальский")
    btn_ru = types.KeyboardButton("🇷🇺 Русский")
    btn_uk = types.KeyboardButton("🇺🇦 Украинский")
    btn_zh_cn = types.KeyboardButton("🇨🇳 Китайский")
    btn_fr = types.KeyboardButton("🇫🇷 Французский")
    btn_ka = types.KeyboardButton("🇬🇪 Грузинский")
    btn_uz = types.KeyboardButton("🇺🇿 Узбекский")
    markup.add(btn_ru, btn_en, btn_fr, btn_uk, btn_pt, btn_pl, btn_kk, btn_ka, btn_ja, btn_zh_cn,
               btn_uz, btn_it, btn_hy, btn_de, btn_ar, btn_az, btn_be, btn_es)
    return markup


def currency_markup():
    markup = types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    button_1 = types.KeyboardButton('Доллар 🇺🇸')
    button_2 = types.KeyboardButton('Евро 🇪🇺')
    button_3 = types.KeyboardButton('Фунт стерлинг 🇬🇧')
    button_4 = types.KeyboardButton('Юань 🇨🇳')
    button_5 = types.KeyboardButton('Йена 🇯🇵')
    button_6 = types.KeyboardButton('Лира 🇹🇷')
    button_7 = types.KeyboardButton('Тенге 🇰🇿')
    button_8 = types.KeyboardButton('Рубль 🇧🇾')
    button_9 = types.KeyboardButton('Гривна 🇺🇦')
    button_10 = types.KeyboardButton('Доллар 🇦🇺')
    button_11 = types.KeyboardButton('Манат 🇦🇿')
    button_12 = types.KeyboardButton('Рэнд 🇿🇦')
    button_13 = types.KeyboardButton('Драм 🇦🇲')
    button_14 = types.KeyboardButton('Лев 🇧🇬')
    button_15 = types.KeyboardButton('Реал 🇧🇷')
    button_16 = types.KeyboardButton('Доллар 🇭🇰')
    button_17 = types.KeyboardButton('Форинт 🇭🇺')
    button_18 = types.KeyboardButton('Крона 🇩🇰')
    button_19 = types.KeyboardButton('Рупия 🇮🇳')
    button_20 = types.KeyboardButton('Доллар 🇨🇦')
    button_21 = types.KeyboardButton('Сом 🇰🇬')
    button_22 = types.KeyboardButton('Лей 🇲🇩')
    button_23 = types.KeyboardButton('Крона 🇳🇴')
    button_24 = types.KeyboardButton('Злотый 🇵🇱')
    button_25 = types.KeyboardButton('Лей 🇷🇴')
    button_26 = types.KeyboardButton('Доллар 🇸🇬')
    button_27 = types.KeyboardButton('Сомони 🇹🇯')
    button_28 = types.KeyboardButton('Манат 🇹🇲')
    button_29 = types.KeyboardButton('Сум 🇺🇿')
    button_30 = types.KeyboardButton('Крона 🇨🇿')
    button_31 = types.KeyboardButton('Крона 🇸🇪')
    button_32 = types.KeyboardButton('Франк 🇨🇭')
    button_33 = types.KeyboardButton('Вон 🇰🇷')
    markup.add(button_1, button_2, button_3, button_4, button_5, button_6, button_7, button_8, button_9, button_10,
               button_11, button_12, button_13, button_14, button_15, button_16, button_17, button_18, button_19,
               button_20,
               button_21, button_22, button_23, button_24, button_25, button_26, button_27, button_28, button_29,
               button_30,
               button_31, button_32, button_33)
    return markup


def start_markup():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button_1 = types.KeyboardButton('/help')
    markup.add(button_1)
    return markup


def crypto_markup():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn1 = types.KeyboardButton("Bitcoin")
    btn2 = types.KeyboardButton("Ethereum")
    btn3 = types.KeyboardButton("Tether")
    btn4 = types.KeyboardButton("BNB")
    btn5 = types.KeyboardButton("Litecoin")
    btn6 = types.KeyboardButton("Solana")
    btn8 = types.KeyboardButton("Cardano")
    btn10 = types.KeyboardButton("Avalanche")
    markup.add(btn1, btn2, btn3, btn4, btn5, btn6, btn8, btn10)
    return markup


@bot.message_handler(commands=["start"])
def start(m, res=False):
    bot.send_message(m.chat.id, '''Добро пожаловать в SearchIt! Бот способен находить любую информацию, опираясь на данные из Интернета, переводить что угодно на девятнадцать языков мира, получать курс тридцати трёх денежных валют и девяти криптовалют, а также узнавать погоду в любой точке мира.
В случае возникновения проблем, ты всегда можешь расчитывать на оперативный ответ от разработчиков.
Подробнее о функционале бота можно узнать с помощью функции /help.
Приятной работы!''', reply_markup=start_markup())


@bot.message_handler(commands=['help'])
def help_command(message):
    bot.send_message(
        message.chat.id,
        '1) Для поиска информации о чём либо воспользуйтеся функцией /search.\n' +
        '2) Для перевода любого слова(ов) воспользуйтеся функцией /translate.\n' +
        '3) Для получения курса самых популярных валют воспользуйтеся функцией /currency(временно не работает).\n' +
        '4) Для того чтобы узнать погоду в любом населённом пункте на планете воспользуйся функцией /weather.\n' +
        '5) Для получения курса самых популярных криптовалют воспользуйся функцией /criptocurrency.\n' +
        '6) При возникновении технических проблем воспользуйтеся функцией /tech_problem.\n',
        reply_markup=regular_markup()
    )


@bot.message_handler(commands=['search'])
def word_to_find(message):
    mg = bot.send_message(message.chat.id, 'Введи слово, информацию о котором хочешь узнать.', reply_markup=hideBoard)
    bot.register_next_step_handler(mg, choose_the_word)


def choose_the_word(message):
    mg = bot.send_message(message.chat.id, 'Выбери слово из списка. Если слово не найдено, то набери вручную.',
                          reply_markup=wiki_markup(message.text))
    bot.register_next_step_handler(mg, handle_text)


def handle_text(message):
    bot.send_message(message.chat.id, wiki.summary(message.text, sentences=4), reply_markup=regular_markup())


@bot.message_handler(commands=["translate"])
def first_language(m):
    mesg = bot.send_message(m.chat.id, 'Выберите язык, из которого будешь переводить.', reply_markup=translate_markup())
    bot.register_next_step_handler(mesg, second_language)


def second_language(m):
    global fl
    fl = lang[m.text[3:]]
    mesg = bot.send_message(m.chat.id, 'Выбери язык, в который будешь переводить.', reply_markup=translate_markup())
    bot.register_next_step_handler(mesg, phrase)


def phrase(m):
    global sl
    sl = lang[m.text[3:]]
    mesg = bot.send_message(m.chat.id, f'Введи слова(о) для перевода.', reply_markup=hideBoard)
    bot.register_next_step_handler(mesg, trans)


def trans(m):
    global fl, sl
    translator = Translator(from_lang=fl, to_lang=sl)
    bot.send_message(m.chat.id, translator.translate(m.text), reply_markup=regular_markup())


@bot.message_handler(commands='currency')
def currency(message):
    global funcflag
    funcflag = True
    bot.send_message(message.chat.id, 'Выбери курс, который тебя интересует', reply_markup=currency_markup())


def answer_to_user(message, **kwargs):
    parsed_date = parse_date(actual_date=message.text)
    if isinstance(parsed_date, date):
        bot.send_message(message.chat.id, get_currency(actual_currency=kwargs['valute'], date_to_parse=parsed_date),
                         reply_markup=regular_markup())
    else:
        bot.send_message(message.chat.id, 'Я не понял вас. Убедись, что твоя дата в формате dd mm yyyy.',
                         reply_markup=regular_markup())


@bot.message_handler(commands=['weather'])
def send_name(message):
    mg = bot.send_message(message.chat.id, 'Напиши название населённого пункта, погода в котором тебя интересует',
                          reply_markup=hideBoard)
    bot.register_next_step_handler(mg, test)


def test(message):
    try:
        place = message.text
        config_dict = get_default_config()
        config_dict['language'] = 'ru'

        owm = OWM(PYOWM_TOKEN, config_dict)
        mgr = owm.weather_manager()
        observation = mgr.weather_at_place(place)
        w = observation.weather

        t = w.temperature("celsius")
        t1 = t['temp']
        t2 = t['feels_like']
        t3 = t['temp_max']
        t4 = t['temp_min']
        wi = w.wind()['speed']
        humi = w.humidity
        cl = w.clouds
        st = w.status
        dt = w.detailed_status
        ti = w.reference_time('iso')
        pr = w.pressure['press']
        vd = w.visibility_distance
        bot.send_message(message.chat.id,
                         "В населённом пункте " + str(place) + " температура " + str(t1) + " °C." + "\n" +
                         "Ощущается как " + str(t2) + " °C." + "\n" +
                         "Скорость ветра " + str(wi) + " м/с." + "\n" +
                         "Давление " + str(pr) + " мм.рт.ст." + "\n" +
                         "Влажность " + str(humi) + " %." + "\n" +
                         "Видимость " + str(vd) + "  метров.", reply_markup=regular_markup())
    except:
        bot.send_message(message.chat.id, "Такой город не найден!", reply_markup=regular_markup())
        print(str(message.text), "- не найден")


@bot.message_handler(commands=['criptocurrency'])
def choose_course(message):
    mg = bot.send_message(message.chat.id, 'Выбери криптовалюту из таблицы.', reply_markup=crypto_markup())
    bot.register_next_step_handler(mg, get_course)


def get_course(message):
    if message.text == 'Bitcoin':
        course = cg.get_price(ids='bitcoin', vs_currencies='usd')
        bot.send_message(message.chat.id, f'Курс Bitcoin на данный момент равен {course["bitcoin"]["usd"]:.2f}$.',
                         reply_markup=regular_markup())
    if message.text == 'Tether':
        course = cg.get_price(ids='tether', vs_currencies='usd')
        bot.send_message(message.chat.id, f'Курс Tether на данный момент равен {course["tether"]["usd"]:.2f}$.',
                         reply_markup=regular_markup())
    if message.text == 'BNB':
        course = cg.get_price(ids='binancecoin', vs_currencies='usd')
        bot.send_message(message.chat.id, f'Курс BNB на данный момент равен {course["binancecoin"]["usd"]:.2f}$.',
                         reply_markup=regular_markup())
    if message.text == 'Litecoin':
        course = cg.get_price(ids='litecoin', vs_currencies='usd')
        bot.send_message(message.chat.id, f'Курс Litecoin на данный момент равен {course["litecoin"]["usd"]:.2f}$.',
                         reply_markup=regular_markup())
    if message.text == 'Solana':
        course = cg.get_price(ids='solana', vs_currencies='usd')
        bot.send_message(message.chat.id, f'Курс Solana на данный момент равен {course["solana"]["usd"]:.2f}$.',
                         reply_markup=regular_markup())
    if message.text == 'Ethereum':
        course = cg.get_price(ids='ethereum', vs_currencies='usd')
        bot.send_message(message.chat.id, f'Курс Ethereum на данный момент равен {course["ethereum"]["usd"]:.2f}$.',
                         reply_markup=regular_markup())
    if message.text == 'Cardano':
        course = cg.get_price(ids='cardano', vs_currencies='usd')
        bot.send_message(message.chat.id, f'Курс Cardano на данный момент равен {course["cardano"]["usd"]:.2f}$.',
                         reply_markup=regular_markup())
    if message.text == 'Monero':
        course = cg.get_price(ids='monero', vs_currencies='usd')
        bot.send_message(message.chat.id, f'Курс Monero на данный момент равен {course["monero"]["usd"]:.2f}$.',
                         reply_markup=regular_markup())
    if message.text == 'Avalanche':
        course = cg.get_price(ids='avalanche-2', vs_currencies='usd')
        bot.send_message(message.chat.id, f'Курс Avalanche на данный момент равен {course["avalanche-2"]["usd"]:.2f}$.',
                         reply_markup=regular_markup())


@bot.message_handler(commands=['tech_problem'])
def test_tech_info(message):
    mesg = bot.send_message(message.chat.id, 'Введи описание проблемы.', reply_markup=hideBoard)
    bot.register_next_step_handler(mesg, test_tech)


def test_tech(message):
    bot.send_message(message.chat.id, 'Сообщение успешно отправлено.', reply_markup=regular_markup())
    bot.send_message(1471561757, message.text)
    bot.send_message(1471561757, message.chat.id)


@bot.message_handler(commands=['commercial_ask'])
def test_command_info(message):
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.add(
        telebot.types.InlineKeyboardButton('Володя',
                                           url='telegram.me/vzlodey')
    )
    bot.send_message(message.chat.id, 'Перейди по ссылке для обсуждения сотрудниества.', reply_markup=keyboard)


@bot.message_handler(commands=['techadmin'])
def test_info(message):
    mesg = bot.send_message(message.chat.id, 'Вводи номер.', reply_markup=hideBoard)
    bot.register_next_step_handler(mesg, test1)


def test1(message):
    global number_tech
    number_tech = int(message.text)
    mesg = bot.send_message(message.chat.id, 'Вводи сообщение.')
    bot.register_next_step_handler(mesg, test2)


def test2(message):
    global number_tech
    bot.send_message(number_tech, message.text)
    bot.send_message(message.chat.id, 'Сообщение успешно отправлено.', reply_markup=regular_markup())


@bot.message_handler(content_types=["text"])
def erorr(message):
    global funcflag
    if not funcflag:
        bot.send_message(message.chat.id, '''Для функционирования с ботом, напиши одну из команд.
Подробнее о командах можно узнать с помощью /help''', reply_markup=regular_markup())
    else:
        if message.text == 'Доллар 🇺🇸':
            msg = bot.send_message(message.chat.id, 'Отправь мне интересующую тебя дату в формате dd mm yyyy.')
            bot.register_next_step_handler(message=msg, callback=answer_to_user, valute='Доллар США')
        if message.text == 'Евро 🇪🇺':
            msg = bot.send_message(message.chat.id, 'Отправь мне интересующую тебя дату в формате dd mm yyyy.')
            bot.register_next_step_handler(message=msg, callback=answer_to_user, valute='Евро')
        if message.text == 'Фунт стерлинг 🇬🇧':
            msg = bot.send_message(message.chat.id, 'Отправь мне интересующую тебя дату в формате dd mm yyyy.')
            bot.register_next_step_handler(message=msg, callback=answer_to_user, valute='Фунт стерлингов')
        if message.text == 'Юань 🇨🇳':
            msg = bot.send_message(message.chat.id, 'Отправь мне интересующую тебя дату в формате dd mm yyyy.')
            bot.register_next_step_handler(message=msg, callback=answer_to_user, valute='Китайский юань')
        if message.text == 'Йена 🇯🇵':
            msg = bot.send_message(message.chat.id, 'Отправь мне интересующую тебя дату в формате dd mm yyyy.')
            bot.register_next_step_handler(message=msg, callback=answer_to_user, valute='Японских иен')
        if message.text == 'Лира 🇹🇷':
            msg = bot.send_message(message.chat.id, 'Отправь мне интересующую тебя дату в формате dd mm yyyy.')
            bot.register_next_step_handler(message=msg, callback=answer_to_user, valute='Турецких лир')
        if message.text == 'Тенге 🇰🇿':
            msg = bot.send_message(message.chat.id, 'Отправь мне интересующую тебя дату в формате dd mm yyyy.')
            bot.register_next_step_handler(message=msg, callback=answer_to_user, valute='Казахстанских тенге')
        if message.text == 'Рубль 🇧🇾':
            msg = bot.send_message(message.chat.id, 'Отправь мне интересующую тебя дату в формате dd mm yyyy.')
            bot.register_next_step_handler(message=msg, callback=answer_to_user, valute='Белорусский рубль')
        if message.text == 'Гривна 🇺🇦':
            msg = bot.send_message(message.chat.id, 'Отправь мне интересующую тебя дату в формате dd mm yyyy.')
            bot.register_next_step_handler(message=msg, callback=answer_to_user, valute='Украинских гривен')
        if message.text == 'Доллар 🇦🇺':
            msg = bot.send_message(message.chat.id, 'Отправь мне интересующую тебя дату в формате dd mm yyyy.')
            bot.register_next_step_handler(message=msg, callback=answer_to_user, valute='Австралийский доллар')
        if message.text == 'Манат 🇦🇿':
            msg = bot.send_message(message.chat.id, 'Отправь мне интересующую тебя дату в формате dd mm yyyy.')
            bot.register_next_step_handler(message=msg, callback=answer_to_user, valute='Азербайджанский манат')
        if message.text == 'Рэнд 🇿🇦':
            msg = bot.send_message(message.chat.id, 'Отправь мне интересующую тебя дату в формате dd mm yyyy.')
            bot.register_next_step_handler(message=msg, callback=answer_to_user, valute='Южноафриканских рэндов')
        if message.text == 'Драм 🇦🇲':
            msg = bot.send_message(message.chat.id, 'Отправь мне интересующую тебя дату в формате dd mm yyyy.')
            bot.register_next_step_handler(message=msg, callback=answer_to_user, valute='Армянских драмов')
        if message.text == 'Лев 🇧🇬':
            msg = bot.send_message(message.chat.id, 'Отправь мне интересующую тебя дату в формате dd mm yyyy.')
            bot.register_next_step_handler(message=msg, callback=answer_to_user, valute='Болгарский лев')
        if message.text == 'Реал 🇧🇷':
            msg = bot.send_message(message.chat.id, 'Отправь мне интересующую тебя дату в формате dd mm yyyy.')
            bot.register_next_step_handler(message=msg, callback=answer_to_user, valute='Бразильский реал')
        if message.text == 'Доллар 🇭🇰':
            msg = bot.send_message(message.chat.id, 'Отправь мне интересующую тебя дату в формате dd mm yyyy.')
            bot.register_next_step_handler(message=msg, callback=answer_to_user, valute='Гонконгских долларов')
        if message.text == 'Форинт 🇭🇺':
            msg = bot.send_message(message.chat.id, 'Отправь мне интересующую тебя дату в формате dd mm yyyy.')
            bot.register_next_step_handler(message=msg, callback=answer_to_user, valute='Венгерских форинтов')
        if message.text == 'Крона 🇩🇰':
            msg = bot.send_message(message.chat.id, 'Отправь мне интересующую тебя дату в формате dd mm yyyy.')
            bot.register_next_step_handler(message=msg, callback=answer_to_user, valute='Датская крона')
        if message.text == 'Рупия 🇮🇳':
            msg = bot.send_message(message.chat.id, 'Отправь мне интересующую тебя дату в формате dd mm yyyy.')
            bot.register_next_step_handler(message=msg, callback=answer_to_user, valute='Индийских рупий')
        if message.text == 'Доллар 🇨🇦':
            msg = bot.send_message(message.chat.id, 'Отправь мне интересующую тебя дату в формате dd mm yyyy.')
            bot.register_next_step_handler(message=msg, callback=answer_to_user, valute='Канадский доллар')
        if message.text == 'Сом 🇰🇬':
            msg = bot.send_message(message.chat.id, 'Отправь мне интересующую тебя дату в формате dd mm yyyy.')
            bot.register_next_step_handler(message=msg, callback=answer_to_user, valute='Киргизских сомов')
        if message.text == 'Лей 🇲🇩':
            msg = bot.send_message(message.chat.id, 'Отправь мне интересующую тебя дату в формате dd mm yyyy.')
            bot.register_next_step_handler(message=msg, callback=answer_to_user, valute='Молдавских леев')
        if message.text == 'Крона 🇳🇴':
            msg = bot.send_message(message.chat.id, 'Отправь мне интересующую тебя дату в формате dd mm yyyy.')
            bot.register_next_step_handler(message=msg, callback=answer_to_user, valute='Норвежских крон')
        if message.text == 'Злотый 🇵🇱':
            msg = bot.send_message(message.chat.id, 'Отправь мне интересующую тебя дату в формате dd mm yyyy.')
            bot.register_next_step_handler(message=msg, callback=answer_to_user, valute='Польский злотый')
        if message.text == 'Лей 🇷🇴':
            msg = bot.send_message(message.chat.id, 'Отправь мне интересующую тебя дату в формате dd mm yyyy.')
            bot.register_next_step_handler(message=msg, callback=answer_to_user, valute='Румынский лей')
        if message.text == 'Доллар 🇸🇬':
            msg = bot.send_message(message.chat.id, 'Отправь мне интересующую тебя дату в формате dd mm yyyy.')
            bot.register_next_step_handler(message=msg, callback=answer_to_user, valute='Сингапурский доллар')
        if message.text == 'Сомони 🇹🇯':
            msg = bot.send_message(message.chat.id, 'Отправь мне интересующую тебя дату в формате dd mm yyyy.')
            bot.register_next_step_handler(message=msg, callback=answer_to_user, valute='Таджикских сомони')
        if message.text == 'Манат 🇹🇲':
            msg = bot.send_message(message.chat.id, 'Отправь мне интересующую тебя дату в формате dd mm yyyy.')
            bot.register_next_step_handler(message=msg, callback=answer_to_user, valute='Новый туркменский манат')
        if message.text == 'Сум 🇺🇿':
            msg = bot.send_message(message.chat.id, 'Отправь мне интересующую тебя дату в формате dd mm yyyy.')
            bot.register_next_step_handler(message=msg, callback=answer_to_user, valute='Узбекских сумов')
        if message.text == 'Крона 🇨🇿':
            msg = bot.send_message(message.chat.id, 'Отправь мне интересующую тебя дату в формате dd mm yyyy.')
            bot.register_next_step_handler(message=msg, callback=answer_to_user, valute='Чешских крон')
        if message.text == 'Крона 🇸🇪':
            msg = bot.send_message(message.chat.id, 'Отправь мне интересующую тебя дату в формате dd mm yyyy.')
            bot.register_next_step_handler(message=msg, callback=answer_to_user, valute='Шведских крон')
        if message.text == 'Франк 🇨🇭':
            msg = bot.send_message(message.chat.id, 'Отправь мне интересующую тебя дату в формате dd mm yyyy.')
            bot.register_next_step_handler(message=msg, callback=answer_to_user, valute='Швейцарский франк')
        if message.text == 'Вон 🇰🇷':
            msg = bot.send_message(message.chat.id, 'Отправь мне интересующую тебя дату в формате dd mm yyyy.')
            bot.register_next_step_handler(message=msg, callback=answer_to_user, valute='Вон Республики Корея')
        funcflag = False


bot.infinity_polling()
