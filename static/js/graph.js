var ctx = document.getElementById('myChart').getContext('2d'); //'mychart' canvas에 렌더링
var gradient = ctx.createLinearGradient(0, 0, 0, 450);

gradient.addColorStop(0, 'rgba(0, 199, 214, 0.32)');
gradient.addColorStop(0.3, 'rgba(0, 199, 214, 0.1)');
gradient.addColorStop(1, 'rgba(0, 199, 214, 0)');

var graphData = {
    type: 'line',
    data: {
        labels: [],
        datasets: [
            {
                label: 'velocity',
                data: [],
                backgroundColor: gradient,
                pointBackgroundColor: '#00c7d6',
                borderWidth: 1,
                borderColor: '#0e1a2f',
            }
        ]
    },
    options: {
        reponsive: true,
        scales: {
            yAxes: [{
          ticks: {
            fontColor: '#5e6a81'
          },
                gridLines: {
                    color: 'rgba(200, 200, 200, 0.08)',
                    lineWidth: 1
                }
            }],
        xAxes:[{
          ticks: {
            fontColor: '#5e6a81'
          }
        }]
        },
        elements: {
            line: {
                tension: 0.4
            }
        },
        legend: {
            display: false
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

var myChart = new Chart(ctx, graphData);
var socket = new WebSocket('ws://localhost:8000/ws/control/'); //해당 서버에 대한 웹소켓 연결 설정

let counter = 0
//서버로부터 전송받은 데이터
//onmessage 이벤트 트리거시 차트의 데이터와 레이블을 업데이트하고 차트에서 업데이트 메소드를 호출
socket.onmessage = function(e){
    djangoData = JSON.parse(e.data);

    var newGraphData = graphData.data.datasets[0].data;
    var newx = graphData.data.labels;
    var axis = counter
    
    // 데이터가 200개가 누적되면 1개씩 pop, push 되도록 하려면?
    if(counter>=1000){
        // counter = 0
        // for(var i=0; i<75; i++){
        newGraphData.shift();
        newx.pop();
        //}
    }

    newGraphData.push(djangoData.value);
    newx.push(axis); //0.00부터 카운팅되도록
    graphData.data.datasets[0].data = newGraphData;
    counter = counter + 1
    myChart.update();

    document.querySelector('#app').innerText = djangoData.value;
        
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