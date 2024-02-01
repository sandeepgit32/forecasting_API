// Get the modal for clock
var modal = document.getElementById("myModal");
    
// Get the button that opens the modal
var btn = document.getElementById("myBtn");

// Get the <span> element that closes the modal
var span = document.getElementsByClassName("modal-close")[0];

// When the user clicks the button, open the modal 
btn.onclick = function() {
  modal.style.display = "block";
}

// When the user clicks on <span> (x), close the modal
span.onclick = function() {
  modal.style.display = "none";
}

// When the user clicks anywhere outside of the modal, close it
window.onclick = function(event) {
  if (event.target == modal) {
    modal.style.display = "none";
  }
}

// This is for able to see chart. We are using Apex Chart. U can check the documentation of Apex Charts too..
// Last six months income and expenditure
var income_last_few_months = JSON.parse(document.getElementById("apex1-data1")
  .getAttribute('income_last_few_months'));
var expenditure_last_few_months = JSON.parse(document.getElementById("apex1-data2")
  .getAttribute('expenditure_last_few_months'));
// Template variable string has ' (single quotes) instead of " (double quotes) 
// Before parsing the sting using JSON.parse, we need to conver all ' (single quotes) to " (double quotes) 
var last_few_months_text = JSON.parse(document.getElementById("apex1-data3")
  .getAttribute('last_few_months_text').replaceAll("\'","\""));
// var options = {
//   series: [{
//     name: 'Total Budget',
//     data: income_last_few_months
//   }, {
//     name: 'Expenditure',
//     data: expenditure_last_few_months
//   }],
//   chart: {
//     type: 'area',
//     height: 400
//   },
//   dataLabels: {
//     enabled: false
//   },
//   colors: ['#33b2df', '#3e7d06'],
//   stroke: {
//     curve: 'straight'
//   },
//   markers: {
//     size: 5,
//     hover: {
//       size: 9
//     }
//   },
//   xaxis: {
//     categories: last_few_months_text,
//   },
// };
var options = {
  series: [{
    name: 'Total Budget',
    data: income_last_few_months
  }, {
    name: 'Expenditure',
    data: expenditure_last_few_months
  }],
    chart: {
    type: 'bar',
    height: 400
  },
  plotOptions: {
    bar: {
      horizontal: false,
      borderRadius: 1,
      dataLabels: {
        position: 'top',
      },
    }
  },
  dataLabels: {
    enabled: true,
    offsetY: -16,
    style: {
      fontSize: '10px',
      colors: ['#008000', '#cc0000']
    }
  },
  colors: ['#00b300', '#ff6666'],
  stroke: {
    show: true,
    width: 1,
    colors: ['#666666']
  },
  fill: {
    opacity: 0.5
  },
  tooltip: {
    shared: true,
    intersect: false
  },
  xaxis: {
    categories: last_few_months_text,
  },
};

var chart = new ApexCharts(document.querySelector("#apex1"), options);
chart.render();



// Category-wise MTD expenditure
var category_wise_expenditure_MTD = JSON.parse(document.getElementById("apex2-data1")
  .getAttribute('category_wise_expenditure_MTD').replaceAll("\'","\""));
var options = {
  series: category_wise_expenditure_MTD['MTD_expenditure'],
  chart: {
  type: 'donut',
  height: 400
},
colors: ['#33b2df', '#77b300', '#ff6666', '#9999ff', '#e69900', '#85adad'],
labels: category_wise_expenditure_MTD['category'],
responsive: [{
  breakpoint: 480,
  options: {
    chart: {
      width: 200
    },
    legend: {
      position: 'bottom'
    }
  }
}]
};

var chart = new ApexCharts(document.querySelector("#apex2"), options);
chart.render();

// Sidebar Toggle Codes;

var sidebarOpen = false;
var sidebar = document.getElementById("sidebar");
var sidebarCloseIcon = document.getElementById("sidebarIcon");

function toggleSidebar() {
  if (!sidebarOpen) {
    sidebar.classList.add("sidebar_responsive");
    sidebarOpen = true;
  }
}

function closeSidebar() {
  if (sidebarOpen) {
    sidebar.classList.remove("sidebar_responsive");
    sidebarOpen = false;
  }
}


// Expenditure percent and time percent
current_expenditure_percent = JSON.parse(document.getElementById("target1-data1")
  .getAttribute('current_expenditure_percent'))
days_passed_percent = JSON.parse(document.getElementById("target1-data2")
  .getAttribute('days_passed_percent'))

  var options = {
  series: [current_expenditure_percent, days_passed_percent],
  chart: {
    height: 400,
    type: 'radialBar',
  },
  plotOptions: {
    radialBar: {
      dataLabels: {
        name: {
          fontSize: '20px',
        },
        value: {
          fontSize: '30px',
        },
        total: {
          show: true,
          label: 'Expenditure',
          formatter: function (w) {
            // By default this function returns the average of all series. The below is just an example to show the use of custom formatter function
            return current_expenditure_percent + '%'
          }
        }
      }
    }
  },
  labels: ['Expenditure', 'Time passed'],
  colors: ['#33b2df', '#59b300'],
};

var chart = new ApexCharts(document.querySelector("#target1"), options);
chart.render();


// cumulative_expenditure_day_wise_MTD
cumulative_expenditure_day_wise_MTD = JSON.parse(document.getElementById("target2-data1")
  .getAttribute('cumulative_expenditure_day_wise_mtd'))
cumulative_expected_expenditure_day_wise = JSON.parse(document.getElementById("target2-data2")
  .getAttribute('cumulative_expected_expenditure_day_wise'))
var options = {
  series: [{
    name: 'Expected expenditure',
    data: cumulative_expected_expenditure_day_wise
  },
  {
    name: 'Actual expenditure',
    type: 'line',
    data: cumulative_expenditure_day_wise_MTD
  }],
  chart: {
    height: 400,
    type: 'area',
  },
  dataLabels: {
    enabled: false
  },
  colors: ['#33b2df', '#3e7d06'],
  stroke: {
    curve: 'straight'
  },
  markers: {
    size: 5,
    hover: {
      size: 9
    }
  },
  xaxis: {
    categories: Array.from({length: cumulative_expected_expenditure_day_wise.length}, (_, i) => i + 1),
    title: {
      text: 'Days of the month'
    }
  },
  tooltip: {
    x: {
      format: 'dd/MM/yy HH:mm'
    },
  },
};

var chart = new ApexCharts(document.querySelector("#target2"), options);
chart.render();
