from django.shortcuts import render
from django.http import HttpResponse
from .models import *
from ctypes import *
from channels.generic.websocket import WebsocketConsumer
import json
from random import randint, uniform
from time import sleep

'''
DWORD = unsigned long int
python int == c long
제품명 : PCIe-Rxx05-MLIII (SGD7) (네트워크) 
            => 실험실 컴퓨터에 붙은 RTEX 종이는 무시할것..해당사항 없음
set~ : setting함수 (보통)
'''
loaddll = PyDLL('./AXL.dll') # 불러오기 성공
axis = 0

def main(request):
    return render(request, 'control/ready_to_control.html', context={'text': 'Hello'})

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
        print("0번축의 보드 번호, 모듈위치, 모듈아이디: ",lBoardNo.value, ", ",lModulePos.value,", ",uModuleID.value)
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
 
####TODO:##########################  모션 구동의 용어 해설  #################################

# 이건 low 혹은 high를 serve on 으로 받아들이겠다를 셋팅하는 함수이다.
# 자꾸 1053 에러가 뜬 것은 해당 기기가 디폴트로 low 혹은 high...를 받는데 바꾸라고 해서 에러가 떴을 확률이 있다.

def signal_servo_on(axis):
    AxmSignalServoOn = loaddll['AxmSignalServoOn']
    AxmSignalIsServoOn = loaddll['AxmSignalIsServoOn']

    level = c_ulong()
    res_AxmSignalServoOn = AxmSignalServoOn(axis,1) #  Enable = 1, Disable = 0
    AxmSignalIsServoOn(axis, pointer(level))

    if res_AxmSignalServoOn == 0000:
        print("servo on 성공(0-off,1-on) : ", "on" if level.value==1 else "off")
    elif res_AxmSignalServoOn == 4053:
        print("해당 축 모션 초기화 실패")
    elif res_AxmSignalServoOn == 4101:
        print("해당 축이 존재하지 않음")

####TODO:########################## 서보모터(모션 파라미터) #################################

# unit per pulse(프로그램상 지령값을 펄스 단위로 설정)
def set_moveUnitPerPulse(axis):
    #FIXME: dUnit = 1.000000 # 1회전시 이동 거리
    # lPulse = 1 # 1회전을 위한 펄스 수
    # dUnit = 1 # 1회전시 이동 거리

    lpPulse = c_long()
    dpUnit = c_long()

    AxmMotSetMoveUnitPerPulse = loaddll['AxmMotSetMoveUnitPerPulse']
    AxmMotGetMoveUnitPerPulse = loaddll['AxmMotGetMoveUnitPerPulse']

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

    MinVelocity = c_double()
    
    # 초기속도 단위는 unit per pulse가 1/1인 경우의 초당 펄스
    AxmMotSetMinVel = startvel(axis,1000) # [axis]축의 초기속도는 1
    AxmMotGetMinVel = check_vel(axis, pointer(MinVelocity))

    if AxmMotSetMinVel == 0000 and AxmMotGetMinVel == 0000:
        print("초기 속도 : " , MinVelocity.value)
    elif AxmMotSetMinVel == 4053:
        print("start speed : 해당 축 모션 초기화 실패")
    elif AxmMotSetMinVel == 4101:
        print("start speed : 해당 축이 존재하지 않음")
    else:
        print("알 수 없는 이유로 초기속도 설정에 실패함")

####TODO:##########################      모션 신호 설정      ################################
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

    print("***********************************************************************************")
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
    print("***********************************************************************************")

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

    res = AxmSignalSetInpos(axis, 1) #High로 설정
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
        print("뭔지 모를 이유로 signal_set_limit 결정 실패")

#############################################################################################
######################################### 전처리 함수 #######################################

# 원점 검색(AxmHomeSetMethod, AxmHomeSetVel 로 설정 후 AxmHomeSetStart 호출, 검색시작)
def mot_set_home_start(axis):
    AxmHomeSetMethod = loaddll['AxmHomeSetMethod']
    AxmHomeSetVel = loaddll['AxmHomeSetVel']
    AxmHomeSetStart = loaddll['AxmHomeSetStart']
    AxmHomeGetResult = loaddll['AxmHomeGetResult']
    AxmHomeGetRate = loaddll['AxmHomeGetRate']

    
    uHomeResult = c_ulong()
    uHomeStepNumber,uHomeMainStepNumber = c_ulong(), c_ulong()

    AxmHomeSetMethod(axis,0,4,0,1000,0)
    AxmHomeSetVel(axis,100, 100, 20, 1, 400, 400)

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

################################# (input)테스트해볼 5가지 함수 ###############################

def HomeSearchMove(request): # 원점찾기(완성)
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
    signal_servo_on(lAxisNo) #servo on

    signal_read_servo_alarm(lAxisNo) # 현재 알람 상태 확인
    status_read_sensor(lAxisNo) # 현재 센서 상태 확인 (262179)
    signal_servo_alarm_Reset(lAxisNo) # 알람 발생 원인 제거 후 현재 알람 상태 벗어남

    signal_set_inpos(lAxisNo) # axis의 inpos 신호 사용 여부 결정(사용안함)

    signal_set_limit(lAxisNo) # 지정 축의 리미트 센서 사용 유무 및 신호 actio level 설정
    signal_read_limit(lAxisNo) # 알람 신호 읽기 (지정 축의 리미트 센서 신호의 입력상태를 반환)
    signal_read_inpos(lAxisNo) # 지정 축의 Inpositon 신호의 입력 상태를 반환한다.

    mot_set_home_start(lAxisNo) # 원점 탐색

    return render(request, 'control/ready_to_control.html')

#FIXME: AxmMovePos 에 대해서는 속도 측정이 되지 않음
def AxmMovePos(request): # 위치구동 - 종점탈출(완성)
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
        mov = MovePos()
        mov.lAxisNo = int(request.POST['lAxisNo'])
        mov.dPos = int(request.POST['dPos'])
        mov.dVel = int(request.POST['dVel'])
        mov.dAccel = int(request.POST['dAccel'])
        mov.dDecel = int(request.POST['dDecel'])
        mov.save()

    #****************************** 55pg 순서대로 ***********************************************************
    signal_set_limit(int(mov.lAxisNo)) # 지정 축의 리미트 센서 사용 유무 및 신호 action level 설정
    set_moveUnitPerPulse(int(mov.lAxisNo)) #axis의 움직이는 거리당 출력되는 펄스 (1:1) 
    set_startVel(int(mov.lAxisNo)) #axis 초기속도 설정
    signal_read_limit(int(mov.lAxisNo)) # 알람 신호 읽기 (지정 축의 리미트 센서 신호의 입력상태를 반환)

    # 현재 위치는 원점으로 설정한다.
    AxmStatusSetActPos = loaddll['AxmStatusSetActPos']
    res = AxmStatusSetActPos(int(mov.lAxisNo), 0)
    if res == 0000:
        print("AxmStatusSetActPos 함수 실행 성공")
    elif res == 4053:
        print("해당 축 모션 초기화 실패")
    elif res == 4101:
        print("해당 축이 존재하지 않음")
    else:
        print("뭔지 모를 이유로 AxmStatusSetActPos 설정 실패")
        
    AxmStatusSetCmdPos = loaddll['AxmStatusSetCmdPos']
    res2 = AxmStatusSetCmdPos(int(mov.lAxisNo), 0)
    if res2 == 0000:
        print("AxmStatusSetCmdPos 함수 실행 성공")
    elif res2 == 4053:
        print("해당 축 모션 초기화 실패")
    elif res2 == 4101:
        print("해당 축이 존재하지 않음")
    else:
        print("뭔지 모를 이유로 AxmStatusSetCmdPos 설정 실패")

    signal_servo_on(int(mov.lAxisNo)) #servo on
    mot_set_abs_mode(int(mov.lAxisNo)) # axis 이동거리 계산 모드 설정
    mot_set_profile_mode(int(mov.lAxisNo)) # axis의 구동 속도 프로파일 설정

    AxmStatusReadVel = loaddll['AxmStatusReadVel']
    dVelocity = c_int()
    AxmStatusReadVel(axis, pointer(dVelocity))

    AxmMovePos = loaddll['AxmMovePos']


    print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&>> ", dVelocity.value)
    ResAxmMovePos = AxmMovePos(
        (mov.lAxisNo), 
        (mov.dPos), 
        (mov.dVel), 
        (mov.dAccel), 
        (mov.dDecel)
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
    return render(request, 'control/ready_to_control.html')

def AxmMoveStartPos(request): # 위치구동 - 시점탈출(완성)
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
        mov = MoveStartPos()
        mov.lAxisNo = int(request.POST['lAxisNo'])
        mov.dPos = int(request.POST['dPos'])
        mov.dVel = int(request.POST['dVel'])
        mov.dAccel = int(request.POST['dAccel'])
        mov.dDecel = int(request.POST['dDecel'])
        mov.save()

    #****************************** 55pg 순서대로 ***********************************************************
    signal_set_limit(int(mov.lAxisNo)) # 지정 축의 리미트 센서 사용 유무 및 신호 action level 설정
    set_moveUnitPerPulse(int(mov.lAxisNo)) # axis의 움직이는 거리당 출력되는 펄스 (1:1) 
    set_startVel(int(mov.lAxisNo)) # axis 초기속도 설정
    signal_read_limit(int(mov.lAxisNo)) # 알람 신호 읽기 (지정 축의 리미트 센서 신호의 입력상태를 반환)

    # 현재 위치는 원점으로 설정한다.
    AxmStatusSetActPos = loaddll['AxmStatusSetActPos']
    res = AxmStatusSetActPos(int(mov.lAxisNo), 0)
    if res == 0000:
        print("AxmStatusSetActPos 함수 실행 성공")
    elif res == 4053:
        print("해당 축 모션 초기화 실패")
    elif res == 4101:
        print("해당 축이 존재하지 않음")
    else:
        print("뭔지 모를 이유로 AxmStatusSetActPos 설정 실패")
        
    AxmStatusSetCmdPos = loaddll['AxmStatusSetCmdPos']
    res2 = AxmStatusSetCmdPos(int(mov.lAxisNo), 0)
    if res2 == 0000:
        print("AxmStatusSetCmdPos 함수 실행 성공")
    elif res2 == 4053:
        print("해당 축 모션 초기화 실패")
    elif res2 == 4101:
        print("해당 축이 존재하지 않음")
    else:
        print("뭔지 모를 이유로 AxmStatusSetCmdPos 설정 실패")

    signal_servo_on(int(mov.lAxisNo)) #servo on
    mot_set_abs_mode(int(mov.lAxisNo)) # axis 이동거리 계산 모드 설정
    mot_set_profile_mode(int(mov.lAxisNo)) # axis의 구동 속도 프로파일 설정
    AxmMoveStartPos = loaddll['AxmMoveStartPos']

    isInvalidAxis(int(mov.lAxisNo))
    ResAxmMoveStartPos = AxmMoveStartPos(
        (mov.lAxisNo), 
        (mov.dPos), 
        (mov.dVel), 
        (mov.dAccel), 
        (mov.dDecel)
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

    return render(request, 'control/ready_to_control.html')

def AxmMoveVel(request): # 속도구동(조그구동) (완성)
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
        mov = MoveVel()
        mov.lAxisNo = int(request.POST['lAxisNo'])
        mov.dVel = int(request.POST['dVel'])
        mov.dAccel = int(request.POST['dAccel'])
        mov.dDecel = int(request.POST['dDecel'])
        mov.save()

    global axis
    axis = mov.lAxisNo
    
    signal_set_limit(int(mov.lAxisNo)) # 지정 축의 리미트 센서 사용 유무 및 신호 action level 설정
    set_moveUnitPerPulse(int(mov.lAxisNo)) #axis의 움직이는 거리당 출력되는 펄스 (1:1) 
    set_startVel(int(mov.lAxisNo)) #axis 초기속도 설정
    signal_read_limit(int(mov.lAxisNo)) # 알람 신호 읽기 (지정 축의 리미트 센서 신호의 입력상태를 반환)
    
    AxmMoveVel = loaddll['AxmMoveVel']

    isInvalidAxis(int(mov.lAxisNo))
    ResAxmMoveVel = AxmMoveVel(
        (mov.lAxisNo), 
        (mov.dVel), 
        (mov.dAccel), 
        (mov.dDecel)
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
        print("뭔가 모를 이유로 AxmMovePos 가 실행되지 않음. Error: ",ResAxmMoveVel)

    return render(request, 'control/ready_to_control.html')

'''
# def mot_move_stop(axis):
#     AxmMoveSStop = loaddll['AxmMoveSStop']
#     res = AxmMoveSStop(axis)

#     if res == 0000:
#         print("AxmMoveSStop 함수 실행 성공. 해당 축 모션 구동 감속 정지.")
#     elif res == 4053:
#         print("해당 축 모션 초기화 실패")
#     elif res == 4101:
#         print("해당 축이 존재하지 않음")
#     else:
#         print("뭔지 모를 이유로 AxmMoveSStop 설정 실패. error: ",AxmMoveSStop)
'''
def AxmMoveSStop(request): # 속도구동 중지 함수 (완성)    
    AxmStatusReadInMotion = loaddll['AxmStatusReadInMotion']
    upStatus = c_long()

    print("전역변수 확인: ",axis)

    AxmMoveEStop = loaddll['AxmMoveEStop']
    
    res = AxmStatusReadInMotion(axis, pointer(upStatus)) # 모션 구동 상태 파악
    if res==0000: 
        print("AxmMoveEStop 성공")
    elif res == 4053:
        print("해당 축 모션 초기화 실패")
    elif res == 4101:
        print("해당 축이 존재하지 않음")
    else:
        print("뭔지 모를 이유로 AxmMoveEStop  실패")

    if upStatus.value == 1: #만약 모션이 구동중이라면
        res2 = AxmMoveEStop(axis)
        if res2 == 0000:
            print("AxmMoveEStop 함수 실행 성공. 해당 축 모션 구동 감속 정지.")
        elif res2 == 4053:
            print("해당 축 모션 초기화 실패")
        elif res2 == 4101:
            print("해당 축이 존재하지 않음")
        else:
            print("뭔지 모를 이유로 AxmMoveEStop 설정 실패. error: ",AxmMoveEStop)
    else:
        print("모션이 구동하지 않음")
    
    return render(request, 'control/ready_to_control.html')

################################# (output)테스트해볼 2가지 함수 #################################
veldata = 0

'''
def AxmStatusReadVel(axis): # 속도 측정 함수
    AxmStatusReadVel = loaddll['AxmStatusReadVel']
    AxmStatusReadInMotion = loaddll['AxmStatusReadInMotion']
    upStatus = c_long()
    dVelocity = c_double()
    global veldata

    res = AxmStatusReadInMotion(axis, pointer(upStatus)) # 모션 구동 상태 파악
    if res==0000: 
        print("AxmStatusReadInMotion 성공")
    elif res == 4053:
        print("해당 축 모션 초기화 실패")
    elif res == 4101:
        print("해당 축이 존재하지 않음")
    else:
        print("뭔지 모를 이유로 AxmStatusReadInMotion 실패. error: ",res)
    
    
    # dVelocity.value 를 실시간으로 보여줘야함.
    # 밀리초 단위로 나오는 값이라 DB에 담은 후에 그걸 꺼내는건 힘들어보임. 
    # dVelocity.value 를 프론트단의 JS로 실시간으로 넘겨줄 수 있어야함.
    
    while True:
        # AxmStatusReadInMotion(axis, pointer(upStatus)) # 모션 구동 상태 파악
        # if upStatus.value == 1:
        #     AxmStatusReadVel(axis, pointer(dVelocity))
           
        #     veldata = dVelocity.value
        #     #print("현재속도 >> ",veldata)
        # else:
        #     break
        #veldata = uniform(0,4.32e-322)
        sleep(0.1)
'''  

# channels를 통한 소켓 통신(백엔드 to 프론트엔드)
class GraphConsumer(WebsocketConsumer):
    global veldata, axis
    def connect(self):
        self.accept()

        AxmStatusReadVel = loaddll['AxmStatusReadVel'] # 속도 값의 단위는 unit/sec
        AxmStatusReadInMotion = loaddll['AxmStatusReadInMotion']

        upStatus = c_long()
        dVelocity = c_int()

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
                AxmStatusReadVel(axis, pointer(dVelocity))
            
                veldata = dVelocity.value
                print("현재속도 >> ", veldata)
                self.send(json.dumps({'value': veldata}))
                sleep(0.01)
            else:
                break
            AxmStatusReadInMotion(axis, pointer(upStatus)) # 모션 구동 상태 파악
        
        # #TODO: graph.js 테스트용 코드
        # for i in range(5000):
        #     self.send(json.dumps({'value': randint(0,5000)}))
        #     sleep(0.01)

    def disconnect(self, code):
        print("socket 통신 cut 신호 수신")

    def receive(self, text_data):
        test = json.loads(text_data)
        print(test)
