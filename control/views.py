import gc
from random import randint
from django.shortcuts import render
from django.http import HttpResponse
from .models import *
from ctypes import *
from channels.generic.websocket import WebsocketConsumer
import json
from time import sleep
from django.contrib.auth.models import User

'''
DWORD = unsigned long int
python int == c long
'''
loaddll = PyDLL('./AXL.dll') # 불러오기 성공
axis = 0

def main(request):
    return render(request, 'control/ready_to_control.html')

##############################       보드 정보       #####################################
def board_count():
    lBoardCounts = c_long()
    AxlGetBoardCount = loaddll['AxlGetBoardCount']
    
    if AxlGetBoardCount(pointer(lBoardCounts)):
        print("보드 개수 : ",lBoardCounts.value)
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
    users = User.objects.all()

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
    
    result = show_boards() # 축 정보 #result 는 str
    return render(request, 'control/ready_to_control.html', {'users':users , 'result':result})

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
        print("AxlIsOpened : 라이브러리가 초기화되어 있습니다.")
        return AxlIsOpened
    else:
        print("AxlIsOpened : 라이브러리가 초기화되지 않았습니다.")
        return AxlIsOpened

# 모션 모듈의 존재 여부 확인
def is_moduleExists():
    uStatus = c_ulong()
    AxmInfoIsMotionModule = loaddll['AxmInfoIsMotionModule']
    Code = AxmInfoIsMotionModule(pointer(uStatus))
    
    print("============================================")
    if uStatus.value == 1 and Code == 0000:
        print("모듈 존재 : 모듈이 존재합니다")
    elif uStatus.value == 0 and Code == 0000:
        print("모듈이 없습니다")
    elif Code == 1053:
        print("모듈 존재 : AXL 라이브러리 초기화 실패")
    else:
        print("모듈 존재 : 알 수 없는 에러로 모듈의 존재를 확인할 수 없음. Error:", uStatus.value, Code)
    print("============================================")

    Axis_counter() # 축의 수 확인

    return Code

# 지정 축의 보드 번호, 모듈 위치, 모듈 아이디 확인
def info_get_axis(axis):
    AxmInfoGetAxis = loaddll['AxmInfoGetAxis']
    lBoardNo, lModulePos = c_long(), c_long()
    uModuleID = c_ulong()

    res = AxmInfoGetAxis(axis, pointer(lBoardNo),pointer(lModulePos),pointer(uModuleID))
    print("============================================")
    if res==0000:
        print(axis,"번축의 보드 번호, 모듈위치, 모듈아이디: ",lBoardNo.value, ", ",lModulePos.value,", ",uModuleID.value)
        return uModuleID.value
    elif res == 4053:
        print("해당 축 모션 초기화 실패")
    elif res == 4101:
        print("해당 축이 존재하지 않음")
    else:
        print("뭔지 모를 이유로 0번 축의 보드/모듈정보 읽기 실패")

    if is_lib_open():
        print("lib 초기화 되어있음")
    else:
        print("lib 초기화되지 않았음")
    print("============================================")

# 시스템에 장착된 축의 수 및 정보 확인
def Axis_counter():
    # 장착된 축의 개수 확인
    lAxisCount = c_long()
    AxmInfoGetAxisCount = loaddll['AxmInfoGetAxisCount']
    AxisCount = AxmInfoGetAxisCount(pointer(lAxisCount))
    print("============================================")
    if AxisCount == 0000:
        print("시스템에 장착된 축 개수 : ", lAxisCount.value," 개")
    elif AxisCount == 1053:
        print("축 개수 : AXL 라이브러리 초기화 실패")
    elif AxisCount == 4051:
        print("축 개수 : 시스템에 장착된 모션 모듈이 없음")
    else:
        print("축 개수 : 알 수 없는 에러로 개수를 알 수 없음")
    print("============================================")

    return lAxisCount.value
    '''
    # 지정 베이스 보드의 지정 모듈에서 첫 번째 축 번호를 확인
    lBoardNo, lModulsPos = 1, 0
    lFirstAxisNo = c_long()
    AxmInfoGetFirstAxisNo = loaddll['AxmInfoGetFirstAxisNo']
    firstAxis = AxmInfoGetFirstAxisNo(lBoardNo,lModulsPos,pointer(lFirstAxisNo))

    if firstAxis == 0000:
        print("1번 베이스 보드의 0번째 모듈의 시작 축 번호 : ", lFirstAxisNo.value)
    elif firstAxis == 1053:
        print("AxmInfoGetFirstAxisNo : AXL lib 초기화 실패")
    elif firstAxis == 1101:
        print("AxmInfoGetFirstAxisNo : 유효하지 않은 보드 번호")
    else:
        print("AxmInfoGetFirstAxisNo : 알 수 없는 이유로 에러")
    print("============================================")
    '''

# 해당 축이 사용 가능한지 확인
def isInvalidAxis(axis):
    AxmInfoIsInvalidAxisNo = loaddll['AxmInfoIsInvalidAxisNo']
    uReturn = AxmInfoIsInvalidAxisNo(axis)

    if uReturn != 0000:
        # print(uReturn," : 해당 축이 없음")
        return False
    else:
        #print(axis," 번 축은 사용할 수 있음")
        return True

# 해당 축의 제어 가능 여부 반환
def get_axis_status(axis):
    AxmInfoGetAxisStatus = loaddll['AxmInfoGetAxisStatus']
    isControl = AxmInfoGetAxisStatus(axis)

    if isControl != 0000:
        #print(isControl, " : 제어 불가능")
        return False
    elif isControl == 0000:
        #print(isControl, " : 제어 가능")
        return True

#TODO: 장착된 축들의 상태를 화면에 출력해줄 것
def show_boards():
    axis_count = Axis_counter() # 축의 개수 
    response = []

    # 장착된 축의 개수만큼 0~n 번 축이 배정되므로 이렇게 하면 빠짐없이 검사가 가능하다.
    for i in range(axis_count):
        valid = isInvalidAxis(i) # 해당 축의 사용가능 여부에 따라
        if valid == True:
            control_valid = get_axis_status(i) # 사용 가능하다면 제어 가능 여부 파악
            if control_valid == True:
                print(i, "는 제어 가능한 상태")
                response.append(str(i)+" 축은 제어 가능한 상태")
            else:
                print(i, "는 제어 불가능한 상태")
                response.append(str(i)+" 축은 제어 불가능한 상태")
        else:
            response.append(str(i)+" 축은 사용 불가능한 상태")


    # str = ''
    # separtor = ','
    # for idx, val in enumerate(response):
    #     str += val + ('' if idx == len(response) -1 else separtor)

    # print(str)
    return response

# 라이브러리 종료
def close_lib():
    AxlClose = loaddll['AxlClose']
    if (AxlClose()):
        print("라이브러리가 종료됨 : ",AxlClose())
    else:
        print("라이브러리가 종료되지 않음 : ",AxlClose())
 
##############################  모션 구동의 용어 해설  #################################

# 이건 low 혹은 high를 serve on 으로 받아들이겠다를 셋팅하는 함수이다.
def signal_servo_on(request):
    users = User.objects.all()

    if request.method == 'POST':
        lAxisNo = int(request.POST.get('lAxisNo'))

    AxmSignalServoOn = loaddll['AxmSignalServoOn']
    AxmSignalIsServoOn = loaddll['AxmSignalIsServoOn']

    level = c_ulong()


    res_AxmSignalServoOn = AxmSignalServoOn(lAxisNo,1) #  Enable = 1, Disable = 0
    AxmSignalIsServoOn(lAxisNo, pointer(level))

    if res_AxmSignalServoOn == 0000:
        print("servo on 성공(0-off,1-on) : ", "on" if level.value==1 else "off")
    elif res_AxmSignalServoOn == 4053:
        print("해당 축 모션 초기화 실패")
    elif res_AxmSignalServoOn == 4101:
        print("해당 축이 존재하지 않음")
    else:
        print(lAxisNo, "서브온 실패")

    return render(request, 'control/ready_to_control.html',{'users':users})
    
def signal_servo_off(request):
    users = User.objects.all()

    if request.method == 'POST':
        lAxisNo = int(request.POST.get('lAxisNo'))

    AxmSignalServoOn = loaddll['AxmSignalServoOn']
    AxmSignalIsServoOn = loaddll['AxmSignalIsServoOn']

    level = c_ulong()

    res_AxmSignalServoOn = AxmSignalServoOn(lAxisNo,0) #  Enable = 1, Disable = 0
    AxmSignalIsServoOn(lAxisNo, pointer(level))

    if res_AxmSignalServoOn == 0000:
        print("servo on 성공(0-off,1-on) : ", "on" if level.value==1 else "off")
    elif res_AxmSignalServoOn == 4053:
        print("해당 축 모션 초기화 실패")
    elif res_AxmSignalServoOn == 4101:
        print("해당 축이 존재하지 않음")
    else:
        print(lAxisNo, "servo off 실패")

    return render(request, 'control/ready_to_control.html',{'users':users})
    
############################## 서보모터(모션 파라미터) #################################

# unit per pulse(프로그램상 지령값을 펄스 단위로 설정)
def set_moveUnitPerPulse(axis):
    #FIXME: dUnit = 1.000000 # 1회전시 이동 거리
    # lPulse = 1 # 1회전을 위한 펄스 수
    # dUnit = 1 # 1회전시 이동 거리

    lpPulse = c_double()
    dpUnit = c_long()

    AxmMotSetMoveUnitPerPulse = loaddll['AxmMotSetMoveUnitPerPulse']
    AxmMotGetMoveUnitPerPulse = loaddll['AxmMotGetMoveUnitPerPulse']

    AxmMotSetMoveUnitPerPulse.argtypes=[c_long,c_double,c_long]
    setpulse = AxmMotSetMoveUnitPerPulse(axis,1,1)
    getpulse = AxmMotGetMoveUnitPerPulse(axis,pointer(dpUnit),pointer(lpPulse))
    if setpulse == 0000 and getpulse == 0000:
        print("unit per pulse 단위 적용 >> lpPulse : ",lpPulse.value, ", ","dpunit : ",dpUnit.value) # 0축의 움직이는 거리당 출력되는 펄스 수를 반환한다.
    elif setpulse == 4053:
        print("unit per pulse : 해당 축 모션 초기화 실패")
    elif setpulse == 4254:
        print("unit per pulse : 구동 단위 값이 0으로 설정됨")
    else:
        print("알 수 없는 이유로 unit per pulse 설정이 실패함")

# 축 초기속도 설정( start speed )
def set_startVel(axis):
    startvel = loaddll['AxmMotSetMinVel']
    check_vel = loaddll['AxmMotGetMinVel']

    MinVelocity = c_int()
    
    # 초기속도 단위는 unit per pulse가 1/1인 경우의 초당 펄스
    AxmMotSetMinVel = startvel(axis,1) # [axis]축의 초기속도는 1
    AxmMotGetMinVel = check_vel(axis, pointer(MinVelocity))

    if AxmMotSetMinVel == 0000 and AxmMotGetMinVel == 0000:
        print("초기 속도 : " , MinVelocity.value)
    elif AxmMotSetMinVel == 4053:
        print("start speed : 해당 축 모션 초기화 실패")
    elif AxmMotSetMinVel == 4101:
        print("start speed : 해당 축이 존재하지 않음")
    else:
        print("알 수 없는 이유로 초기속도 설정에 실패함")

##############################      모션 신호 설정      ################################
# 현재 알람 상태 확인
def signal_read_servo_alarm(axis):
    upStatus = c_ulong()
    AxmSignalReadServoAlarm = loaddll['AxmSignalReadServoAlarm']

    res = AxmSignalReadServoAlarm(axis, pointer(upStatus))
    if res == 0000:
        print("0축 알람 신호 : ", "활성화" if upStatus.value==0 else "비활성화")
    else:
        print("알람 신호를 알 수 없음. ErrorCode : ",res)

# 알람 발생 원인 제거 후 현재 알람 상태 벗어남
def signal_servo_alarm_Reset(axis):
    AxmSignalServoAlarmReset = loaddll['AxmSignalServoAlarmReset']

    # 0축에 Servo Alarm Reset
    resetalarm = AxmSignalServoAlarmReset(axis,1) #ENABLE = 1
    if resetalarm == 0000:
        print("alarm reset 성공")
    elif resetalarm == 4053:
        print("해당 축 모션 초기화 실패")
    elif resetalarm == 4101:
        print("해당 축이 존재하지 않음")
    else:
        print("뭔지 모를 이유로 알람 리셋 실패")

# 지정 축의 외부 센서 및 모터 관련 신호들의 상태를 반환한다
def status_read_sensor(axis):
    status = c_ulong()
    AxmStatusReadMechanical = loaddll['AxmStatusReadMechanical']

    res = AxmStatusReadMechanical(axis, pointer(status))
    if res == 0000:
        print("센서 감지 상태 : ",status.value)
    else:
        print("센서 상태 읽어올 수 없음")

# 알람 신호 읽기 (지정 축의 리미트 센서 신호의 입력상태를 반환)
def signal_read_limit(axis):
    uPositiveStatus, uNegativeStatus = c_ulong(), c_ulong()
    AxmSignalReadLimit = loaddll['AxmSignalReadLimit']
    res = AxmSignalReadLimit(axis,pointer(uPositiveStatus),pointer(uNegativeStatus))

    if res==0000:
        print("지정 축의 리미트 센서 신호 읽기 성공(0-비활성화,1-활성화)")
        print("센서가 감지되지 않았는데도 현재 상태가 1로 반환된다면 현재 설정된 Active Level이 센서 입력상태와 반대로 설정.")
        print("(+) 리미트 센서 신호 입력 상태 uPositiveStatus : ",uPositiveStatus.value)
        print("(-) 리미트 센서 신호 입력 상태 uNegativeStatus : ",uNegativeStatus.value)
    elif res == 4053:
        print("해당 축 모션 초기화 실패")
    elif res == 4101:
        print("해당 축이 존재하지 않음")
    else:
        print("뭔지 모를 이유로 알람 읽기 실패")

# 지정 축의 Inpositon 신호의 입력 상태를 반환한다.
def signal_read_inpos(axis):
    upStatus = c_ulong()
    AxmSignalReadInpos = loaddll['AxmSignalReadInpos']
    res = AxmSignalReadInpos(axis, pointer(upStatus))

    if res==0000: #활성화 된 상태
        print("지정 축의 inposition 신호 읽기 성공(0-비활성화,1-활성화) : ",upStatus.value)
    elif res == 4053:
        print("해당 축 모션 초기화 실패")
    elif res == 4101:
        print("해당 축이 존재하지 않음")
    else:
        print("뭔지 모를 이유로 inposition 읽기 실패")

# 지정 축의 InPos 신호 Range 결정
def signal_set_inpos_range(axis):
    #FIXME: 뭔지 모를 이유로 inpos 신호 범위 결정 실패
    AxmSignalSetInposRange = loaddll['AxmSignalSetInposRange']
    AxmSignalGetInposRange = loaddll['AxmSignalGetInposRange']

    dInposRange = c_double()
    res = AxmSignalSetInposRange(axis, 10) # axis의 inpos range는 10
    AxmSignalGetInposRange(axis,pointer(dInposRange))
    if res == 0000:
        print("0번축 inpos 신호 범위 설정 10 : ",dInposRange)
    elif res == 4053:
        print("해당 축 모션 초기화 실패")
    elif res == 4101:
        print("해당 축이 존재하지 않음")
    else:
        print("뭔지 모를 이유로 inpos 신호 범위 결정 실패")
    
# 지정 축의 InPos 신호 사용 여부 결정
def signal_set_inpos(axis):
    AxmSignalSetInpos = loaddll['AxmSignalSetInpos']
    AxmSignalGetInpos = loaddll['AxmSignalGetInpos']
    uUse = c_ulong()

    res = AxmSignalSetInpos(axis, 0) #High로 설정
    AxmSignalGetInpos(axis, pointer(uUse))

    if res == 0000:
        print("0번축 inpos 신호 : ",uUse.value)
    elif res == 4053:
        print("해당 축 모션 초기화 실패")
    elif res == 4101:
        print("해당 축이 존재하지 않음")
    else:
        print("뭔지 모를 이유로 inpos 신호 사용 결정 실패")

# 지정 축의 리미트 센서 사용 유무 및 신호 action level 설정 (설정되는거 확인함)
def signal_set_limit(axis):
    AxmSignalSetLimit = loaddll['AxmSignalSetLimit']
    AxmSignalGetLimit = loaddll['AxmSignalGetLimit']

    uStopMode, uPositiveLevel, uNegativeLevel = c_ulong(), c_ulong(), c_ulong()
    res = AxmSignalSetLimit(axis, 0, 2, 2) #급정지, 사용안함 , 안함
    AxmSignalGetLimit(axis,pointer(uStopMode),pointer(uPositiveLevel),pointer(uNegativeLevel))

    if res == 0000:
        print("리미트 센서 : ", uStopMode.value,", ", 
                               uPositiveLevel.value,", ", 
                               uNegativeLevel.value)
    elif res == 4053:
        print("해당 축 모션 초기화 실패")
    elif res == 4101:
        print("해당 축이 존재하지 않음")
    else:
        print("뭔지 모를 이유로 signal_set_limit 결정 실패. Error: ",res)

#############################################################################################
##################################### 구동 전처리 함수 #######################################

# 원점 검색(AxmHomeSetMethod, AxmHomeSetVel 로 설정 후 AxmHomeSetStart 호출, 검색시작)
def mot_set_home_start(axis):
    AxmHomeSetMethod = loaddll['AxmHomeSetMethod']
    AxmHomeSetVel = loaddll['AxmHomeSetVel']
    AxmHomeSetStart = loaddll['AxmHomeSetStart']
    AxmHomeGetResult = loaddll['AxmHomeGetResult']
    AxmHomeGetRate = loaddll['AxmHomeGetRate']

    
    uHomeResult = c_ulong()
    uHomeStepNumber,uHomeMainStepNumber = c_ulong(), c_ulong()

    AxmHomeSetMethod.argtypes=[c_long,c_long,c_ulong,c_ulong,c_double,c_double]
    AxmHomeSetVel.argtypes=[c_long,c_double,c_double,c_double,c_double,c_double,c_double]

    AxmHomeSetMethod(axis,0,4,0,1000,0)
    AxmHomeSetVel(axis,60000, 3000, 1000, 50, 20000, 80000)

    AxmHomeSetStart(axis)

    while True:
        AxmHomeGetResult(axis,pointer(uHomeResult))

        if uHomeResult.value == 2:
            #진행률 확인
            AxmHomeGetRate(axis,pointer(uHomeMainStepNumber),pointer(uHomeStepNumber))
            print("현재 원점 검색 진행률 : ",uHomeStepNumber.value," %")
            sleep(1)
        elif uHomeResult.value == 1:
            AxmHomeGetRate(axis,pointer(uHomeMainStepNumber),pointer(uHomeStepNumber))
            print("현재 원점 검색 진행률 : ",uHomeStepNumber.value," %")
            sleep(1)
            print("원점 검색 완료")
            break
        else:
            print("이외의 에러로 종료")
            break

# 절대/상대모드 선택 : 원점 검색 필수
def mot_set_abs_mode(axis):
    AxmMotSetAbsRelMode = loaddll['AxmMotSetAbsRelMode']
    AxmMotGetAbsRelMode = loaddll['AxmMotGetAbsRelMode']
    
    mode = c_ulong()
    res = AxmMotSetAbsRelMode(axis, 0) # 절대 모드로 설정
    AxmMotGetAbsRelMode(axis,pointer(mode))
    if res == 0000:
        print("절대/상대 모드 설정(0-절대,1-상대): ","절대모드" if mode.value == 0 else "상대모드")
    elif res == 4053:
        print("해당 축 모션 초기화 실패")
    elif res == 4101:
        print("해당 축이 존재하지 않음")
    else:
        print("뭔지 모를 이유로 절대 상대 모드 설정 실패")

# 속도 프로파일 설정
def mot_set_profile_mode(axis):
    AxmMotSetProfileMode = loaddll['AxmMotSetProfileMode']
    AxmMotGetProfileMode = loaddll['AxmMotGetProfileMode']

    uProfile = c_ulong()
    res = AxmMotSetProfileMode(axis, 0) # SYM_TRAPEZOIDE_MODE
    AxmMotGetProfileMode(axis,pointer(uProfile))
    if res==0000:
        print("profile mode : ",uProfile.value)
    elif res == 4053:
        print("해당 축 모션 초기화 실패")
    elif res == 4101:
        print("해당 축이 존재하지 않음")
    else:
        print("뭔지 모를 이유로 profile 모드 설정 실패")

'''
# 가속도 단위 설정
def mot_set_accel_unit(axis):
    AxmMotSetAccelUnit = loaddll['AxmMotSetAccelUnit']
    AxmMotGetAccelUnit = loaddll['AxmMotGetAccelUnit']
    uAccelUnit = c_ulong()

    res = AxmMotSetAccelUnit(axis, 0) #0축의 가속도 단위 unit/sec2 설정
    res2 = AxmMotGetAccelUnit(axis, pointer(uAccelUnit))
    if res == 0000 and res2 == 0000:
        print("0축의 가속도단위 설정 완료 : ","UNIT_SEC2" if uAccelUnit.value == 0 else "SEC")
    else:
        print("가속도 설정 실패. error: ",res)
'''
# 지정 축의 알람 신호 Active level 설정
def signal_set_servo_alarm(axis):
    AxmSignalSetServoAlarm = loaddll['AxmSignalSetServoAlarm']
    res = AxmSignalSetServoAlarm(axis, 1) # High

    if res == 0000:
        print("AxmSignalSetServoAlarm 함수 실행 성공")
    elif res == 4053:
        print("해당 축 모션 초기화 실패")
    elif res == 4101:
        print("해당 축이 존재하지 않음")
    else:
        print("뭔지 모를 이유로 AxmSignalSetServoAlarm 설정 실패")

def signal_set_stop(axis):
    AxmSignalSetStop = loaddll['AxmSignalSetStop']
    res = AxmSignalSetStop(axis,0,1) # 0축, 급정지, 정지신호 사용 High

    if res == 0000:
        print("AxmSignalSetStop 함수 실행 성공")
    elif res == 4053:
        print("해당 축 모션 초기화 실패")
    elif res == 4101:
        print("해당 축이 존재하지 않음")
    else:
        print("뭔지 모를 이유로 AxmSignalSetStop 설정 실패")

################################# (input)테스트해볼 5가지 단축구동 함수 ###############################

def HomeSearchMove(request): # 원점찾기(완성)
    users = User.objects.all()
    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 보드 상태 확인 >>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
    board_status()
    board_count()
    info_get_axis(0) # 0번축 보드/모듈 정보 확인 : 보드번호=1, 모듈위치=0, 모듈아이디=35
    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")

    print(">>>>>>>>>>>>>>>>>>>>>>> 라이브러리 open, 모듈 존재 확인 >>>>>>>>>>>>>>>>>>>>>>>")
    is_lib_open()
    is_moduleExists() # 알수없는 에러로 모듈존재를 확인할 수 없음
    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")

    if request.method == 'POST':
        lAxisNo = int(request.POST.get('lAxisNo'))

    axis = lAxisNo
    set_moveUnitPerPulse(lAxisNo) #axis의 움직이는 거리당 출력되는 펄스 (1:1) 
    set_startVel(lAxisNo) #axis 초기속도 설정
    #signal_servo_on(lAxisNo) #servo on

    signal_read_servo_alarm(lAxisNo) # 현재 알람 상태 확인
    status_read_sensor(lAxisNo) # 현재 센서 상태 확인 (262179)
    signal_servo_alarm_Reset(lAxisNo) # 알람 발생 원인 제거 후 현재 알람 상태 벗어남

    signal_set_inpos(lAxisNo) # axis의 inpos 신호 사용 여부 결정(사용안함)

    signal_set_limit(lAxisNo) # 지정 축의 리미트 센서 사용 유무 및 신호 actio level 설정
    signal_read_limit(lAxisNo) # 알람 신호 읽기 (지정 축의 리미트 센서 신호의 입력상태를 반환)
    signal_read_inpos(lAxisNo) # 지정 축의 Inpositon 신호의 입력 상태를 반환한다.

    mot_set_home_start(lAxisNo) # 원점 탐색

    return render(request, 'control/ready_to_control.html', {'users':users})

def AxmMovePos(request): # 위치구동 - 종점탈출(완성)
    users = User.objects.all()
    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 보드 상태 확인 >>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
    board_status()
    board_count()
    info_get_axis(0) # 0번축 보드/모듈 정보 확인 : 보드번호=1, 모듈위치=0, 모듈아이디=35
    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")

    print(">>>>>>>>>>>>>>>>>>>>>>> 라이브러리 open, 모듈 존재 확인 >>>>>>>>>>>>>>>>>>>>>>")
    is_lib_open()
    is_moduleExists() # 알수없는 에러로 모듈존재를 확인할 수 없음
    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")

    if request.method == 'POST':
        # mov = MovePos()
        lAxisNo = int(request.POST['lAxisNo'])
        dPos = c_double(int(request.POST['dPos']))
        dVel = c_double(int(request.POST['dVel']))
        dAccel = c_double(int(request.POST['dAccel']))
        dDecel = c_double(int(request.POST['dDecel']))
        # mov.save()

    #****************************** 55pg 순서대로 ***********************************************************
    signal_set_limit(lAxisNo)# 지정 축의 리미트 센서 사용 유무 및 신호 action level 설정
    set_moveUnitPerPulse(lAxisNo) #axis의 움직이는 거리당 출력되는 펄스 (1:1) 
    set_startVel(lAxisNo) #axis 초기속도 설정
    signal_read_limit(lAxisNo) # 알람 신호 읽기 (지정 축의 리미트 센서 신호의 입력상태를 반환)

    # 현재 위치는 원점으로 설정한다.
    AxmStatusSetActPos = loaddll['AxmStatusSetActPos']
    res = AxmStatusSetActPos((lAxisNo), 0)
    if res == 0000:
        print("AxmStatusSetActPos 함수 실행 성공")
    elif res == 4053:
        print("해당 축 모션 초기화 실패")
    elif res == 4101:
        print("해당 축이 존재하지 않음")
    else:
        print("뭔지 모를 이유로 AxmStatusSetActPos 설정 실패")
        
    AxmStatusSetCmdPos = loaddll['AxmStatusSetCmdPos']
    res2 = AxmStatusSetCmdPos((lAxisNo), 0)
    if res2 == 0000:
        print("AxmStatusSetCmdPos 함수 실행 성공")
    elif res2 == 4053:
        print("해당 축 모션 초기화 실패")
    elif res2 == 4101:
        print("해당 축이 존재하지 않음")
    else:
        print("뭔지 모를 이유로 AxmStatusSetCmdPos 설정 실패")

    #signal_servo_on(lAxisNo) #servo on
    mot_set_abs_mode(lAxisNo) # axis 이동거리 계산 모드 설정
    mot_set_profile_mode(lAxisNo) # axis의 구동 속도 프로파일 설정

    AxmStatusReadVel = loaddll['AxmStatusReadVel']
    dVelocity = c_int()
    AxmStatusReadVel(axis, pointer(dVelocity))

    AxmMovePos = loaddll['AxmMovePos']
    AxmMovePos.argtypes = [c_long,c_double,c_double,c_double,c_double]
    print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&>> ", dVelocity.value)
    ResAxmMovePos = AxmMovePos(
        (lAxisNo), 
        (dPos).value, 
        (dVel).value, 
        (dAccel).value, 
        (dDecel).value
    ) # input값 잘 받아오는거 확인함
    print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&>> ", dVelocity.value)

    if ResAxmMovePos == 0000:
        print("AxmMovePos 함수 실행 성공")
    elif ResAxmMovePos == 4154:
        print("AXT_RT_MOTION_ERROR_GANTRY_ENABLE : Gantry Slave 축에 Move 명령이 내려졌을 때")
    elif ResAxmMovePos == 4201:
        print("AXT_RT_MOTION_HOME_SEARCHING : 홈을 찾고있는 중일 때 또는 다른 모션 함수들을 사용할 때")
    elif ResAxmMovePos == 4255:
        print("AXT_RT_MOTION_SETTING_ERROR : 속도, 가속도, 저크, 프로파일 설정이 잘못됨")
    else:
        print("뭔가 모를 이유로 AxmMovePos 가 실행되지 않음. Error: ",ResAxmMovePos)

    #AxmStatusReadVel(mov.lAxisNo)
    
    #임시 템플릿
    return render(request, 'control/ready_to_control.html', {'users':users})

def AxmMoveStartPos(request): # 위치구동 - 시점탈출(완성)
    users = User.objects.all()
    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 보드 상태 확인 >>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
    board_status()
    board_count()
    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")

    print(">>>>>>>>>>>>>>>>>>>>>>> 라이브러리 open, 모듈 존재 확인 >>>>>>>>>>>>>>>>>>>>>>")
    is_lib_open()
    is_moduleExists() 
    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")

    if request.method == 'POST':
        # mov = MoveStartPos()
        lAxisNo = int(request.POST['lAxisNo'])
        dPos = c_double(int(request.POST['dPos']))
        dVel = c_double(int(request.POST['dVel']))
        dAccel = c_double(int(request.POST['dAccel']))
        dDecel = c_double(int(request.POST['dDecel']))
        # mov.save()

    #****************************** 55pg 순서대로 ***********************************************************
    signal_set_limit(lAxisNo) # 지정 축의 리미트 센서 사용 유무 및 신호 action level 설정
    set_moveUnitPerPulse(lAxisNo) # axis의 움직이는 거리당 출력되는 펄스 (1:1) 
    set_startVel(lAxisNo) # axis 초기속도 설정
    signal_read_limit(lAxisNo) # 알람 신호 읽기 (지정 축의 리미트 센서 신호의 입력상태를 반환)

    # 현재 위치는 원점으로 설정한다.
    AxmStatusSetActPos = loaddll['AxmStatusSetActPos']
    res = AxmStatusSetActPos(lAxisNo, 0)
    if res == 0000:
        print("AxmStatusSetActPos 함수 실행 성공")
    elif res == 4053:
        print("해당 축 모션 초기화 실패")
    elif res == 4101:
        print("해당 축이 존재하지 않음")
    else:
        print("뭔지 모를 이유로 AxmStatusSetActPos 설정 실패")
        
    AxmStatusSetCmdPos = loaddll['AxmStatusSetCmdPos']
    res2 = AxmStatusSetCmdPos(lAxisNo, 0)
    if res2 == 0000:
        print("AxmStatusSetCmdPos 함수 실행 성공")
    elif res2 == 4053:
        print("해당 축 모션 초기화 실패")
    elif res2 == 4101:
        print("해당 축이 존재하지 않음")
    else:
        print("뭔지 모를 이유로 AxmStatusSetCmdPos 설정 실패")

    #signal_servo_on(lAxisNo) #servo on
    mot_set_abs_mode(lAxisNo) # axis 이동거리 계산 모드 설정
    mot_set_profile_mode(lAxisNo) # axis의 구동 속도 프로파일 설정
    AxmMoveStartPos = loaddll['AxmMoveStartPos']

    isInvalidAxis(lAxisNo)
    print(dPos.value)

    AxmMoveStartPos.argtypes = [c_int, c_double, c_double, c_double, c_double]
    ResAxmMoveStartPos = AxmMoveStartPos(
        lAxisNo, 
        (dPos).value, 
        (dVel).value, 
        (dAccel).value, 
        (dDecel).value
    )

    #AxmStatusReadVel(mov.lAxisNo) # 속도 측정
    if ResAxmMoveStartPos == 0000:
        print("AxmMoveStartPos 성공")
    elif ResAxmMoveStartPos == 4154:
        print(" AXT_RT_MOTION_ERROR_GANTRY_ENABLE : Gantry Slave 축에 Move 명령이 내려졌을 때")
    elif ResAxmMoveStartPos == 4201:
        print(" AXT_RT_MOTION_HOME_SEARCHING : 홈을 찾고있는 중일 때 또는 다른 모션 함수들을 사용할 때")
    elif ResAxmMoveStartPos == 4255:
        print("AXT_RT_MOTION_SETTING_ERROR : 속도, 가속도, 저크, 프로파일 설정이 잘못됨")
    else:
        print("뭔가 모를 이유로 AxmMoveStartPos 가 실행되지 않음")

    return render(request, 'control/ready_to_control.html', {'users':users})

def AxmMoveVel(request): # 속도구동(조그구동) (완성)
    users = User.objects.all()
    # 종료 명령이 나올 때까지 계속 움직이는 형태
    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> 보드 상태 확인 >>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
    board_status()
    board_count()
    info_get_axis(0) # 0번축 보드/모듈 정보 확인 : 보드번호=1, 모듈위치=0, 모듈아이디=35
    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")

    print(">>>>>>>>>>>>>>>>>>>>>>> 라이브러리 open, 모듈 존재 확인 >>>>>>>>>>>>>>>>>>>>>>")
    is_lib_open()
    is_moduleExists() 
    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")

    if request.method == 'POST':
        # mov = MoveVel()
        lAxisNo = int(request.POST['lAxisNo'])
        dVel = c_double(int(request.POST['dVel']))
        dAccel = c_double(int(request.POST['dAccel']))
        dDecel = c_double(int(request.POST['dDecel']))
        # mov.save()

    global axis
    axis = lAxisNo
    
    signal_set_limit(lAxisNo) # 지정 축의 리미트 센서 사용 유무 및 신호 action level 설정
    set_moveUnitPerPulse(lAxisNo) #axis의 움직이는 거리당 출력되는 펄스 (1:1) 
    set_startVel(lAxisNo) #axis 초기속도 설정
    signal_read_limit(lAxisNo) # 알람 신호 읽기 (지정 축의 리미트 센서 신호의 입력상태를 반환)
    
    AxmMoveVel = loaddll['AxmMoveVel']
    AxmMoveVel.argtypes=[c_long,c_double,c_double,c_double]
    isInvalidAxis(lAxisNo)
    ResAxmMoveVel = AxmMoveVel(
        (lAxisNo), 
        (dVel).value, 
        (dAccel).value, 
        (dDecel).value
    )
    
    if ResAxmMoveVel == 0000:
        print("ResAxmMoveVel 함수 실행 성공")
    elif ResAxmMoveVel == 4154:
        print("AXT_RT_MOTION_ERROR_GANTRY_ENABLE : Gantry Slave 축에 Move 명령이 내려졌을 때")
    elif ResAxmMoveVel == 4201:
        print("AXT_RT_MOTION_HOME_SEARCHING : 홈을 찾고있는 중일 때 또는 다른 모션 함수들을 사용할 때")
    elif ResAxmMoveVel == 4255:
        print("AXT_RT_MOTION_SETTING_ERROR : 속도, 가속도, 저크, 프로파일 설정이 잘못됨")
    else:
        print("뭔가 모를 이유로 AxmMoveVel 가 실행되지 않음. Error: ",ResAxmMoveVel)

    return render(request, 'control/ready_to_control.html', {'users':users})

def AxmMoveEStop(request): # 긴급 정지 함수 (완성)    
    users = User.objects.all()
    AxmStatusReadInMotion = loaddll['AxmStatusReadInMotion']
    upStatus = c_long()

    for i in range(8): #최대 8축이라 가정 (0~7번축 차례로 scan)
        axis = isInvalidAxis(i) # 제어 가능한 축 번호 반환(int)

        AxmMoveEStop = loaddll['AxmMoveEStop']
        res = AxmStatusReadInMotion(axis, pointer(upStatus)) # 모션 구동 상태 파악

        if upStatus.value == 1: #만약 모션이 구동중이라면
            res2 = AxmMoveEStop(axis)
        else:
            pass

    return render(request, 'control/ready_to_control.html',{'users':users})

#TODO: 속도구동 감속 정지 함수
def AxmMoveSStop(request):  
    users = User.objects.all()
    AxmStatusReadInMotion = loaddll['AxmStatusReadInMotion']
    upStatus = c_long()

    for i in range(8): #최대 8축이라 가정 (0~7번축 차례로 scan)
        axis = isInvalidAxis(i) # 제어 가능한 축 번호 반환(int)

        AxmMoveSStop = loaddll['AxmMoveSStop']
        res = AxmStatusReadInMotion(axis, pointer(upStatus)) # 모션 구동 상태 파악

        if upStatus.value == 1: #만약 모션이 구동중이라면
            res2 = AxmMoveSStop(axis)
        else:
            pass

    return render(request, 'control/ready_to_control.html',{'users':users})

################################# (input)테스트해볼 다축구동 함수 ###############################

multiaxis=[]
def AxmMoveStartMultiPos(request): 
    users = User.objects.all()
    multiaxis.clear()
    # 다축위치 구동 - 시점탈출
    # 축 개수만큼 배열을 선언해서 for문 돌리는 식으로 구현
    # (축개수, 축번호 배열, 구동거리 배열, 속도 배열, 가속도 배열, 감속도 배열)
    
    print(">>>>>>>>>>>>>>>>>>>>>>> 라이브러리 open, 모듈 존재 확인 >>>>>>>>>>>>>>>>>>>>>>")
    is_lib_open()
    is_moduleExists() 
    print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
    
    if request.method == 'POST':
        lAxisNo = request.POST.getlist('lAxisNo') #list
        dPos = request.POST.getlist('dPos')
        dVel = request.POST.getlist('dVel')
        dAccel = request.POST.getlist('dAccel')
        dDecel = request.POST.getlist('dDecel')
    
    lAxisNo2 = [int(x) for x in lAxisNo] #[1,2,...]
    dPos2 = [int(x) for x in dPos]
    dVel2 = [int(x) for x in dVel]
    dAccel2 = [int(x) for x in dAccel]
    dDecel2 = [int(x) for x in dDecel]

    for i in range(len(lAxisNo2)):
        multiaxis.append(lAxisNo2[i])

    AxmStatusSetActPos = loaddll['AxmStatusSetActPos']
    AxmStatusSetCmdPos = loaddll['AxmStatusSetCmdPos']

    for i in range(len(lAxisNo2)):
        print(">>>>>>>>>>>>>>>> 다축구동 {}축 전처리 <<<<<<<<<<<<<<<".format(lAxisNo2[i]))

        signal_set_limit(lAxisNo2[i])
        set_moveUnitPerPulse(lAxisNo2[i])
        set_startVel(lAxisNo2[i])
        signal_read_limit(lAxisNo2[i])

        res_AxmStatusSetActPos = AxmStatusSetActPos(lAxisNo2[i],i)
        res_AxmStatusSetCmdPos = AxmStatusSetCmdPos(lAxisNo2[i],i)

        #signal_servo_on(lAxisNo2[i])

        mot_set_abs_mode(lAxisNo2[i])
        mot_set_profile_mode(lAxisNo2[i])

    if res_AxmStatusSetActPos == 0000:
        print("AxmStatusSetActPos 함수 실행 성공")
    elif res_AxmStatusSetActPos == 4053:
        print("해당 축 모션 초기화 실패")
    elif res_AxmStatusSetActPos == 4101:
        print("해당 축이 존재하지 않음")
    else:
        print("뭔지 모를 이유로 AxmStatusSetActPos 설정 실패",res_AxmStatusSetActPos)

    if res_AxmStatusSetCmdPos == 0000:
        print("AxmStatusSetCmdPos 함수 실행 성공")
    elif res_AxmStatusSetCmdPos == 4053:
        print("해당 축 모션 초기화 실패")
    elif res_AxmStatusSetCmdPos == 4101:
        print("해당 축이 존재하지 않음")
    else:
        print("뭔지 모를 이유로 AxmStatusSetCmdPos 설정 실패",res_AxmStatusSetCmdPos)

    #TODO: 파이썬과 c의 메모리 할당 방식의 차이가 에러의 원인?
    def to_c_array(py_list):
        arr = (c_int * len(py_list))(*py_list)
        return arr

    def to_c_array2(py_list):
        arr = (c_double * len(py_list))(*py_list)
        return arr

    a = to_c_array(lAxisNo2)
    b = to_c_array2(dPos2)
    c = to_c_array2(dVel2)
    d = to_c_array2(dAccel2)
    e = to_c_array2(dDecel2)

    for i in range(len(lAxisNo2)):
        print(">>>",i,"번 축의 세팅")
        print("축 : ",a[i], ",위치 : ",b[i],
              ",속도 : ", c[i], ",가속 : ",d[i], ",감속 : ", e[i])
    print("------------------------------------------------------------")
    
    AxmMoveStartMultiPos = loaddll['AxmMoveStartMultiPos'] 
    AxmMoveStartMultiPos.argtypes = [c_long, POINTER(c_long), POINTER(c_double), POINTER(c_double), POINTER(c_double), POINTER(c_double)]
    # FIXME: MLIII 통신 기준, 지정된 축에 대한 구동 위치 값이 오버플로우임
    res = AxmMoveStartMultiPos(len(lAxisNo2), a,b,c,d,e)
    
    
    if res == 0000:
        print("AxmMoveStartMultiPos 성공")
    elif res == 4154:
        print(" AXT_RT_MOTION_ERROR_GANTRY_ENABLE : Gantry Slave 축에 Move 명령이 내려졌을 때")
    elif res == 4201:
        print(" AXT_RT_MOTION_HOME_SEARCHING : 홈을 찾고있는 중일 때 또는 다른 모션 함수들을 사용할 때")
    elif res == 4255:
        print("AXT_RT_MOTION_SETTING_ERROR : 속도, 가속도, 저크, 프로파일 설정이 잘못됨")
    elif res == 4536:
        print("MLIII 통신 기준, 지정된 축에 대한 구동 위치 값이 오버플로우임")
    else:
        print("뭔가 모를 이유로 AxmMoveStartMultiPos 가 실행되지 않음. error: ",res)
    
    return render(request, 'control/ready_to_control.html',{'users':users})

################################# (output)테스트해볼 2가지 함수 #################################
veldata = 0

# channels를 통한 소켓 통신(백엔드 to 프론트엔드)
class GraphConsumer(WebsocketConsumer):
    global veldata, axis
    def connect(self):
        self.accept()

        AxmStatusReadVel = loaddll['AxmStatusReadVel'] # 속도 값의 단위는 unit/sec
        AxmStatusReadInMotion = loaddll['AxmStatusReadInMotion']

        upStatus = c_long()
        dVelocity = c_double()
        upStatus2 = c_long()
        dVelocity2 = c_double()
        upStatus3 = c_long()
        dVelocity3 = c_double()
        upStatus4 = c_long()
        dVelocity4 = c_double()

        # 다축 구동
        # 축 별 속도를 html로 보내서 각각 보여준다.
        if len(multiaxis) >= 2:
            # multiaxis 각각의 축에 대한 구동상태 파악
            while True: 
                # 한 보드당 최대 4개 축이니까 3 가지 경우를 작성

                # 축이 2개
                if len(multiaxis)==2:
                    AxmStatusReadInMotion(multiaxis[0], pointer(upStatus))  # 0번 축 모션 구동 상태 파악
                    AxmStatusReadInMotion(multiaxis[1], pointer(upStatus2)) # 1번 축 모션 구동 상태 파악
                    
                    # veldata, veldata2를 그냥 html로 보내주면 되지않나?
                    if upStatus.value == 1 or upStatus2.value == 1:
                        col = AxmStatusReadVel(multiaxis[0], pointer(dVelocity))
                        col2 = AxmStatusReadVel(multiaxis[1], pointer(dVelocity2))
                        if col == 0000 or col2 == 0000:
                            veldata = dVelocity.value
                            veldata2 = dVelocity2.value
                            message = {
                                'veldata' : veldata,
                                'veldata2' : veldata2,
                            }
                            self.send(text_data=json.dumps(message))
                            sleep(0.005)
                        elif col == 0000 or col2 == 0000:
                            print("모션 초기화 실패")
                        else:
                            print("안됨 : ",col2)
                    else:
                        break

                # 축이 3개
                if len(multiaxis)==3:
                    AxmStatusReadInMotion(multiaxis[0], pointer(upStatus))  # 0번 축 모션 구동 상태 파악
                    AxmStatusReadInMotion(multiaxis[1], pointer(upStatus2)) # 1번 축 모션 구동 상태 파악
                    AxmStatusReadInMotion(multiaxis[2], pointer(upStatus3)) # 2번 축 모션 구동 상태 파악

                    if upStatus.value == 1 or upStatus2.value == 1 or upStatus3.value == 1:
                        col = AxmStatusReadVel(multiaxis[0], pointer(dVelocity))
                        col2 = AxmStatusReadVel(multiaxis[1], pointer(dVelocity2))
                        col3 = AxmStatusReadVel(multiaxis[2], pointer(dVelocity3))

                        if col == 0000 or col2 == 0000 or col3 == 0000:
                            veldata = dVelocity.value
                            veldata2 = dVelocity2.value
                            veldata3 = dVelocity3.value
                            message = {
                                'veldata' : veldata,
                                'veldata2' : veldata2,
                                'veldata3' : veldata3,
                            }
                            self.send(text_data=json.dumps(message))
                            sleep(0.005)
                        elif col == 0000 or col2 == 0000 or col3 == 0000:
                            print("모션 초기화 실패")
                        else:
                            print("안됨 : ",col)
                    else:
                        break
                
                # 축이 4개
                if len(multiaxis)==4:
                    AxmStatusReadInMotion(multiaxis[0], pointer(upStatus))  # 0번 축 모션 구동 상태 파악
                    AxmStatusReadInMotion(multiaxis[1], pointer(upStatus2)) # 1번 축 모션 구동 상태 파악
                    AxmStatusReadInMotion(multiaxis[2], pointer(upStatus3)) # 2번 축 모션 구동 상태 파악
                    AxmStatusReadInMotion(multiaxis[3], pointer(upStatus4)) # 2번 축 모션 구동 상태 파악

                    if upStatus.value == 1 or upStatus2.value == 1 or upStatus3.value == 1 or upStatus4.value == 1:
                        col = AxmStatusReadVel(multiaxis[0], pointer(dVelocity))
                        col2 = AxmStatusReadVel(multiaxis[1], pointer(dVelocity2))
                        col3 = AxmStatusReadVel(multiaxis[2], pointer(dVelocity3))
                        col4 = AxmStatusReadVel(multiaxis[3], pointer(dVelocity4))

                        if col == 0000 or col2 == 0000 or col3 == 0000 or col4 == 0000:
                            veldata = dVelocity.value
                            veldata2 = dVelocity2.value
                            veldata3 = dVelocity3.value
                            veldata4 = dVelocity4.value
                            message = {
                                'veldata' : veldata,
                                'veldata2' : veldata2,
                                'veldata3' : veldata3,
                                'veldata4' : veldata4,
                            }
                            self.send(text_data=json.dumps(message))
                            sleep(0.005)
                        elif col == 0000 or col2 == 0000 or col3 == 0000 or col4 == 0000:
                            print("모션 초기화 실패")
                        else:
                            print("안됨 : ",col)
                    else:
                        break
        # 단축 구동    
        else:
            res1 = AxmStatusReadInMotion(axis, pointer(upStatus)) # 모션 구동 상태 파악
            if res1==0000: 
                print("AxmStatusReadInMotion 성공")
            elif res1 == 4053:
                print("해당 축 모션 초기화 실패")
            elif res1 == 4101:
                print("해당 축이 존재하지 않음")
            else:
                print("뭔지 모를 이유로 AxmStatusReadInMotion 실패. error: ",res1)
            
            while True: 
                AxmStatusReadInMotion(axis, pointer(upStatus)) # 모션 구동 상태 파악
                if upStatus.value == 1:
                    col = AxmStatusReadVel(axis, pointer(dVelocity))
                    if col == 0000:
                        veldata = dVelocity.value
                        self.send(json.dumps({'veldata': veldata}))
                        sleep(0.005)
                    elif col == 4053:
                        print("모션 초기화 실패")
                    else:
                        print("안됨 : ",col)
                else:
                    break
                AxmStatusReadInMotion(axis, pointer(upStatus)) # 모션 구동 상태 파악

        self.send(json.dumps({'value': 0}))
        print(multiaxis)


        #TODO: graph.js 테스트용 코드. 축이 2개라고 가정
        # count=200
        # a=400
        # for i in range(2000):
        #     # python 객체를 json 문자열로 변환하는 dumps
        #     message = {
        #         'count' : count,
        #         'a' : a,
        #     }
        #     self.send(text_data=json.dumps(message))
        #     count += 4
        #     a += 2
        #     sleep(0.005)

    def disconnect(self, code):
        print("socket 통신 cut 신호 수신")

    def receive(self, text_data):
        test = json.loads(text_data)
        print(test)