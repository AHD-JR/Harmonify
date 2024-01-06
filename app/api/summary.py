from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime, timezone, timedelta
from app.api.order import orderTable
from app.utils import permissions
from app.schema import User, OrderType

router = APIRouter(
    prefix='/api',
    tags=['Summary']
)


@router.get("/get_summary_today")
def get_summary_today(current_user: User = Depends(permissions.is_admin)):
    try:
        date = datetime.now(timezone(timedelta(hours=1)))
        today = date.replace(hour=0, minute=0, microsecond=0)
        todayISO = today.isoformat()

        pipeline = [
            {
                "$match": {
                    "createdAt": {"$gte": datetime.fromisoformat(todayISO)},
                    "$or": [{"orderType": OrderType.instant_order}, {"orderType": OrderType.shipment}],
                    "revoked": False,
                }
            },
            {
                "$unwind": "$items"
            },
            {
                "$group": {
                    "_id": "$createdBy",
                    "items": {
                        "$push": {
                            "name": "$items.name",
                            "price": "$items.price",
                            "quantity": "$items.quantity",
                            "total": {
                                "$multiply": ["$items.price", "$items.quantity"]
                            },
                        }
                    },
                    "totalSales": {
                        "$sum": {
                            "$sum": {
                                "$multiply": ["$items.price", "$items.quantity"]
                            }
                        }
                    },
                }
            },
            {
                "$lookup": {
                    "from": "users",
                    "localField": "_id",
                    "foreignField": "_id",
                    "as": "user"
                }
            },
            {
                "$unwind": "$user"
            },
            {
                "$group": {
                    "_id": '$host',
                    "users": {
                        "$push": {"username": "$user.username", "totalSales": "$totalSales", "items": "$items"}
                    },
                    "overallTotalSales": {"$sum": "$totalSales"}
                }
            },
        ]

        result = list(orderTable.aggregate(pipeline))

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/get_summary_date_to_date")
def get_summary_date_to_date(start_date, end_date, current_user: User = Depends(permissions.is_admin)):
    try:
        from_date = datetime.strptime(start_date, '%Y-%m-%d')
        to_date = datetime.strptime(end_date, '%Y-%m-%d')

        from_date = from_date.replace(hour=0, minute=0, second=0, microsecond=0)
        to_date = to_date.replace(hour=23, minute=59, second=59, microsecond=999)

        lagos_timezone = timezone(timedelta(hours=1))
        from_date = from_date.replace(tzinfo=lagos_timezone)
        to_date = to_date.replace(tzinfo=lagos_timezone)

        from_date_iso = datetime.fromisoformat(str(from_date))
        to_date_iso = datetime.fromisoformat(str(to_date))

        pipeline = [
            {
                "$match": {
                    "createdAt": {"$gte": from_date_iso, "$lte": to_date_iso},
                    "$or": [{"orderType": OrderType.instant_order}, {"orderType": OrderType.shipment}],
                    "revoked": False,
                }
            },
            {
                "$unwind": "$items"
            },
            {
                "$group": {
                    "_id": "$createdBy",
                    "items": {
                        "$push": {
                            "name": "$items.name",
                            "price": "$items.price",
                            "quantity": "$items.quantity",
                            "total": {
                                "$multiply": ["$items.price", "$items.quantity"]
                            },
                        }
                    },
                    "totalSales": {
                        "$sum": {
                            "$sum": {
                                "$multiply": ["$items.price", "$items.quantity"]
                            }
                        }
                    },
                }
            },
            {
                "$lookup": {
                    "from": "users",
                    "localField": "_id",
                    "foreignField": "_id",
                    "as": "user"
                }
            },
            {
                "$unwind": "$user"
            },
            {
                "$group": {
                    "_id": '$host',
                    "users": {
                        "$push": {"username": "$user.username", "totalSales": "$totalSales", "items": "$items"}
                    },
                    "overallTotalSales": {"$sum": "$totalSales"}
                }
            },
        ]

        result = list(orderTable.aggregate(pipeline))

        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))