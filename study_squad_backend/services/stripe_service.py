import stripe

from config import settings
from services.pricing_plans import PLANS

stripe.api_key = settings.stripe_secret_key


def create_checkout_session(user_id: int, user_email: str, tier: str) -> str:
    """Tanlangan tarif uchun Stripe Checkout sessiyasi yaratadi va to'lov URL qaytaradi."""
    if tier not in ("pro", "master"):
        raise ValueError("Faqat 'pro' yoki 'master' tarifini sotib olish mumkin")

    plan = PLANS[tier]

    session = stripe.checkout.Session.create(
        mode="subscription",
        customer_email=user_email,
        line_items=[{
            "price_data": {
                "currency": "usd",
                "unit_amount": plan["price_cents"],
                "recurring": {"interval": "month"},
                "product_data": {"name": f"Study Squad {plan['name']} tarifi"},
            },
            "quantity": 1,
        }],
        success_url=settings.frontend_success_url,
        cancel_url=settings.frontend_cancel_url,
        metadata={"user_id": str(user_id), "tier": tier},
    )
    return session.url


def verify_webhook_event(payload: bytes, sig_header: str):
    """Stripe webhook imzosini tekshiradi va event obyektini qaytaradi."""
    return stripe.Webhook.construct_event(
        payload, sig_header, settings.stripe_webhook_secret
    )
