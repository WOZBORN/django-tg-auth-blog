import json
import secrets

from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt

from .models import TelegramUser, Post


@csrf_exempt
def telegram_register(request):
    if request.method == 'POST':
        try:
            print(request.body)
            data = json.loads(request.body)
        except json.JSONDecodeError as e:
            print(e)
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        tg_id = data.get('tg_id')
        nickname = data.get('nickname')

        if not tg_id or not nickname:
            return JsonResponse({'error': 'Missing tg_id or nickname'}, status=400)

        user, created = TelegramUser.objects.get_or_create(
            tg_id=tg_id,
            defaults={'telegram_nickname': nickname}
        )

        if not created:
            user.telegram_nickname = nickname

        user.token = secrets.token_urlsafe(16)
        user.save()

        return JsonResponse(
            data={'status': 'ok', 'token': user.token},
            status=201
        )
    else:
        return JsonResponse(
            data={'error': 'Only POST method allowed'},
            status=405
        )


def get_current_user(request):
    user_id = request.session.get('user_id')
    if user_id:
        try:
            return TelegramUser.objects.get(id=user_id)
        except TelegramUser.DoesNotExist:
            pass
    return None


def index_view(request):
    return render(request, 'index.html')


def login_view(request):
    if request.method == 'POST':
        token = request.POST.get('token')
        if not token:
            return HttpResponse('Токен не передан', status=400)
        try:
            user = TelegramUser.objects.get(token=token)
            request.session['user_id'] = user.id
            return redirect('posts')
        except TelegramUser.DoesNotExist:
            return HttpResponse('Неверный токен', status=401)
    return redirect('index')



def posts_view(request):
    user = get_current_user(request)
    if not user:
        return redirect('index')

    if request.method == 'POST':
        title = request.POST.get('title')
        text = request.POST.get('text')
        if title and text:
            Post.objects.create(author=user, title=title, text=text)
        return redirect('posts')

    posts = Post.objects.all().order_by('-created_at')
    return render(request, 'posts.html', {'posts': posts, 'user': user})


def check_user(request):
    tg_id = request.GET.get('tg_id')
    if tg_id:
        try:
            user = TelegramUser.objects.get(tg_id=tg_id)
            return JsonResponse({
                'is_registered': True,
                'telegram_nickname': user.telegram_nickname,
                'token': user.token,
                'status': 'ok'}
            )
        except TelegramUser.DoesNotExist:
            return JsonResponse({'is_registered': False})
    return JsonResponse({'error': 'tg_id not provided'})