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
API_TOKEN = "fluf9aJYBrtQ1a9yuuqrcMh2M4A8Ui8MKsgbyUk0PkYi301WuCqtLtGn4GO"
api_headers = {"api-token": API_TOKEN}

users_db = {}
total_orders_global = 142
exchange_rate = 15000

# الأقسام الأساسية والمنتجات المضافة من قبل الأدمن
store_categories = {
    "🎮 شحن العاب": [],
    "📱 شحن تطبيقات": [],
    "🛡 دعم حسابات": []
}

pending_topup = {}
admin_states = {}
user_temp_order = {}
bot_is_active = True

def get_mhd_products():
    try:
        url = f"{API_BASE}/client/api/products"
        response = requests.get(url, headers=api_headers)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"Error fetching products: {e}")
    return None

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
            'spent': 2.0,
            'orders': 1,
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
                    new_rate = int(''.join(numbers))
                    exchange_rate = new_rate
                    admin_states.clear()
                    bot.reply_to(message, f"✅ تم تحديث سعر الصرف بنجاح!\nسعر الصرف الجديد: {exchange_rate:,} ل.س لكل 1$")
                    show_admin_panel(message)
                    return
            except Exception:
                pass
            bot.reply_to(message, "⚠️ يرجى إرسال رقم صحيح لسعر الصرف.")
            return

        elif admin_st == 'waiting_add_id':
            text = message.text.strip()
            try:
                target_id = int(text)
                admin_states['target_id'] = target_id
                admin_states['state'] = 'waiting_add_amount'
                bot.reply_to(message, "ارسل المبلغ المراد إضافته ⏬")
                return
            except Exception:
                bot.reply_to(message, "⚠️ يرجى إرسال ايدي (ID) صحيح كأرقام.")
                return

        elif admin_st == 'waiting_add_amount':
            text = message.text.strip()
            try:
                numbers = re.findall(r'\d+\.?\d*', text)
                amount = float(numbers[0]) if numbers else 0.0
                target_id = admin_states.get('target_id')
                
                if target_id not in users_db:
                    users_db[target_id] = {'name': 'مستخدم', 'balance': 0.0, 'spent': 0.0, 'orders': 0, 'banned': False, 'currency': 'USD'}
                
                users_db[target_id]['balance'] += amount
                current_bal = users_db[target_id]['balance']
                
                admin_states.clear()
                bot.reply_to(message, f"✅ تمت إضافة المبلغ ({amount}) بنجاح للمستخدم `{target_id}`.\nرصيده الحالي: {current_bal}", parse_mode='Markdown')
                
                try:
                    bot.send_message(target_id, f"تم اضافة المبلغ: {amount}\nرصيدك الحالي: {current_bal}\nاستمتع بطلب من خدماتنا")
                except Exception:
                    pass
                
                show_admin_panel(message)
                return
            except Exception:
                bot.reply_to(message, "⚠️ يرجى إرسال مبلغ صحيح.")
                return

        elif admin_st == 'waiting_sub_id':
            text = message.text.strip()
            try:
                target_id = int(text)
                admin_states['target_id'] = target_id
                admin_states['state'] = 'waiting_sub_amount'
                bot.reply_to(message, "ارسل المبلغ المراد خصمه ⏬")
                return
            except Exception:
                bot.reply_to(message, "⚠️ يرجى إرسال ايدي (ID) صحيح كأرقام.")
                return

        elif admin_st == 'waiting_sub_amount':
            text = message.text.strip()
            try:
                numbers = re.findall(r'\d+\.?\d*', text)
                amount = float(numbers[0]) if numbers else 0.0
                target_id = admin_states.get('target_id')
                
                if target_id not in users_db:
                    users_db[target_id] = {'name': 'مستخدم', 'balance': 0.0, 'spent': 0.0, 'orders': 0, 'banned': False, 'currency': 'USD'}
                
                users_db[target_id]['balance'] -= amount
                current_bal = users_db[target_id]['balance']
                
                admin_states.clear()
                bot.reply_to(message, f"✅ تم خصم المبلغ ({amount}) بنجاح من المستخدم `{target_id}`.\nرصيده الحالي: {current_bal}", parse_mode='Markdown')
                
                try:
                    bot.send_message(target_id, f"تم خصم مبلغ {amount} من رصيدك.\nرصيدك الحالي: {current_bal}")
                except Exception:
                    pass
                
                show_admin_panel(message)
                return
            except Exception:
                bot.reply_to(message, "⚠️ يرجى إرسال مبلغ صحيح.")
                return

        elif admin_st == 'waiting_product_details':
            text = message.text.strip()
            parts = [p.strip() for p in text.split('|')]
            if len(parts) == 3:
                try:
                    p_id = int(parts[0])
                    p_name = parts[1]
                    p_price = float(parts[2])
                    cat_name = admin_states.get('target_category')
                    
                    if cat_name in store_categories:
                        store_categories[cat_name].append({
                            'id': p_id,
                            'name': p_name,
                            'price': p_price,
                            'available': True
                        })
                        admin_states.clear()
                        bot.reply_to(message, f"✅ تم إضافة المنتج بنجاح إلى قسم ({cat_name})!")
                        show_admin_panel(message)
                        return
                except Exception:
                    pass
            bot.reply_to(message, "⚠️ الصيغة غير صحيحة. يرجى الإرسال بهذا الشكل تماماً:\n`ID_المنتج | اسم المنتج | السعر`\nمثال:\n`105 | ببجي موبايل - 60 شدة | 1.2`", parse_mode='Markdown')
            return

    if user_id in pending_topup:
        state = pending_topup[user_id].get('state')
        
        if state == 'waiting_amount':
            amount_text = message.text.strip()
            pending_topup[user_id]['amount'] = amount_text
            pending_topup[user_id]['state'] = 'waiting_operation_id'
            bot.reply_to(message, "ارسل رقم عملية التحويل ⏬")
            return
            
        elif state == 'waiting_operation_id':
            op_id = message.text.strip()
            pending_topup[user_id]['op_id'] = op_id
            
            u_name = users_db.get(user_id, {}).get('name', message.from_user.first_name)
            amount = pending_topup[user_id]['amount']
            curr_type = pending_topup[user_id]['curr_type']
            method_key = pending_topup[user_id]['method_key']
            method_name = pending_topup[user_id]['method_name']
            
            bot.reply_to(message, "تم استلام طلب تعبئة رصيدك ستوافق عليها الإدارة ✅")
            
            admin_msg = (
                f"📌 طلب تعبئة رصيد جديد ({method_name}):\n\n"
                f"📌 اسم المستخدم: {u_name}\n"
                f"📌 ايدي حسابه التلغرام: `{user_id}`\n"
                f"📌 مبلغ: {amount} {'$' if curr_type=='USD' else 'ل.س'}\n"
                f"📌 رقم العملية: {op_id}"
            )
            
            markup_admin_approval = types.InlineKeyboardMarkup()
            markup_admin_approval.add(
                types.InlineKeyboardButton('✅ موافق', callback_data=f'approve_topup_{user_id}_{amount}_{curr_type}_{method_key}'),
                types.InlineKeyboardButton('❌ غير موافق', callback_data=f'reject_topup_{user_id}')
            )
            
            bot.send_message(ADMIN_ID, admin_msg, parse_mode='Markdown', reply_markup=markup_admin_approval)
            del pending_topup[user_id]
            return

    if '💱 العملة:' in message.text:
        if user_id not in users_db:
            users_db[user_id] = {'name': message.from_user.first_name, 'balance': 0.0, 'spent': 0.0, 'orders': 0, 'banned': False, 'currency': 'USD'}
        
        current_curr = users_db[user_id]['currency']
        if current_curr == 'USD':
            users_db[user_id]['currency'] = 'SYP'
            bot.reply_to(message, "تم تغيير العملة بنجاح إلى (الليرة السورية 🇸🇾).")
        else:
            users_db[user_id]['currency'] = 'USD'
            bot.reply_to(message, "تم تغيير العملة بنجاح إلى (الدولار الأمريكي 💵).")
        
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
        
        markup_account = types.InlineKeyboardMarkup()
        markup_account.add(types.InlineKeyboardButton('💳 تعبئة رصيدك', callback_data='top_up_balance'))
        bot.reply_to(message, account_info, parse_mode='Markdown', reply_markup=markup_account)

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
    status_text = "🟢 حالة البوت: يعمل" if bot_is_active else "🔴 حالة البوت: متوقف (مطفأ)"
    toggle_btn_text = "🔴 إطفاء البوت" if bot_is_active else "🟢 تشغيل البوت"
    
    admin_text = f"⚙️ **لوحة تحكم الأدمن الرئيسية:**\n{status_text}\nسعر الصرف الحالي: {exchange_rate:,} ل.س لكل 1$\nاختر العملية المطلوبة:"
    
    markup_admin = types.InlineKeyboardMarkup()
    markup_admin.add(types.InlineKeyboardButton(toggle_btn_text, callback_data='adm_toggle_bot'))
    markup_admin.add(types.InlineKeyboardButton('🌐 منتجات موقع MHD API', callback_data='cat_api_products'))
    markup_admin.add(types.InlineKeyboardButton('➕ اضافة منتج داخل قسم', callback_data='adm_add_product'))
    markup_admin.add(types.InlineKeyboardButton('➕ اضافة رصيد يدوي', callback_data='adm_add_balance'))
    markup_admin.add(types.InlineKeyboardButton('➖ خصم رصيد يدوي', callback_data='adm_sub_balance'))
    markup_admin.add(types.InlineKeyboardButton('💱 تغيير سعر الصرف', callback_data='adm_exchange_rate'))
    
    bot.send_message(message.chat.id, admin_text, parse_mode='Markdown', reply_markup=markup_admin)

@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    global bot_is_active, exchange_rate
    data = call.data
    user_id = call.from_user.id
    
    if not bot_is_active and user_id != ADMIN_ID:
        return

    if data == 'cat_api_products':
        if user_id != ADMIN_ID:
            bot.answer_callback_query(call.id, "هذا الزر مخصص للأدمن فقط!", show_alert=True)
            return
        products = get_mhd_products()
        if not products:
            bot.answer_callback_query(call.id, "عذراً، لا توجد منتجات متاحة حالياً عبر الـ API.", show_alert=True)
            return
        
        markup_prods = types.InlineKeyboardMarkup()
        for p in products[:25]:
            markup_prods.add(types.InlineKeyboardButton(f"{p['name']} - ${p['price']} (ID: {p['id']})", callback_data=f"buy_{p['id']}"))
        
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, "🌐 جميع خدمات ومنتجات موقع MHD API المتاحة (مع المعرفات والأسعار):", reply_markup=markup_prods)
        return

    if data.startswith('cat_'):
        cat_key = data.replace('cat_', '')
        bot.answer_callback_query(call.id)
        
        if cat_key in store_categories:
            prods = store_categories[cat_key]
            if not prods:
                bot.send_message(call.message.chat.id, f"عذراً، لا توجد منتجات مضافة حالياً في قسم ({cat_key}). يرجى إضافتها من لوحة الأدمن.")
                return
            
            markup_prods = types.InlineKeyboardMarkup()
            curr = users_db.get(user_id, {}).get('currency', 'USD')
            for p in prods:
                p_price = p['price']
                if curr == 'SYP':
                    price_display = f"{p_price * exchange_rate:,.0f} ل.س"
                else:
                    price_display = f"${p_price}"
                markup_prods.add(types.InlineKeyboardButton(f"{p['name']} ({price_display})", callback_data=f"buy_{p['id']}"))
            
            bot.send_message(call.message.chat.id, f"📁 منتجات قسم ({cat_key}):", reply_markup=markup_prods)
        return

    if data == 'pay_sham_usd':
        bot.answer_callback_query(call.id)
        sham_msg = (
            f"تحويل Sham Cash (دولار 💵)\n"
            f"قم بالتحويل على حساب Sham Cash التالي ⏬\n"
            f"ebae7d2aa7d10e62f02b1199d87208f4\n"
            f"اسم الحساب: جورج عيسى بركات."
        )
        bot.send_message(call.message.chat.id, sham_msg)
        pending_topup[user_id] = {'state': 'waiting_amount', 'curr_type': 'USD', 'method_key': 'sham_usd', 'method_name': 'Sham Cash (USD)'}
        bot.send_message(call.message.chat.id, "ادخل مبلغ الدولار الذي أرسلته (مثال: 5) ⏬")

    elif data == 'pay_sham_syp':
        bot.answer_callback_query(call.id)
        sham_msg = (
            f"تحويل Sham Cash (ليرة سورية 🇸🇾)\n"
            f"قم بالتحويل على حساب Sham Cash التالي ⏬\n"
            f"ebae7d2aa7d10e62f02b1199d87208f4\n"
            f"اسم الحساب: جورج عيسى بركات."
        )
        bot.send_message(call.message.chat.id, sham_msg)
        pending_topup[user_id] = {'state': 'waiting_amount', 'curr_type': 'SYP', 'method_key': 'sham_syp', 'method_name': 'Sham Cash (SYP)'}
        bot.send_message(call.message.chat.id, "ادخل المبلغ الذي ارسلته ⏬")

    elif data == 'pay_syriatel':
        bot.answer_callback_query(call.id)
        syriatel_msg = (
            f"تحويل Syriatel Cash ليرة سورية 🇸🇾\n"
            f"كل 1$ = {exchange_rate:,} ل.س\n\n"
            f"كود تحويل ⏪ 92189062 \n"
            f"⚠️ التحويل حصرا من خيار (تحويل يدوي)."
        )
        bot.send_message(call.message.chat.id, syriatel_msg)
        pending_topup[user_id] = {'state': 'waiting_amount', 'curr_type': 'SYP', 'method_key': 'syriatel', 'method_name': 'Syriatel Cash'}
        bot.send_message(call.message.chat.id, "ادخل المبلغ الذي ارسلته ⏬")

    elif data == 'pay_mtn':
        bot.answer_callback_query(call.id)
        mtn_msg = (
            f"تحويل MTN Cash ليرة سورية 🇸🇾\n"
            f"كل 1$ = {exchange_rate:,} ل.س\n\n"
            f"كود تحويل ⏬\n 8338 3112 0672 4992"
        )
        bot.send_message(call.message.chat.id, mtn_msg)
        pending_topup[user_id] = {'state': 'waiting_amount', 'curr_type': 'SYP', 'method_key': 'mtn', 'method_name': 'MTN Cash'}
        bot.send_message(call.message.chat.id, "ادخل المبلغ الذي ارسلته ⏬")

    elif data.startswith('approve_topup_'):
        if user_id != ADMIN_ID:
            bot.answer_callback_query(call.id, "هذا الزر للأدمن فقط!", show_alert=True)
            return
            
        parts = data.split('_')
        target_user_id = int(parts[2])
        amount_str = parts[3]
        curr_type = parts[4] if len(parts) > 4 else 'USD'
        method_key = parts[5] if len(parts) > 5 else ''
        
        try:
            numbers = re.findall(r'\d+\.?\d*', amount_str)
            raw_amount = float(numbers[0]) if numbers else 0.0
        except Exception:
            raw_amount = 0.0

        final_amount_to_process = raw_amount
        if method_key == 'syriatel':
            final_amount_to_process = raw_amount * 0.95
        elif method_key == 'mtn':
            final_amount_to_process = raw_amount * 0.92

        if curr_type == 'SYP':
            added_usd = final_amount_to_process / exchange_rate
        else:
            added_usd = final_amount_to_process

        if target_user_id not in users_db:
            users_db[target_user_id] = {'name': 'مستخدم', 'balance': 0.0, 'spent': 0.0, 'orders': 0, 'banned': False, 'currency': 'USD'}

        users_db[target_user_id]['balance'] += added_usd
        total_bal = users_db[target_user_id]['balance']
        
        user_curr = users_db[target_user_id].get('currency', 'USD')
        if user_curr == 'SYP':
            disp_bal = f"{total_bal * exchange_rate:,.0f} ل.س"
        else:
            disp_bal = f"{total_bal} $"

        bot.answer_callback_query(call.id, "تمت الموافقة وإضافة الرصيد بنجاح!")
        bot.edit_message_text(f"{call.message.text}\n\n✅ **الحالة:** تم قبول الطلب وإضافة ما يعادل ({added_usd:.2f} $) بنجاح.", chat_id=call.message.chat.id, message_id=call.message.message_id, parse_mode='Markdown')
        
        try:
            bot.send_message(target_user_id, f"تم اضافة المبلغ برصيدك الان {disp_bal}\nاستمتع بطلب من خدماتنا")
        except Exception:
            pass

    elif data.startswith('reject_topup_'):
        if user_id != ADMIN_ID:
            bot.answer_callback_query(call.id, "هذا الزر للأدمن فقط!", show_alert=True)
            return
        parts = data.split('_')
        target_user_id = int(parts[2])
        bot.answer_callback_query(call.id, "تم رفض الطلب.")
        bot.edit_message_text(f"{call.message.text}\n\n❌ **الحالة:** تم رفض الطلب من قبل الإدارة.", chat_id=call.message.chat.id, message_id=call.message.message_id, parse_mode='Markdown')
        try:
            bot.send_message(target_user_id, "عذراً، تم رفض طلب تعبئة الرصيد من قبل الإدارة.")
        except Exception:
            pass

    elif data.startswith('buy_'):
        product_id = int(data.split('_')[1])
        
        selected_product = None
        for cat_list in store_categories.values():
            for p in cat_list:
                if p['id'] == product_id:
                    selected_product = p
                    break
            if selected_product:
                break
        
        if not selected_product:
            api_prods = get_mhd_products()
            if api_prods:
                for p in api_prods:
                    if p['id'] == product_id:
                        selected_product = p
                        break

        if not selected_product:
            bot.answer_callback_query(call.id, "المنتج غير موجود أو غير متوفر.")
            return

        user_balance = users_db.get(user_id, {}).get('balance', 0.0)
        product_price_usd = selected_product['price']

        if user_balance < product_price_usd:
            bot.answer_callback_query(call.id, "رصيدك غير كافٍ لإتمام هذه العملية!", show_alert=True)
            return

        user_temp_order[user_id] = {
            "product_id": selected_product['id'],
            "product_name": selected_product['name'],
            "price": product_price_usd
        }

        bot.answer_callback_query(call.id)
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=f"لقد اخترت: *{selected_product['name']}*\nالسعر: ${product_price_usd}\n\nالرجاء إرسال **آيدي اللاعب (Player ID)** أو المعلومات المطلوبة للشحن الآن في رسالة:",
            parse_mode="Markdown"
        )
        bot.register_next_step_handler(call.message, process_player_id)

    elif data == 'top_up_balance':
        show_topup_methods(call.message)

    elif data.startswith('adm_'):
        if user_id != ADMIN_ID:
            bot.answer_callback_query(call.id, "هذا الزر مخصص للأدمن فقط!", show_alert=True)
            return
        
        if data == 'adm_toggle_bot':
            bot_is_active = not bot_is_active
            status_word = "تشغيل" if bot_is_active else "إطفاء"
            bot.answer_callback_query(call.id, f"تم {status_word} البوت بنجاح!")
            try:
                bot.delete_message(call.message.chat.id, call.message.message_id)
            except Exception:
                pass
            show_admin_panel(call.message)
            return

        if data == 'adm_exchange_rate':
            admin_states['state'] = 'waiting_new_rate'
            bot.answer_callback_query(call.id)
            bot.send_message(call.message.chat.id, f"💱 سعر الصرف الحالي هو: {exchange_rate:,} ل.س.\n\nأرسل سعر الصرف الجديد الآن كأرقام فقط ⏬")
            return
            
        elif data == 'adm_add_balance':
            admin_states['state'] = 'waiting_add_id'
            bot.answer_callback_query(call.id)
            bot.send_message(call.message.chat.id, "أرسل ايدي (ID) العميل المراد إضافة الرصيد له ⏬")
            return
            
        elif data == 'adm_sub_balance':
            admin_states['state'] = 'waiting_sub_id'
            bot.answer_callback_query(call.id)
            bot.send_message(call.message.chat.id, "أرسل ايدي (ID) العميل المراد خصم الرصيد منه ⏬")
            return

        elif data == 'adm_add_product':
            bot.answer_callback_query(call.id)
            markup_cat_select = types.InlineKeyboardMarkup()
            for cat_name in store_categories.keys():
                markup_cat_select.add(types.InlineKeyboardButton(cat_name, callback_data=f"selectcat_{cat_name}"))
            bot.send_message(call.message.chat.id, "اختر القسم الذي تريد إضافة المنتج إليه ⏬", reply_markup=markup_cat_select)
            return

    elif data.startswith('selectcat_'):
        if user_id != ADMIN_ID:
            return
        cat_name = data.replace('selectcat_', '')
        admin_states['target_category'] = cat_name
        admin_states['state'] = 'waiting_product_details'
        bot.answer_callback_query(call.id)
        bot.send_message(
            call.message.chat.id,
            f"لقد اخترت قسم: **{cat_name}**\n\nالآن أرسل تفاصيل المنتج بهذا الشكل تماماً:\n`ID_المنتج | اسم المنتج | السعر بالدولار`\n\nمثال:\n`105 | ببجي موبايل - 60 شدة | 1.2`\n\n*(يمكنك معرفة ID المنتج والسعر بدقة من زر 'منتجات موقع MHD API' في لوحة الأدمن)*",
            parse_mode='Markdown'
        )

def process_player_id(message):
    user_id = message.from_user.id
    player_id = message.text.strip()

    if user_id not in user_temp_order:
        bot.send_message(message.chat.id, "انتهت الجلسة أو حدث خطأ. الرجاء البدء من جديد.")
        return

    order_info = user_temp_order[user_id]
    product_id = order_info['product_id']
    price = order_info['price']
    product_name = order_info['product_name']

    users_db[user_id]['balance'] -= price
    users_db[user_id]['spent'] += price
    users_db[user_id]['orders'] += 1

    wait_msg = bot.send_message(message.chat.id, "⏳ جاري إرسال طلبك إلى موقع الخدمات الرقمية ومعالجته...")

    response = create_mhd_order(product_id=product_id, quantity=1, player_id=player_id)

    try:
        bot.delete_message(message.chat.id, wait_msg.message_id)
    except Exception:
        pass

    if response and response.get("status") == "OK":
        data = response.get("data", {})
        order_status = data.get("status", "wait")
        replay_api = data.get("replay_api")

        success_text = (
            f"✅ **تم إرسال الطلب بنجاح!**\n\n"
            f"📦 المنتج: {product_name}\n"
            f"🆔 الآيدي: {player_id}\n"
            f"🔖 حالة الطلب بالموقع: `{order_status}`\n"
        )

        if replay_api:
            success_text += f"\n🔑 **معلومات التسليم:**\n`{replay_api}`"

        bot.send_message(message.chat.id, success_text, parse_mode="Markdown")
    else:
        users_db[user_id]['balance'] += price
        users_db[user_id]['spent'] -= price
        users_db[user_id]['orders'] -= 1
        
        err_msg = response.get("message", "خطأ غير معروف") if response else "فشل الاتصال بالموقع"
        bot.send_message(message.chat.id, f"❌ **فشل تنفيذ الطلب من الموقع:**\n{err_msg}\n\n💰 تم إرجاع المبلغ إلى رصيدك.", parse_mode="Markdown")

    del user_temp_order[user_id]

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
