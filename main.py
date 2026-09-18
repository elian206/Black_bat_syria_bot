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
        },
        "Free Fire 🕹": {
            "سيرفر 1 💎": [
                {"id": 6774, "name": "110 جوهرة", "price": 1.05},
                {"id": 6774, "name": "231 جوهرة", "price": 2.1},
                {"id": 6775, "name": "583 جوهرة", "price": 5.22},
                {"id": 6772, "name": "1188 جوهرة", "price": 10.44},
                {"id": 6776, "name": "2420 جوهرة", "price": 20.82}
            ],
            "سيرفر 2 💎": [
                {"id": 6756, "name": "110 جوهرة", "price": 1.03},
                {"id": 6757, "name": "231 جوهرة", "price": 2.05},
                {"id": 6758, "name": "583 جوهرة", "price": 5.17},
                {"id": 6755, "name": "1188 جوهرة", "price": 10.45},
                {"id": 6760, "name": "2420 جوهرة", "price": 20.66}
            ],
            "عضويات 1 💳": [
                {"id": 6783, "name": "اسبوعية", "price": 2.4}
            ],
            "عضويات 2 💳": [
                {"id": 3341, "name": "اسبوعية", "price": 2.4},
                {"id": 3342, "name": "شهرية", "price": 11.13},
                {"id": 3343, "name": "تصريح بويا", "price": 3.45}
            ]
        },
        "Jawaker 🕹": {
            "سيرفر 1 🪙": [
                {"id": 72, "name": "توكنز جواكر سيرفر 1", "price_per_unit": 0.00012, "min_qty": 1000}
            ],
            "سيرفر 2 🪙": [
                {"id": 84, "name": "توكنز جواكر سيرفر 2", "price_per_unit": 0.000121, "min_qty": 1000}
            ],
            "خدمات أخرى 💳": [
                {"id": 1259, "name": "زر عرض الاسبوعي", "price": 21.3},
                {"id": 167, "name": "مسرعات احمر (1)", "price": 1.75},
                {"id": 183, "name": "مسرعات احمر (2)", "price": 8.23},
                {"id": 200, "name": "مسرعات احمر (3)", "price": 15.3},
                {"id": 961, "name": "مسرعات احمر (4)", "price": 27.85},
                {"id": 108, "name": "باقات جاهزة 230K توكنز", "price": 28.15}
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
        bot.reply_to(message, "⚠️ البوت متوقف حالياً للصيانة من قبل الإدارة.")
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

    if user_id in user_temp_order and user_temp_order[user_id].get('waiting_jawaker_qty'):
        try:
            qty = int(message.text.strip())
            j_data = user_temp_order[user_id]
            min_q = j_data['min_qty']
            if qty < min_q:
                bot.reply_to(message, f"⚠️ أقل كمية مسموحة هي {min_q} توكنز. يرجى إدخال كمية صحيحة:")
                return
            
            total_price = qty * j_data['price_per_unit']
            user_temp_order[user_id]['quantity'] = qty
            user_temp_order[user_id]['price'] = total_price
            user_temp_order[user_id]['waiting_jawaker_qty'] = False
            user_temp_order[user_id]['waiting_jawaker_id'] = True

            bot.reply_to(message, f"🔹 الكمية المطلوبة: {qty} توكنز\n💵 السعر الإجمالي: {format_price(user_id, total_price)}\n\nالرجاء إرسال **آيدي حسابه (Player ID)** الآن ⏬", parse_mode="Markdown")
            return
        except ValueError:
            bot.reply_to(message, "⚠️ يرجى إرسال رقم صحيح للكمية:")
            return

    if user_id in user_temp_order and user_temp_order[user_id].get('waiting_jawaker_id'):
        pid = message.text.strip()
        user_temp_order[user_id]['player_id'] = pid
        user_temp_order[user_id]['waiting_jawaker_id'] = False
        o_info = user_temp_order[user_id]

        markup_conf = types.InlineKeyboardMarkup()
        markup_conf.add(types.InlineKeyboardButton("نعم ✅", callback_data="confirm_order_yes"), types.InlineKeyboardButton("لا ❌", callback_data="confirm_order_no"))
        
        bot.send_message(message.chat.id, f"📋 **ملخص الطلب:**\n▫️ الخدمة: {o_info['product_name']}\n▫️ الكمية: {o_info['quantity']} توكنز\n▫️ السعر الإجمالي: {format_price(user_id, o_info['price'])}\n▫️ الآيدي: `{o_info['player_id']}`\n\n❓ **هل تريد إكمال طلبك؟**", parse_mode="Markdown", reply_markup=markup_conf)
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
                show_admin_panel(message)
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
            bot.reply_to(message, f"✅ تم إرسال الرسالة بنجاح إلى ({success_count}) عميل.")
            show_admin_panel(message)
            return

    if user_id in pending_topup:
        state = pending_topup[user_id].get('state')
        if state == 'waiting_amount':
            try:
                val = float(message.text.strip())
            except ValueError:
                bot.reply_to(message, "⚠️ يرجى إرسال رقم صالح فقط.")
                return

            min_limit = pending_topup[user_id]['min_limit']
            if val < min_limit:
                bot.reply_to(message, f"⚠️ عذراً، الحد الأدنى للإيداع لهذه الطريقة هو {min_limit} {'ل.س' if min_limit > 1 else '$'}. يرجى إدخال مبلغ أكبر:")
                return

            pending_topup[user_id]['amount'] = message.text.strip()
            pending_topup[user_id]['state'] = 'waiting_operation_id'
            bot.reply_to(message, "الرجاء إرسال **رقم العملية (رقم التحويل)** الآن ⏬", parse_mode='Markdown')
            return
            
        elif state == 'waiting_operation_id':
            op_id = message.text.strip()
            pending_topup[user_id]['op_id'] = op_id
            
            markup_confirm_topup = types.InlineKeyboardMarkup()
            markup_confirm_topup.add(
                types.InlineKeyboardButton('نعم ✅', callback_data='topup_confirm_yes'),
                types.InlineKeyboardButton('لا ❌', callback_data='topup_confirm_no')
            )
            bot.reply_to(message, "ارسل رقم العملة (رقم العملية) ولتأكيد الطلب اضغط الزر المناسب:", reply_markup=markup_confirm_topup)
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
        bot.reply_to(message, "📞 للتواصل مع الدعم الفني أو الاستفسار، يمكنك الضغط على الزر أدناه للانتقال للملف الشخصي للأدمن مباشرة 👇", reply_markup=markup_support)
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
        
        bal_display = f"{bal * exchange_rate:,.0f} ل.س" if curr == 'SYP' else f"{bal} $"
        spnt_display = f"{spnt * exchange_rate:,.0f} ل.س" if curr == 'SYP' else f"{spnt} $"

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
    toggle_bot_text = '🔴 إطفاء البوت' if bot_is_active else '🟢 تشغيل البوت'
    markup_admin.add(types.InlineKeyboardButton(toggle_bot_text, callback_data='adm_toggle_bot'))
    markup_admin.add(types.InlineKeyboardButton('📢 إرسال رسالة للجميع', callback_data='adm_broadcast'))
    markup_admin.add(types.InlineKeyboardButton('💱 تغيير سعر الصرف', callback_data='adm_exchange_rate'))
    markup_admin.add(types.InlineKeyboardButton('➕ إضافة رصيد يدوي', callback_data='adm_add_bal'), types.InlineKeyboardButton('➖ خصم رصيد يدوي', callback_data='adm_deduct_bal'))
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

    elif data == 'adm_toggle_bot':
        if user_id != ADMIN_ID:
            return
        bot_is_active = not bot_is_active
        status_msg = "🟢 تم تشغيل البوت بنجاح!" if bot_is_active else "🔴 تم إطفاء البوت بنجاح!"
        bot.answer_callback_query(call.id, status_msg)
        try:
            status_text = "🟢 حالة البوت: يعمل" if bot_is_active else "🔴 حالة البوت: متوقف"
            admin_text = f"⚙️ **لوحة تحكم الأدمن:**\n{status_text}\nسعر الصرف الحالي: {exchange_rate:,} ل.س\nإجمالي الطلبات الكلي: {total_orders_global}"
            markup_admin = types.InlineKeyboardMarkup()
            toggle_bot_text = '🔴 إطفاء البوت' if bot_is_active else '🟢 تشغيل البوت'
            markup_admin.add(types.InlineKeyboardButton(toggle_bot_text, callback_data='adm_toggle_bot'))
            markup_admin.add(types.InlineKeyboardButton('📢 إرسال رسالة للجميع', callback_data='adm_broadcast'))
            markup_admin.add(types.InlineKeyboardButton('💱 تغيير سعر الصرف', callback_data='adm_exchange_rate'))
            markup_admin.add(types.InlineKeyboardButton('➕ إضافة رصيد يدوي', callback_data='adm_add_bal'), types.InlineKeyboardButton('➖ خصم رصيد يدوي', callback_data='adm_deduct_bal'))
            markup_admin.add(types.InlineKeyboardButton('👥 سجل العملاء', callback_data='adm_users_log'))
            markup_admin.add(types.InlineKeyboardButton('💻 كود البوت', callback_data='adm_get_source_code'))
            bot.edit_message_text(admin_text, chat_id=call.message.chat.id, message_id=call.message.message_id, parse_mode='Markdown', reply_markup=markup_admin)
        except Exception:
            show_admin_panel(call.message)
        return

    elif data == 'adm_get_source_code':
        if user_id != ADMIN_ID:
            return
        bot.answer_callback_query(call.id, "جاري إرسال كود البوت...")
        try:
            with open(__file__, 'rb') as f:
                bot.send_document(call.message.chat.id, f, caption="💻 تفضل ملف كود البوت الحالي.")
        except Exception as e:
            bot.send_message(call.message.chat.id, f"❌ حدث خطأ أثناء إرسال الكود: {e}")
        return

    elif data == 'adm_exchange_rate':
        if user_id != ADMIN_ID:
            return
        admin_states['state'] = 'waiting_new_rate'
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, f"💱 سعر الصرف الحالي هو: {exchange_rate:,} ل.س\n\nأرسل سعر الصرف الجديد الآن:")
        return

    elif data == 'adm_add_bal':
        if user_id != ADMIN_ID:
            return
        admin_states['state'] = 'waiting_add_balance'
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, "➕ أرسل الآيدي والمبلغ للإضافة بهذا الشكل:\n`الايدي المبلغ`", parse_mode='Markdown')
        return

    elif data == 'adm_deduct_bal':
        if user_id != ADMIN_ID:
            return
        admin_states['state'] = 'waiting_deduct_balance'
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, "➖ أرسل الآيدي والمبلغ للخصم بهذا الشكل:\n`الايدي المبلغ`", parse_mode='Markdown')
        return

    elif data == 'adm_broadcast':
        if user_id != ADMIN_ID:
            return
        admin_states['state'] = 'waiting_broadcast_msg'
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, "📢 أرسل الرسالة التي تريد نشرها لجميع العملاء الآن:")
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
            log_msg = f"👤 اسم العميل: {u_name}\n🆔 آيدي العميل: `{uid}`\n💰 رصيده: ${u_bal}\n💸 صرفه: ${u_spent}\n📦 طلباته: {u_orders}"
            bot.send_message(call.message.chat.id, log_msg, parse_mode='Markdown')
        return

    elif data == 'my_topup_log':
        bot.answer_callback_query(call.id)
        u_data = users_db.get(user_id, {})
        history = u_data.get('topup_history', [])
        if not history:
            bot.send_message(call.message.chat.id, "📜 ليس لديك أي عمليات تعبئة رصيد سابقة.")
        else:
            msg = "📜 **سجل عمليات تعبئة الرصيد:**\n\n" + "\n".join([f"🔹 {item}" for item in history])
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
                msg += f"#{idx} | الخدمة: {ord_info['name']} | الحالة: {ord_info.get('status', 'قيد التنفيذ')}\n"
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
                    ord_info['status'] = str(status_val) if status_val else "مكتمل / قيد التنفيذ"
            updated_msg += f"#{idx} | الخدمة: {ord_info['name']} | الحالة: {ord_info['status']}\n"

        markup_refresh = types.InlineKeyboardMarkup()
        markup_refresh.add(types.InlineKeyboardButton('🔄 تحديث الطلبات', callback_data='refresh_my_orders'))
        try:
            bot.edit_message_text(updated_msg, chat_id=call.message.chat.id, message_id=call.message.message_id, parse_mode='Markdown', reply_markup=markup_refresh)
        except Exception:
            bot.send_message(call.message.chat.id, updated_msg, parse_mode='Markdown', reply_markup=markup_refresh)
        return

    elif data in ['pay_sham_usd', 'pay_sham_syp', 'pay_syriatel', 'pay_mtn']:
        bot.answer_callback_query(call.id)
        if data == 'pay_sham_usd':
            m_name, curr_type, min_limit, details_msg = 'Sham Cash (دولار)', 'USD', 1, "🟩 **تحويل Sham Cash (دولار 💵)**\n\nالحد الأدنى للإيداع: 1$\nحساب التحويل:\n`ebae7d2aa7d10e62f02b1199d87208f4`\nاسم الحساب: جورج عيسى بركات.\n\nالرجاء إرسال **المبلغ المراد تعبئته** الآن ⏬"
        elif data == 'pay_sham_syp':
            m_name, curr_type, min_limit, details_msg = 'Sham Cash (ليرة سورية)', 'SYP', 50, f"🟩 **تحويل Sham Cash ليرة سورية 🇸🇾**\n\nالحد الأدنى للإيداع: 50 ل.س\nكل 1$ = {exchange_rate:,} ل.س\nالحساب: `ebae7d2aa7d10e62f02b1199d87208f4`\nاسم الحساب: جورج عيسى بركات.\n\nالرجاء إرسال **المبلغ المراد تعبئته** الآن ⏬"
        elif data == 'pay_syriatel':
            m_name, curr_type, min_limit, details_msg = 'Syriatel Cash', 'SYP', 80, f"🟥 **تحويل Syriatel Cash 🇸🇾**\n\nالحد الأدنى للإيداع: 80 ل.س\nكل 1$ = {exchange_rate:,} ل.س\nكود تحويل ⏪ `92189062`\n\nالرجاء إرسال **المبلغ المراد تعبئته** الآن ⏬"
        else:
            m_name, curr_type, min_limit, details_msg = 'MTN Cash', 'SYP', 100, f"🟨 **تحويل MTN Cash 🇸🇾**\n\nالحد الأدنى للإيداع: 100 ل.س\nكل 1$ = {exchange_rate:,} ل.س\nكود التحويل ⏬\n`8338 3112 0672 4992`\n\nالرجاء إرسال **المبلغ المراد تعبئته** الآن ⏬"

        pending_topup[user_id] = {'method_name': m_name, 'curr_type': curr_type, 'min_limit': min_limit, 'state': 'waiting_amount'}
        bot.send_message(call.message.chat.id, details_msg, parse_mode='Markdown')
        return

    elif data == 'topup_confirm_yes':
        if user_id not in pending_topup:
            bot.answer_callback_query(call.id, "انتهت الجلسة.", show_alert=True)
            return
        
        u_name = users_db.get(user_id, {}).get('name', call.from_user.first_name)
        amount = pending_topup[user_id]['amount']
        curr_type = pending_topup[user_id]['curr_type']
        method_name = pending_topup[user_id]['method_name']
        op_id = pending_topup[user_id]['op_id']

        bot.answer_callback_query(call.id, "تم استلام طلب تعبئة رصيدك ستوافق عليها الإدارة ✅")
        bot.edit_message_text("تم استلام طلب تعبئة رصيدك ستوافق عليها الإدارة ✅", chat_id=call.message.chat.id, message_id=call.message.message_id)

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

    elif data == 'topup_confirm_no':
        if user_id in pending_topup:
            del pending_topup[user_id]
        bot.answer_callback_query(call.id, "تم الإلغاء والإرجاع إلى القائمة.")
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
            markup_games.add(types.InlineKeyboardButton("Free Fire 🕹", callback_data="game_freefire"))
            markup_games.add(types.InlineKeyboardButton("Jawaker 🕹", callback_data="game_jawaker"))
            bot.send_message(call.message.chat.id, "اختر اللعبة المطلوبة ّ⏬", reply_markup=markup_games)
        return

    elif data == "game_pubg":
        bot.answer_callback_query(call.id)
        markup_pubg = types.InlineKeyboardMarkup()
        markup_pubg.add(types.InlineKeyboardButton("سيرفر 1 🆔", callback_data="pubg_srv1"))
        markup_pubg.add(types.InlineKeyboardButton("سيرفر 2 🆔", callback_data="pubg_srv2"))
        markup_pubg.add(types.InlineKeyboardButton("اكواد 📱", callback_data="pubg_codes"))
        markup_pubg.add(types.InlineKeyboardButton("عضويات 💳", callback_data="pubg_mems"))
        
        pubg_image_url = "https://w7.pngwing.com/pngs/303/305/png-transparent-pubg-mobile-hd-logo-thumbnail.png"
        try:
            bot.send_photo(
                call.message.chat.id, 
                pubg_image_url, 
                caption="🎮 **قسم شحن شدات وأعضاء PUBG Mobile**\nاختر القسم المناسب من الأزرار أدناه ⏬", 
                parse_mode="Markdown", 
                reply_markup=markup_pubg
            )
        except Exception:
            bot.send_message(call.message.chat.id, "🎮 **قسم شحن شدات وأعضاء PUBG Mobile**\nاختر القسم المناسب ⏬", reply_markup=markup_pubg)
        return

    elif data == "game_freefire":
        bot.answer_callback_query(call.id)
        markup_ff = types.InlineKeyboardMarkup()
        markup_ff.add(types.InlineKeyboardButton("سيرفر 1 💎", callback_data="ff_srv1"))
        markup_ff.add(types.InlineKeyboardButton("سيرفر 2 💎", callback_data="ff_srv2"))
        markup_ff.add(types.InlineKeyboardButton("عضويات 1 💳", callback_data="ff_mems1"))
        markup_ff.add(types.InlineKeyboardButton("عضويات 2 💳", callback_data="ff_mems2"))
        bot.send_message(call.message.chat.id, "🔥 **قسم شحن Free Fire**\nاختر القسم المناسب ⏬", reply_markup=markup_ff)
        return

    elif data == "game_jawaker":
        bot.answer_callback_query(call.id)
        markup_jw = types.InlineKeyboardMarkup()
        markup_jw.add(types.InlineKeyboardButton("سيرفر 1 🪙", callback_data="jw_srv1"))
        markup_jw.add(types.InlineKeyboardButton("سيرفر 2 🪙", callback_data="jw_srv2"))
        markup_jw.add(types.InlineKeyboardButton("زر عرض الاسبوعي 💳", callback_data="buyprod_1259"))
        markup_jw.add(types.InlineKeyboardButton("مسرعات 🚀", callback_data="jw_speeds"))
        markup_jw.add(types.InlineKeyboardButton("باقات جاهزة 💳", callback_data="buyprod_108"))
        bot.send_message(call.message.chat.id, "🂡 **قسم شحن Jawaker**\nاختر القسم المناسب ⏬", reply_markup=markup_jw)
        return

    elif data == "jw_speeds":
        bot.answer_callback_query(call.id)
        speeds_list = store_categories["🎮 شحن ألعاب"]["Jawaker 🕹"]["خدمات أخرى 💳"][1:5]
        markup_spds = types.InlineKeyboardMarkup()
        for p in speeds_list:
            markup_spds.add(types.InlineKeyboardButton(f"{p['name']} - {format_price(user_id, p['price'])}", callback_data=f"buyprod_{p['id']}"))
        bot.send_message(call.message.chat.id, "🚀 اختر مسرعات جواكر المطلوبة:", reply_markup=markup_spds)
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

    elif data in ["ff_srv1", "ff_srv2", "ff_mems1", "ff_mems2"]:
        bot.answer_callback_query(call.id)
        ff_map = {
            "ff_srv1": "سيرفر 1 💎",
            "ff_srv2": "سيرفر 2 💎",
            "ff_mems1": "عضويات 1 💳",
            "ff_mems2": "عضويات 2 💳"
        }
        sub_name = ff_map[data]
        products_list = store_categories["🎮 شحن ألعاب"]["Free Fire 🕹"][sub_name]
        
        markup_prods = types.InlineKeyboardMarkup()
        for p in products_list:
            formatted_p_price = format_price(user_id, p['price'])
            markup_prods.add(types.InlineKeyboardButton(f"{p['name']} - {formatted_p_price}", callback_data=f"buyprod_{p['id']}"))
        
        bot.send_message(call.message.chat.id, f"🔥 منتجات {sub_name}:", reply_markup=markup_prods)
        return

    elif data in ["jw_srv1", "jw_srv2"]:
        bot.answer_callback_query(call.id)
        jw_key = "سيرفر 1 🪙" if data == "jw_srv1" else "سيرفر 2 🪙"
        jw_info = store_categories["🎮 شحن ألعاب"]["Jawaker 🕹"][jw_key][0]
        
        user_temp_order[user_id] = {
            "product_id": jw_info['id'],
            "product_name": jw_info['name'],
            "price_per_unit": jw_info['price_per_unit'],
            "min_qty": jw_info['min_qty'],
            "waiting_jawaker_qty": True
        }
        bot.send_message(call.message.chat.id, f"🪙 أقدمت على طلب {jw_info['name']}.\nالحد الأدنى للطلب: {jw_info['min_qty']} توكنز.\n\nالرجاء إرسال **الكمية** المطلوبة الآن كرقماً صحيحاً ⏬")
        return

    elif data.startswith('buycode_'):
        prod_id = int(data.split('_')[1])
        selected_code = next((p for p in store_categories["🎮 شحن ألعاب"]["PUBG Mobile 🕹"]["اكواد 📱"] if p['id'] == prod_id), None)
                
        if not selected_code:
            bot.answer_callback_query(call.id, "الكود غير موجود.")
            return

        user_balance = users_db.get(user_id, {}).get('balance', 0.0)
        p_price = selected_code['price']

        if user_balance < p_price:
            bot.answer_callback_query(call.id, "رصيدك غير كافٍ!", show_alert=True)
            bot.send_message(call.message.chat.id, "❌ عذراً، ليس لديك رصيد كافي، قم بتعبئة رصيدك 💳")
            return

        user_temp_code[user_id] = {"product_id": selected_code['id'], "product_name": selected_code['name'], "price": p_price}
        markup_conf = types.InlineKeyboardMarkup()
        markup_conf.add(types.InlineKeyboardButton("نعم ✅", callback_data="confirm_code_yes"), types.InlineKeyboardButton("لا ❌", callback_data="confirm_code_no"))

        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, f"🔹 الخدمة: {selected_code['name']}\n💵 السعر: {format_price(user_id, p_price)}\n\n❓ هل تريد إتمام الشراء؟", parse_mode="Markdown", reply_markup=markup_conf)
        return

    elif data.startswith('confirm_code_'):
        action = data.split('_')[2]
        if action == 'yes':
            if user_id not in user_temp_code:
                bot.answer_callback_query(call.id, "انتهت الجلسة.")
                return
            
            code_info = user_temp_code[user_id]
            users_db[user_id]['balance'] -= code_info['price']
            users_db[user_id]['spent'] += code_info['price']
            users_db[user_id]['orders_count'] += 1

            bot.answer_callback_query(call.id, "جاري طلب الكود...")
            response = create_mhd_code_order(product_id=code_info['product_id'], quantity=1)

            if response and response.get("status") == "OK":
                uuid_val = response.get("order_uuid")
                code_content = response.get("code") or response.get("message") or "تم تسليم الكود بنجاح"
                users_db[user_id]['orders_history'].append({"name": code_info['product_name'], "player_id": "كود", "uuid": uuid_val, "status": f"الكود: {code_content}", "is_code": True})
                total_orders_global += 1
                bot.send_message(call.message.chat.id, f"✅ **تم شراء الكود بنجاح!**\n🔑 الكود:\n`{code_content}`", parse_mode="Markdown")
            else:
                users_db[user_id]['balance'] += code_info['price']
                users_db[user_id]['spent'] -= code_info['price']
                users_db[user_id]['orders_count'] -= 1
                bot.send_message(call.message.chat.id, "❌ فشل جلب الكود من الموقع، تم إرجاع المبلغ لرصيدك.")
            del user_temp_code[user_id]
        else:
            if user_id in user_temp_code:
                del user_temp_code[user_id]
            bot.answer_callback_query(call.id, "تم الإلغاء.")
        return

    elif data.startswith('buyprod_'):
        prod_id = int(data.split('_')[1])
        selected_prod = None
        
        # البحث ضمن كل الألعاب المتاحة
        all_games = store_categories["🎮 شحن ألعاب"]
        for g_name, g_content in all_games.items():
            for sub_name, plist in g_content.items():
                if sub_name == "اكواد 📱": continue
                selected_prod = next((p for p in plist if p['id'] == prod_id), None)
                if selected_prod: break
            if selected_prod: break
            
        if not selected_prod:
            # البحث في خدمات جواكر الأخرى
            other_list = store_categories["🎮 شحن ألعاب"]["Jawaker 🕹"]["خدمات أخرى 💳"]
            selected_prod = next((p for p in other_list if p['id'] == prod_id), None)
                
        if not selected_prod:
            bot.answer_callback_query(call.id, "المنتج غير موجود.")
            return

        if users_db.get(user_id, {}).get('balance', 0.0) < selected_prod['price']:
            bot.answer_callback_query(call.id, "رصيدك غير كافٍ!", show_alert=True)
            bot.send_message(call.message.chat.id, "❌ عذراً، رصيدك غير كافي.")
            return

        user_temp_order[user_id] = {"product_id": selected_prod['id'], "product_name": selected_prod['name'], "price": selected_prod['price']}
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, f"🔹 الخدمة: {selected_prod['name']}\n💵 السعر: {format_price(user_id, selected_prod['price'])}\n\nالرجاء إرسال **آيدي حسابه (Player ID)** الآن ⏬", parse_mode="Markdown")
        bot.register_next_step_handler(call.message, process_player_id)
        return

    elif data.startswith('confirm_order_'):
        action = data.split('_')[2]
        if action == 'yes':
            if user_id not in user_temp_order: return
            o_info = user_temp_order[user_id]
            
            user_balance = users_db.get(user_id, {}).get('balance', 0.0)
            if user_balance < o_info['price']:
                bot.answer_callback_query(call.id, "رصيدك غير كافٍ!", show_alert=True)
                return

            users_db[user_id]['balance'] -= o_info['price']
            users_db[user_id]['spent'] += o_info['price']
            users_db[user_id]['orders_count'] += 1

            bot.answer_callback_query(call.id, "جاري إرسال الطلب للموقع...")
            qty_val = o_info.get('quantity', 1)
            response = create_mhd_order(product_id=o_info['product_id'], quantity=qty_val, player_id=o_info['player_id'])

            if response and response.get("status") == "OK":
                users_db[user_id]['orders_history'].append({"name": o_info['product_name'], "player_id": o_info['player_id'], "uuid": response.get("order_uuid"), "status": "قيد التنفيذ", "is_code": False})
                total_orders_global += 1
                bot.send_message(call.message.chat.id, "✅ تم تنفيذ طلبك بنجاح 🤝")
            else:
                users_db[user_id]['balance'] += o_info['price']
                users_db[user_id]['spent'] -= o_info['price']
                users_db[user_id]['orders_count'] -= 1
                bot.send_message(call.message.chat.id, "❌ فشل تنفيذ الطلب، تم إرجاع المبلغ لرصيدك.")
            del user_temp_order[user_id]
        else:
            if user_id in user_temp_order: del user_temp_order[user_id]
            bot.answer_callback_query(call.id, "تم الإلغاء.")
        return

    elif data.startswith('approve_topup_'):
        if user_id != ADMIN_ID: return
        parts = data.split('_')
        target_id, amount = int(parts[2]), float(parts[3])
        if target_id not in users_db:
            users_db[target_id] = {'name': 'مستخدم', 'balance': 0.0, 'spent': 0.0, 'orders_count': 0, 'banned': False, 'currency': 'USD', 'topup_history': [], 'orders_history': []}
        users_db[target_id]['balance'] += amount
        users_db[target_id]['topup_history'].append(f"تعبئة رصيد ناجحة: +${amount}")
        bot.answer_callback_query(call.id, "تمت الموافقة بنجاح!")
        bot.edit_message_text(f"{call.message.text}\n\n✅ **الحالة:** تم قبول الطلب.", chat_id=call.message.chat.id, message_id=call.message.message_id, parse_mode='Markdown')
        try:
            bot.send_message(target_id, f"✅ تمت الموافقة على تعبئة رصيدك وإضافة مبلغ {amount}$ بنجاح!")
        except Exception:
            pass

    elif data.startswith('reject_topup_'):
        if user_id != ADMIN_ID: return
        target_id = int(data.split('_')[2])
        if target_id in users_db:
            users_db[target_id]['topup_history'].append("رفض طلب تعبئة رصيد")
        bot.answer_callback_query(call.id, "تم رفض الطلب.")
        bot.edit_message_text(f"{call.message.text}\n\n❌ **الحالة:** تم رفض الطلب.", chat_id=call.message.chat.id, message_id=call.message.message_id, parse_mode='Markdown')
        try:
            bot.send_message(target_id, "❌ عذراً، تم رفض طلب تعبئة الرصيد.")
        except Exception:
            pass

    elif data == 'top_up_balance':
        show_topup_methods(call.message)

def process_player_id(message):
    user_id = message.from_user.id
    if user_id not in user_temp_order:
        return
    user_temp_order[user_id]['player_id'] = message.text.strip()
    o_info = user_temp_order[user_id]

    markup_conf = types.InlineKeyboardMarkup()
    markup_conf.add(types.InlineKeyboardButton("نعم ✅", callback_data="confirm_order_yes"), types.InlineKeyboardButton("لا ❌", callback_data="confirm_order_no"))
    
    bot.send_message(message.chat.id, f"📋 **ملخص الطلب:**\n▫️ الخدمة: {o_info['product_name']}\n▫️ السعر: {format_price(user_id, o_info['price'])}\n▫️ الآيدي: `{o_info['player_id']}`\n\n❓ **هل تريد إكمال طلبك؟**", parse_mode="Markdown", reply_markup=markup_conf)

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
