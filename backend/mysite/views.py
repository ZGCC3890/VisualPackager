from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.contrib.auth import authenticate

@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        username = data.get('username', '')
        password = data.get('password', '')
        user = authenticate(username=username, password=password)
        if user is not None:
            return JsonResponse({'success': True, 'message': '登录成功'})
        else:
            return JsonResponse({'success': False, 'message': '用户名或密码错误'})
    return JsonResponse({'success': False, 'message': '仅支持 POST 请求'})
