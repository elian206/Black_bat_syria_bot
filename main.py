import telebot
from telebot import types
from flask import Flask, request
from threading import Thread
import requests
import uuid
import re
import os

TOKEN = '8909052904:AAHEsWa85CbV5Kwxs4Y1kG7h7TMtHpx-TMw'
bot = telebot.TeleBot(TOKEN)

try:
    bot.remove_webhook()
except Exception:
    pass

ADMIN_ID = 8534087775
ADMIN_USERNAME = "black_bat_s"
CHANNEL_USERNAME = '@black1_bat_syria'

API_BASE = "https://mhd-game.com/api"
API_TOKEN = "Fluf9aJYBrtQ1a9ywuqrcMh2M4A8UIa8MKsgbyUk0PkYi301WuCqtLtGn4GO"
api_headers = {"api-token": API_TOKEN}

users_db = {}
total_orders_global = 0  
exchange_rate = 15000  

store_categories = {
    "🎮 شحن ألعاب": {
        "PUBG Mobile 🕹": {
            "سيرفر 1 🆔": [
                {"id": 6766, "name": "60 شدة", "price": 0.98},
                {"id": 6767, "name": "325 شدة", "price": 4.84},
                {"id": 6768, "name": "660 شدة", "price": 9.68},
                {"id": 6769, "name": "1800 شدة", "price": 24.2},
                {"id": 6770, "name": "3850 شدة", "price": 47.21},
                {"id": 6771, "name": "8100 شدة", "price": 92.3}
            ],
            "سيرفر 2 🆔": [
                {"id": 6744, "name": "60 شدة", "price": 0.98},
                {"id": 6761, "name": "325 شدة", "price": 4.85},
                {"id": 6762, "name": "660 شدة", "price": 9.68},
                {"id": 6763, "name": "1800 شدة", "price": 24.3},
                {"id": 6764, "name": "3850 شدة", "price": 47.3},
                {"id": 6765, "name": "8100 شدة", "price": 92.35}
            ],
            "اكواد 📱": [
                {"id": 119, "name": "كود 60 شدة", "price": 0.98},
                {"id": 137, "name": "كود 325 شدة", "price": 4.88},
                {"id": 150, "name": "كود 660 شدة", "price": 9.8},
                {"id": 168, "name": "كود 1800 شدة", "price": 24.2},
                {"id": 184, "name": "كود 3850 شدة", "price": 48.0},
                {"id": 201, "name": "كود 8100 شدة", "price": 96.34}
            ],
            "عضويات 💳": [
                {"id": 208, "name": "شعار الخرافي", "price": 4.9},
                {"id": 195, "name": "ترقية للاسلحة النارية", "price": 2.95},
                {"id": 178, "name": "شراء الاول", "price": 0.99},
                {"id": 292, "name": "الشعار الاسطوري الاسبوعي", "price": 2.93},
                {"id": 288, "name": "الصفقات الاسبوعية 2", "price": 2.93},
                {"id": 282, "name": "الصفقات الاسبوعية 1", "price": 0.98},
                {"id": 277, "name": "بطاقة النخبة بلس (Lv1-100)", "price": 28.66},
                {"id": 272, "name": "بطاقة النخبة (Lv1-100)", "price": 12.1},
                {"id": 266, "name": "بطاقة النخبة (Lv1-50)", "price": 5.93},
                {"id": 264, "name": "Prime Plus (من الشهور 12)", "price": 117.3},
                {"id": 259, "name": "Prime Plus (من الشهور 6)", "price": 57.85},
                {"id": 256, "name": "Prime Plus (من الشهور 3)", "price": 29.7},
                {"id": 249, "name": "Prime Plus (من الشهور 1)", "price": 9.9},
                {"id": 241, "name": "Prime (من الشهور 12)", "price": 11.85},
                {"id": 234, "name": "Prime (من الشهور 6)", "price": 5.88},
                {"id": 228, "name": "Prime (من الشهور 3)", "price": 2.96},
                {"id": 220, "name": "Prime (من الشهور 1)", "price": 0.99}
            ]
        }
    },
    "📱 شحن تطبيقات": {},
    "🛡 دعم حسابات": {}
}

pending_topup = {}
admin_states = {}
user_temp_order = {}
user_temp_code = {}
bot_is_active = True

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

def format_price(user_id, price_in_usd):
    curr = users_db.get(user_id, {}).get('currency', 'USD')
    if curr == 'SYP':
        syp_amount = price_in_usd * exchange_rate
        return f"{syp_amount:,.0f} ل.س"
    else:
        return f"${price_in_usd}"

def create_mhd_order(product_id, quantity, player_id):
    try:
        unique_order_uuid = str(uuid.uuid4())
        url = f"{API_BASE}/client/api/newOrder/{product_id}/params"
        params = {"qty": quantity, "playerId": player_id, "order_uuid": unique_order_uuid}
        response = requests.get(url, headers=api_headers, params=params)
        res_json = response.json()
        res_json['order_uuid'] = unique_order_uuid
        return res_json
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}

def create_mhd_code_order(product_id, quantity=1):
    try:
        unique_order_uuid = str(uuid.uuid4())
        url = f"{API_BASE}/client/api/newOrder/{product_id}/params"
        params = {"qty": quantity, "order_uuid": unique_order_uuid}
        response = requests.get(url, headers=api_headers, params=params)
        res_json = response.json()
        res_json['order_uuid'] = unique_order_uuid
        return res_json
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}

def check_mhd_order_status(order_uuid):
    try:
        url = f"{API_BASE}/client/api/orderStatus"
        params = {"order_uuid": order_uuid}
        response = requests.get(url, headers=api_headers, params=params)
        return response.json()
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}

def check_subscription(user_id):
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        if member.status in ['member', 'administrator', 'creator']:
            return True
    except Exception:
        pass
    return False

@bot.message_handler(commands=['start'])
def send_welcome(message):
    global bot_is_active
    user_id = message.from_user.id
    if not bot_is_active and user_id != ADMIN_ID:
        return

    if user_id not in users_db:
        users_db[user_id] = {
            'name': message.from_user.first_name,
            'balance': 0.0, 'spent': 0.0, 'orders_count': 0,
            'banned': False, 'currency': 'USD',
            'topup_history': [], 'orders_history': []
        }
    
    if users_db[user_id]['banned']:
        bot.reply_to(message, "عذراً، أنت محظور من استخدام هذا البوت.")
        return

    if not check_subscription(user_id) and user_id != ADMIN_ID:
        markup_sub = types.InlineKeyboardMarkup()
        markup_sub.add(types.InlineKeyboardButton('📢 اشترك في القناة الان', url='https://t.me/black1_bat_syria'))
        markup_sub.add(types.InlineKeyboardButton('✅ تحقق من الاشتراك', callback_data='check_sub'))
        bot.reply_to(message, "⚠️ عذراً، يجب عليك الاشتراك في قناة المتجر أولاً لتتمكن من استخدام البوت.\n\nرابط القناة: https://t.me/black1_bat_syria", reply_markup=markup_sub)
        return

    show_main_menu(message.chat.id, message.from_user.first_name, user_id)

def show_main_menu(chat_id, user_name, user_id):
    global total_orders_global
    current_curr = users_db.get(user_id, {}).get('currency', 'USD')
    curr_btn_text = '💱 العملة: دولار ($)' if current_curr == 'USD' else '💱 العملة: ليرة سورية (ل.س)'

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton('🛍 خدمات متجرنا'))
    markup.add(types.KeyboardButton('👤 حسابك'), types.KeyboardButton('💳 تعبئة رصيد'))
    markup.add(types.KeyboardButton('📞 الدعم'), types.KeyboardButton(curr_btn_text))
    
    if chat_id == ADMIN_ID:
        markup.add(types.KeyboardButton('⚙️ لوحة تحكم الأدمن'))
    
    markup_inline = types.InlineKeyboardMarkup()
    markup_inline.add(types.InlineKeyboardButton(f'📊 الطلبات المنفذة: {total_orders_global}', callback_data='show_global_orders_count'))

    welcome_msg = f"أهلاً بك {user_name} بمتجر BLACK BAT 📱\nنشكرك على التعامل معنا 🤝\nقم باختيار ماذا تريد من خدماتنا ⏬"
    bot.send_message(chat_id, welcome_msg, reply_markup=markup)
    bot.send_message(chat_id, "📊 لمعرفة وإحصاءات الطلبات المنفذة بالمتجر اضغط الزر أدناه:", reply_markup=markup_inline)

@bot.callback_query_handler(func=lambda call: call.data == 'check_sub')
def verify_sub(call):
    global bot_is_active
    user_id = call.from_user.id
    if not bot_is_active and user_id != ADMIN_ID:
        return
        
    if check_subscription(user_id) or user_id == ADMIN_ID:
        bot.answer_callback_query(call.id, "تم التحقق بنجاح! أهلاً بك.")
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except Exception:
            pass
        show_main_menu(call.message.chat.id, call.from_user.first_name, user_id)
    else:
        bot.answer_callback_query(call.id, "لم تقم بالاشتراك بعد، يرجى الاشتراك ومحاولة مجدداً.", show_alert=True)

@bot.message_handler(func=lambda message: True)
def handle_text_messages(message):
    global exchange_rate, bot_is_active, total_orders_global
    user_id = message.from_user.id
    
    if not bot_is_active and user_id != ADMIN_ID:
        return
    
    if user_id in users_db and users_db[user_id]['banned']:
        return

    if user_id == ADMIN_ID:
        admin_st = admin_states.get('state')
        if admin_st == 'waiting_new_rate':
            try:
                numbers = re.findall(r'\d+', message.text.strip())
                if numbers:
                    exchange_rate = int(''.join(numbers))
                    admin_states.clear()
                    bot.reply_to(message, f"✅ تم تحديث سعر الصرف بنجاح: {exchange_rate:,} ل.س")
                    return
            except Exception:
                pass
            bot.reply_to(message, "⚠️ يرجى إرسال رقم صحيح.")
            return

        elif admin_st == 'waiting_add_balance':
            try:
                parts = message.text.strip().split()
                target_id = int(parts[0])
                amount = float(parts[1])
                if target_id not in users_db:
                    users_db[target_id] = {'name': 'مستخدم', 'balance': 0.0, 'spent': 0.0, 'orders_count': 0, 'banned': False, 'currency': 'USD', 'topup_history': [], 'orders_history': []}
                users_db[target_id]['balance'] += amount
                users_db[target_id]['topup_history'].append(f"إضافة يدوية من الإدارة: +${amount}")
                admin_states.clear()
                bot.reply_to(message, f"✅ تمت إضافة مبلغ {amount}$ بنجاح للمستخدم `{target_id}`", parse_mode='Markdown')
                try:
                    bot.send_message(target_id, f"🎁 قامت الإدارة بإضافة رصيد لحسابك بقيمة {amount}$!")
                except Exception:
                    pass
                return
            except Exception:
                bot.reply_to(message, "⚠️ الصيغة خاطئة. اتبع النمط: `الايدي المبلغ`", parse_mode='Markdown')
                return

        elif admin_st == 'waiting_deduct_balance':
            try:
                parts = message.text.strip().split()
                target_id = int(parts[0])
                amount = float(parts[1])
                if target_id not in users_db:
                    users_db[target_id] = {'name': 'مستخدم', 'balance': 0.0, 'spent': 0.0, 'orders_count': 0, 'banned': False, 'currency': 'USD', 'topup_history': [], 'orders_history': []}
                users_db[target_id]['balance'] -= amount
                users_db[target_id]['topup_history'].append(f"خصم يدوي من الإدارة: -${amount}")
                admin_states.clear()
                bot.reply_to(message, f"✅ تم خصم مبلغ {amount}$ بنجاح من المستخدم `{target_id}`", parse_mode='Markdown')
                try:
                    bot.send_message(target_id, f"⚠️ قامت الإدارة بخصم مبلغ {amount}$ من رصيدك.")
                except Exception:
                    pass
                return
            except Exception:
                bot.reply_to(message, "⚠️ الصيغة خاطئة. اتبع النمط: `الايدي المبلغ`", parse_mode='Markdown')
                return

        elif admin_st == 'waiting_broadcast_msg':
            broadcast_text = message.text
            admin_states.clear()
            success_count = 0
            for uid in users_db.keys():
                try:
                    bot.send_message(uid, broadcast_text)
                    success_count += 1
                except Exception:
                    pass
            bot.reply_to(message, f"✅ تم إرسال الإذاعة بنجاح إلى {success_count} مستخدم.")
            return

    text = message.text
    if text == '🛍 خدمات متجرنا':
        markup = types.InlineKeyboardMarkup()
        for cat in store_categories.keys():
            markup.add(types.InlineKeyboardButton(cat, callback_data=f"cat_{cat}"))
        bot.reply_to(message, "اختر القسم المناسب:", reply_markup=markup)

    elif text == '👤 حسابك':
        u_data = users_db.get(user_id, {'balance': 0.0, 'spent': 0.0, 'orders_count': 0})
        bal_formatted = format_price(user_id, u_data['balance'])
        spent_formatted = format_price(user_id, u_data['spent'])
        info = (
            f"👤 معلومات حسابك:\n\n"
            f"🆔 ايدي: `{user_id}`\n"
            f"💰 الرصيد: {bal_formatted}\n"
            f"🛒 الطلبات المنفذة: {u_data['orders_count']}\n"
            f"💸 الإجمالي المنفق: {spent_formatted}"
        )
        bot.reply_to(message, info, parse_mode='Markdown')

    elif text == '💳 تعبئة رصيد':
        bot.reply_to(message, f"لتعبئة الرصيد، يرجى التواصل مع الأدمن عبر المعرف التالي:\n@{ADMIN_USERNAME}")

    elif text == '📞 الدعم':
        bot.reply_to(message, f"للحصول على الدعم الفني، يرجى التواصل مع الإدارة:\n@{ADMIN_USERNAME}")

    elif '💱 العملة:' in text:
        curr = users_db[user_id].get('currency', 'USD')
        if curr == 'USD':
            users_db[user_id]['currency'] = 'SYP'
            bot.reply_to(message, "✅ تم تحويل العملة إلى الليرة السورية (ل.س).")
        else:
            users_db[user_id]['currency'] = 'USD'
            bot.reply_to(message, "✅ تم تحويل العملة إلى الدولار الأمريكي ($).")
        show_main_menu(message.chat.id, message.from_user.first_name, user_id)

    elif text == '⚙️ لوحة تحكم الأدمن' and user_id == ADMIN_ID:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton('📊 إحصائيات البوت', callback_data='admin_stats'))
        markup.add(types.InlineKeyboardButton('💱 تعديل سعر الصرف', callback_data='admin_set_rate'))
        markup.add(types.InlineKeyboardButton('➕ إضافة رصيد لمستخدم', callback_data='admin_add_bal'))
        markup.add(types.InlineKeyboardButton('➖ خصم رصيد من مستخدم', callback_data='admin_deduct_bal'))
        markup.add(types.InlineKeyboardButton('📢 إذاعة عامة', callback_data='admin_broadcast'))
        bot.reply_to(message, "⚙️ مرحباً بك في لوحة تحكم الأدمن:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    global exchange_rate, total_orders_global
    user_id = call.from_user.id
    data = call.data

    if data == 'show_global_orders_count':
        bot.answer_callback_query(call.id, f"إجمالي الطلبات المنفذة في المتجر: {total_orders_global}")
        return

    if user_id == ADMIN_ID:
        if data == 'admin_stats':
            total_users = len(users_db)
            bot.answer_callback_query(call.id, f"عدد المستخدمين: {total_users}\nإجمالي الطلبات: {total_orders_global}", show_alert=True)
            return
        elif data == 'admin_set_rate':
            admin_states['state'] = 'waiting_new_rate'
            bot.send_message(user_id, f"سعر الصرف الحالي هو: {exchange_rate:,} ل.س\nأرسل سعر الصرف الجديد برقم صحيح:")
            return
        elif data == 'admin_add_bal':
            admin_states['state'] = 'waiting_add_balance'
            bot.send_message(user_id, "أرسل الآيدي والمبلغ بالشكل التالي:\n`الايدي المبلغ`", parse_mode='Markdown')
            return
        elif data == 'admin_deduct_bal':
            admin_states['state'] = 'waiting_deduct_balance'
            bot.send_message(user_id, "أرسل الآيدي والمبلغ بالشكل التالي:\n`الايدي المبلغ`", parse_mode='Markdown')
            return
        elif data == 'admin_broadcast':
            admin_states['state'] = 'waiting_broadcast_msg'
            bot.send_message(user_id, "أرسل النص المراد إذاعته لجميع المستخدمين:")
            return

    if data.startswith("cat_"):
        cat_name = data.replace("cat_", "")
        if cat_name in store_categories:
            games = store_categories[cat_name]
            if not games:
                bot.answer_callback_query(call.id, "لا توجد خدمات حالياً في هذا القسم.", show_alert=True)
                return
            markup = types.InlineKeyboardMarkup()
            for g_name in games.keys():
                markup.add(types.InlineKeyboardButton(g_name, callback_data=f"game_{cat_name}_{g_name}"))
            bot.edit_message_text("اختر القسم المناسب:", call.message.chat.id, call.message.message_id, reply_markup=markup)

    elif data.startswith("game_"):
        parts = data.split("_", 2)
        cat_name = parts[1]
        game_name = parts[2]
        
        if game_name == "PUBG Mobile 🕹":
            try:
                bot.delete_message(call.message.chat.id, call.message.message_id)
            except Exception:
                pass
            pubg_image_url = "https://upload.wikimedia.org/wikipedia/en/thumb/9/9f/Pubg_mobile_logo.png/220px-Pubg_mobile_logo.png"
            markup = types.InlineKeyboardMarkup()
            sections = store_categories[cat_name][game_name].keys()
            for sec in sections:
                markup.add(types.InlineKeyboardButton(sec, callback_data=f"sec_{cat_name}_{game_name}_{sec}"))
            bot.send_photo(call.message.chat.id, pubg_image_url, caption="🎮 أهلاً بك في قسم شحن PUBG Mobile\nاختر نوع الشحن المطلوب:", reply_markup=markup)
        else:
            sections = store_categories[cat_name][game_name].keys()
            markup = types.InlineKeyboardMarkup()
            for sec in sections:
                markup.add(types.InlineKeyboardButton(sec, callback_data=f"sec_{cat_name}_{game_name}_{sec}"))
            bot.edit_message_text("اختر القسم الفرعي:", call.message.chat.id, call.message.message_id, reply_markup=markup)

    elif data.startswith("sec_"):
        parts = data.split("_", 3)
        cat_name = parts[1]
        game_name = parts[2]
        sec_name = parts[3]
        
        items = store_categories[cat_name][game_name][sec_name]
        markup = types.InlineKeyboardMarkup()
        for idx, item in enumerate(items):
            p_formatted = format_price(user_id, item['price'])
            markup.add(types.InlineKeyboardButton(f"{item['name']} - {p_formatted}", callback_data=f"item_{cat_name}_{game_name}_{sec_name}_{idx}"))
        
        try:
            bot.edit_message_text("اختر المنتج المناسب:", call.message.chat.id, call.message.message_id, reply_markup=markup)
        except Exception:
            bot.send_message(call.message.chat.id, "اختر المنتج المناسب:", reply_markup=markup)

    elif data.startswith("item_"):
        parts = data.split("_", 4)
        cat_name = parts[1]
        game_name = parts[2]
        sec_name = parts[3]
        item_idx = int(parts[4])
        
        item = store_categories[cat_name][game_name][sec_name][item_idx]
        user_temp_order[user_id] = {'item': item, 'sec': sec_name}
        
        if sec_name in ["اكواد 📱"]:
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("✅ تأكيد الشراء", callback_data="confirm_code_order"))
            p_formatted = format_price(user_id, item['price'])
            bot.answer_callback_query(call.id)
            bot.send_message(call.message.chat.id, f"📦 منتج: {item['name']}\n💰 السعر: {p_formatted}\n\nاضغط لتأكيد الشراء من رصيدك:")
            bot.send_message(call.message.chat.id, "اضغط تأكيد لتنفيذ الطلب:", reply_markup=markup)
        else:
            bot.answer_callback_query(call.id)
            bot.send_message(call.message.chat.id, f"📦 لقد اخترت: {item['name']}\n\nيرجى إرسال الآيدي (Player ID) الخاص بك الآن:")
            bot.register_next_step_handler(call.message, process_player_id)

def process_player_id(message):
    global total_orders_global
    user_id = message.from_user.id
    player_id = message.text.strip()
    
    if user_id not in user_temp_order:
        bot.reply_to(message, "⚠️ حدث خطأ أو انتهت الجلسة. أعد المحاولة من جديد.")
        return
        
    order_info = user_temp_order[user_id]
    item = order_info['item']
    
    if users_db[user_id]['balance'] < item['price']:
        bot.reply_to(message, f"❌ رصيدك غير كافٍ لإتمام عملية الشراء.\nرصيدك الحالي: {format_price(user_id, users_db[user_id]['balance'])}\nسعر المنتج: {format_price(user_id, item['price'])}")
        return
        
    bot.reply_to(message, "⏳ جاري تنفيذ الطلب عبر السيرفر، يرجى الانتظار...")
    
    res = create_mhd_order(item['id'], 1, player_id)
    if res.get('status') == 'SUCCESS' or res.get('status') == 'PENDING' or 'order_uuid' in res:
        users_db[user_id]['balance'] -= item['price']
        users_db[user_id]['spent'] += item['price']
        users_db[user_id]['orders_count'] += 1
        total_orders_global += 1
        
        bot.reply_to(message, f"✅ تم إرسال الطلب بنجاح!\n🆔 الآيدي: `{player_id}`\n📦 المنتج: {item['name']}\n💰 السعر المخصوم: {format_price(user_id, item['price'])}", parse_mode='Markdown')
    else:
        err_msg = res.get('message', 'خطأ غير معروف')
        bot.reply_to(message, f"❌ فشل تنفيذ الطلب من الخادم:\n{err_msg}")

@bot.callback_query_handler(func=lambda call: call.data == 'confirm_code_order')
def confirm_code_order_callback(call):
    global total_orders_global
    user_id = call.from_user.id
    if user_id not in user_temp_order:
        bot.answer_callback_query(call.id, "انتهت الجلسة، أعد المحاولة.", show_alert=True)
        return
        
    order_info = user_temp_order[user_id]
    item = order_info['item']
    
    if users_db[user_id]['balance'] < item['price']:
        bot.answer_callback_query(call.id, "رصيدك غير كافٍ!", show_alert=True)
        return
        
    bot.answer_callback_query(call.id, "جاري استخراج الكود...")
    res = create_mhd_code_order(item['id'], 1)
    
    if res.get('status') == 'SUCCESS' or 'order_uuid' in res:
        users_db[user_id]['balance'] -= item['price']
        users_db[user_id]['spent'] += item['price']
        users_db[user_id]['orders_count'] += 1
        total_orders_global += 1
        
        code_result = res.get('code', res.get('message', 'تم الشراء بنجاح ولم يرجع كود نصي مباشر، راجع الإدارة'))
        bot.send_message(call.message.chat.id, f"✅ تم شراء الكود بنجاح!\n📦 المنتج: {item['name']}\n🔑 الكود: `{code_result}`", parse_mode='Markdown')
    else:
        err_msg = res.get('message', 'خطأ غير معروف')
        bot.send_message(call.message.chat.id, f"❌ فشل تنفيذ الطلب:\n{err_msg}")

if __name__ == "__main__":
    def run_flask():
        app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

    t = Thread(target=run_flask)
    t.start()
    bot.infinity_polling()
