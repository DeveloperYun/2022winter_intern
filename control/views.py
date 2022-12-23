from django.shortcuts import render
from django.http import HttpResponse
from .models import *
from ctypes import *

loaddll = WinDLL('./AXL.dll') # 불러오기 성공

def is_lib_open():
    AxlIsOpened = loaddll['AxlIsOpened']
    if AxlIsOpened():
        print("라이브러리가 초기화되어 있습니다.")
    else:
        print("라이브러리가 초기화되지 않았습니다.")

def main(request):
    return render(request, 'control/control.html')

def control_initialization(request):
    #라이브러리 초기화 여부 확인 (보드에 연결되지 않으면 초기화 안되는게 맞음)
    AxlOpenNoReset = loaddll['AxlOpenNoReset']
    # AxlOpenNoReset.argtypes=(c_int,)
    # AxlOpenNoReset.restype=(c_ulong)
    check = AxlOpenNoReset(7)
    
    if check == 1001: #AXT_RT_OPEN_ERROR
        #라이브러리 초기화 (DWORD = unsigned long int)
        AxlOpen = loaddll['AxlOpen']
        # AxlOpen.argtypes=(c_int,)
        # AxlOpen.restype = (c_ulong)
        code = AxlOpen()
        print(code)

        # 0000  함수실행 성공
        # 1001  라이브러리가 오픈되지 않음
        if (code == 0000):
            print("초기화 성공")
        else:
            print("초기화 실패")

    return render(request, 'control/ready_to_control.html')

def AxmMovePos(request):
    is_lib_open()

    if request.method == 'POST':
        mov = MovePos()
        mov.lAxisNo = request.POST['lAxisNo']
        mov.dPos = request.POST['dPos']
        mov.dVel = request.POST['dVel']
        mov.dAccel = request.POST['dAccel']
        mov.dDecel = request.POST['dDecel']
        mov.save()
    
    #print(type(mov.lAxisNo)) # type이 <class 'str'>
    #move
    AxmMovePos = loaddll['AxmMovePos']
    AxmMovePos.argtypes = (c_long, c_double, c_double, c_double, c_double)
    AxmMovePos.restype = (c_ulong)

    ResAxmMovePos = AxmMovePos(
        int(mov.lAxisNo), 
        float(mov.dPos), 
        float(mov.dVel), 
        float(mov.dAccel), 
        float(mov.dDecel)
    )
    print(ResAxmMovePos)

    #임시 템플릿
    return render(request, 'control/ready_to_control.html')

def AxmMoveStartPos(request):
    is_lib_open()

    if request.method == 'POST':
        mov = MovePos()
        mov.lAxisNo = request.POST['lAxisNo']
        mov.dPos = request.POST['dPos']
        mov.dVel = request.POST['dVel']
        mov.dAccel = request.POST['dAccel']
        mov.dDecel = request.POST['dDecel']
        mov.save()

    AxmMoveStartPos = loaddll['AxmMoveStartPos']
    AxmMoveStartPos.argtypes = (c_long, c_double, c_double, c_double, c_double)
    AxmMoveStartPos.restype = (c_ulong)
    ResAxmMoveStartPos = AxmMoveStartPos(
        int(mov.lAxisNo), 
        float(mov.dPos), 
        float(mov.dVel), 
        float(mov.dAccel), 
        float(mov.dDecel)
    )
    print(ResAxmMoveStartPos)
    return render(request, 'control/ready_to_control.html')

def AxmMoveVel(request):
    is_lib_open()

    if request.method == 'POST':
        mov = MoveVel()
        mov.lAxisNo = request.POST['lAxisNo']
        mov.dVel = request.POST['dVel']
        mov.dAccel = request.POST['dAccel']
        mov.dDecel = request.POST['dDecel']
        mov.save()

    AxmMoveVel = loaddll['AxmMoveVel']
    AxmMoveVel.argtypes = (c_long, c_double, c_double, c_double)
    AxmMoveVel.restype = (c_ulong)

    ResAxmMoveVel = AxmMoveVel(
        int(mov.lAxisNo), 
        float(mov.dVel), 
        float(mov.dAccel), 
        float(mov.dDecel)
    )
    print(ResAxmMoveVel)
    return render(request, 'control/ready_to_control.html')

def AxmMoveToAbsPos(request):
    is_lib_open()

    if request.method == 'POST':
        mov = MovePos()
        mov.lAxisNo = request.POST['lAxisNo']
        mov.dPos = request.POST['dPos']
        mov.dVel = request.POST['dVel']
        mov.dAccel = request.POST['dAccel']
        mov.dDecel = request.POST['dDecel']
        mov.save()

    AxmMoveToAbsPos = loaddll['AxmMoveToAbsPos']
    AxmMoveToAbsPos.argtypes = (c_long, c_double, c_double, c_double, c_double)
    AxmMoveToAbsPos.restype = (c_ulong)
    
    ResAxmMoveToAbsPos = AxmMoveToAbsPos(
        int(mov.lAxisNo), 
        float(mov.dPos), 
        float(mov.dVel), 
        float(mov.dAccel), 
        float(mov.dDecel)
    )
    print(ResAxmMoveToAbsPos)
    return render(request, 'control/ready_to_control.html')

