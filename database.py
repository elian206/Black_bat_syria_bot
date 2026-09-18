import uuid
import requests

# إعدادات الأدمن والاتصال
ADMIN_ID = 8534087775
ADMIN_USERNAME = "black_bat_s"
CHANNEL_USERNAME = '@black1_bat_syria'

# 1. إعدادات الموقع الأول (MHD Game)
API_BASE_1 = "https://mhd-game.com/api"
API_TOKEN_1 = "Fluf9aJYBrtQ1a9ywuqrcMh2M4A8UIa8MKsgbyUk0PkYi301WuCqtLtGn4GO"
api_headers_1 = {"api-token": API_TOKEN_1}

# 2. إعدادات الموقع الثاني (Trendz Brand - SMM API v2)
API_BASE_2 = "https://follow-syria.top/api/v2"
API_TOKEN_2 = "fbb2baeb684627bac22a10b1ba0c9469"

# قواعد البيانات وأرصدة العملاء والسجلات
users_db = {}
total_orders_global = 0  
exchange_rate = 15000  

def format_price(user_id, price_in_usd):
    curr = users_db.get(user_id, {}).get('currency', 'USD')
    if curr == 'SYP':
        syp_amount = price_in_usd * exchange_rate
        return f"{syp_amount:,.0f} ل.س"
    else:
        return f"${price_in_usd}"

# دوال الموقع الأول (MHD)
def create_mhd_order(product_id, quantity, player_id):
    try:
        unique_order_uuid = str(uuid.uuid4())
        url = f"{API_BASE_1}/client/api/newOrder/{product_id}/params"
        params = {"qty": quantity, "playerId": player_id, "order_uuid": unique_order_uuid}
        response = requests.get(url, headers=api_headers_1, params=params)
        res_json = response.json()
        res_json['order_uuid'] = unique_order_uuid
        return res_json
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}

def create_mhd_code_order(product_id, quantity=1):
    try:
        unique_order_uuid = str(uuid.uuid4())
        url = f"{API_BASE_1}/client/api/newOrder/{product_id}/params"
        params = {"qty": quantity, "order_uuid": unique_order_uuid}
        response = requests.get(url, headers=api_headers_1, params=params)
        res_json = response.json()
        res_json['order_uuid'] = unique_order_uuid
        return res_json
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}

def check_mhd_order_status(order_uuid):
    try:
        url = f"{API_BASE_1}/client/api/orderStatus"
        params = {"order_uuid": order_uuid}
        response = requests.get(url, headers=api_headers_1, params=params)
        return response.json()
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}

# دوال الموقع الثاني (Trendz Brand - SMM API v2)
def create_trendz_order(service_id, link, quantity):
    try:
        data = {
            "key": API_TOKEN_2,
            "action": "add",
            "service": service_id,
            "link": link,
            "quantity": quantity
        }
        response = requests.post(API_BASE_2, data=data)
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def check_trendz_order_status(order_id):
    try:
        data = {
            "key": API_TOKEN_2,
            "action": "status",
            "order": order_id
        }
        response = requests.post(API_BASE_2, data=data)
        return response.json()
    except Exception as e:
        return {"error": str(e)}
