import os
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from groq import Groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

@csrf_exempt
@require_http_methods(["POST"])
def chat_with_groq(request):
    try:
        # Parse user input
        data = json.loads(request.body)
        user_message = data.get("message", "")

        if not user_message:
            return JsonResponse({"error": "Message is required"}, status=400)

        # Initialize Groq client
        client = Groq(api_key=GROQ_API_KEY)

        # Send user message to Groq API
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are a helpful travel assistant."},
                {"role": "user", "content": user_message}
            ],
            model="mixtral-8x7b-32768",
            temperature=0.7,
            max_tokens=200
        )

        # Extract response
        bot_reply = response.choices[0].message.content

        return JsonResponse({"reply": bot_reply})

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
