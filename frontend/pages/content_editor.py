import streamlit as st
from frontend import api_client


def render():
    st.markdown("### 🤖 יצירת תוכן ב-AI")

    if "media_id" not in st.session_state:
        st.info("העלה מדיה תחילה כדי לייצר תוכן.")
        return

    user_context = st.text_input(
        "הקשר נוסף (אופציונלי)",
        placeholder="לדוגמה: מסגרת לזוגות, מסגרת לחברים, מסגרת ליום הולדת...",
        key="user_context_input",
    )

    col1, col2 = st.columns([1, 3])
    with col1:
        generate_btn = st.button("✨ צור תוכן ב-AI", use_container_width=True, type="primary")

    if generate_btn:
        with st.spinner("ה-AI מנתח את המדיה ויוצר תוכן שיווקי... ⏳"):
            try:
                result = api_client.generate_content(
                    media_id=st.session_state["media_id"],
                    user_context=user_context,
                )
                st.session_state["generated_content"] = result
                st.success("התוכן נוצר בהצלחה! ניתן לערוך לפני הפרסום.")
            except api_client.NetloveAPIError as e:
                st.error(f"שגיאת AI: {e.detail}")
                return

    if "generated_content" not in st.session_state:
        return

    content = st.session_state["generated_content"]

    st.markdown("---")
    st.markdown("#### ✏️ עריכת תוכן לפני פרסום")

    hook = st.text_input(
        "🎣 Hook – כותרת ראשית",
        value=content.get("hook", ""),
        key="edit_hook",
    )

    caption = st.text_area(
        "📝 Caption – מלל שיווקי",
        value=content.get("caption", ""),
        height=150,
        key="edit_caption",
    )

    hashtags_raw = st.text_area(
        "# האשטאגים (שורה לכל האשטאג, ללא #)",
        value="\n".join(content.get("hashtags", [])),
        height=120,
        key="edit_hashtags",
    )

    song = st.text_input(
        "🎵 המלצת שיר",
        value=content.get("song_recommendation", ""),
        key="edit_song",
    )

    # Sync edits back to session state so publisher gets updated values
    st.session_state["generated_content"] = {
        "hook": hook,
        "caption": caption,
        "hashtags": [h.strip().lstrip("#") for h in hashtags_raw.splitlines() if h.strip()],
        "song_recommendation": song,
    }

    # Preview formatted post
    with st.expander("👁️ תצוגה מקדימה של הפוסט"):
        hashtags_preview = " ".join(f"#{h}" for h in st.session_state["generated_content"]["hashtags"])
        st.markdown(f"**{hook}**")
        st.markdown(caption)
        if hashtags_preview:
            st.markdown(f"`{hashtags_preview}`")
        if song:
            st.markdown(f"🎵 *{song}*")
