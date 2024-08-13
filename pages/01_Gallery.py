import streamlit as st
import os
import json
from PIL import Image
import base64
from io import BytesIO

st.set_page_config(page_title="Image Gallery", page_icon="🖼️", layout="wide")
st.title("Image Gallery")

def get_image_download_link(img, filename):
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    href = f'data:file/png;base64,{img_str}'
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
image_files = [f for f in os.listdir(image_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))]

if not image_files:
    st.warning("No images found in the gallery.")
else:
    cols = st.columns(3)
    for idx, image_file in enumerate(image_files):
        with cols[idx % 3]:
            image_path = os.path.join(image_folder, image_file)
            image = Image.open(image_path)
            
            st.image(image, caption=image_file, use_column_width=True)
            
            # Load and display the prompt
            prompt_file = f"{os.path.splitext(image_file)[0]}.json"
            prompt_path = os.path.join(image_folder, prompt_file)
            if os.path.exists(prompt_path):
                with open(prompt_path, 'r') as f:
                    prompt_data = json.load(f)
                    st.text_area("Prompt:", value=prompt_data['prompt'], height=100, key=f"prompt_{idx}")
            else:
                st.text("Prompt not available")
            
            button_cols = st.columns(2)
            
            with button_cols[0]:
                img_bytes = BytesIO()
                image.save(img_bytes, format='PNG')
                img_b64 = base64.b64encode(img_bytes.getvalue()).decode()
                share_link = f"data:image/png;base64,{img_b64}"
                
                if st.button('Share', key=f'share_{idx}'):
                    st.success('Image link copied to clipboard!')
                    st.markdown(f"""
                    <script>
                        navigator.clipboard.writeText('{share_link}');
                    </script>
                    """, unsafe_allow_html=True)
            
            with button_cols[1]:
                download_link, filename = get_image_download_link(image, image_file)
                if st.button('Download', key=f'download_{idx}'):
                    st.markdown(f'<a href="{download_link}" download="{filename}">Click here if download doesn\'t start automatically</a>', unsafe_allow_html=True)
                    st.markdown(f"""
                    <script>
                        var link = document.createElement('a');
                        link.href = '{download_link}';
                        link.download = '{filename}';
                        document.body.appendChild(link);
                        link.click();
                        document.body.removeChild(link);
                    </script>
                    """, unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)