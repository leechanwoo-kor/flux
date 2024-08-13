import streamlit as st
import replicate
import requests
import os
import uuid
import json
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the REPLICATE_API_TOKEN from environment variables
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")
if not REPLICATE_API_TOKEN:
    raise ValueError("REPLICATE_API_TOKEN is not set in the environment variables")

# Ensure the images folder exists
os.makedirs("images", exist_ok=True)

def generate_image(prompt):
    output = replicate.run(
        "black-forest-labs/flux-dev",
        input={
            "prompt": prompt,
            "guidance": 3.5,
            "num_outputs": 1,
            "aspect_ratio": "1:1",
            "output_format": "webp",
            "output_quality": 80,
            "prompt_strength": 0.8,
            "num_inference_steps": 50
        },
    )

    image_url = output[0] if isinstance(output, list) else output

    response = requests.get(image_url)
    response.raise_for_status()  # This will raise an exception for HTTP errors

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = uuid.uuid4().hex[:8]
    filename = f"generated_image_{timestamp}_{unique_id}.jpg"

    image_path = os.path.join("images", filename)
    with open(image_path, "wb") as f:
        f.write(response.content)

    # Save prompt along with the image
    prompt_filename = f"{os.path.splitext(filename)[0]}.json"
    prompt_path = os.path.join("images", prompt_filename)
    with open(prompt_path, "w") as f:
        json.dump({"prompt": prompt}, f)

    return image_path

# Streamlit app configuration
st.set_page_config(page_title="Flux Dev Image Generator", page_icon="🖼️")
st.title("Flux Dev Image Generator")

prompt = st.text_area("Enter your prompt here...", height=100)

if st.button("Generate Image"):
    if prompt:
        with st.spinner("Generating image..."):
            try:
                image_path = generate_image(prompt)
                st.image(image_path, caption="Generated Image", use_column_width=True)
                st.success(f"Image saved to {image_path}")
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
    else:
        st.warning("Please enter a prompt.")