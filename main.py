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
CHANNEL_USERNAME = '@black1_bat_syria'

API_BASE = "https://mhd-game.com/api"
API_TOKEN = "Fluf9aJYBrtQ1a9ywuqrcMh2M4A8UIa8MKsgbyUk0PkYi301WuCqtLtGn4GO"
api_headers = {"api-token": API_TOKEN}

users_db = {}
total_orders_global = 142
exchange_rate = 15000  # سعر الصرف الافتراضي

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
        url = f"{API_BASE}/client/api/newOrder/{product_id}"
        params = {
            "qty": quantity,
            "playerId": player_id,
            "order_uuid": unique_order_uuid,
        }
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
            'balance': 10.0,
            'spent': 0.0,
            'orders': 0,
            'banned': False,
            'currency': 'USD'
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
    current_curr = users_db.get(user_id, {}).get('currency', 'USD')
    curr_btn_text = '💱 العملة: دولار ($)' if current_curr == 'USD' else '💱 العملة: ليرة سورية (ل.س)'

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('🛍 خدمات متجرنا')
    btn2 = types.KeyboardButton('👤 حسابك')
    btn3 = types.KeyboardButton('💳 تعبئة رصيد')
    btn_curr = types.KeyboardButton(curr_btn_text)
    btn4 = types.KeyboardButton(f'📊 الطلبات المنفذة: {total_orders_global}')
    
    if chat_id == ADMIN_ID:
        btn_admin = types.KeyboardButton('⚙️ لوحة تحكم الأدمن')
        markup.add(btn1)
        markup.add(btn2, btn3)
        markup.add(btn_curr, btn4)
        markup.add(btn_admin)
    else:
        markup.add(btn1)
        markup.add(btn2, btn3)
        markup.add(btn_curr, btn4)
    
    welcome_msg = (
        f"أهلاً بك {user_name} بمتجر BLACK BAT 📱\n"
        f"نشكرك على التعامل معنا 🤝\n"
        f"قم باختيار ماذا تريد من خدماتنا ⏬"
    )
    bot.send_message(chat_id, welcome_msg, reply_markup=markup)

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
    global exchange_rate, bot_is_active
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

    if user_id in pending_topup:
        state = pending_topup[user_id].get('state')
        if state == 'waiting_amount':
            pending_topup[user_id]['amount'] = message.text.strip()
            pending_topup[user_id]['state'] = 'waiting_operation_id'
            bot.reply_to(message, "ارسل رقم عملية التحويل ⏬")
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
            users_db[user_id] = {'name': message.from_user.first_name, 'balance': 0.0, 'spent': 0.0, 'orders': 0, 'banned': False, 'currency': 'USD'}
        current_curr = users_db[user_id]['currency']
        if current_curr == 'USD':
            users_db[user_id]['currency'] = 'SYP'
            bot.reply_to(message, "تم تغيير العملة إلى (الليرة السورية 🇸🇾).")
        else:
            users_db[user_id]['currency'] = 'USD'
            bot.reply_to(message, "تم تغيير العملة إلى (الدولار الأمريكي 💵).")
        show_main_menu(message.chat.id, message.from_user.first_name, user_id)
        return

    if message.text == '🛍 خدمات متجرنا':
        markup_cats = types.InlineKeyboardMarkup()
        for cat_name in store_categories.keys():
            markup_cats.add(types.InlineKeyboardButton(cat_name, callback_data=f"cat_{cat_name}"))
        bot.reply_to(message, "اختر القسم المطلوب لتصفح الخدمات والمنتجات ⏬", reply_markup=markup_cats)

    elif message.text == '👤 حسابك':
        u_data = users_db.get(user_id, {'name': message.from_user.first_name, 'balance': 0.0, 'spent': 0.0, 'orders': 0, 'currency': 'USD'})
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
            f"▫️ عدد طلباتك: {u_data['orders']}\n"
            f"▫️ العملة الحالية: {curr}"
        )
        markup_acc = types.InlineKeyboardMarkup()
        markup_acc.add(types.InlineKeyboardButton('💳 تعبئة رصيدك', callback_data='top_up_balance'))
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
    bot.reply_to(message, "💳 اختر طريقة تعبئة الرصيد المفضلة لديك:", reply_markup=markup_topup)

def show_admin_panel(message):
    global bot_is_active
    status_text = "🟢 حالة البوت: يعمل" if bot_is_active else "🔴 حالة البوت: متوقف"
    admin_text = f"⚙️ **لوحة تحكم الأدمن:**\n{status_text}\nسعر الصرف: {exchange_rate:,} ل.س"
    markup_admin = types.InlineKeyboardMarkup()
    markup_admin.add(types.InlineKeyboardButton('💱 تغيير سعر الصرف', callback_data='adm_exchange_rate'))
    bot.send_message(message.chat.id, admin_text, parse_mode='Markdown', reply_markup=markup_admin)

@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    global bot_is_active, exchange_rate
    data = call.data
    user_id = call.from_user.id
    
    if not bot_is_active and user_id != ADMIN_ID:
        return

    if data.startswith('cat_'):
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
            markup_prods.add(types.InlineKeyboardButton(f"{p['name']} - {formatted_p_price}", callback_data=f"buyprod_{p['id']}"))
        
        bot.send_message(call.message.chat.id, f"📦 منتجات {sub_name}:", reply_markup=markup_prods)
        return

    elif data.startswith('buyprod_'):
        prod_id = int(data.split('_')[1])
        selected_prod = None
        
        pubg_sub_cats = store_categories["🎮 شحن ألعاب"]["PUBG Mobile 🕹"]
        for sub_name, plist in pubg_sub_cats.items():
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
            bot.send_message(call.message.chat.id, "❌ عذراً، ليس لديك رصيد كافي لاتمام طلبك، قم بتعبئة رصيدك 💳")
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
            users_db[user_id]['orders'] += 1

            bot.answer_callback_query(call.id, "جاري إرسال الطلب للموقع...")
            response = create_mhd_order(product_id=p_id, quantity=1, player_id=player_id)

            if response and response.get("status") == "OK":
                bot.send_message(call.message.chat.id, "✅ تم تنفيذ طلبك بنجاح، شكرا للتعامل معنا 🤝")
            else:
                users_db[user_id]['balance'] += price
                users_db[user_id]['spent'] -= price
                users_db[user_id]['orders'] -= 1
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
            users_db[target_id] = {'name': 'مستخدم', 'balance': 0.0, 'spent': 0.0, 'orders': 0, 'banned': False, 'currency': 'USD'}
        users_db[target_id]['balance'] += amount
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
        parse_mode="Markdown",
        reply_markup=markup_conf
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
