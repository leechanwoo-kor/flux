import streamlit as st
import os
import json
from PIL import Image
import base64
from io import BytesIO
from datetime import datetime
import re

st.set_page_config(page_title="Image Gallery", page_icon="🖼️", layout="wide")
st.title("Image Gallery")


def get_image_download_link(img, filename):
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    href = f"data:file/png;base64,{img_str}"
    return href, filename


def get_button_style():
    return """
        <style>
        .stButton > button {
            width: 100%;
            border-radius: 5px;
            height: 3em;
            background-color: #4CAF50;
            color: white;
            font-size: 16px;
            border: none;
            cursor: pointer;
            transition: all 0.3s ease 0s;
        }
        .stButton > button:hover {
            background-color: #45a049;
        }
        </style>
    """


st.markdown(get_button_style(), unsafe_allow_html=True)

image_folder = "images"
image_files = [
    f
    for f in os.listdir(image_folder)
    if f.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".webp"))
]

if not image_files:
    st.warning("No images found in the gallery.")
else:
    # Sorting options
    sort_option = st.selectbox("Sort by:", ["Newest", "Oldest", "Model"])

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
        else:
            prompt = "Prompt not available"
            model = "Model info not available"

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
                "timestamp": timestamp,
            }
        )

    # Sort image data
    if sort_option == "Newest":
        image_data.sort(key=lambda x: x["timestamp"], reverse=True)
    elif sort_option == "Oldest":
        image_data.sort(key=lambda x: x["timestamp"])
    elif sort_option == "Model":
        image_data.sort(key=lambda x: x["model"])

    # Display images
    cols = st.columns(3)
    for idx, data in enumerate(image_data):
        with cols[idx % 3]:
            image = Image.open(data["path"])

            st.image(image, caption=data["file"], use_column_width=True)

            st.text_area(
                "Prompt:", value=data["prompt"], height=100, key=f"prompt_{idx}"
            )
            st.text(f"Model: {data['model']}")
            st.text(f"Generated: {data['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")

            button_cols = st.columns(2)

            with button_cols[0]:
                img_bytes = BytesIO()
                image.save(img_bytes, format="PNG")
                img_b64 = base64.b64encode(img_bytes.getvalue()).decode()
                share_link = f"data:image/png;base64,{img_b64}"

                if st.button("Share", key=f"share_{idx}"):
                    st.success("Image link copied to clipboard!")
                    st.markdown(
                        f"""
                    <script>
                        navigator.clipboard.writeText('{share_link}');
                    </script>
                    """,
                        unsafe_allow_html=True,
                    )

            with button_cols[1]:
                download_link, filename = get_image_download_link(image, data["file"])
                if st.button("Download", key=f"download_{idx}"):
                    st.markdown(
                        f'<a href="{download_link}" download="{filename}">Click here if download doesn\'t start automatically</a>',
                        unsafe_allow_html=True,
                    )
                    st.markdown(
                        f"""
                    <script>
                        var link = document.createElement('a');
                        link.href = '{download_link}';
                        link.download = '{filename}';
                        document.body.appendChild(link);
                        link.click();
                        document.body.removeChild(link);
                    </script>
                    """,
                        unsafe_allow_html=True,
                    )

    st.markdown("<br><br>", unsafe_allow_html=True)
