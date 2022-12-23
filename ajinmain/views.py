from django.shortcuts import render
from django.http import HttpResponse

def index(request):
    # HttpResponse는 요청에 대한 응답을 할때 사용한다
    return render(request, 'ajinmain/ajinmain.html')