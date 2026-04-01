"""
AI content generation service using OpenAI GPT-4o multimodal.

For images: sends a single base64-encoded image block + prompt.
For videos: sends up to 8 extracted frame blocks + prompt.

The model returns a strict JSON object with:
  - hook: str       (כותרת ראשית מושכת)
  - caption: str    (מלל שיווקי רגשי)
  - hashtags: [str] (עד 5 האשטגים)
"""

import json
from openai import AsyncOpenAI
from backend.models.content import GeneratedContent
from backend.utils.encoding import bytes_to_base64

SYSTEM_PROMPT = """אתה מומחה שיווק דיגיטלי של העסק Netlove – חנות מסגרות בעיצוב אישי בסגנון נטפליקס.
המסגרות מיועדות לזכרונות יקרים: זוגות, משפחות, חברים, אירועים מיוחדים.

המשתמש שולח לך תמונה או פריימים מסרטון של מסגרת Netlove.
עליך לנתח את המדיה – כולל כל טקסט שכתוב על המסגרת (שם סרט, שם זוג, תאריך, אירוע וכו') – וליצור תוכן שיווקי בעברית.

החזר אך ורק JSON תקני (ללא markdown, ללא ```json```) בפורמט הבא:
{
  "hook": "כותרת ראשית קצרה ומושכת – שורה אחת בלבד, עד 8 מילים",
  "caption": "2-3 משפטים יפים שמעוררים רגש ומניעים לפעולה, ואז CTA ברור בסוף",
  "hashtags": ["hashtag1", "hashtag2", "hashtag3", "hashtag4", "hashtag5"]
}

כללים חשובים:
- Hook: שורה אחת בלבד! קצר, ישיר, רגשי. אם יש שם/טקסט על המסגרת – שלב אותו בהוק.
- Caption: 2-3 משפטים יפים שמספרים סיפור ומזמינים לפעולה. הזכר את מסגרות Netlove.
  אם יש שם סרט/אירוע/שם על המסגרת – ציין אותו ("מסגרת [שם] שלכם ❤️").
  סיים תמיד ב-CTA ברור: "הלינק בביו 🔗" / "הזמינו עכשיו" / "כתבו לנו בDM".
- Hashtags: עד 5 בלבד! בחר את הרלוונטיים ביותר. כלול תמיד #netlove.
- כל התוכן בעברית (האשטגים יכולים להיות גם אנגלית)."""

USER_PROMPT_TEMPLATE = "נתח את {media_description} שלמטה וצור תוכן שיווקי לפי ההוראות.\n{context_note}\nזכור: החזר JSON בלבד."


async def generate_content(
    file_path: str,
    media_type: str,
    user_context: str = "",
) -> GeneratedContent:
    from backend.config import get_settings
    from backend.services.video_service import extract_frames

    settings = get_settings()
    if not settings.openai_api_key:
        raise ValueError("OPENAI_API_KEY לא מוגדר בקובץ .env")

    client = AsyncOpenAI(api_key=settings.openai_api_key)
    context_note = f"\nהקשר נוסף מהמשתמש: {user_context}" if user_context else ""

    if media_type == "video":
        frames = extract_frames(file_path)
        image_blocks = [
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{bytes_to_base64(frame)}",
                    "detail": "low",
                },
            }
            for frame in frames
        ]
        user_text = USER_PROMPT_TEMPLATE.format(
            media_description="פריימים מהסרטון",
            context_note=context_note,
        )
        content_blocks = [{"type": "text", "text": user_text}] + image_blocks
    else:
        with open(file_path, "rb") as f:
            image_data = bytes_to_base64(f.read())
        user_text = USER_PROMPT_TEMPLATE.format(
            media_description="התמונה",
            context_note=context_note,
        )
        content_blocks = [
            {"type": "text", "text": user_text},
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{image_data}",
                    "detail": "high",
                },
            },
        ]

    response = await client.chat.completions.create(
        model=settings.openai_model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": content_blocks},
        ],
        max_tokens=800,
        temperature=0.8,
    )

    raw = response.choices[0].message.content or "{}"
    raw = raw.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[-2] if "```" in raw else raw
        raw = raw.lstrip("json").strip()

    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        data = {}

    hashtags = data.get("hashtags", [])
    if isinstance(hashtags, list):
        hashtags = [h if h.startswith("#") else f"#{h}" for h in hashtags[:5]]

    return GeneratedContent(
        hook=data.get("hook", ""),
        caption=data.get("caption", ""),
        hashtags=hashtags,
    )
