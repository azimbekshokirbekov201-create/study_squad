import json

from google import genai
from google.genai import types

from config import settings


TASK_SYSTEM = """Sen Study Squad uchun AI Task Planner va Proof Checker san.
Vazifalarni foydalanuvchining maqsadiga mos, aniq, o'lchanadigan va bajarib bo'ladigan qilib tuz.
Vazifalar bir-biridan farqli bo'lsin. Javobni faqat JSON formatida ber.
"""


def _client() -> genai.Client:
    if not settings.gemini_api_key:
        raise RuntimeError("GEMINI_API_KEY sozlanmagan. Railway Variables yoki .env ga qo'shing.")
    return genai.Client(api_key=settings.gemini_api_key)


def generate_tasks(goal: str, count: int) -> list[dict]:
    prompt = f"""{TASK_SYSTEM}
Maqsad: {goal}
Bugun uchun {count} ta vazifa tuz.
Har bir element: title, description, ai_reason.
JSON: {{\"tasks\":[{{\"title\":\"...\",\"description\":\"...\",\"ai_reason\":\"...\"}}]}}"""
    response = _client().models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
        config=types.GenerateContentConfig(response_mime_type="application/json"),
    )
    try:
        data = json.loads(response.text)
        return data.get("tasks", [])[:count]
    except Exception as exc:
        raise RuntimeError("AI vazifalarni JSON formatida qaytara olmadi.") from exc


def check_proof(task_title: str, task_description: str, image_bytes: bytes, mime_type: str) -> tuple[str, str]:
    prompt = f"""{TASK_SYSTEM}
Quyidagi vazifa bajarilganini rasm orqali tekshir.
Vazifa: {task_title}
Tavsif: {task_description or 'Tavsif berilmagan'}
Rasmda vazifaga mos dalil ko'rinadimi?
Faqat JSON qaytar: {{\"status\":\"approved|rejected|uncertain\",\"feedback\":\"qisqa izoh\"}}
Agar rasm vazifani ishonchli tasdiqlamasa, rejected yoki uncertain tanla. Rasmda ko'rinmaydigan narsani tasdiqlama.
"""
    response = _client().models.generate_content(
        model="gemini-2.5-flash",
        contents=[prompt, types.Part.from_bytes(data=image_bytes, mime_type=mime_type)],
        config=types.GenerateContentConfig(response_mime_type="application/json"),
    )
    try:
        data = json.loads(response.text)
        status = data.get("status", "uncertain")
        if status not in {"approved", "rejected", "uncertain"}:
            status = "uncertain"
        return status, data.get("feedback", "AI rasmni aniq tasdiqlay olmadi.")
    except Exception as exc:
        raise RuntimeError("AI rasm tekshiruvini o'qib bo'lmadi.") from exc
