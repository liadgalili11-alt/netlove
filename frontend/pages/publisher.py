import streamlit as st
from frontend import api_client

PLATFORM_ICONS = {
    "instagram": "📸",
    "facebook": "👤",
    "tiktok": "🎵",
}

PLATFORM_LABELS = {
    "instagram": "Instagram",
    "facebook": "Facebook",
    "tiktok": "TikTok",
}


def render():
    st.markdown("### 🚀 פרסום ברשתות החברתיות")

    if "media_id" not in st.session_state:
        st.info("העלה מדיה תחילה.")
        return

    if "generated_content" not in st.session_state:
        st.info("צור תוכן ב-AI תחילה.")
        return

    st.markdown("**בחר פלטפורמות לפרסום:**")
    col1, col2, col3 = st.columns(3)
    with col1:
        ig = st.checkbox("📸 Instagram", value=True, key="pub_instagram")
    with col2:
        fb = st.checkbox("👤 Facebook", value=True, key="pub_facebook")
    with col3:
        tt = st.checkbox("🎵 TikTok", value=False, key="pub_tiktok")

    selected_platforms = []
    if ig:
        selected_platforms.append("instagram")
    if fb:
        selected_platforms.append("facebook")
    if tt:
        selected_platforms.append("tiktok")

    can_publish = bool(selected_platforms)

    st.markdown("---")

    publish_btn = st.button(
        "🚀 פרסם עכשיו לכל הפלטפורמות הנבחרות",
        disabled=not can_publish,
        use_container_width=True,
        type="primary",
    )

    if not can_publish:
        st.caption("יש לבחור לפחות פלטפורמה אחת.")

    if publish_btn and can_publish:
        content = st.session_state["generated_content"]
        media_id = st.session_state["media_id"]

        with st.spinner(f"מפרסם ל-{', '.join(PLATFORM_LABELS[p] for p in selected_platforms)}..."):
            try:
                results = api_client.publish_all(
                    media_id=media_id,
                    content=content,
                    platforms=selected_platforms,
                )
                _render_results(results)
            except api_client.NetloveAPIError as e:
                st.error(f"שגיאת פרסום: {e.detail}")


def _render_results(results: list[dict]):
    st.markdown("#### תוצאות פרסום")
    for result in results:
        platform = result.get("platform", "")
        icon = PLATFORM_ICONS.get(platform, "🌐")
        label = PLATFORM_LABELS.get(platform, platform)

        if result.get("success"):
            post_id = result.get("post_id", "")
            st.success(f"{icon} **{label}** – פורסם בהצלחה! Post ID: `{post_id}`")
        else:
            error = result.get("error", "שגיאה לא ידועה")
            st.error(f"{icon} **{label}** – נכשל: {error}")
