import os
import base64
import uuid
import io
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rembg import remove
from PIL import Image
from celery.result import AsyncResult


@csrf_exempt
def remove_background(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST allowed"}, status=405)

    try:
        image_file = request.FILES.get("image")
        if not image_file:
            return JsonResponse({"error": "No image uploaded"}, status=400)

        # Get the base filename (without extension) and sanitize
        original_name = os.path.splitext(image_file.name)[0]
        original_name = original_name.replace(" ", "_")  # Remove spaces
        final_filename = f"{original_name}_removed.png"

        # Open and convert image
        input_image = Image.open(image_file).convert("RGBA")

        # Save image to buffer
        input_buffer = io.BytesIO()
        input_image.save(input_buffer, format="PNG")
        input_buffer.seek(0)

        # Run background removal
        output_data = remove(input_buffer.read())

        # Save result to buffer
        output_buffer = io.BytesIO()
        output_buffer.write(output_data)
        output_buffer.seek(0)

        # Ensure media directory exists
        os.makedirs(settings.MEDIA_ROOT, exist_ok=True)
        output_path = os.path.join(settings.MEDIA_ROOT, final_filename)

        # Save to disk
        with open(output_path, 'wb') as f:
            f.write(output_buffer.getvalue())

        # Encode result as base64
        base64_image = base64.b64encode(output_buffer.getvalue()).decode('utf-8')

        return JsonResponse({
            "status": "success",
            "filename": final_filename,
            "image": base64_image,
            "image_url": f"/media/{final_filename}"
        })

    except Exception as e:
        import traceback
        print("Error in remove_background:", traceback.format_exc())
        return JsonResponse({"error": "Something went wrong while processing the image."}, status=500)


def get_task_result(request, task_id):
    task = AsyncResult(task_id)
    if task.ready():
        result = task.result
        if isinstance(result, dict) and 'image' in result:
            return JsonResponse(result)
        else:
            return JsonResponse({"status": "completed", "result": result})
    elif task.failed():
        return JsonResponse({"status": "failed", "error": str(task.traceback)}, status=500)
    else:
        return JsonResponse({"status": "pending"})
