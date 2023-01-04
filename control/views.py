from django.shortcuts import render
from django.http import HttpResponse
from .models import *
from ctypes import *

# DWORD = unsigned long int
# python int == c long

loaddll = PyDLL('./AXL.dll') # 불러오기 성공

############################## 초기화 함수 처리가 최우선! ##############################
# control initialization 버튼 누르자마자 아래 함수가 처음 실행
def control_initialization(request):
    #라이브러리 초기화 (보드에 연결되지 않으면 초기화 안되는게 맞음)
    
    if is_lib_open() == False:
        print("라이브러리 초기화는 처음이에요")
        AxlOpen = loaddll['AxlOpen']
        # AxlOpen.argtypes=(c_int,)
        # AxlOpen.restype = (c_ulong)
        code = AxlOpen()  # 0000  함수실행 성공
                        # 1001  라이브러리가 오픈되지 않음
        if (code == 0000):
            print("초기화 성공")
        else:
            print("초기화 실패")
    else:
        print("라이브러리 초기화가 처음이 아니에요")
        open_no_reset()
    
    return render(request, 'control/ready_to_control.html')


def open_no_reset():

    AxlOpenNoReset = loaddll['AxlOpenNoReset'] 
    reopen = AxlOpenNoReset()

    if(reopen == 0000):
        print("재 초기화 성공 : 기존값 유지")
    else:
        print("재 초기화 실패")


# 라이브러리 초기화 확인
def is_lib_open():
    AxlIsOpened = loaddll['AxlIsOpened']

    if AxlIsOpened:
        print("라이브러리가 초기화되어 있습니다.")
        return AxlIsOpened
    else:
        print("라이브러리가 초기화되지 않았습니다.")
        return AxlIsOpened


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

# 시스템에 장착된 축의 수 및 정보 확인
def Axis_counter():
    # 장착된 축의 개수 확인
    lAxisCount = c_long()
    AxmInfoGetAxisCount = loaddll['AxmInfoGetAxisCount']
    AxisCount = AxmInfoGetAxisCount(pointer(lAxisCount))
    print(lAxisCount) 
    print("============================================")
    if AxisCount == 0000:
        print("시스템에 장착된 축 개수 : ", lAxisCount)
    elif AxisCount == 1053:
        print("축 개수 : AXL 라이브러리 초기화 실패")
    elif AxisCount == 4051:
        print("축 개수 : 시스템에 장착된 모션 모듈이 없음")
    else:
        print("축 개수 : 알 수 없는 에러로 개수를 알 수 없음")
    print("============================================")

    # 지정 베이스 보드의 지정 모듈에서 첫 번째 축 번호를 확인
    lBoardNo, lModulsPos = 0, 0
    lFirstAxisNo = c_long()
    AxmInfoGetFirstAxisNo = loaddll['AxmInfoGetFirstAxisNo']
    firstAxis = AxmInfoGetFirstAxisNo(lBoardNo,lModulsPos,pointer(lFirstAxisNo))
    print("0번 베이스 보드의 1번째 모듈의 시작 축 번호 : ", firstAxis)
    print("============================================")

# 해당 축이 사용 가능한지 확인, 제어 가능한지 확인
def isInvalidAxis(axis):
    AxmInfoIsInvalidAxisNo = loaddll['AxmInfoIsInvalidAxisNo']
    uReturn = AxmInfoIsInvalidAxisNo(axis)
    AxmInfoGetAxisStatus = loaddll['AxmInfoGetAxisStatus']
    isControl = AxmInfoGetAxisStatus(axis)

    if uReturn != 0000:
        print(uReturn," : 해당 축이 없음")
    else:
        print(axis," 번 축은 사용할 수 있음")
        if isControl != 0000:
            print(isControl, " : 제어 불가능")
        elif isControl == 0000:
            print(isControl, " : 제어 가능")

# 라이브러리 종료
def close_lib():
    AxlClose = loaddll['AxlClose']
    if (AxlClose()):
        print("라이브러리가 종료됨 : ",AxlClose())
    else:
        print("라이브러리가 종료되지 않음 : ",AxlClose())
 
#############################################################################################

####TODO:########################## 서보모터(모션 파라미터) #################################

# 축 초기속도 설정
def set_startVel():
    startvel = loaddll['AxmMotSetMinVel']
    
    AxmMotSetMinVel = startvel(0,1) # 0축의 초기속도는 1
    print("초기 속도 : " , AxmMotSetMinVel)


def set_moveUnitPerPulse():
    pass












#############################################################################################

def main(request):
    return render(request, 'control/control.html')





#################### (input)테스트해볼 4가지 함수 ####################
# AxmMoveStartPos, AxmMoveToAbsPos table에러 발생

def AxmMovePos(request):
    is_lib_open()
    is_moduleExists()
    
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


