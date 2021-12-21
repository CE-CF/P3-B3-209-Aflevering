// select buttons from html doc
var graph_buttons = document.querySelectorAll('.graph-buttons');

// add click listeners to room buttons
for (let i = 0; i < graph_buttons.length; i++){
  graph_buttons[i].addEventListener('click', changeGraph);
}

// get historic data from <script> "data" attribute
function getHistoryData() {
  var scripts = document.getElementsByTagName('script');
  var lastScript = scripts[scripts.length-1];
  var scriptName = lastScript;
  return {
     data : scriptName.getAttribute('data'),
  };
}

var historyData = getHistoryData().data;
var jsFormat = historyData.replaceAll("'", '"').replaceAll("True", 1).replaceAll("False", 0);
var jsonHistoryData = JSON.parse(jsFormat);

/* changeGraph(r)
is triggered when user clicks a "room button"
*/
export function changeGraph(r) {
  var roomNames = ["Bathroom", "Bedroom", "Garage", "Kitchen", "Living Room"]

  var room = (r.target.id).slice(4,5);

  var dataTimeStamps = [];
  var powerStateData = [];
  var tempData = [];
  var humidData = [];

  if (parseInt(r) == 0) {
    // TODO: implement overview of on/off periods for all rooms
    console.log('implement overview of on/off periods for all rooms')
  } else {
    var latestDate;
    jsonHistoryData.load.forEach(function(element, index){
      // if the historic data is from the room just chosen
      if(element[1] == parseInt(room)) {
        var timeSep = element[0].split(", ");
          if(latestDate != timeSep[0]){
            latestDate = timeSep[0];
            dataTimeStamps.push([timeSep[1], timeSep[0]])
          } else {
            dataTimeStamps.push(timeSep[1])
          }
        console.log(timeSep)
        powerStateData.push(element[2]);
        tempData.push(element[3]);
        humidData.push(element[4]);
      }
    });
  }

  // put the historic data into the "data-set" of the graph
  options.xaxis.categories = dataTimeStamps;
  options.series[0].data = powerStateData;
  options.series[1].data = tempData;
  options.series[2].data = humidData;

  const chart = new ApexCharts(document.querySelector('#chart'), options);

  chart.render();

  // update configurations (has to happen after render)
  try {
    chart.updateOptions({
      title: {
        text: roomNames[parseInt(room) - 1]
      }
    });
  } catch (e) {
    alert(e)
  }
}



// data an config for chart
var options = {
series: [{
    name: 'Rooms',
    type: 'area',
    data: [0]
  }, {
    name: 'Temperature',
    type: 'line',
    data: [0]
  }, {
    name: 'Humidity',
    type: 'line',
    data: [0]
  }],
  layout: {
    padding: {
      bottom: 200
    }
  },
  chart: {
    height: 600,
    width: 800,
    type: 'line',
    stacked: false,
    background: '#f4f4f4'
  },
  grid: {
    padding: {
        bottom: 10
    }
  },
  dataLabels: {
    enabled: false
  },
  stroke: {
    width: [1, 4, 4],
    curve: ['stepline', 'straight', 'straight'],
    colors: ['#FFB800', '#b01717', '#0074cc']
  },
  fill: {
    colors: ['#FFD915']
  },
  title: {
    text: 'Choose a room...',
    align: 'center',
    style: {
      color: '#334',
      fontSize: '20px',
    },
    offsetX: -40,
    offsetY: 10
  },
  colors: ['#FFB800', '#b01717', '#0074cc'],
  xaxis: {
    categories: [''],
    tickAmount: 8,
    labels: {
      maxHeight: 200
    }
  },
  yaxis: [
    {
      tickAmount: 1,
      decimalsInFloat: 0,
      axisTicks: {
        show: true
      },
      axisBorder: {
        show: true,
        color: '#DB9617'
      },
      labels: {
        style: {
          fontSize: '12px',
          fontWeight: '700',
          colors: '#DB9617',
        }
      },
      title: {
        text: "Rooms On",
        style: {
          color: '#DB9617',
          fontSize: '20px',
        }
      },
      tooltip: {
        enabled: false
      }
    },
    {
      seriesName: 'Temperature',
      min: 10,
      max: 30,
      decimalsInFloat: 0,
      opposite: true,
      axisTicks: {
        show: true,
      },
      axisBorder: {
        show: true,
        color: '#b01717'
      },
      labels: {
        style: {
          colors: '#b01717',
          fontSize: '12px',
          fontWeight: '700',
        }
      },
      title: {
        text: "Temperature (celcius)",
        style: {
          color: '#b01717',
          fontSize: '20px',
        }
      },
    },
    {
      seriesName: 'Humidity',
      min: 0,
      max: 100,
      decimalsInFloat: 0,
      opposite: true,
      axisTicks: {
        show: true,
      },
      axisBorder: {
        show: true,
        color: '#0074cc'
      },
      labels: {
        style: {
          colors: '#0074cc',
          fontSize: '12px',
          fontWeight: '700',
        },
      },
      title: {
        text: "Humidity (%)",
        style: {
          color: '#0074cc',
          fontSize: '20px',
        }
      },
    },
  ],
  tooltip: {
    fixed: {
      enabled: true,
      position: 'topLeft', // topRight, topLeft, bottomRight, bottomLeft
      offsetY: 30,
      offsetX: 60,
      shared: true,
      intersect: false,
      y: [{
        formatter: function (y) {
          if(typeof y !== "undefined") {
            return  y.toFixed(0) + " points";
          }
          return y;

        }
      }, {
        formatter: function (y) {
          if(typeof y !== "undefined") {
            return  y.toFixed(2) + " $";
          }
          return y;
        }
      }]
    },
  },
  legend: {
    horizontalAlign: 'left',
    offsetX: 40
  }
};

// graph init data
// options.series[0].data = [1, 2, 2, 1, 3, 5, 4, 2]
// options.series[1].data = [21.1, 23, 23.1, 24, 24.1, 24.9, 26.5, 22.5]
// options.series[2].data = [20, 29, 37, 36, 44, 45, 50, 58]
// options.xaxis.categories = [['10:00', '14-11'], '16:00', '22:00', ['04:00', '15-11'], '10:00', '10:00', '16:00', '22:00'];

// changeGraph('1');

const chart = new ApexCharts(document.querySelector('#chart'), options);

chart.render();
