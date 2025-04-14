from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.utils import timezone
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from .models import Freight, FreightPlan
from .packing_3d import Packing3D, Item

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

# ========== 保存货物信息（可同时保存方案） ==========
@csrf_exempt
def save_freight_view(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': '仅支持 POST 请求'})

    try:
        data          = json.loads(request.body)
        username      = data.get('username')
        destination   = data.get('destination', '')
        freight_arr   = data.get('freight_data', [])
        plan_json     = data.get('plan')          # 可能为 None

        if not freight_arr:
            return JsonResponse({'success': False, 'message': '没有货物信息'})

        user = User.objects.filter(username=username).first()
        if not user:
            return JsonResponse({'success': False, 'message': '用户不存在，请先登录！'})

        # 创建 FreightPlan（即使 plan_json 为 None 也创建，用来归档货物）
        title = timezone.now().strftime('%Y-%m-%d %H:%M') + f' · {destination}'
        plan_obj = FreightPlan.objects.create(
            user        = user,
            destination = destination,
            raw_json    = plan_json,      # None 也允许
            title       = title
        )

        # 校验并批量插入货物
        freight_objs = []
        for item in freight_arr:
            length = float(item.get('length', 0))
            width  = float(item.get('width', 0))
            height = float(item.get('height', 0))
            weight = float(item.get('weight', 0))
            if any(v < 0 for v in [length, width, height, weight]):
                return JsonResponse({'success': False, 'message': '长宽高重量必须 >= 0'})
            if any(v < 1 for v in [length, width, height]):
                return JsonResponse({'success': False, 'message': '长宽高必须 >= 1cm'})

            freight_objs.append(Freight(
                user         = user,
                plan         = plan_obj,
                product_name = item.get('productName', ''),
                length       = length,
                width        = width,
                height       = height,
                weight       = weight
            ))
        Freight.objects.bulk_create(freight_objs)

        return JsonResponse({'success': True, 'message': '货物信息已保存！'})

    except Exception as e:
        return JsonResponse({'success': False, 'message': f'保存失败: {e}'}, status=500)


# ========== 生成装箱方案 ==========
@csrf_exempt
def plan_view(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': '仅支持 POST 请求'}, status=405)

    try:
        data         = json.loads(request.body)
        goods        = data.get('goodsList', [])
        std_info     = data.get('stdInfo', {})
        outer_limit  = data.get('outerLimit', {})

        required = ['length', 'width', 'height', 'weight']
        if not goods or not std_info or not outer_limit or not all(k in std_info for k in required):
            return JsonResponse({'success': False, 'message': '参数不完整'})

        # 转成 {name: Item}
        items = {
            g['productName']: Item(
                g['productName'],
                g['length'], g['width'], g['height'],
                g['weight'], 1
            ) for g in goods
        }

        packer = Packing3D()
        result = packer.plan_packing(items, std_info, outer_limit)

        return JsonResponse({'success': True, 'plan': result})

    except Exception as e:
        return JsonResponse({'success': False, 'message': f'装箱失败: {e}'}, status=500)


# ========== 历史方案列表 ==========
@csrf_exempt
def list_plans_view(request):
    username = request.GET.get('username')
    user = User.objects.filter(username=username).first()
    qs = FreightPlan.objects.filter(user=user).order_by('-created')
    return JsonResponse({
        'plans': [{'id': p.id, 'title': p.title} for p in qs]
    })


# ========== 方案详情（含货物+方案） ==========
@csrf_exempt
def plan_detail_view(request, pk):
    plan = FreightPlan.objects.filter(id=pk).first()
    if not plan:
        return JsonResponse({'success': False, 'message': '方案不存在'}, status=404)

    freight_list = list(plan.items.values(
        'product_name', 'length', 'width', 'height', 'weight'
    ))

    return JsonResponse({
        'success': True,
        'destination': plan.destination,
        'plan': plan.raw_json,            # 可能为 null
        'freight_data': freight_list
    })
    
# ========== 重命名方案 ==========
@csrf_exempt
def rename_plan_view(request, pk):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'POST only'}, status=405)
    data = json.loads(request.body)
    new_title = data.get('title', '').strip()
    if not new_title:
        new_title = timezone.now().strftime('%Y-%m-%d %H:%M') + ' · 新方案'
    plan = FreightPlan.objects.filter(id=pk).first()
    if not plan:
        return JsonResponse({'success': False, 'message': '方案不存在'}, status=404)
    plan.title = new_title
    plan.save(update_fields=['title'])
    return JsonResponse({'success': True, 'title': new_title})

# ========== 删除方案 ==========
@csrf_exempt
def delete_plan_view(request, pk):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'message': 'POST only'}, status=405)
    plan = FreightPlan.objects.filter(id=pk).first()
    if not plan:
        return JsonResponse({'success': False, 'message': '方案不存在'}, status=404)
    plan.delete()
    return JsonResponse({'success': True})
