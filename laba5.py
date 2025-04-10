import json
import requests

API_KEY = ""
HEADERS = {"X-API-Key": API_KEY}
FILENAME = "orders_data.json"

def read_orders():
    with open(FILENAME, "r") as f:
        return json.load(f)

def write_orders(data):
    with open(FILENAME, "w") as f:
        json.dump(data, f, indent=4)

def check_and_update_orders():
    orders = read_orders()
    updated_orders = []

    for order in orders:
        order_id = order["orderID"]
        url = f"https://api.ataix.kz/api/orders/{order_id}"
        response = requests.get(url, headers=HEADERS)
        result = response.json().get("result", {})
        status = result.get("status")

        if status == "filled":
            order["status"] = "filled"

        else:
            # Запоминаем цену
            price = float(result.get("price", order["price"]))
            quantity = order["quantity"]
            symbol = order["symbol"]
            
            # Отменяем ордер
            requests.delete(url, headers=HEADERS)
            order["status"] = "cancelled"
            
            # Создаем новый ордер с ценой +1%
            new_price = round(price * 1.01, 6)
            new_order_payload = {
                "symbol": symbol,
                "side": "buy",
                "type": "limit",
                "price": str(new_price),
                "quantity": quantity
            }
            post_response = requests.post(
                "https://api.ataix.kz/api/orders",
                headers=HEADERS,
                json=new_order_payload
            )
            new_result = post_response.json().get("result", {})
            new_order = {
                "orderID": new_result.get("orderID", "unknown"),
                "price": str(new_price),
                "quantity": quantity,
                "symbol": symbol,
                "created": new_result.get("created", ""),
                "status": "created"
            }
            updated_orders.append(new_order)

        updated_orders.append(order)

    write_orders(updated_orders)

# Запускаем
check_and_update_orders()
