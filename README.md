<h2>2022 동계 현장실습 실무과제 저장용 레포
<h3> 프로젝트 개요 및 설명</h3>
본 프로젝트는 경북대학교 2022년 동계 방학 현장 실습(8주)의 실습 결과물이다.
분산형 모션 제어 제품(이하 네트워크 제품)을 웹 기반으로 제어하기 위한 것이 주요 목표이다.

<h3>프로젝트에 사용된 tools</h3>
<h5>python : 3.9.5</h5><h5>Django : 3.2</h5>
<h5>pyinstaller : 5.0.1</h5>
<h5>channels : 3.0.2</h5>
<h5>asgiref : 3.2.10</h5>

<h3>요구조사에 따라 작성한 유즈케이스 다이아그램</h3>

![20240315_201251](https://github.com/DeveloperYun/2022winter_intern/assets/81633639/14c8365f-dc0a-40f3-862c-61d853c4d4e1)

<h3>주요 기능 목록</h3>
1. AxmMovePos (테스트 용 단축 구동)<br/>
2. AxmMoveStartPos (단축 구동)<br/>
3. AxmMoveVel (단축 구동)<br/>
4. AxmHomeSetStart (단축 구동)<br/>
5. AxmMoveStartMultiPos (다축 구동)<br/>
6. AxmStatusReadVel (속도 읽기)<br/>
7. AxmMoveSStop, AxmMoveEStop, AxmMoveStop (정지)<br/>

<h3>주요 화면</h3> 

1. 접속화면 및 회원/로그인 화면<br/>
![image](https://github.com/DeveloperYun/2022winter_intern/assets/81633639/e94a9b32-ead4-4f5a-a2af-47ff1ecac754)

2. 로그인 후 대시보드 화면<br/>
![image](https://github.com/DeveloperYun/2022winter_intern/assets/81633639/188327b9-f8ec-40d0-9866-d1a1565c4e83)

3. 동작 화면<br/>
![image](https://github.com/DeveloperYun/2022winter_intern/assets/81633639/d4de6fa1-39a7-4bfd-bfaf-8077ea3b62dd)

4. 모바일 화면<br/>
![image](https://github.com/DeveloperYun/2022winter_intern/assets/81633639/d704e893-b07b-4785-9410-9f5961662ca7)

5. 원격 제어 화면<br/>
![image](https://github.com/DeveloperYun/2022winter_intern/assets/81633639/8c6c543d-21d4-4584-afd6-6d5cb31699d1)

-----
<h3>배포 방식</h3>
해당 배포는 보드가 연결되어있는 컴퓨터에 파이썬 및 장고가 설치되어있지 않은 환경이라도 장고 웹 서버를 구동하여 
어느 환경에서든 보드를 컨트롤 할 수 있게 하는 것이 목적이다.
사정상 클라우드를 활용한 배포 대신 실행 파일로 배포한다.

-----
시연영상: https://www.youtube.com/watch?v=B0ldawMC3Dk
