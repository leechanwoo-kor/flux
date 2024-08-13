import streamlit as st
import os
import json
from PIL import Image
import io
from datetime import datetime
import re
import math

st.set_page_config(page_title="Image Gallery", page_icon="🖼️", layout="wide")
st.title("Image Gallery")


def get_image_bytes(img):
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    return buffered.getvalue()


def display_pagination():
    col1, col2, col3 = st.columns([1, 3, 1])
    with col1:
        if st.session_state.page > 1:
            st.button(
                "Previous", on_click=prev_page, key=f"prev_{st.session_state.page}"
            )
    with col2:
        st.write(f"Page {st.session_state.page} of {total_pages}")
    with col3:
        if st.session_state.page < total_pages:
            st.button("Next", on_click=next_page, key=f"next_{st.session_state.page}")


image_folder = "images"
image_files = [
    f
    for f in os.listdir(image_folder)
    if f.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".webp"))
]

if not image_files:
    st.warning("No images found in the gallery.")
else:
    # Prepare image data
    image_data = []
    for image_file in image_files:
        image_path = os.path.join(image_folder, image_file)
        info_file = f"{os.path.splitext(image_file)[0]}.json"
        info_path = os.path.join(image_folder, info_file)

        if os.path.exists(info_path):
            with open(info_path, "r") as f:
                info = json.load(f)
            prompt = info.get("prompt", "Prompt not available")
            model = info.get("model", "Model info not available")
            seed = info.get("seed", "Seed not available")
        else:
            prompt = "Prompt not available"
            model = "Model info not available"
            seed = "Seed not available"

        # Extract timestamp from filename
        timestamp_match = re.search(r"(\d{8}_\d{6})", image_file)
        if timestamp_match:
            timestamp_str = timestamp_match.group(1)
            try:
                timestamp = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")
            except ValueError:
                timestamp = datetime.fromtimestamp(os.path.getctime(image_path))
        else:
            timestamp = datetime.fromtimestamp(os.path.getctime(image_path))

        image_data.append(
            {
                "file": image_file,
                "path": image_path,
                "prompt": prompt,
                "model": model,
                "seed": seed,
                "timestamp": timestamp,
            }
        )

    # Sort image data by newest first
    image_data.sort(key=lambda x: x["timestamp"], reverse=True)

    # Pagination
    images_per_page = 9
    total_pages = math.ceil(len(image_data) / images_per_page)

    if "page" not in st.session_state:
        st.session_state.page = 1

    def next_page():
        st.session_state.page += 1

    def prev_page():
        st.session_state.page -= 1

    # Display images for the current page
    start_idx = (st.session_state.page - 1) * images_per_page
    end_idx = start_idx + images_per_page
    current_page_data = image_data[start_idx:end_idx]

    for row in range(3):
        cols = st.columns(3)
        for col in range(3):
            idx = row * 3 + col
            if idx < len(current_page_data):
                data = current_page_data[idx]
                with cols[col]:
                    image = Image.open(data["path"])

                    st.image(image, caption=data["file"], use_column_width=True)

                    st.markdown("**Prompt:**")
                    st.code(data["prompt"], language="plaintext")

                    st.text(f"Model: {data['model']}")
                    st.text(f"Seed: {data['seed']}")
                    st.text(
                        f"Generated: {data['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}"
                    )

                    image_bytes = get_image_bytes(image)

                    st.download_button(
                        label="Download",
                        data=image_bytes,
                        file_name=data["file"],
                        mime="image/png",
                    )

    st.markdown("<br>", unsafe_allow_html=True)

    # Display bottom pagination controls
    display_pagination()
