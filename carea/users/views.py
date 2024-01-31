from django.shortcuts import render, redirect
from django.contrib.auth import logout

# home 함수를 정의하고, 요청을 받아서 렌더링하고, home.html 템플릿을 사용한다.
def home(request):
    return render(request, 'home.html')

def logout_view(request):
    logout(request)
    return redirect('/')