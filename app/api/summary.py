"""from fastapi import APIRouter, status, HTTPException
from fastapi.responses import JSONResponse
from datetime import datetime, timezone, timedelta
from app.api.user import userTable
from app.api.product import productTable
from app.api.order import orderTable
from typing import List

router = APIRouter(
    tags=['Sumarry'],
    prefix='/api'
)


router = APIRouter()

def calculate_total_sale(item_qty, item_price):
    return item_qty * item_price

@router.get("/get_summary_today", response_model=List[dict])
def get_summary_today():
    try:
        D = datetime.now(timezone(timedelta(hours=1)))
        today = D.replace(hour=0, minute=0, second=0, microsecond=0)
        todayISO = today.isoformat()

        all_staff = userTable.all().values('_id', 'username', 'name')
        all_orders = orderTable.filter(createdAt__gt=todayISO, revoked=False).prefetch_related('items')

        grouped_orders = {}
        for order in all_orders:
            if order.createdBy in grouped_orders:
                grouped_orders[order.createdBy].append(order)
            else:
                grouped_orders[order.createdBy] = [order]

        grouped_orders_array = []
        for key, orders in grouped_orders.items():
            host = next((staff for staff in all_staff if str(staff['_id']) == key), None) or {'name': 'Unknown', 'username': 'Unknown'}
            items = []
            for order in orders:
                for item in order.items:
                    item_data = {
                        'name': item.name,
                        'qtySold': item.quantity,
                        'totalSale': calculate_total_sale(item.quantity, item.price)
                    }
                    items.append(item_data)
            grouped_orders_array.append({'host': host, 'items': items})

        grouped_orders_array_with_duplicates = []
        for host_data in grouped_orders_array:
            items = []
            for item in host_data['items']:
                existing_item = next((i for i in items if i['name'] == item['name']), None)
                if existing_item:
                    existing_item['qtySold'] += item['qtySold']
                    existing_item['totalSale'] += item['totalSale']
                else:
                    items.append(item)
            total_sale = sum(item['totalSale'] for item in items)
            grouped_orders_array_with_duplicates.append({'host': host_data['host'], 'items': items, 'totalSale': total_sale})

        return grouped_orders_array_with_duplicates

    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")



@router.post('/summary_date_to_date')
def get_summary_date_to_date(start_date: str, end_date: str):
    try:
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d")
        end_dt = end_dt.replace(hour=23, minute=59, second=59, microsecond=999)
        
        all_orders = list(orderTable.find({
            "createdAt": {"$gt": start_dt, "$lt": end_dt},
            "revoked": False
        }))

    
        
        all_staff = list(userTable.find({}))
        print(all_staff)
        
        grouped_orders = {}
        for order in all_orders:
            if order["createdBy"] not in grouped_orders:
                grouped_orders[order["createdBy"]] = []
            grouped_orders[order["createdBy"]].append(order)
        
        grouped_orders_array = []
        for key, group in grouped_orders.items():
            host = next((staff for staff in all_staff if str(staff["_id"]) == key), {"name": "Unknown", "username": "Unknown"})
            items = []
            for order in group:
                for item in order["items"]:
                    items.append({
                        "name": item["item"]["name"],
                        "qtySold": item["quantity"],
                        "price": item["item"]["price"],
                        "totalSale": item["quantity"] * item["item"]["price"]
                    })
            grouped_orders_array.append({
                "host": host,
                "items": items
            })
        
        grouped_orders_with_duplicates = []
        for host_data in grouped_orders_array:
            items_dict = {}
            for item in host_data["items"]:
                if item["name"] not in items_dict:
                    items_dict[item["name"]] = {
                        "qtySold": item["qtySold"],
                        "totalSale": item["totalSale"]
                    }
                else:
                    items_dict[item["name"]]["qtySold"] += item["qtySold"]
                    items_dict[item["name"]]["totalSale"] += item["totalSale"]
            items = [{"name": name, **data} for name, data in items_dict.items()]
            total_sale = sum(item["totalSale"] for item in items)
            grouped_orders_with_duplicates.append({
                "host": host_data["host"],
                "items": items,
                "totalSale": total_sale
            })
        
        return {"orders": grouped_orders_with_duplicates}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


"""