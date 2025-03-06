import json
from django.conf import settings

def global_settings(request):
    return {
        'BOT_URL': settings.BOT_URL  # ваша кастомная переменная
    }