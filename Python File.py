import telebot
import requests

VIRUSTOTAL_API_KEY = 'f63bef74509615f9f753d335b8203b8a34ea00569c575f0ffe4c237fd19e8251'

TELEGRAM_BOT_TOKEN = '6461471178:AAHtxYDeaWiTmQmHbaTAewx5EQGYHbBubxQ'

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

@bot.message_handler(commands=['start'])
def handle_start(message):
    bot.reply_to(message, "Привет! Я бот, который сканирует файлы на вредоносное ПО. Просто отправь мне файл, и я скажу, безопасен ли он!")

@bot.message_handler(content_types=['document'])
def handle_file(message):
    file_info = bot.get_file(message.document.file_id)
    file_url = f"https://api.telegram.org/file/bot{TELEGRAM_BOT_TOKEN}/{file_info.file_path}"
    file_response = requests.get(file_url)
    
    params = {'apikey': VIRUSTOTAL_API_KEY}
    files = {'file': file_response.content}
    response = requests.post('https://www.virustotal.com/vtapi/v2/file/scan', files=files, params=params)
    
    if response.status_code == 200:
        result = response.json()
        resource = result.get('resource')
        
        params = {'apikey': VIRUSTOTAL_API_KEY, 'resource': resource}
        response = requests.get('https://www.virustotal.com/vtapi/v2/file/report', params=params)
        
        if response.status_code == 200:
            result = response.json()
            positives = result.get('positives')
            total = result.get('total')
            if positives is not None and positives > 0:
                bot.reply_to(message, f"Файл обнаружен как вредоносный. Позитивные сканы: {positives}/{total}")
            else:
                bot.reply_to(message, "Файл не обнаружен как вредоносный.")
        else:
            bot.reply_to(message, "Произошла ошибка при получении результатов сканирования.")
    else:
        bot.reply_to(message, "Произошла ошибка при отправке файла на сканирование.")

bot.polling()
