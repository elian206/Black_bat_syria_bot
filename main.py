import telebot
from telebot import types
from flask import Flask
from threading import Thread
import requests
import uuid
import re

# إعداد البوت
TOKEN = '8909052904:AAHEsWa85CbV5Kwxs4Y1kG7h7TMtHpx-TMw'
bot = telebot.TeleBot(TOKEN)

# إزالة الويب هوك لتجنب المشاكل عند التشغيل
try:
    bot.remove_webhook()
except Exception:
    pass

# الثوابت ومعلومات الأدمن
ADMIN_ID = 8534087775
ADMIN_USERNAME = "black_bat_s"
CHANNEL_USERNAME = '@black1_bat_syria'

# معلومات API المتجر
API_BASE = "https://mhd-game.com/api"
API_TOKEN = "Fluf9aJYBrtQ1a9ywuqrcMh2M4A8UIa8MKsgbyUk0PkYi301WuCqtLtGn4GO"
api_headers = {"api-token": API_TOKEN}

# قواعد البيانات المؤقتة
users_db = {}
total_orders_global = 0  # عداد الطلبات الكلي
exchange_rate = 15000  # سعر الصرف الافتراضي (قابل للتغيير من الأدمن)

# هيكل المتجر والأسعار (كما وردت في الكود الأصلي)
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

# متغيرات الحالة والتحكم
pending_topup = {}
admin_states = {}
user_temp_order = {}
user_temp_code = {}
bot_is_active = True

# --- دوال مساعدة ---

def format_price(user_id, price_in_usd):
    """تنسيق السعر بناءً على عملة المستخدم"""
    curr = users_db.get(user_id, {}).get('currency', 'USD')
    if curr == 'SYP':
        syp_amount = price_in_usd * exchange_rate
        return f"{syp_amount:,.0f} ل.س"
    else:
        return f"${price_in_usd}"

def create_mhd_order(product_id, quantity, player_id):
    """إنشاء طلب شحن (شدات/عضويات) عبر API الموقع"""
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
    """إنشاء طلب شراء كود عبر API الموقع"""
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
    """التحقق من حالة الطلب من الموقع"""
    try:
        url = f"{API_BASE}/client/api/orderStatus"
        params = {"order_uuid": order_uuid}
        response = requests.get(url, headers=api_headers, params=params)
        return response.json()
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}

def check_subscription(user_id):
    """التحقق من اشتراك المستخدم في القناة"""
    try:
        member = bot.get_chat_member(CHANNEL_USERNAME, user_id)
        if member.status in ['member', 'administrator', 'creator']:
            return True
    except Exception:
        pass
    return False

# --- معالجة الأوامر ---

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
    
    # زر إحصائيات الطلبات العام
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

# --- المعالج الرئيسي للرسائل النصية ---

@bot.message_handler(func=lambda message: True)
def handle_text_messages(message):
    global exchange_rate, bot_is_active, total_orders_global
    user_id = message.from_user.id
    
    if not bot_is_active and user_id != ADMIN_ID:
        return
    
    if user_id in users_db and users_db[user_id]['banned']:
        return

    # 1. معالجة أوامر الأدمن
    if user_id == ADMIN_ID:
        admin_st = admin_states.get('state')
        if admin_st == 'waiting_new_rate':
            try:
                numbers = re.findall(r'\d+', message.text.strip())
                if numbers:
                    exchange_rate = int(''.join(numbers))
                    admin_states.clear()
                    bot.reply_to(message, f"✅ تم تحديث سعر الصرف بنجاح: {exchange_rate:,} ل.س")
                    show_admin_panel(message)
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
                     # تهيئة مستخدم جديد إذا لم يكن موجوداً
                    users_db[target_id] = {'name': 'مستخدم جديد', 'balance': 0.0, 'spent': 0.0, 'orders_count': 0, 'banned': False, 'currency': 'USD', 'topup_history': [], 'orders_history': []}
                users_db[target_id]['balance'] += amount
                users_db[target_id]['topup_history'].append(f"إضافة يدوية من الإدارة: +${amount}")
                admin_states.clear()
                bot.reply_to(message, f"✅ تمت إضافة مبلغ {amount}$ بنجاح للمستخدم `{target_id}`", parse_mode='Markdown')
                try:
                    bot.send_message(target_id, f"🎁 قامت الإدارة بإضافة رصيد لحسابك بقيمة {amount}$!")
                except Exception:
                    pass
                show_admin_panel(message)
                return
            except Exception:
                bot.reply_to(message, "⚠️ الصيغة خاطئة. اتبع النمط: `الايدي المبلغ`", parse_mode='Markdown')
                return

        elif admin_st == 'waiting_deduct_balance':
            try:
                parts = message.text.strip().split()
                target_id = int(parts[0])
                amount =
