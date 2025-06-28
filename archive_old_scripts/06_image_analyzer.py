# 06_image_analyzer.py

import os
from dotenv import load_dotenv
from PIL import Image # The Pillow library for opening images
import base64
import io

# We will use the direct LangChain Google class for this
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

# --- Load Environment Variables ---
load_dotenv()
print("--- Starting Image Analyzer ---")

if "GOOGLE_API_KEY" not in os.environ:
    print("ERROR: GOOGLE_API_KEY not found in .env file.")
    exit()
else:
    print("API key loaded successfully.")

# --- The Multimodal LLM ---
# The Gemini models with "vision" capabilities can understand images.
# gemini-1.5-flash-latest is a great multimodal model.
llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest")

# --- Function to Prepare the Image ---
def get_image_bytes(image_path):
    """Opens an image and prepares it to be sent to the AI."""
    try:
        # Open the image file
        img = Image.open(image_path)
        # Convert the image to bytes, which is what the API needs
        buffered = io.BytesIO()
        # Save the image to the buffer in a standard format like PNG
        img.save(buffered, format="PNG")
        return buffered.getvalue()
    except FileNotFoundError:
        print(f"ERROR: Image file not found at '{image_path}'")
        return None
    except Exception as e:
        print(f"ERROR: Could not process image. {e}")
        return None

# --- Main Test Block ---
if __name__ == "__main__":
    image_path = "product_image.jpeg" # Make sure this file exists in your folder!
    image_data = get_image_bytes(image_path)
    
    if image_data:
        print(f"✅ Successfully loaded image: {image_path}")

        # --- This is how you send an image and text in the same prompt ---
        # We create a HumanMessage with a 'content' list.
        # The list contains both text and image data.
        message = HumanMessage(
            content=[
                {
                    "type": "text",
                    "text": "You are an expert product analyst. Describe this product in detail. What is it made of? What are its key features and potential uses? Be factual.",
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/png;base64,{base64.b64encode(image_data).decode()}"
                    }
                },
            ]
        )
        
        print("\n🤖 Sending image and prompt to Gemini for analysis...")
        print("-" * 30)
        
        # Invoke the LLM with the special multimodal message
        response = llm.invoke([message])
        
        print("--- AI Analysis Result ---")
        print(response.content)
        