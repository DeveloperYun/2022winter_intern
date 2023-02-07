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
        labels: Array.from({length: count.length}, (_, i) => i),
        datasets: [
            {
                label: '0축',
                data: axis0,
                backgroundColor: gradient,
                pointBackgroundColor: '#00c7d6',
                borderWidth: 1,
                borderColor: '#0e1a2f',
            },
            {
                label: '1축',
                data: axis1,
                backgroundColor: gradient2,
                pointBackgroundColor: '#ff6384',
                borderWidth: 1,
                borderColor: '#0e1a2f',
            },
            {
                label: '2축',
                data: axis2,
                backgroundColor: gradient3,
                pointBackgroundColor: '##ffff00',
                borderWidth: 1,
                borderColor: '#0e1a2f',
            },
            {
                label: '3축',
                data: axis3,
                backgroundColor: gradient4,
                pointBackgroundColor: '#9966ff',
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



// 라이브러리에 대한 유형 정보(이 경우 Chart.js)가 프로젝트에 포함되지 않았거나 유형 정보가 올바르지 않거나 오래된 경우에 발생할 수 있습니다.
var myChart = new Chart(ctx, graphData);
var socket = new WebSocket('ws://localhost:8000/ws/control/'); //해당 서버에 대한 웹소켓 연결 설정

let counter = 0
//서버로부터 전송받은 데이터
//onmessage 이벤트 트리거시 차트의 데이터와 레이블을 업데이트하고 차트에서 업데이트 메소드를 호출

var axis0 = [];
var axis1 = [];
var axis2 = [];
var axis3 = [];

socket.onmessage = function(e){
    var djangoData = JSON.parse(e.data);

    if(djangoData.veldata){
        axis0.push(djangoData.veldata);
    }
    if(djangoData.veldata2){
        axis1.push(djangoData.veldata2);
    }
    if(djangoData.veldata3){
        axis2.push(djangoData.veldata3);
    }
    if(djangoData.veldata4){
        axis3.push(djangoData.veldata4);
    }

    if(axis0.length >= 1){
        update_axis0(axis0);
    }
    if(axis1.length >= 1){
        update_axis1(axis1);
    }
    if(axis2.length >= 1){
        update_axis2(axis2);
    }
    if(axis3.length >= 1){
        update_axis3(axis3);
    }

    // var newGraphData = graphData.data.datasets[0].data;
    // var newx = graphData.data.labels;
    // var axis = counter
    
    // // 데이터가 200개가 누적되면 1개씩 pop, push 되도록 하려면?
    // if(counter>=1000){
    //     newGraphData.shift();
    //     newx.pop();
    // }

    // newGraphData.push(djangoData.value);
    // newx.push(axis); //0.00부터 카운팅되도록
    // graphData.data.datasets[0].data = newGraphData;
    // counter = counter + 1
    // myChart.update();

    // document.querySelector('#app').innerText = djangoData.value;
        
}

function update_axis0(veldata){
    var newGraphData = graphData.data.datasets[0].data;
    var newx = graphData.data.labels;
    var axis = counter
    
    // 데이터가 200개가 누적되면 1개씩 pop, push 되도록 하려면?
    if(counter>=400){
        newGraphData.shift();
        newx.pop();
    }

    newGraphData.push(veldata);
    newx.push(axis); //0.00부터 카운팅되도록
    graphData.data.datasets[0].data = newGraphData;
    counter = counter + 1
    myChart.update();
}

function update_axis1(veldata2){
    var newGraphData = graphData.data.datasets[1].data;
    var newx = graphData.data.labels;
    var axis = counter
    
    // 데이터가 200개가 누적되면 1개씩 pop, push 되도록 하려면?
    if(counter>=400){
        newGraphData.shift();
        newx.pop();
    }

    newGraphData.push(veldata2);
    newx.push(axis); //0.00부터 카운팅되도록
    graphData.data.datasets[1].data = newGraphData;
    //counter = counter + 1
    myChart.update();
}

function update_axis2(veldata3){
    var newGraphData = graphData.data.datasets[2].data;
    var newx = graphData.data.labels;
    var axis = counter
    
    // 데이터가 200개가 누적되면 1개씩 pop, push 되도록 하려면?
    if(counter>=400){
        newGraphData.shift();
        newx.pop();
    }

    newGraphData.push(veldata3);
    newx.push(axis); //0.00부터 카운팅되도록
    graphData.data.datasets[2].data = newGraphData;
    //counter = counter + 1
    myChart.update();
}

function update_axis3(veldata4){
    var newGraphData = graphData.data.datasets[3].data;
    var newx = graphData.data.labels;
    var axis = counter
    
    // 데이터가 200개가 누적되면 1개씩 pop, push 되도록 하려면?
    if(counter>=400){
        newGraphData.shift();
        newx.pop();
    }

    newGraphData.push(veldata4);
    newx.push(axis); //0.00부터 카운팅되도록
    graphData.data.datasets[3].data = newGraphData;
    //counter = counter + 1
    myChart.update();
}

// /***************************************** */
// function updatecount(count){
//     var newGraphData = graphData.data.datasets[0].data;
//     var newx = graphData.data.labels;
//     var axis = counter
    
//     // 데이터가 200개가 누적되면 1개씩 pop, push 되도록 하려면?
//     if(counter>=400){
//         newGraphData.shift();
//         newx.pop();
//     }

//     newGraphData.push(count);
//     newx.push(axis); //0.00부터 카운팅되도록
//     graphData.data.datasets[0].data = count;
//     counter = counter + 1
//     myChart.update();
// }

// function updatea(a){
//     var newGraphData = graphData.data.datasets[1].data;
    
//     // 데이터가 200개가 누적되면 1개씩 pop, push 되도록 하려면?
//     if(counter>=400){
//         newGraphData.shift();
//         newx.pop();
//     }

//     newGraphData.push(a);
//     graphData.data.datasets[1].data = a;
//     counter = counter + 1
//     myChart.update();
// }





















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