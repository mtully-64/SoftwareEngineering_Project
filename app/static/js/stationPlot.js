// ===============================
// Draw Weekly Prediction Chart (Google Charts)
// ===============================
function drawWeeklyPredictionChart(stationId) {
  google.charts.load('current', { packages: ['corechart'] });
  google.charts.setOnLoadCallback(() => {
    fetch(`/predict_week?station_id=${stationId}`)
      .then(response => response.json())
      .then(data => {
        const chartData = new google.visualization.DataTable();
        chartData.addColumn('datetime', 'Time');
        chartData.addColumn('number', 'Predicted Bikes');

        data.forEach(entry => {
          chartData.addRow([
            new Date(entry.time),
            entry.predicted_bikes
          ]);
        });

        const options = {
          title: 'Predicted Available Bikes (Next 7 Days)',
          legend: { position: 'bottom' },
          curveType: 'function',
          hAxis: {
            title: 'Date',
            format: 'MMM/dd',
            slantedText: true,
            slantedTextAngle: 20,
            textStyle: {
              fontSize: 6
            },
            gridlines: {
              count: 7
            },
          },
          vAxis: { title: 'Available Bikes', minValue: 0 },
          height: 280
        };

        const chart = new google.visualization.LineChart(
          document.getElementById('weeklyChart')
        );
        chart.draw(chartData, options);
      });
  });
}


function drawDailyTrendChart(stationId) {
  google.charts.load('current', { packages: ['corechart'] });

  google.charts.setOnLoadCallback(() => {
    const data = new google.visualization.DataTable();
    data.addColumn('datetime', 'Time');
    data.addColumn('number', 'Available Bikes');
    data.addColumn('number', 'Free Stands');

    //now the historical date has problem, we need to scrap the station data again
    const url = `/api/station_history?station_id=${stationId}`;

    fetch(url)
      .then(res => res.json())
      .then(rawData => {
        // console.log("Raw data received:", rawData);
        rawData.forEach(entry => {
          data.addRow([
            new Date(entry.time),
            entry.bikes,
            entry.stands
          ]);
        });

        const options = {
          legend: { 
            position: 'bottom',
            alignment: 'center',
            textStyle: {fontSize: 10},
          },
          curveType: 'function',
          hAxis: {
            title: 'Time',
            format: 'HH:mm',
            slantedText: true,
            slantedTextAngle: 20,
            showTextEvery: 4,
          },
          vAxis: {
            viewWindow: {
              min: 0,
              max: 45
            },
            maxValue: 45,
            title: 'Count',
            minValue: 0
          },
          colors: ['#e74c3c', '#2980b9'],
          height: 280,
          weight: '100%',
        };

        const chart = new google.visualization.LineChart(
          document.getElementById('dailyTrendChart')
        );
        chart.draw(data, options);
      })
      .catch(err => {
        console.error("Error drawing daily trend chart:", err);
      });
  });
}


// ===============================
// Draw Station Bar Chart (Available Bikes & Stands)
// ===============================
function drawStationBarChart(station) {
  const ctx = document.getElementById('stationBarChart').getContext('2d');

  // Destroy existing chart if present
  if (window.stationChart) {
    window.stationChart.destroy();
  }

  // Create new bar chart
  window.stationChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: ['Available Bikes', 'Free Stands'],
      datasets: [{
        label: 'Count',
        data: [station.available_bikes, station.available_bike_stands],
        backgroundColor: ['#187a3c', '#a8d5ba']
      }]
    },
    options: {
      layout: { padding: { top: 20 } },
      responsive: true,
      plugins: {
        legend: { display: false },
        title: { display: false },
        datalabels: {
          color: '#333',
          anchor: 'end',
          align: 'top',
          font: {
            weight: 'bold',
            size: 12
          },
          formatter: value => value
        }
      },
      scales: {
        x: { grid: { display: false } },
        y: { beginAtZero: true }
      }
    },
    plugins: [ChartDataLabels]
  });
}


// ===============================
// Show Plot Panel (Right Sidebar)
// ===============================
export function showPlotPanel(station) {
  document.getElementById('plot-title').textContent = station.name;
  document.getElementById('plot-number').textContent = `Station No: ${station.number}`;
  document.getElementById('stationPlotPanel').classList.add('active');

  drawStationBarChart(station);
  drawWeeklyPredictionChart(station.number);
  drawDailyTrendChart(station.number)

}

// ===============================
// Close Plot Panel
// ===============================
export function closePlotPanel() {
  document.getElementById('stationPlotPanel').classList.remove('active');
}

// Make closePlotPanel accessible from global scope
window.closePlotPanel = closePlotPanel;
