import streamlit as st
from frontend import api_client

CONTENT_TYPE_MAP = {
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "png": "image/png",
    "mp4": "video/mp4",
    "mov": "video/mp4",   # treat as mp4 for backend compatibility
    "m4v": "video/mp4",
    "3gp": "video/mp4",
    "avi": "video/mp4",
}

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png", "mp4", "mov", "m4v", "3gp", "avi"}


def render():
    st.markdown("### 📤 העלאת מדיה")
    st.caption("העלה תמונת מוצר (JPG/PNG) או סרטון (MP4/MOV) – כולל סרטונים מהגלריה בנייד.")

    # type=None → allow all files, we validate ourselves (fixes MOV/iPhone block)
    uploaded = st.file_uploader(
        label="גרור קובץ לכאן או לחץ לבחירה",
        type=None,
        label_visibility="collapsed",
    )

    if uploaded is None:
        st.session_state.pop("media_id", None)
        st.session_state.pop("media_type", None)
        st.session_state.pop("uploaded_filename", None)
        st.session_state.pop("generated_content", None)
        return

    # Validate extension ourselves (Streamlit type=None bypasses its own check)
    ext = uploaded.name.rsplit(".", 1)[-1].lower() if "." in uploaded.name else ""
    if ext not in ALLOWED_EXTENSIONS:
        st.error(f"סוג קובץ לא נתמך: .{ext} — יש להעלות JPG, PNG, MP4 או MOV בלבד.")
        return

    # Only re-upload if a new file is selected
    if st.session_state.get("uploaded_filename") != uploaded.name:
        with st.spinner("מעלה קובץ..."):
            ext = uploaded.name.rsplit(".", 1)[-1].lower()
            content_type = CONTENT_TYPE_MAP.get(ext, "application/octet-stream")
            try:
                result = api_client.upload_media(
                    file_bytes=uploaded.read(),
                    filename=uploaded.name,
                    content_type=content_type,
                )
                st.session_state["media_id"] = result["media_id"]
                st.session_state["media_type"] = result["media_type"]
                st.session_state["uploaded_filename"] = uploaded.name
                st.session_state["uploaded_file_bytes"] = uploaded.getvalue()
                st.session_state.pop("generated_content", None)
                st.success(f"הועלה בהצלחה: {uploaded.name}")
            except api_client.NetloveAPIError as e:
                st.error(f"שגיאת העלאה: {e.detail}")
    else:
        st.success(f"קובץ טעון: {uploaded.name}")

    # Preview
    if "media_type" in st.session_state:
        _show_preview()


def _show_preview():
    media_type = st.session_state.get("media_type")
    file_bytes = st.session_state.get("uploaded_file_bytes")
    if not file_bytes:
        return

    st.markdown("---")
    if media_type == "image":
        st.image(file_bytes, caption="תצוגה מקדימה", use_container_width=True)
    else:
        st.video(file_bytes)
