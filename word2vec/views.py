from django.shortcuts import render
from django.http import JsonResponse
# Create your views here.
from word2vec.use import compare

def word2vec(request):
    if request.method == "POST":
        sen1 = request.POST.get('sentence1')
        sen2 = request.POST.get('sentence2')
        res = compare(sen1, sen2)

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
