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

# Define model configurations
MODEL_CONFIGS = {
    "schnell": {
        "model": "black-forest-labs/flux-schnell",
        "params": {
            "num_outputs": 1,
            "aspect_ratio": "1:1",
            "output_format": "webp",
            "output_quality": 90,
        },
    },
    "flux-dev (Disabled)": {
        "model": "black-forest-labs/flux-dev",
        "params": {
            "guidance": 3.5,
            "num_outputs": 1,
            "aspect_ratio": "1:1",
            "output_format": "webp",
            "output_quality": 80,
            "prompt_strength": 0.8,
            "num_inference_steps": 50,
        },
    },
}

def generate_image(prompt, model_key):
    model_config = MODEL_CONFIGS[model_key]

    input_params = model_config["params"].copy()
    input_params["prompt"] = prompt

    output = replicate.run(model_config["model"], input=input_params)

    # Extract the image URL and seed from the output
    if isinstance(output, dict):
        image_url = output.get("image")
        seed = output.get("seed")
    elif isinstance(output, list) and len(output) > 0:
        image_url = output[0]
        seed = None  # The seed might not be available in the list output
    else:
        raise ValueError("Unexpected output format from the model")

    response = requests.get(image_url)
    response.raise_for_status()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = uuid.uuid4().hex[:8]
    filename = f"generated_image_{timestamp}_{unique_id}.{input_params['output_format']}"

    image_path = os.path.join("images", filename)
    with open(image_path, "wb") as f:
        f.write(response.content)

    # Save prompt, model info, and seed along with the image
    info_filename = f"{os.path.splitext(filename)[0]}.json"
    info_path = os.path.join("images", info_filename)
    with open(info_path, "w") as f:
        json.dump({"prompt": prompt, "model": model_key, "seed": seed}, f)

    return image_path, seed

# Streamlit app configuration
st.set_page_config(page_title="Image Generator", page_icon="🖼️")
st.title("Image Generator")

# Model selection
model_options = list(MODEL_CONFIGS.keys())
selected_model = st.selectbox(
    "Select Model",
    model_options,
    index=0,
    format_func=lambda x: x if x != "flux-dev (Disabled)" else f"{x} ⚠️"
)

prompt = st.text_area("Enter your prompt here...", height=100)

if "generated_image" not in st.session_state:
    st.session_state.generated_image = None
if "seed" not in st.session_state:
    st.session_state.seed = None

if st.button("Generate Image"):
    if prompt:
        if selected_model == "flux-dev (Disabled)":
            st.error("The flux-dev model is currently disabled. Please select another model.")
        else:
            with st.spinner("Generating image... This may take a while."):
                try:
                    image_path, seed = generate_image(prompt, selected_model)
                    st.session_state.generated_image = image_path
                    st.session_state.seed = seed
                    st.success(f"Image generated successfully and saved to {image_path}")
                    if seed:
                        st.info(f"Seed value: {seed}")
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
    else:
        st.warning("Please enter a prompt.")

# Display the generated image
if st.session_state.generated_image:
    st.image(
        st.session_state.generated_image,
        caption=f"Generated Image (Seed: {st.session_state.seed if st.session_state.seed else 'Not available'})",
        use_column_width=True,
    )