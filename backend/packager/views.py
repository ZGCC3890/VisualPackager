from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from .models import Freight

@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        username = data.get('username', '')
        password = data.get('password', '')
        user = authenticate(username=username, password=password)
        if user is not None:
            return JsonResponse({'success': True, 'message': '登录成功', 'username': user.username})
        else:
            return JsonResponse({'success': False, 'message': '用户名或密码错误'})
    return JsonResponse({'success': False, 'message': '仅支持 POST 请求'})

@csrf_exempt
def save_freight_view(request):
    """
    用于接收前端提交的货物信息列表，并保存到 Freight 表
    """
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        freight_data_list = data.get('freight_data', [])
        if not freight_data_list:
            return JsonResponse({'success': False, 'message': '没有货物信息'})
        username = data.get('username', '')
        user = User.objects.filter(username=username).first()
        if not user:
            return JsonResponse({'success': False, 'message': '用户不存在，请先登录！'})

        for item in freight_data_list:
            product_name = item.get('productName', '')
            length = float(item.get('length', 0))
            width = float(item.get('width', 0))
            height = float(item.get('height', 0))
            weight = float(item.get('weight', 0))

            if any(v < 0 for v in [length, width, height, weight]):
                return JsonResponse({'success': False, 'message': '长宽高重量必须大于0'})

            freight_obj = Freight(
                user=user,
                product_name=product_name,
                length=length,
                width=width,
                height=height,
                weight=weight
            )
            freight_obj.save()

        return JsonResponse({'success': True, 'message': '货物信息已保存！'})
    return JsonResponse({'success': False, 'message': '仅支持 POST 请求'})