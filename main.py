import telebot
from flask import Flask
from threading import Thread

TOKEN = '7684538975:AAHXbV-nNLG_GaFcJTcgXTQ-YifOSTxhbkl'
bot = telebot.TeleBot(TOKEN)

ADMIN_ID = 697930035

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "أهلاً بك في متجر BLACK BAT للخدمات الرقمية!")

# --- Keep-alive server for Render ---
app = Flask('')

@app.route('/')
def home():
    return "Bot is running!"

def run():
    app.run(host='0.0.0.0', port=10000)

def keep_alive():
    t = Thread(target=run)
    t.start()

if __name__ == "__main__":
    keep_alive()
    bot.infinity_polling(skip_pending=True)

