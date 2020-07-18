from django.shortcuts import render
from django.http import JsonResponse
# Create your views here.
from lstm_method.use import compare

def lstm(request):
    if request.method == "POST":
        sen1 = request.POST.get('sentence1')
        sen2 = request.POST.get('sentence2')
        res = compare('我已经关闭另一个号的花呗了怎么在这个号开通', '蚂蚁花呗关闭了。怎么开通另一个')
        if res>=0.5:
            result = True
        else:
            result = False
        return JsonResponse(
            {
                'result':result,
                'confidence':res
            }
        )
