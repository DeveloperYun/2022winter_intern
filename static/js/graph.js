var ctx = document.getElementById('myChart').getContext('2d'); //'mychart' canvas에 렌더링

//createLinearGradient(시작점 x1, 시작점 y1, 끝점 x2, 끝점 y2) => 선형 그라데이션 지정
//addColorStop(오프셋, 색상) => 그라데이션 경계색 지정 / 오프셋 : 0.0에서 1.0까지의 색상의 상대적인 위치
var gradient = ctx.createLinearGradient(0, 0, 0, 450);
gradient.addColorStop(0, 'rgba(0, 199, 214, 0.32)');
gradient.addColorStop(0.3, 'rgba(0, 199, 214, 0.1)');
gradient.addColorStop(1, 'rgba(0, 199, 214, 0)');

var gradient2 = ctx.createLinearGradient(0, 0, 0, 450);
gradient2.addColorStop(0, 'rgba(255, 99, 132, 0.32)');
gradient2.addColorStop(0.3, 'rgba(255, 99, 132, 0.1)');
gradient2.addColorStop(1, 'rgba(255, 99, 132, 0)');

var gradient3 = ctx.createLinearGradient(0, 0, 0, 450);
gradient3.addColorStop(0, 'rgba(255, 255, 0, 0.32)');
gradient3.addColorStop(0.3, 'rgba(255, 255, 0, 0.1)');
gradient3.addColorStop(1, 'rgba(255, 255, 0, 0)');


var gradient4 = ctx.createLinearGradient(0, 0, 0, 450);
gradient4.addColorStop(0, 'rgba(153, 102, 255, 0.32)');
gradient4.addColorStop(0.3, 'rgba(153, 102, 255, 0.1)');
gradient4.addColorStop(1, 'rgba(153, 102, 255, 0)');

var graphData = {
    type: 'line',
    data: {
        labels: ['0축', '1축', '2축', '3축'],
        datasets: [
            {
                label: '0축',
                data: [],
                backgroundColor: gradient,
                pointBackgroundColor: '#00c7d6',
                borderWidth: 1,
                borderColor: '#0e1a2f',
            },
            {
                label: '1축',
                data: [],
                backgroundColor: gradient2,
                pointBackgroundColor: '#ff6384',
                borderWidth: 1,
                borderColor: '#0e1a2f',
            },
            {
                label: '2축',
                data: [],
                backgroundColor: gradient3,
                pointBackgroundColor: '#ffff00',
                borderWidth: 1,
                borderColor: '#0e1a2f',
            },
            {
                label: '3축',
                data: [],
                backgroundColor: gradient4,
                pointBackgroundColor: '#9966ff',
                borderWidth: 1,
                borderColor: '#0e1a2f',
            }
        ]
    },
    options: {
        reponsive: false,
        scales: {
            yAxes: [{
                ticks: {
                    fontColor: '#5e6a81',
                    autoSkip: false,
                    fontSize: 15
                },
                gridLines: {
                    color: 'rgba(200, 200, 200, 0.08)',
                    lineWidth: 1
                }
            }],
            xAxes:[{
                ticks: {
                    fontColor: '#5e6a81',
                    fontSize: 15,
                    min: 0,
                    max: 600
                }
            }]
        },
        elements: {
            line: {
                tension: 0.1
            }
        },
        legend: {
            display: true
        },
        point: {
            backgroundColor: '#00c7d6'
        },
        tooltips: {
            titleFontFamily: 'Poppins',
            backgroundColor: 'rgba(0,0,0,0.4)',
            titleFontColor: 'white',
            caretSize: 5,
            cornerRadius: 2,
            xPadding: 10,
            yPadding: 10
        }
    }
}


// 라이브러리에 대한 유형 정보(이 경우 Chart.js)가 프로젝트에 포함되지 않았거나 유형 정보가 올바르지 않거나 오래된 경우에 발생할 수 있습니다.
var myChart = new Chart(ctx, graphData);
var socket = new WebSocket('ws://localhost:8000/ws/control/'); //해당 서버에 대한 웹소켓 연결 설정
// http://172.16.10.26:8000/
var counter = 0
//서버로부터 전송받은 데이터
//onmessage 이벤트 트리거시 차트의 데이터와 레이블을 업데이트하고 차트에서 업데이트 메소드를 호출

socket.onmessage = function(e){
    var djangoData = JSON.parse(e.data);
  
    var newGraphData0 = graphData.data.datasets[0].data; //axis0
    var newGraphData1 = graphData.data.datasets[1].data; //axis1
    var newGraphData2 = graphData.data.datasets[2].data; //axis2
    var newGraphData3 = graphData.data.datasets[3].data; //axis3

    var newx = graphData.data.labels; // x축 레이블은 하나
    var axis = counter
    
    if(counter>=600){
        if(newGraphData0.length > 0){
            newGraphData0.shift();
        }
        if(newGraphData1.length > 0){
            newGraphData1.shift();
        }
        if(newGraphData2.length > 0){
            newGraphData2.shift();
        }
        if(newGraphData3.length > 0){
            newGraphData3.shift();
        }
        newx.pop();
    }

    newGraphData0.push(djangoData.veldata);
    newGraphData1.push(djangoData.veldata2);
    newGraphData2.push(djangoData.veldata3);
    newGraphData3.push(djangoData.veldata4);

    newx.push(axis); //0.00부터 카운팅되도록
    graphData.data.datasets[0].data = newGraphData0;
    graphData.data.datasets[1].data = newGraphData1;
    graphData.data.datasets[2].data = newGraphData2;
    graphData.data.datasets[3].data = newGraphData3;

    counter = counter + 1
    myChart.update();

    document.querySelector('#app').innerText = djangoData.veldata;
    document.querySelector('#app1').innerText = djangoData.veldata2;
    document.querySelector('#app2').innerText = djangoData.veldata3;
    document.querySelector('#app3').innerText = djangoData.veldata4;

}


//https://dbza.tistory.com/entry/django-channels-%EB%9D%BC%EC%9D%B4%EB%B8%8C%EB%9F%AC%EB%A6%AC-consumer-%EB%8D%B0%EC%9D%B4%ED%84%B0-%ED%9D%90%EB%A6%84
//ws.send로 컨슈머에게 중지신호를 보내면 컨슈머의 receive에서 받아서 그 안에서 close
//<input id="socket-cut" type="button" value="cut">

document.querySelector('.open-right-area').addEventListener('click', function () {
    document.querySelector('.app-right').classList.add('show');
});


document.querySelector('.menu-button').addEventListener('click', function () {
    document.querySelector('.app-left').classList.add('show');
});

document.querySelector('.close-menu').addEventListener('click', function () {
    document.querySelector('.app-left').classList.remove('show');
});