import os
from django.shortcuts import render
from django.http import JsonResponse
import openai
from django.views import View
from prompt_completion import format
import json
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
def chatbot(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        prompt = data['prompt']
        response = format(prompt)
        print("response: " +response.choices[0].text.strip())
        return JsonResponse({'output': response['choices'][0]['text']})
    else:
        return render(request, 'chatbot/chatbot.html')