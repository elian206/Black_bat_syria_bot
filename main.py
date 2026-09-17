import telebot
from telebot import types
from flask import Flask
from threading import Thread

TOKEN = '8909052904:AAHEsWa85CbV5Kwxs4Y1kG7h7TMtHpx-TMw'
bot = telebot.TeleBot(TOKEN)

try:
    bot.remove_webhook()
except Exception:
    pass

ADMIN_ID = 8534087775
CHANNEL_USERNAME = '@black1_bat_syria'

users_db = {}
total_orders_global = 142
exchange_rate = 15000

# قاموس مؤقت لحفظ حالات تعبئة الرصيد للمستخدمين
pending_topup = {}

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
    user_id = message.from_user.id
    
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
    user_id = call.from_user.id
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
    user_id = message.from_user.id
    
    if user_id in users_db and users_db[user_id]['banned']:
        return

    # معالجة إدخال المبلغ ورقم العملية لعملية التعبئة
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
            
            # إرسال رسالة للمستخدم
            bot.reply_to(message, "تم استلام طلب تعبئة رصيدك ستوافق عليها الإدارة ✅")
            
            # إرسال إشعار للأدمن مع زري الموافقة والرفض
            admin_msg = (
                f"📌 طلب تعبئة رصيد جديد:\n\n"
                f"📌 اسم المستخدم: {u_name}\n"
                f"📌 ايدي الحساب: `{user_id}`\n"
                f"📌 المبلغ: {amount}\n"
                f"📌 رقم العملية: {op_id}"
            )
            
            markup_admin_approval = types.InlineKeyboardMarkup()
            # نخزن في الـ callback_data ايدي المستخدم والمبلغ لتسهيل إعطاء الرصيد
            markup_admin_approval.add(
                types.InlineKeyboardButton('✅ موافق', callback_data=f'approve_topup_{user_id}_{amount}'),
                types.InlineKeyboardButton('❌ غير موافق', callback_data=f'reject_topup_{user_id}')
            )
            
            bot.send_message(ADMIN_ID, admin_msg, parse_mode='Markdown', reply_markup=markup_admin_approval)
            
            # حذف الحالة المؤقتة
            del pending_topup[user_id]
            return

    if '💱 العملة:' in message.text:
        if user_id not in users_db:
            users_db[user_id] = {'name': message.from_user.first_name, 'balance': 0.0, 'spent': 0.0, 'orders': 0, 'banned': False, 'currency': 'USD'}
        
        current_curr = users_db[user_id]['currency']
        if current_curr == 'USD':
            users_db[user_id]['currency'] = 'SYP'
            bot.reply_to(message, "تم تغيير العملة بنجاح إلى (الليرة السورية 🇸🇾). ستظهر الأسعار والرصيد بناءً على سعر الصرف الحالي.")
        else:
            users_db[user_id]['currency'] = 'USD'
            bot.reply_to(message, "تم تغيير العملة بنجاح إلى (الدولار الأمريكي 💵).")
        
        show_main_menu(message.chat.id, message.from_user.first_name, user_id)
        return

    if message.text == '🛍 خدمات متجرنا':
        markup_services = types.InlineKeyboardMarkup()
        markup_services.add(types.InlineKeyboardButton('🕹 شحن ألعاب', callback_data='service_games'))
        markup_services.add(types.InlineKeyboardButton('📱 شحن تطبيقات', callback_data='service_apps'))
        markup_services.add(types.InlineKeyboardButton('🤳 دعم حسابات', callback_data='service_support'))
        markup_services.add(types.InlineKeyboardButton('📲 بيع حسابات', callback_data='service_accounts'))
        
        bot.reply_to(message, "اهلا بك في خدماتنا، نتمنا ان تعجبك.\nاختر الخدمة التي تريدها ⏬", reply_markup=markup_services)

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
    markup_topup.add(types.InlineKeyboardButton('🟩 Sham Cash', callback_data='pay_sham'))
    markup_topup.add(types.InlineKeyboardButton('🟥 Syriatel Cash', callback_data='pay_syriatel'))
    markup_topup.add(types.InlineKeyboardButton('🟨 MTN Cash', callback_data='pay_mtn'))
    
    bot.reply_to(message, "💳 اختر طريقة تعبئة الرصيد المفضلة لديك:", reply_markup=markup_topup)

def show_admin_panel(message):
    admin_text = f"⚙️ **لوحة تحكم الأدمن الرئيسية:**\nسعر الصرف الحالي: {exchange_rate} ل.س لكل 1$\nاختر العملية المطلوبة:"
    markup_admin = types.InlineKeyboardMarkup()
    markup_admin.add(types.InlineKeyboardButton('➕ اضافة رصيد يدوي', callback_data='adm_add_balance'))
    markup_admin.add(types.InlineKeyboardButton('➖ خصم رصيد يدوي', callback_data='adm_sub_balance'))
    markup_admin.add(types.InlineKeyboardButton('➕ اضافة أزرار', callback_data='adm_add_btn'))
    markup_admin.add(types.InlineKeyboardButton('❌ حذف أزرار', callback_data='adm_del_btn'))
    markup_admin.add(types.InlineKeyboardButton('💳 طرق التعبئة', callback_data='adm_pay_methods'))
    markup_admin.add(types.InlineKeyboardButton('👥 سجل جميع العملاء', callback_data='adm_users_list'))
    markup_admin.add(types.InlineKeyboardButton('👑 إضافة أدمن', callback_data='adm_add_admin'))
    markup_admin.add(types.InlineKeyboardButton('🔗 تغيير ربط المواقع', callback_data='adm_change_link'))
    markup_admin.add(types.InlineKeyboardButton('📢 رسالة للجميع', callback_data='adm_broadcast'))
    markup_admin.add(types.InlineKeyboardButton('💱 تغيير سعر الصرف', callback_data='adm_exchange_rate'))
    markup_admin.add(types.InlineKeyboardButton('🚫 حظر مستخدم', callback_data='adm_ban'))
    markup_admin.add(types.InlineKeyboardButton('✅ فك الحظر', callback_data='adm_unban'))
    
    bot.send_message(message.chat.id, admin_text, parse_mode='Markdown', reply_markup=markup_admin)

@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    data = call.data
    user_id = call.from_user.id
    
    if data == 'pay_sham':
        bot.answer_callback_query(call.id)
        sham_msg = (
            f"تحويل Sham Cash ليرة سورية 💵\n"
            f"كل 1$ = {exchange_rate:,} ل.س\n"
            f"اقل مبلغ للتعبئة هو: 1دولار💲\n"
            f"قم بالتحويل على هذا الحساب ⏬\n"
            f"ebae7d2aa7d10e62f02b1199d87208f4\n"
            f"اسم الحساب: جورج عيسى بركات."
        )
        bot.send_message(call.message.chat.id, sham_msg)
        # تفعيل حالة انتظار المبلغ من العميل
        pending_topup[user_id] = {'state': 'waiting_amount'}
        bot.send_message(call.message.chat.id, "ادخل المبلغ الذي أرسلته ⏬")

    elif data.startswith('approve_topup_'):
        if user_id != ADMIN_ID:
            bot.answer_callback_query(call.id, "هذا الزر للأدمن فقط!", show_alert=True)
            return
            
        parts = data.split('_')
        target_user_id = int(parts[2])
        amount_str = parts[3]
        
        # محاولة استخراج رقم أو قيمة لإضافتها للرصيد
        try:
            # استخراج الأرقام من نص المبلغ لو وُجدت رموز مثل $ أو ل.س
            import re
            numbers = re.findall(r'\d+\.?\d*', amount_str)
            added_amount = float(numbers[0]) if numbers else 0.0
        except Exception:
            added_amount = 0.0

        # تحديث رصيد المستخدم
        if target_user_id in users_db:
            users_db[target_user_id]['balance'] += added_amount
            total_bal = users_db[target_user_id]['balance']
        else:
            # افتراض بيانات أولية لو لم يكن مسجلاً بقاموس البيانات
            users_db[target_user_id] = {'name': 'مستخدم', 'balance': added_amount, 'spent': 0.0, 'orders': 0, 'banned': False, 'currency': 'USD'}
            total_bal = added_amount

        bot.answer_callback_query(call.id, "تمت الموافقة وإضافة الرصيد بنجاح!")
        bot.edit_message_text(f"{call.message.text}\n\n✅ **الحالة:** تم قبول الطلب من قبل الأدمن.", chat_id=call.message.chat.id, message_id=call.message.message_id, parse_mode='Markdown')
        
        # إرسال رسالة للعميل
        try:
            client_msg = (
                f"تم اضافة المبلغ: {amount_str}\n"
                f"رصيدك الان: {total_bal} $\n"
                f"استمتع بطلب من خدماتنا"
            )
            bot.send_message(target_user_id, client_msg)
        except Exception:
            pass

    elif data.startswith('reject_topup_'):
        if user_id != ADMIN_ID:
            bot.answer_callback_query(call.id, "هذا الزر للأدمن فقط!", show_alert=True)
            return
            
        parts = data.split('_')
        target_user_id = int(parts[2])
        
        bot.answer_callback_query(call.id, "تم رفض الطلب.")
        bot.edit_message_text(f"{call.message.text}\n\n❌ **الحالة:** تم رفض الطلب.", chat_id=call.message.chat.id, message_id=call.message.message_id, parse_mode='Markdown')
        
        try:
            bot.send_message(target_user_id, "عذراً، تم رفض طلب تعبئة الرصيد من قبل الإدارة. يرجى التأكد من معلومات التحويل.")
        except Exception:
            pass

    elif data.startswith('service_'):
        service_names = {
            'service_games': 'شحن ألعاب 🕹',
            'service_apps': 'شحن تطبيقات 📱',
            'service_support': 'دعم حسابات 🤳',
            'service_accounts': 'بيع حسابات 📲'
        }
        bot.answer_callback_query(call.id, f"تم اختيار: {service_names.get(data)}")
        bot.send_message(call.message.chat.id, f"لقد اخترت قسم ({service_names.get(data)}). يمكنك إتمام الطلب عبر التواصل مع الإدارة.")

    elif data in ['pay_syriatel', 'pay_mtn']:
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, "هذه الطريقة قيد المفعيل قريباً.")

    elif data == 'top_up_balance':
        show_topup_methods(call.message)

    elif data.startswith('adm_'):
        if user_id != ADMIN_ID:
            bot.answer_callback_query(call.id, "هذا الزر مخصص للأدمن فقط!", show_alert=True)
            return
        
        actions_map = {
            'adm_add_balance': "أرسل المعرف والآيدي والمبلغ لإضافة الرصيد يدويًا.",
            'adm_sub_balance': "أرسل المعرف والآيدي والمبلغ لخصم الرصيد يدويًا.",
            'adm_add_btn': "أدخل تفاصيل الزر الجديد المراد إضافته.",
            'adm_del_btn': "اختر الزر المراد حذفه من القوائم.",
            'adm_pay_methods': "إدارة وتعديل طرق تعبئة الرصيد المتاحة.",
            'adm_users_list': f"📊 إجمالي العملاء المسجلين: {len(users_db)} مستخدم.",
            'adm_add_admin': "أرسل آيدي المستخدم الجديد لتعيينه كأدمن.",
            'adm_change_link': "أرسل رابط الموقع أو المنصة البديل للربط.",
            'adm_broadcast': "أرسل النص المراد بثه وإرساله لجميع العملاء داخل البوت.",
            'adm_exchange_rate': f"سعر الصرف الحالي هو: {exchange_rate} ل.س.",
            'adm_ban': "أرسل آيدي المستخدم المراد حظره.",
            'adm_unban': "أرسل آيدي المستخدم المراد فك الحظر عنه."
        }
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, f"🛠 [لوحة التحكم]:\n{actions_map.get(data, 'جاري التنفيذ...')}")

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
