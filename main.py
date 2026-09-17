import telebot
from telebot import types
from flask import Flask
from threading import Thread
import requests
import uuid
import re

TOKEN = '8909052904:AAHEsWa85CbV5Kwxs4Y1kG7h7TMtHpx-TMw'
bot = telebot.TeleBot(TOKEN)

try:
    bot.remove_webhook()
except Exception:
    pass

ADMIN_ID = 8534087775
ADMIN_USERNAME = "black_bat_s" # تم تحديث معرف الدعم ليصبح حسابك المطلوب
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
        
        params = {
            "qty": quantity,
            "playerId": player_id,
            "order_uuid": unique_order_uuid,
        }
        
        response = requests.get(url, headers=api_headers, params=params)
        try:
            res_json = response.json()
        except ValueError:
            return {"status": "ERROR", "message": f"الموقع أرسل رداً غير صالح. الكود: {response.status_code}"}
            
        res_json['order_uuid'] = unique_order_uuid
        return res_json
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}

def create_mhd_code_order(product_id, quantity=1):
    try:
        unique_order_uuid = str(uuid.uuid4())
        url = f"{API_BASE}/client/api/newOrder/{product_id}/params"
        
        params = {
            "qty": quantity,
            "order_uuid": unique_order_uuid,
        }
        
        response = requests.get(url, headers=api_headers, params=params)
        try:
            res_json = response.json()
        except ValueError:
            return {"status": "ERROR", "message": f"الموقع أرسل رداً غير صالح. الكود: {response.status_code}"}
            
        res_json['order_uuid'] = unique_order_uuid
        return res_json
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}

def check_mhd_order_status(order_uuid):
    try:
        url = f"{API_BASE}/client/api/orderStatus"
        params = {"order_uuid": order_uuid}
        response = requests.get(url, headers=api_headers, params=params)
        try:
            res_data = response.json()
            return res_data
        except ValueError:
            return {"status": "ERROR", "message": "استجابة غير صالحة من سيرفر الموقع"}
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
            'balance': 0.0,
            'spent': 0.0,
            'orders_count': 0,
            'banned': False,
            'currency': 'USD',
            'topup_history': [],
            'orders_history': []
        }
    
    if users_db[user_id]['banned']:
        bot.reply_to(message, "عذراً، أنت محظور من استخدام هذا البوت.")
        return

    if not check_subscription(user_id) and user_id != ADMIN_ID:
        markup_sub = types.InlineKeyboardMarkup()
        btn_channel = types.InlineKeyboardButton('📢 اشترك في القناة الان', url='https://t.me/black1_bat_syria')
        btn_check = types.InlineKeyboardButton('✅ تحقق من الاشتراك', callback_data='check_sub')
        markup_sub.add(btn_channel)
        markup_sub.add(btn_check)
        
        bot.reply_to(message, "⚠️ عذراً، يجب عليك الاشتراك في قناة المتجر أولاً لتتمكن من استخدام البوت.\n\nرابط القناة: https://t.me/black1_bat_syria\n\nبعد الاشتراك، اضغط على زر التحقق بالأسفل 👇", reply_markup=markup_sub)
        return

    show_main_menu(message.chat.id, message.from_user.first_name, user_id)

def show_main_menu(chat_id, user_name, user_id):
    global total_orders_global
    current_curr = users_db.get(user_id, {}).get('currency', 'USD')
    curr_btn_text = '💱 العملة: دولار ($)' if current_curr == 'USD' else '💱 العملة: ليرة سورية (ل.س)'

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('🛍 خدمات متجرنا')
    btn2 = types.KeyboardButton('👤 حسابك')
    btn3 = types.KeyboardButton('💳 تعبئة رصيد')
    btn_support = types.KeyboardButton('📞 الدعم') 
    btn_curr = types.KeyboardButton(curr_btn_text)
    
    if chat_id == ADMIN_ID:
        btn_admin = types.KeyboardButton('⚙️ لوحة تحكم الأدمن')
        markup.add(btn1)
        markup.add(btn2, btn3)
        markup.add(btn_support, btn_curr)
        markup.add(btn_admin)
    else:
        markup.add(btn1)
        markup.add(btn2, btn3)
        markup.add(btn_support, btn_curr)
    
    markup_inline = types.InlineKeyboardMarkup()
    markup_inline.add(types.InlineKeyboardButton(f'📊 الطلبات المنفذة: {total_orders_global}', callback_data='show_global_orders_count'))

    welcome_msg = (
        f"أهلاً بك {user_name} بمتجر BLACK BAT 📱\n"
        f"نشكرك على التعامل معنا 🤝\n"
        f"قم باختيار ماذا تريد من خدماتنا ⏬"
    )
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
            text = message.text.strip()
            try:
                numbers = re.findall(r'\d+', text)
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
                    users_db[target_id] = {'name': 'مستخدم', 'balance': 0.0, 'spent': 0.0, 'orders_count': 0, 'banned': False, 'currency': 'USD', 'topup_history': [], 'orders_history': []}
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
                bot.reply_to(message, "⚠️ الصيغة خاطئة. يرجى الإرسال بهذا الشكل:\n`الايدي المبلغ` (مثال: `123456789 10`)", parse_mode='Markdown')
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
                show_admin_panel(message)
                return
            except Exception:
                bot.reply_to(message, "⚠️ الصيغة خاطئة. يرجى الإرسال بهذا الشكل:\n`الايدي المبلغ` (مثال: `123456789 5`)", parse_mode='Markdown')
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
            bot.reply_to(message, f"✅ تم إرسال الرسالة بنجاح إلى ({success_count}) عميل.")
            show_admin_panel(message)
            return

    if user_id in pending_topup:
        state = pending_topup[user_id].get('state')
        if state == 'waiting_amount':
            pending_topup[user_id]['amount'] = message.text.strip()
            pending_topup[user_id]['state'] = 'waiting_operation_id'
            
            # إضافة الأزرار المطلوبة عند خطوة إرسال رقم العملية/العملة
            markup_confirm_topup = types.InlineKeyboardMarkup()
            markup_confirm_topup.add(
                types.InlineKeyboardButton('نعم ✅', callback_data='topup_confirm_yes'),
                types.InlineKeyboardButton('لا ❌', callback_data='topup_confirm_no')
            )
            bot.reply_to(message, "ارسل رقم العملة (رقم العملية) ولتأكيد الطلب اضغط الزر المناسب:", reply_markup=markup_confirm_topup)
            return
            
        elif state == 'waiting_operation_id':
            op_id = message.text.strip()
            pending_topup[user_id]['op_id'] = op_id
            u_name = users_db.get(user_id, {}).get('name', message.from_user.first_name)
            amount = pending_topup[user_id]['amount']
            curr_type = pending_topup[user_id]['curr_type']
            method_name = pending_topup[user_id]['method_name']
            
            bot.reply_to(message, "تم استلام طلب تعبئة رصيدك ستوافق عليها الإدارة ✅")
            admin_msg = (
                f"📌 طلب تعبئة رصيد جديد ({method_name}):\n\n"
                f"📌 اسم المستخدم: {u_name}\n"
                f"📌 ايدي التلغرام: `{user_id}`\n"
                f"📌 المبلغ: {amount} {'$' if curr_type=='USD' else 'ل.س'}\n"
                f"📌 رقم العملية: {op_id}"
            )
            markup_app = types.InlineKeyboardMarkup()
            markup_app.add(
                types.InlineKeyboardButton('✅ موافق', callback_data=f'approve_topup_{user_id}_{amount}_{curr_type}'),
                types.InlineKeyboardButton('❌ غير موافق', callback_data=f'reject_topup_{user_id}')
            )
            bot.send_message(ADMIN_ID, admin_msg, parse_mode='Markdown', reply_markup=markup_app)
            del pending_topup[user_id]
            return

    if '💱 العملة:' in message.text:
        if user_id not in users_db:
            users_db[user_id] = {'name': message.from_user.first_name, 'balance': 0.0, 'spent': 0.0, 'orders_count': 0, 'banned': False, 'currency': 'USD', 'topup_history': [], 'orders_history': []}
        current_curr = users_db[user_id]['currency']
        if current_curr == 'USD':
            users_db[user_id]['currency'] = 'SYP'
            bot.reply_to(message, "تم تغيير العملة إلى (الليرة السورية 🇸🇾).")
        else:
            users_db[user_id]['currency'] = 'USD'
            bot.reply_to(message, "تم تغيير العملة إلى (الدولار الأمريكي 💵).")
        show_main_menu(message.chat.id, message.from_user.first_name, user_id)
        return

    if message.text == '📞 الدعم':
        markup_support = types.InlineKeyboardMarkup()
        markup_support.add(types.InlineKeyboardButton('💬 تواصل مع الأدمن مباشرة', url=f'https://t.me/{ADMIN_USERNAME}'))
        bot.reply_to(message, "📞 للتواصل مع الدعم الفني أو الاستفسار عن أي مشكلة، يمكنك الضغط على الزر أدناه للانتقال للملف الشخصي للأدمن مباشرة 👇", reply_markup=markup_support)
        return

    if message.text == '🛍 خدمات متجرنا':
        markup_cats = types.InlineKeyboardMarkup()
        for cat_name in store_categories.keys():
            markup_cats.add(types.InlineKeyboardButton(cat_name, callback_data=f"cat_{cat_name}"))
        bot.reply_to(message, "اختر القسم المطلوب لتصفح الخدمات والمنتجات ⏬", reply_markup=markup_cats)

    elif message.text == '👤 حسابك':
        if user_id not in users_db:
            users_db[user_id] = {'name': message.from_user.first_name, 'balance': 0.0, 'spent': 0.0, 'orders_count': 0, 'banned': False, 'currency': 'USD', 'topup_history': [], 'orders_history': []}
        u_data = users_db[user_id]
        curr = u_data.get('currency', 'USD')
        bal = u_data['balance']
        spnt = u_data['spent']
        
        if curr == 'SYP':
            bal_display = f"{bal * exchange_rate:,.0f} ل.س"
            spnt_display = f"{spnt * exchange_rate:,.0f} ل.س"
        else:
            bal_display = f"{bal} $"
            spnt_display = f"{spnt} $"

        account_info = (
            f"👤 **معلومات حسابك الشخصي:**\n\n"
            f"▫️ اسمك: {u_data['name']}\n"
            f"▫️ رصيدك: {bal_display}\n"
            f"▫️ مصروفك: {spnt_display}\n"
            f"▫️ عدد طلباتك: {u_data['orders_count']}\n"
            f"▫️ العملة الحالية: {curr}"
        )
        markup_acc = types.InlineKeyboardMarkup()
        markup_acc.add(types.InlineKeyboardButton('💳 تعبئة رصيدك', callback_data='top_up_balance'))
        markup_acc.add(types.InlineKeyboardButton('📜 سجل تعبئة الرصيد', callback_data='my_topup_log'))
        markup_acc.add(types.InlineKeyboardButton('📦 سجل طلباته', callback_data='my_orders_log'))
        bot.reply_to(message, account_info, parse_mode='Markdown', reply_markup=markup_acc)

    elif message.text == '💳 تعبئة رصيد' or message.text == 'تعبئة رصيد':
        show_topup_methods(message)

    elif message.text == '⚙️ لوحة تحكم الأدمن' and user_id == ADMIN_ID:
        show_admin_panel(message)

def show_topup_methods(message):
    markup_topup = types.InlineKeyboardMarkup()
    markup_topup.add(types.InlineKeyboardButton('🟩 Sham Cash (تحويل دولار 💵)', callback_data='pay_sham_usd'))
    markup_topup.add(types.InlineKeyboardButton('🟩 Sham Cash (تحويل ليرة سورية 🇸🇾)', callback_data='pay_sham_syp'))
    markup_topup.add(types.InlineKeyboardButton('🟥 Syriatel Cash (ليرة سورية 🇸🇾)', callback_data='pay_syriatel'))
    markup_topup.add(types.InlineKeyboardButton('🟨 MTN Cash (ليرة سورية 🇸🇾)', callback_data='pay_mtn'))
    
    if isinstance(message, types.Message):
        bot.send_message(message.chat.id, "💳 اختر طريقة تعبئة الرصيد المفضلة لديك:", reply_markup=markup_topup)
    else:
        bot.send_message(message.message.chat.id, "💳 اختر طريقة تعبئة الرصيد المفضلة لديك:", reply_markup=markup_topup)

def show_admin_panel(message):
    global bot_is_active, total_orders_global
    status_text = "🟢 حالة البوت: يعمل" if bot_is_active else "🔴 حالة البوت: متوقف"
    admin_text = f"⚙️ **لوحة تحكم الأدمن:**\n{status_text}\nسعر الصرف الحالي: {exchange_rate:,} ل.س\nإجمالي الطلبات الكلي: {total_orders_global}"
    
    markup_admin = types.InlineKeyboardMarkup()
    markup_admin.add(types.InlineKeyboardButton('💱 تغيير سعر الصرف', callback_data='adm_exchange_rate'))
    markup_admin.add(
        types.InlineKeyboardButton('➕ إضافة رصيد يدوي', callback_data='adm_add_bal'),
        types.InlineKeyboardButton('➖ خصم رصيد يدوي', callback_data='adm_deduct_bal')
    )
    markup_admin.add(types.InlineKeyboardButton('📢 إرسال رسالة للجميع', callback_data='adm_broadcast'))
    markup_admin.add(types.InlineKeyboardButton('👥 سجل العملاء', callback_data='adm_users_log'))
    markup_admin.add(types.InlineKeyboardButton('💻 كود البوت', callback_data='adm_get_source_code'))
    
    if isinstance(message, types.Message):
        bot.send_message(message.chat.id, admin_text, parse_mode='Markdown', reply_markup=markup_admin)
    else:
        bot.send_message(message.message.chat.id, admin_text, parse_mode='Markdown', reply_markup=markup_admin)

@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    global bot_is_active, exchange_rate, total_orders_global
    data = call.data
    user_id = call.from_user.id
    
    if not bot_is_active and user_id != ADMIN_ID:
        return

    if data == 'show_global_orders_count':
        bot.answer_callback_query(call.id, f"إجمالي الطلبات المنفذة في المتجر حالياً: {total_orders_global} طلب")
        try:
            markup_inline = types.InlineKeyboardMarkup()
            markup_inline.add(types.InlineKeyboardButton(f'📊 الطلبات المنفذة: {total_orders_global}', callback_data='show_global_orders_count'))
            bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=markup_inline)
        except Exception:
            pass
        return

    elif data == 'adm_get_source_code':
        if user_id != ADMIN_ID:
            return
        bot.answer_callback_query(call.id, "جاري إرسال كود البوت...")
        try:
            with open(__file__, 'rb') as f:
                bot.send_document(call.message.chat.id, f, caption="💻 تفضل ملف كود البوت الحالي. يمكنك التعديل عليه وإرساله لي لاحقاً في أي وقت مع طلباتك الجديدة.")
        except Exception as e:
            bot.send_message(call.message.chat.id, f"❌ حدث خطأ أثناء إرسال الكود: {e}")
        return

    elif data == 'adm_exchange_rate':
        if user_id != ADMIN_ID:
            return
        admin_states['state'] = 'waiting_new_rate'
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, f"💱 سعر الصرف الحالي هو: {exchange_rate:,} ل.س\n\nأرسل سعر الصرف الجديد الآن (أرقام فقط):")
        return

    elif data == 'adm_add_bal':
        if user_id != ADMIN_ID:
            return
        admin_states['state'] = 'waiting_add_balance'
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, "➕ أرسل الآيدي والمبلغ للإضافة بهذا الشكل:\n`الايدي المبلغ`\nمثال: `8534087775 10`", parse_mode='Markdown')
        return

    elif data == 'adm_deduct_bal':
        if user_id != ADMIN_ID:
            return
        admin_states['state'] = 'waiting_deduct_balance'
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, "➖ أرسل الآيدي والمبلغ للخصم بهذا الشكل:\n`الايدي المبلغ`\nمثال: `8534087775 5`", parse_mode='Markdown')
        return

    elif data == 'adm_broadcast':
        if user_id != ADMIN_ID:
            return
        admin_states['state'] = 'waiting_broadcast_msg'
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, "📢 أرسل الرسالة التي تريد نشرها لجميع العملاء الآن (سيتم إرسالها فوراً عند الإرسال):")
        return

    elif data == 'adm_users_log':
        if user_id != ADMIN_ID:
            return
        bot.answer_callback_query(call.id)
        total_users = len(users_db)
        bot.send_message(call.message.chat.id, f"👥 **عدد العملاء الكلي:** `{total_users}`", parse_mode='Markdown')
        
        for uid, udata in users_db.items():
            u_name = udata.get('name', 'بدون اسم')
            u_bal = udata.get('balance', 0.0)
            u_spent = udata.get('spent', 0.0)
            u_orders = udata.get('orders_count', 0)
            
            log_msg = (
                f"👤 اسم العميل: {u_name}\n"
                f"🆔 آيدي العميل: `{uid}`\n"
                f"💰 رصيده: ${u_bal}\n"
                f"💸 صرفه: ${u_spent}\n"
                f"📦 عدد طلباته: {u_orders}"
            )
            bot.send_message(call.message.chat.id, log_msg, parse_mode='Markdown')
        return

    elif data == 'my_topup_log':
        bot.answer_callback_query(call.id)
        u_data = users_db.get(user_id, {})
        history = u_data.get('topup_history', [])
        if not history:
            bot.send_message(call.message.chat.id, "📜 ليس لديك أي عمليات تعبئة رصيد سابقة.")
        else:
            msg = "📜 **سجل عمليات تعبئة الرصيد الخاصة بك:**\n\n" + "\n".join([f"🔹 {item}" for item in history])
            bot.send_message(call.message.chat.id, msg, parse_mode='Markdown')
        return

    elif data == 'my_orders_log':
        bot.answer_callback_query(call.id)
        u_data = users_db.get(user_id, {})
        orders = u_data.get('orders_history', [])
        if not orders:
            bot.send_message(call.message.chat.id, "📦 ليس لديك أي طلبات سابقة.")
        else:
            msg = "📦 **سجل طلباتك:**\n\n"
            for idx, ord_info in enumerate(orders, 1):
                msg += f"#{idx} | الخدمة: {ord_info['name']} | الكود/الحالة: {ord_info.get('status', 'قيد التنفيذ')}\n"
            
            markup_refresh = types.InlineKeyboardMarkup()
            markup_refresh.add(types.InlineKeyboardButton('🔄 تحديث الطلبات', callback_data='refresh_my_orders'))
            bot.send_message(call.message.chat.id, msg, parse_mode='Markdown', reply_markup=markup_refresh)
        return

    elif data == 'refresh_my_orders':
        bot.answer_callback_query(call.id, "جاري تحديث حالات الطلبات...")
        u_data = users_db.get(user_id, {})
        orders = u_data.get('orders_history', [])
        if not orders:
            bot.edit_message_text("📦 لا توجد طلبات لتحديثها.", chat_id=call.message.chat.id, message_id=call.message.message_id)
            return

        updated_msg = "📦 **سجل طلباتك (المحدث):**\n\n"
        for idx, ord_info in enumerate(orders, 1):
            uuid_str = ord_info.get('uuid')
            if uuid_str and not ord_info.get('is_code'):
                res = check_mhd_order_status(uuid_str)
                if res and isinstance(res, dict):
                    status_val = res.get("status") or res.get("state") or res.get("message")
                    if status_val:
                        ord_info['status'] = str(status_val)
                    else:
                        ord_info['status'] = "مكتمل / قيد التنفيذ"
                else:
                    ord_info['status'] = "قيد التنفيذ"
            
            updated_msg += f"#{idx} | الخدمة: {ord_info['name']} | التفاصيل/الحالة: {ord_info['status']}\n"

        markup_refresh = types.InlineKeyboardMarkup()
        markup_refresh.add(types.InlineKeyboardButton('🔄 تحديث الطلبات', callback_data='refresh_my_orders'))
        try:
            bot.edit_message_text(updated_msg, chat_id=call.message.chat.id, message_id=call.message.message_id, parse_mode='Markdown', reply_markup=markup_refresh)
        except Exception:
            bot.send_message(call.message.chat.id, updated_msg, parse_mode='Markdown', reply_markup=markup_refresh)
        return

    elif data in ['pay_sham_usd', 'pay_sham_syp', 'pay_syriatel', 'pay_mtn']:
        bot.answer_callback_query(call.id)
        curr_type = 'USD' if data == 'pay_sham_usd' else 'SYP'
        
        if data == 'pay_sham_usd':
            m_name = 'Sham Cash (دولار)'
            details_msg = (
                f"🟩 **تحويل Sham Cash (دولار 💵)**\n\n"
                f"قم بالتحويل على هذا الحساب ⏬\n"
                f"`ebae7d2aa7d10e62f02b1199d87208f4`\n"
                f"اسم الحساب: جورج عيسى بركات.\n\n"
                f"الرجاء إرسال **المبلغ المراد تعبئته** في رسالة الآن ⏬"
            )
        elif data == 'pay_sham_syp':
            m_name = 'Sham Cash (ليرة سورية)'
            details_msg = (
                f"🟩 **تحويل Sham Cash ليرة سورية 💵**\n\n"
                f"كل 1$ = {exchange_rate:,} ل.س\n"
                f"اقل مبلغ للتعبئة هو: 1 دولار 💲\n\n"
                f"قم بالتحويل على هذا الحساب ⏬\n"
                f"`ebae7d2aa7d10e62f02b1199d87208f4`\n"
                f"اسم الحساب: جورج عيسى بركات.\n\n"
                f"الرجاء إرسال **المبلغ المراد تعبئته** في رسالة الآن ⏬"
            )
        elif data == 'pay_syriatel':
            m_name = 'Syriatel Cash'
            details_msg = (
                f"🟥 **تحويل Syriatel Cash ليرة سورية 💵**\n\n"
                f"كل 1$ = {exchange_rate:,} ل.س\n\n"
                f"كود تحويل ⏪ `92189062`\n\n"
                f"⚠️ التحويل حصرا من خيار (تحويل يدوي) اذا قمت بتحويل رصيد عادي لن يتم الموافقة ع طلب التعبئة.\n\n"
                f"الرجاء إرسال **المبلغ المراد تعبئته** في رسالة الآن ⏬"
            )
        else:
            m_name = 'MTN Cash'
            details_msg = (
                f"🟨 **تحويل MTN Cash ليرة سورية 💵**\n\n"
                f"كل 1$ = {exchange_rate:,} ل.س\n\n"
                f"كود تحويل ⏬\n`8338 3112 0672 4992`\n\n"
                f"⚠️ التحويل حصرا من خيار (عن طريق رقم المحفظة) اذا قمت بتحويل رصيد عادي لن يتم الموافقة ع طلب التعبئة.\n\n"
                f"الرجاء إرسال **المبلغ المراد تعبئته** في رسالة الآن ⏬"
            )

        pending_topup[user_id] = {
            'method_name': m_name,
            'curr_type': curr_type,
            'state': 'waiting_amount'
        }
        bot.send_message(call.message.chat.id, details_msg, parse_mode='Markdown')
        return

    # معالجة أزرار نعم ولا الخاصة بتعبئة الرصيد
    elif data == 'topup_confirm_yes':
        if user_id not in pending_topup:
            bot.answer_callback_query(call.id, "انتهت الجلسة.", show_alert=True)
            return
        bot.answer_callback_query(call.id, "تم التأكيد، يرجى إرسال رقم العملية الآن:")
        bot.edit_message_text("أرسل الآن **رقم العملية (رقم التحويل)** في رسالة:", chat_id=call.message.chat.id, message_id=call.message.message_id, parse_mode='Markdown')
        return

    elif data == 'topup_confirm_no':
        if user_id in pending_topup:
            del pending_topup[user_id]
        bot.answer_callback_query(call.id, "تم الإلغاء والإرجاع إلى قائمة تعبئة الرصيد.")
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except Exception:
            pass
        show_topup_methods(call.message)
        return

    elif data.startswith('cat_'):
        cat_key = data.replace('cat_', '')
        bot.answer_callback_query(call.id)
        if cat_key == "🎮 شحن ألعاب":
            markup_games = types.InlineKeyboardMarkup()
            markup_games.add(types.InlineKeyboardButton("PUBG Mobile 🕹", callback_data="game_pubg"))
            bot.send_message(call.message.chat.id, "اختر اللعبة المطلوبة ⏬", reply_markup=markup_games)
        return

    elif data == "game_pubg":
        bot.answer_callback_query(call.id)
        markup_pubg = types.InlineKeyboardMarkup()
        markup_pubg.add(types.InlineKeyboardButton("سيرفر 1 🆔", callback_data="pubg_srv1"))
        markup_pubg.add(types.InlineKeyboardButton("سيرفر 2 🆔", callback_data="pubg_srv2"))
        markup_pubg.add(types.InlineKeyboardButton("اكواد 📱", callback_data="pubg_codes"))
        markup_pubg.add(types.InlineKeyboardButton("عضويات 💳", callback_data="pubg_mems"))
        bot.send_message(call.message.chat.id, "اختر القسم المناسب لـ PUBG Mobile 🕹", reply_markup=markup_pubg)
        return

    elif data in ["pubg_srv1", "pubg_srv2", "pubg_codes", "pubg_mems"]:
        bot.answer_callback_query(call.id)
        sub_key_map = {
            "pubg_srv1": "سيرفر 1 🆔",
            "pubg_srv2": "سيرفر 2 🆔",
            "pubg_codes": "اكواد 📱",
            "pubg_mems": "عضويات 💳"
        }
        sub_name = sub_key_map[data]
        products_list = store_categories["🎮 شحن ألعاب"]["PUBG Mobile 🕹"][sub_name]
        
        markup_prods = types.InlineKeyboardMarkup()
        for p in products_list:
            formatted_p_price = format_price(user_id, p['price'])
            if sub_name == "اكواد 📱":
                markup_prods.add(types.InlineKeyboardButton(f"{p['name']} - {formatted_p_price}", callback_data=f"buycode_{p['id']}"))
            else:
                markup_prods.add(types.InlineKeyboardButton(f"{p['name']} - {formatted_p_price}", callback_data=f"buyprod_{p['id']}"))
        
        bot.send_message(call.message.chat.id, f"📦 منتجات {sub_name}:", reply_markup=markup_prods)
        return

    elif data.startswith('buycode_'):
        prod_id = int(data.split('_')[1])
        selected_code = None
        
        codes_list = store_categories["🎮 شحن ألعاب"]["PUBG Mobile 🕹"]["اكواد 📱"]
        for p in codes_list:
            if p['id'] == prod_id:
                selected_code = p
                break
                
        if not selected_code:
            bot.answer_callback_query(call.id, "الكود غير موجود.")
            return

        user_balance = users_db.get(user_id, {}).get('balance', 0.0)
        p_price = selected_code['price']

        if user_balance < p_price:
            bot.answer_callback_query(call.id, "رصيدك غير كافٍ!", show_alert=True)
            bot.send_message(call.message.chat.id, "❌ عذراً، ليس لديك رصيد كافي لإتمام طلبك، قم بتعبئة رصيدك 💳")
            return

        user_temp_code[user_id] = {
            "product_id": selected_code['id'],
            "product_name": selected_code['name'],
            "price": p_price
        }

        formatted_price = format_price(user_id, p_price)
        formatted_balance = format_price(user_id, user_balance)

        markup_conf = types.InlineKeyboardMarkup()
        markup_conf.add(
            types.InlineKeyboardButton("نعم ✅", callback_data="confirm_code_yes"),
            types.InlineKeyboardButton("لا ❌", callback_data="confirm_code_no")
        )

        bot.answer_callback_query(call.id)
        bot.send_message(
            call.message.chat.id,
            f"🔹 **اسم الخدمة:** {selected_code['name']}\n"
            f"💵 **سعر الخدمة:** {formatted_price}\n"
            f"💰 **رصيدك:** {formatted_balance}\n\n"
            f"❓ **هل تريد إتمام شراء هذا الكود؟**",
            parse_mode="Markdown",
            reply_markup=markup_conf
        )
        return

    elif data.startswith('confirm_code_'):
        action = data.split('_')[2]
        if action == 'yes':
            if user_id not in user_temp_code:
                bot.answer_callback_query(call.id, "انتهت الجلسة.")
                return
            
            code_info = user_temp_code[user_id]
            p_id = code_info['product_id']
            p_name = code_info['product_name']
            price = code_info['price']

            if users_db[user_id]['balance'] < price:
                bot.answer_callback_query(call.id, "رصيدك غير كافٍ!", show_alert=True)
                return

            users_db[user_id]['balance'] -= price
            users_db[user_id]['spent'] += price
            users_db[user_id]['orders_count'] += 1

            bot.answer_callback_query(call.id, "جاري طلب الكود من الموقع...")
            response = create_mhd_code_order(product_id=p_id, quantity=1)

            if response and response.get("status") == "OK":
                uuid_val = response.get("order_uuid")
                code_content = response.get("code") or response.get("message") or "تم تسليم الكود بنجاح"
                
                users_db[user_id]['orders_history'].append({
                    "name": p_name,
                    "player_id": "بدون أيدي (كود)",
                    "uuid": uuid_val,
                    "status": f"الكود: {code_content}",
                    "is_code": True
                })
                
                total_orders_global += 1
                
                bot.send_message(
                    call.message.chat.id, 
                    f"✅ **تم شراء الكود بنجاح!**\n\n"
                    f"📦 الخدمة: {p_name}\n"
                    f"🔑 **الكود الخاص بك:**\n`{code_content}`",
                    parse_mode="Markdown"
                )
            else:
                users_db[user_id]['balance'] += price
                users_db[user_id]['spent'] -= price
                users_db[user_id]['orders_count'] -= 1
                err_msg = response.get("message", "خطأ غير معروف") if response else "فشل الاتصال"
                bot.send_message(call.message.chat.id, f"❌ فشل جلب الكود من الموقع: {err_msg}\nتم إرجاع المبلغ لرصيدك.")

            del user_temp_code[user_id]
        else:
            if user_id in user_temp_code:
                del user_temp_code[user_id]
            bot.answer_callback_query(call.id, "تم الإلغاء.")
            markup_pubg = types.InlineKeyboardMarkup()
            markup_pubg.add(types.InlineKeyboardButton("سيرفر 1 🆔", callback_data="pubg_srv1"))
            markup_pubg.add(types.InlineKeyboardButton("سيرفر 2 🆔", callback_data="pubg_srv2"))
            markup_pubg.add(types.InlineKeyboardButton("اكواد 📱", callback_data="pubg_codes"))
            markup_pubg.add(types.InlineKeyboardButton("عضويات 💳", callback_data="pubg_mems"))
            bot.send_message(call.message.chat.id, "تم إرجاعك إلى قائمة PUBG Mobile 🕹", reply_markup=markup_pubg)
        return

    elif data.startswith('buyprod_'):
        prod_id = int(data.split('_')[1])
        selected_prod = None
        
        pubg_sub_cats = store_categories["🎮 شحن ألعاب"]["PUBG Mobile 🕹"]
        for sub_name, plist in pubg_sub_cats.items():
            if sub_name == "اكواد 📱":
                continue
            for p in plist:
                if p['id'] == prod_id:
                    selected_prod = p
                    break
            if selected_prod:
                break
                
        if not selected_prod:
            bot.answer_callback_query(call.id, "المنتج غير موجود.")
            return

        user_balance = users_db.get(user_id, {}).get('balance', 0.0)
        p_price = selected_prod['price']

        if user_balance < p_price:
            bot.answer_callback_query(call.id, "رصيدك غير كافٍ!", show_alert=True)
            bot.send_message(call.message.chat.id, "❌ عذراً، ليس لديك رصيد كافي لإتمام طلبك، قم بتعبئة رصيدك 💳")
            return

        user_temp_order[user_id] = {
            "product_id": selected_prod['id'],
            "product_name": selected_prod['name'],
            "price": p_price
        }

        formatted_price = format_price(user_id, p_price)
        formatted_balance = format_price(user_id, user_balance)

        bot.answer_callback_query(call.id)
        bot.send_message(
            call.message.chat.id,
            f"🔹 **اسم الخدمة:** {selected_prod['name']}\n"
            f"💵 **سعر الخدمة:** {formatted_price}\n"
            f"💰 **رصيدك بالبوت:** {formatted_balance}\n\n"
            f"الرجاء إرسال **آيدي حسابه (Player ID)** في رسالة الآن ⏬",
            parse_mode="Markdown"
        )
        bot.register_next_step_handler(call.message, process_player_id)
        return

    elif data.startswith('confirm_order_'):
        action = data.split('_')[2]
        if action == 'yes':
            if user_id not in user_temp_order:
                bot.answer_callback_query(call.id, "انتهت الجلسة.")
                return
            
            order_info = user_temp_order[user_id]
            p_id = order_info['product_id']
            p_name = order_info['product_name']
            price = order_info['price']
            player_id = order_info['player_id']

            users_db[user_id]['balance'] -= price
            users_db[user_id]['spent'] += price
            users_db[user_id]['orders_count'] += 1

            bot.answer_callback_query(call.id, "جاري إرسال الطلب للموقع...")
            response = create_mhd_order(product_id=p_id, quantity=1, player_id=player_id)

            if response and response.get("status") == "OK":
                uuid_val = response.get("order_uuid")
                users_db[user_id]['orders_history'].append({
                    "name": p_name,
                    "player_id": player_id,
                    "uuid": uuid_val,
                    "status": "قيد التنفيذ",
                    "is_code": False
                })
                
                total_orders_global += 1
                
                bot.send_message(call.message.chat.id, "✅ تم تنفيذ طلبك بنجاح، شكرا للتعامل معنا 🤝")
            else:
                users_db[user_id]['balance'] += price
                users_db[user_id]['spent'] -= price
                users_db[user_id]['orders_count'] -= 1
                err_msg = response.get("message", "خطأ غير معروف") if response else "فشل الاتصال"
                bot.send_message(call.message.chat.id, f"❌ فشل تنفيذ الطلب من الموقع: {err_msg}\nتم إرجاع المبلغ لرصيدك.")

            del user_temp_order[user_id]
        else:
            if user_id in user_temp_order:
                del user_temp_order[user_id]
            bot.answer_callback_query(call.id, "تم الإلغاء.")
            markup_pubg = types.InlineKeyboardMarkup()
            markup_pubg.add(types.InlineKeyboardButton("سيرفر 1 🆔", callback_data="pubg_srv1"))
            markup_pubg.add(types.InlineKeyboardButton("سيرفر 2 🆔", callback_data="pubg_srv2"))
            markup_pubg.add(types.InlineKeyboardButton("اكواد 📱", callback_data="pubg_codes"))
            markup_pubg.add(types.InlineKeyboardButton("عضويات 💳", callback_data="pubg_mems"))
            bot.send_message(call.message.chat.id, "تم إرجاعك إلى قائمة PUBG Mobile 🕹", reply_markup=markup_pubg)
        return

    elif data.startswith('approve_topup_'):
        if user_id != ADMIN_ID:
            return
        parts = data.split('_')
        target_id = int(parts[2])
        amount = float(parts[3])
        if target_id not in users_db:
            users_db[target_id] = {'name': 'مستخدم', 'balance': 0.0, 'spent': 0.0, 'orders_count': 0, 'banned': False, 'currency': 'USD', 'topup_history': [], 'orders_history': []}
        users_db[target_id]['balance'] += amount
        users_db[target_id]['topup_history'].append(f"تعبئة رصيد ناجحة: +${amount}")
        bot.answer_callback_query(call.id, "تمت الموافقة بنجاح!")
        bot.edit_message_text(f"{call.message.text}\n\n✅ **الحالة:** تم قبول الطلب وإضافة الرصيد.", chat_id=call.message.chat.id, message_id=call.message.message_id, parse_mode='Markdown')
        try:
            bot.send_message(target_id, f"✅ تمت الموافقة على تعبئة رصيدك وإضافة مبلغ {amount}$ بنجاح!")
        except Exception:
            pass

    elif data.startswith('reject_topup_'):
        if user_id != ADMIN_ID:
            return
        target_id = int(data.split('_')[2])
        if target_id in users_db:
            users_db[target_id]['topup_history'].append("رفض طلب تعبئة رصيد من الإدارة")
        bot.answer_callback_query(call.id, "تم رفض الطلب.")
        bot.edit_message_text(f"{call.message.text}\n\n❌ **الحالة:** تم رفض الطلب.", chat_id=call.message.chat.id, message_id=call.message.message_id, parse_mode='Markdown')
        try:
            bot.send_message(target_id, "❌ عذراً، تم رفض طلب تعبئة الرصيد من قبل الإدارة.")
        except Exception:
            pass

    elif data == 'top_up_balance':
        show_topup_methods(call.message)

def process_player_id(message):
    user_id = message.from_user.id
    player_id = message.text.strip()

    if user_id not in user_temp_order:
        bot.send_message(message.chat.id, "انتهت الجلسة.")
        return

    user_temp_order[user_id]['player_id'] = player_id
    p_name = user_temp_order[user_id]['product_name']
    p_price = user_temp_order[user_id]['price']

    formatted_price = format_price(user_id, p_price)

    markup_conf = types.InlineKeyboardMarkup()
    markup_conf.add(
        types.InlineKeyboardButton("نعم ✅", callback_data="confirm_order_yes"),
        types.InlineKeyboardButton("لا ❌", callback_data="confirm_order_no")
    )
    
    bot.send_message(
        message.chat.id,
        f"📋 **ملخص الطلب:**\n"
        f"▫️ الخدمة: {p_name}\n"
        f"▫️ السعر: {formatted_price}\n"
        f"▫️ الآيدي: `{player_id}`\n\n"
        f"❓ **تريد اكمال طلبك؟**",
        parse_mode="Markdown"قامت      reply_markup=markup_conf
    )

app = Flask('')

@app.route('/')
def home():
    return "Bot is running 24/7 successfully!"

def run():
    app.run(host='0.0.0.0', port=10000)

def keep_alive():
    t = Thread(target=run)
    t.start()

if __name__ == "__main__":
    keep_alive()
    bot.infinity_polling(skip_pending=True)
