from celery import shared_task
from PIL import Image
import io
import base64
import numpy as np
import os

# You'll need to install these dependencies
# pip install rembg

@shared_task
def process_image_task(image_bytes):
    try:
        # Load image from bytes
        img = Image.open(io.BytesIO(image_bytes))
        
        # Import rembg here to avoid loading it at module level
        from rembg import remove
        
        # Remove background
        output = remove(img)
        
        # Convert back to base64 for JSON response
        buffered = io.BytesIO()
        output.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        return {"status": "completed", "image": img_str}
    
    except Exception as e:
        print(f"Error processing image: {e}")
        return {"status": "error", "message": str(e)}