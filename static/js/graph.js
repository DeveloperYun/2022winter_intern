var ctx = document.getElementById('myChart').getContext('2d'); //'mychart' canvas에 렌더링
var graphData = {
    type: 'bar',
    data: {
        labels: [],
        datasets: [
            {
                label: 'velocity',
                data: [],
                lineTension: 0,
                borderWidth: 2,
                fillColor: 'rgba(44, 171, 221, 0.6)',
                borderColor: 'rgba(44, 171, 221, 0.6)',
                backgroundColor: 'rgba(44, 171, 221, 0.6)',
                fill: false,
            }
        ]
    },
    options: {
        reponsive: true,
        scales: {
            x: {
                type: 'time',
                time: {
                    unit: 'millisecond'
                }
            },
            y: {
                stacked: true,
            }
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
    //console.log(djangoData);

    var newGraphData = graphData.data.datasets[0].data;
    var newx = graphData.data.labels;
    var axis = counter
    //console.log(newx)
    
    // 데이터가 200개가 누적되면 1개씩 pop, push 되도록 하려면?
    if(counter>=400){
        // counter = 0
        // for(var i=0; i<75; i++){
        newGraphData.shift();
        newx.pop();
        //}
        //console.log(counter);
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
document.querySelector('#socket-cut').onclick = function(e){
    socket.close();
}