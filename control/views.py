from django.shortcuts import render
from django.http import HttpResponse
from .models import *
from ctypes import *

# DWORD = unsigned long int
# python int == c long
# 제품명 : PCIe-Rxx05-MLIII (네트워크)
# set~ : setting함수 (보통)

loaddll = PyDLL('./AXL.dll') # 불러오기 성공

############################## 기타 정보 #####################################
def board_count():
    lBoardCounts = c_long()
    AxlGetBoardCount = loaddll['AxlGetBoardCount']
    
    if AxlGetBoardCount(pointer(lBoardCounts)):
        print("보드 개수 : ",lBoardCounts)
    else:
        print("라이브러리 초기화 안됨")

def board_status():
    uReturn = c_ulong()
    AxlGetBoardStatus = loaddll['AxlGetBoardStatus']

    uReturn = AxlGetBoardStatus(0)
    if uReturn:
        print("0번 보드 문제발생: ",uReturn)
    else:
        print("0번 보드 정상적으로 초기화됨")

    uReturn = AxlGetBoardStatus(1)
    if uReturn:
        print("1번 보드 문제발생: ",uReturn)
    else:
        print("1번 보드 정상적으로 초기화됨")

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

####TODO:##########################  모션 구동의 용어 해설  #################################

# 이건 low 혹은 high를 serve on 으로 받아들이겠다를 셋팅하는 함수이다.
# 자꾸 1053 에러가 뜬 것은 해당 기기가 디폴트로 low 혹은 high...를 받는데 바꾸라고 해서 에러가 떴을 확률이 있다.

def signalset_servo_on_level(axis):
    #FIXME: 0으로 설정됨
    AxmSignalSetServoOnLevel = loaddll['AxmSignalSetServoOnLevel']
    AxmSignalGetServoOnLevel = loaddll['AxmSignalGetServoOnLevel']

    res_AxmSignalSetServoOnLevel = AxmSignalSetServoOnLevel(axis, 1) # axis 축에 레벨설정
    if res_AxmSignalSetServoOnLevel == 0000:
        print("servo on 레벨 설정 성공 : ",res_AxmSignalSetServoOnLevel)
    elif res_AxmSignalSetServoOnLevel == 4053:
        print("해당 축 모션 초기화 실패")
    elif res_AxmSignalSetServoOnLevel == 4101:
        print("해당 축이 존재하지 않음")

    uLevel = c_ulong()
    AxmSignalGetServoOnLevel(axis, pointer(uLevel))
    print("설정한 Servo-On level : ",uLevel)

def signal_servo_on(axis):
    AxmSignalServoOn = loaddll['AxmSignalServoOn']
    AxmSignalIsServoOn = loaddll['AxmSignalIsServoOn']

    level = c_ulong()
    res_AxmSignalServoOn = AxmSignalServoOn(axis,1) #  Enable = 1, Disable = 0
    AxmSignalIsServoOn(axis, pointer(level))

    if res_AxmSignalServoOn == 0000:
        print("servo on 성공 : ",level)
    elif res_AxmSignalServoOn == 4053:
        print("해당 축 모션 초기화 실패")
    elif res_AxmSignalServoOn == 4101:
        print("해당 축이 존재하지 않음")
    


#############################################################################################

####TODO:########################## 서보모터(모션 파라미터) #################################
#FIXME: pulseout_method, Encoder_input_method : 1054(지원하지 않는 하드웨어)
#FIXME: lpPulse = 10000, dpunit = 5e-323 , 초기속도 = 4.94e-322 

# unit per pulse
def set_moveUnitPerPulse(axis):
    lAxisNo = axis
    lPulse = 10000 # 1회전을 위한 펄스 수
    dUnit = 10 # 1회전시 이동 거리

    lpPulse = c_long()
    dpUnit = c_double()

    AxmMotSetMoveUnitPerPulse = loaddll['AxmMotSetMoveUnitPerPulse']
    AxmMotGetMoveUnitPerPulse = loaddll['AxmMotGetMoveUnitPerPulse']
    setpulse = AxmMotSetMoveUnitPerPulse(lAxisNo,dUnit,lPulse)
    getpulse = AxmMotGetMoveUnitPerPulse(lAxisNo,pointer(dpUnit),pointer(lpPulse))

    if setpulse == 0000:
        print("unit per pulse 단위 적용")
    elif setpulse == 4053:
        print("unit per pulse : 해당 축 모션 초기화 실패")
    elif setpulse == 4254:
        print("unit per pulse : 구동 단위 값이 0으로 설정됨")
    else:
        print("알 수 없는 이유로 unit per pulse 설정이 실패함")

    
    if getpulse == 0000:
        print("lpPulse : ",lpPulse, ", ","dpunit : ",dpUnit)
    elif getpulse == 4053:
        print("unit per pulse : 해당 축 모션 초기화 실패")
    elif getpulse == 4254:
        print("unit per pulse : 구동 단위 값이 0으로 설정됨")
    else:
        print("알 수 없는 이유로 unit per pulse 설정이 실패함")

# 축 초기속도 설정( start speed )
def set_startVel(axis):
    startvel = loaddll['AxmMotSetMinVel']
    check_vel = loaddll['AxmMotGetMinVel']

    MinVelocity = c_double()
    
    # 초기속도 단위는 unit per pulse가 1/1인 경우의 초당 펄스
    AxmMotSetMinVel = startvel(axis,100) # [axis]축의 초기속도는 1
    AxmMotGetMinVel = check_vel(axis, pointer(MinVelocity))

    if AxmMotSetMinVel == 0000:
        print("초기 속도 : " , MinVelocity)
    elif AxmMotSetMinVel == 4053:
        print("start speed : 해당 축 모션 초기화 실패")
    elif AxmMotSetMinVel == 4101:
        print("start speed : 해당 축이 존재하지 않음")
    else:
        print("알 수 없는 이유로 초기속도 설정에 실패함")

'''
# PulseOut Method 
def pulseout_method(axis):
    AxmMotSetPulseOutMethod = loaddll['AxmMotSetPulseOutMethod']
    AxmMotGetPulseOutMethod = loaddll['AxmMotGetPulseOutMethod']

    uMethod = c_ulong()
    # axis 축의 펄스 출력 방식을 OneLowHighLow 로 설정
    res_AxmMotSetPulseOutMethod = AxmMotSetPulseOutMethod(axis, 0x6) # OneLowHighLow = 0x3
    if res_AxmMotSetPulseOutMethod == 0000:
        print("pulseout_method : 설정 완료")
        # 설정 값 잘 들어갔나 확인
        AxmMotGetPulseOutMethod(axis, pointer(uMethod))
        print("pulseout_method : ",uMethod)
    elif res_AxmMotSetPulseOutMethod == 4053:
        print("pulseout_method : 해당 축 모션 초기화 실패")
    elif res_AxmMotSetPulseOutMethod == 4101:
        print("pulseout_method : 해당 축이 존재하지 않음")
    else:
        print("알 수 없는 이유로 펄스 출력 방식이 설정되지 않음. ErrorCode: ",res_AxmMotSetPulseOutMethod)

# Encoder Input Method
def Encoder_input_method(axis):
    AxmMotSetEncInputMethod = loaddll['AxmMotSetEncInputMethod']
    AxmMotGetEncInputMethod = loaddll['AxmMotGetEncInputMethod']

    Method = c_ulong()

    # ObverseSqr4Mode 설정
    res_AxmMotSetEncInputMethod = AxmMotSetEncInputMethod(axis, 0x3) # 정방향 4체배
    if res_AxmMotSetEncInputMethod == 0000:
        print("Encoder_input_method : 설정 완료")
        AxmMotGetEncInputMethod(axis, pointer(Method))
        print("Encoder_input_method : ", Method)
    elif res_AxmMotSetEncInputMethod == 4053:
        print("Encoder_input_method : 해당 축 모션 초기화 실패")
    elif res_AxmMotSetEncInputMethod == 4101:
        print("Encoder_input_method : 해당 축이 존재하지 않음")
    else:
        print("알 수 없는 이유로 인코더 인풋 메소드가 설정되지 않음. ErrorCode: ",res_AxmMotSetEncInputMethod) 
'''
#############################################################################################


####TODO:##########################      모션 신호 설정     #################################


#############################################################################################
def main(request):
    return render(request, 'control/control.html')
################################# (input)테스트해볼 4가지 함수 ###############################
#TODO: AxmMovePos 함수 하나 구동될 때 까지 test
def AxmMovePos(request):
    print("================= 보드 상태 확인 =================")
    board_status()
    board_count()
    print("==================================================")

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

    set_moveUnitPerPulse(int(mov.lAxisNo))
    set_startVel(int(mov.lAxisNo))
    #signalset_servo_on_level(int(mov.lAxisNo))
    signal_servo_on(int(mov.lAxisNo))
    '''
    pulseout_method(int(mov.lAxisNo))
    Encoder_input_method(int(mov.lAxisNo))
    '''
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
    print("================= 보드 상태 확인 =================")
    board_status()
    board_count()
    print("==================================================")

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

    set_moveUnitPerPulse(int(mov.lAxisNo))
    set_startVel(int(mov.lAxisNo))
    #signalset_servo_on_level(int(mov.lAxisNo))
    signal_servo_on(int(mov.lAxisNo))

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


