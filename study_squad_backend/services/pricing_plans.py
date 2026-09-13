"""Study Squad tarif rejalari.

Narxlar sentlarda (Stripe talabi), chunki Stripe eng kichik pul birligini talab qiladi.
"""

PLANS = {
    "basic": {
        "name": "Basic",
        "price_usd": 0,
        "price_cents": 0,
        "ai_daily_limit": 20,
        "features": [
            "Kuniga 20 ta AI Coach so'rovi",
            "Squad accountability",
            "Coin va streak tizimi",
        ],
        "how_to_get": "200 coin evaziga yoki bepul boshlash",
    },
    "pro": {
        "name": "Pro",
        "price_usd": 4.99,
        "price_cents": 499,
        "ai_daily_limit": 50,
        "features": [
            "Kuniga 50 ta AI Coach so'rovi",
            "Batafsil progress analytics",
            "Google Meet integratsiyasi",
        ],
        "how_to_get": "Stripe orqali oylik to'lov",
    },
    "master": {
        "name": "Master",
        "price_usd": 9.99,
        "price_cents": 999,
        "ai_daily_limit": None,
        "features": [
            "Pro'dagi barcha imkoniyatlar",
            "Haftalik shaxsiy AI hisobot",
            "Ustuvor qo'llab-quvvatlash",
            "Maxsus squad belgisi (badge)",
        ],
        "how_to_get": "Stripe orqali oylik to'lov",
    },
}
