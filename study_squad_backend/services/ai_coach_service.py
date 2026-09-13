from google import genai

from config import settings


SYSTEM_PROMPT = """Sen Study Squad ilovasidagi AI Study Coach'san.

Sening asosiy vazifang:
- o'quvchiga o'qish bo'yicha maslahat berish
- kunlik va haftalik reja tuzishda yordam berish
- motivatsiya berish
- IELTS, ingliz tili, matematika, dasturlash va boshqa o'quv maqsadlarida yordam berish
- foydalanuvchining progressiga qarab shaxsiy tavsiyalar berish

QOIDALAR:
1. Agar foydalanuvchi boshqa tilda yozmasa, har doim o'zbek tilida javob ber.
2. Javoblar qisqa, aniq va amaliy bo'lsin. Odatda 2-4 gap yetarli.
3. Foydalanuvchining progressi, streaki yoki natijalari berilsa, ulardan foydalan.
4. Do'stona, motivatsion, lekin professional ohangda gapir.
5. Agar foydalanuvchi qiynalayotgan bo'lsa, avval qisqa qo'llab-quvvatlash ber, keyin amaliy yechim taklif qil.

SALOMLASHISH QOIDASI:
- Har bir xabarda salomlashma.
- "Study Squadga xush kelibsiz!" kabi gaplarni qayta-qayta yozma.
- Foydalanuvchi oddiy savol bergan bo'lsa, to'g'ridan-to'g'ri javob ber.
- Faqat suhbatning haqiqiy birinchi xabarida qisqa salomlashish mumkin.
- Keyingi barcha xabarlarda salomlashishni takrorlama.
- "Salom", "Assalomu alaykum" kabi so'zlarni foydalanuvchi o'zi yozsa, tabiiy tarzda javob berishing mumkin.

MUHIM:
- O'zingni har bir javobda qaytadan tanishtirma.
- "Men Study Squad AI Coachman" kabi gaplarni takrorlama.
- Foydalanuvchining savoliga aloqasiz kirish gaplarini yozma.
- Javobni imkon qadar foydalanuvchining savoliga bevosita bog'la.
"""


def _get_client() -> genai.Client:
    """Gemini client yaratadi."""
    if not settings.gemini_api_key:
        raise RuntimeError(
            "GEMINI_API_KEY sozlanmagan. Railway Variables yoki .env ga qo'shing."
        )

    return genai.Client(api_key=settings.gemini_api_key)


def get_ai_response(
    user_message: str,
    context: str | None = None
) -> str:
    """
    Foydalanuvchi xabariga AI Coach javobini qaytaradi.

    context:
        Foydalanuvchining progress/streak kabi ma'lumotlari.
    """

    client = _get_client()

    prompt_parts = [
        SYSTEM_PROMPT,
        "\nFoydalanuvchining joriy xabari:",
        user_message.strip(),
    ]

    if context:
        prompt_parts.insert(
            1,
            f"\nFoydalanuvchining progress ma'lumotlari:\n{context}"
        )

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents="\n".join(prompt_parts),
    )

    if not response.text:
        return "Hozircha javob tayyorlay olmadim. Iltimos, yana bir marta urinib ko'ring."

    return response.text.strip()


def get_daily_tip(context: str) -> str:
    """
    Foydalanuvchining kunlik progressiga qarab
    qisqa va amaliy tavsiya generatsiya qiladi.
    """

    client = _get_client()

    prompt = f"""{SYSTEM_PROMPT}

Bu alohida Daily Tip funksiyasi.
Foydalanuvchining bugungi progressi:

{context}

Shu ma'lumot asosida bugun uchun bitta qisqa,
aniq va amaliy tavsiya yoz.

Talablar:
- 1-2 gap
- motivatsion, lekin haddan tashqari uzun emas
- foydalanuvchining progressiga mos
- salomlashma
- "Study Squadga xush kelibsiz" deb yozma
- o'zingni tanishtirma
"""

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )

    if not response.text:
        return "Bugun kichik bo'lsa ham bitta muhim vazifani yakunlashga harakat qil. 🔥"

    return response.text.strip()