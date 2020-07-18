from django.shortcuts import render
from django.http import JsonResponse
# Create your views here.
from normal.use2 import compare

def normal(request):
    if request.method == "POST":
        sen1 = request.POST.get('sentence1')
        sen2 = request.POST.get('sentence2')
        print(sen1)
        print(sen2)
        result = compare(sen1, sen2)
        return JsonResponse(
            {
                'result':result,
                'confidence':1
            }
        )
