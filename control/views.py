from django.shortcuts import render
from django.http import HttpResponse
from .models import *
from ctypes import *
import os

# DWORD = unsigned long int
# python int == c long
#loaddll = cdll.LoadLibrary("C:\\Users\\yhb38\\Desktop\\EzSoftwareUC_V4.3.0.4163_20211109_General\\ReleaseFiles\\AXL(Library)\\Library\\64Bit\\AXL.dll")
if os.path.isfile('C:\\AXL.dll'):
    loaddll = cdll.LoadLibrary('./AXL.dll') # 불러오기 성공
else:
    print("there's no dll file")
# 초기화 함수 처리가 최우선!
def control_initialization(request):
    #라이브러리 초기화 여부 확인 (보드에 연결되지 않으면 초기화 안되는게 맞음)
    AxlOpenNoReset = loaddll['AxlOpenNoReset']
    # AxlOpenNoReset.argtypes=(c_int,)
    # AxlOpenNoReset.restype=(c_ulong)
    check = AxlOpenNoReset(7)
    
    if check == 1001: #AXT_RT_OPEN_ERROR
        #라이브러리 초기화 
        AxlOpen = loaddll['AxlOpen']
        # AxlOpen.argtypes=(c_int,)
        # AxlOpen.restype = (c_ulong)
        code = AxlOpen()  # 0000  함수실행 성공
                          # 1001  라이브러리가 오픈되지 않음
        if (code == 0000):
            print("초기화 성공")
        else:
            print("초기화 실패")

    return render(request, 'control/ready_to_control.html')

# 모션 모듈의 존재 여부 확인
def is_moduleExists():
    uStatus = c_ulong()
    AxmInfoIsMotionModule = loaddll['AxmInfoIsMotionModule']
    Code = AxmInfoIsMotionModule(pointer(uStatus))
    
    print("============================================")
    if Code == 0000:
        print("모듈 존재 : 모듈이 존재합니다")
    elif Code == 1053:
        print("모듈 존재 : AXL 라이브러리 초기화 실패")
    else:
        print("모듈 존재 : 알 수 없는 에러로 모듈의 존재를 확인할 수 없음")
    print("============================================")

    Axis_counter() # 축의 수 확인

    return Code

# 시스템에 장착된 축의 수 확인
def Axis_counter():
    AxmInfoGetAxisCount = loaddll['AxmInfoGetAxisCount']
    lAxisCount = c_long()
    AxisCount = AxmInfoGetAxisCount(pointer(lAxisCount)) 
    print("============================================")
    if AxisCount == 0000:
        print("시스템에 장착된 축 개수 : ", AxisCount)
    elif AxisCount == 1053:
        print("축 개수 : AXL 라이브러리 초기화 실패")
    elif AxisCount == 4051:
        print("축 개수 : 시스템에 장착된 모션 모듈이 없음")
    else:
        print("축 개수 : 알 수 없는 에러로 개수를 알 수 없음")
    print("============================================")

# 라이브러리 초기화 확인
def is_lib_open():
    AxlIsOpened = loaddll['AxlIsOpened']
    if AxlIsOpened():
        print("라이브러리가 초기화되어 있습니다.")
    else:
        print("라이브러리가 초기화되지 않았습니다.")

# 라이브러리 종료
def close_lib():
    AxlClose = loaddll['AxlClose']
    if (AxlClose()):
        print("라이브러리가 종료됨 : ",AxlClose())
    else:
        print("라이브러리가 종료되지 않음 : ",AxlClose())
 
def main(request):
    return render(request, 'control/control.html')

# 축 초기속도 설정
def set_startVel():
    startvel = loaddll['AxmMotSetMinVel']
    
    AxmMotSetMinVel = startvel(0,1) # 0축의 초기속도는 1
    print("초기 속도 : " , AxmMotSetMinVel)

# 해당 축이 사용 가능한지 확인, 제어 가능한지 확인
def isInvalidAxis(axis):
    AxmInfoIsInvalidAxisNo = loaddll['AxmInfoIsInvalidAxisNo']
    uReturn = AxmInfoIsInvalidAxisNo(axis)
    AxmInfoGetAxisStatus = loaddll['AxmInfoGetAxisStatus']
    isControl = AxmInfoGetAxisStatus(axis)

    if uReturn != 0000:
        print(uReturn," : 해당 축이 없음")
    else:
        if isControl != 0000:
            print(isControl, " : 제어 불가능")
        elif isControl == 0000:
            print(isControl, " : 제어 가능")

#################### (input)테스트해볼 4가지 함수 ####################
def AxmMovePos(request):
    is_lib_open()
    is_moduleExists()
    '''
    code = is_moduleExists()
    if code == 0000:
          .....
    else: 예외처리
    '''
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

    isInvalidAxis(int(mov.lAxisNo))
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

def AxmMoveStartPos(request): # + AxmStatusReadVel()
    is_lib_open()
    is_moduleExists()

    dVelocity = c_double()
    if request.method == 'POST':
        mov = MoveStartPos()
        mov.lAxisNo = request.POST['lAxisNo']
        mov.dPos = request.POST['dPos']
        mov.dVel = request.POST['dVel']
        mov.dAccel = request.POST['dAccel']
        mov.dDecel = request.POST['dDecel']
        mov.save()

    AxmMoveStartPos = loaddll['AxmMoveStartPos']
    AxmMoveStartPos.argtypes = (c_long, c_double, c_double, c_double, c_double)
    AxmMoveStartPos.restype = (c_ulong)

    isInvalidAxis(int(mov.lAxisNo))
    ResAxmMoveStartPos = AxmMoveStartPos(
        int(mov.lAxisNo), 
        float(mov.dPos), 
        float(mov.dVel), 
        float(mov.dAccel), 
        float(mov.dDecel)
    )
    print(ResAxmMoveStartPos)

    # AxmStatusReadVel
    AxmStatusReadVel = loaddll['AxmStatusReadVel']
    now_velocity = AxmStatusReadVel(int(mov.lAxisNo),pointer(dVelocity))
    print("속도 >>",now_velocity)

    return render(request, 'control/ready_to_control.html')

def AxmMoveVel(request):
    is_lib_open()
    is_moduleExists()

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

    isInvalidAxis(int(mov.lAxisNo))
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
    is_moduleExists()

    if request.method == 'POST':
        mov = MoveToAbsPos()
        mov.lAxisNo = request.POST['lAxisNo']
        mov.dPos = request.POST['dPos']
        mov.dVel = request.POST['dVel']
        mov.dAccel = request.POST['dAccel']
        mov.dDecel = request.POST['dDecel']
        mov.save()

    AxmMoveToAbsPos = loaddll['AxmMoveToAbsPos']
    AxmMoveToAbsPos.argtypes = (c_long, c_double, c_double, c_double, c_double)
    AxmMoveToAbsPos.restype = (c_ulong)
    
    isInvalidAxis(int(mov.lAxisNo))
    ResAxmMoveToAbsPos = AxmMoveToAbsPos(
        int(mov.lAxisNo), 
        float(mov.dPos), 
        float(mov.dVel), 
        float(mov.dAccel), 
        float(mov.dDecel)
    )
    print(ResAxmMoveToAbsPos)
    return render(request, 'control/ready_to_control.html')

#################### (output)테스트해볼 2가지 함수 ####################
# def AxmStatusReadMotionInfo(request):
#     pass

# def AxmStatusReadVel(axis):
#     velo = loaddll['AxmStatusReadVel']


