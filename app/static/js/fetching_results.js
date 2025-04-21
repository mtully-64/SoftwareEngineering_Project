// ===============================
// Function: predict()
// Description: Sends user-selected date, time, and station to backend
//              and displays predicted bike availability
// ===============================
function predict() {
    console.log("predict function is called");

    // Show the prediction card if hidden
    document.getElementById('prediction-card').classList.remove('d-none');

    // Collect input values
    const date = document.getElementById("date").value;
    const time = document.getElementById("time").value;
    const station_id = document.getElementById("station_id").value;
    const resultDiv = document.getElementById("result");

    // Input validation
    if (!date || !time || !station_id) {
        resultDiv.innerHTML = "Please select date time and station.";
        return;
    }

    // Format time to HH:MM:SS format
    const formattedTime = `${time}:00`;

    // Send GET request to Flask backend with query parameters
    fetch(`/predict?date=${date}&time=${formattedTime}&station_id=${station_id}`, {
        method: "GET"
    })
    .then(response => response.json())
    .then(data => {
        // Handle prediction response
        if (data.predicted_available_bikes !== undefined) {
            resultDiv.innerHTML = `Predicted Available Bikes: ${data.predicted_available_bikes}`;
        } else {
            resultDiv.innerHTML = `Error: ${data.error || "Something went wrong"}`;
        }
    })
    .catch(error => {
        // Handle fetch error
        resultDiv.innerHTML = `Error: ${error.message}`;
    });
}

// ===============================
// Function: drawWeeklyPredictionChart()
// Description: Draws a Google Chart with weekly bike predictions for a station
// ===============================
function drawWeeklyPredictionChart(stationId) {
    // Load Google Charts
    google.charts.load('current', { packages: ['corechart'] });

    // Once Google Charts is ready, fetch and draw chart
    google.charts.setOnLoadCallback(() => {
        fetch(`/predict_week?station_id=${stationId}`)
        .then(response => response.json())
        .then(data => {
            // Create and populate chart data table
            const chartData = new google.visualization.DataTable();
            chartData.addColumn('datetime', 'Time');
            chartData.addColumn('number', 'Predicted Bikes');

            data.forEach(entry => {
                chartData.addRow([
                    new Date(entry.time),
                    entry.predicted_bikes
                ]);
            });

            // Chart display options
            // const options = {
            //     title: 'Weekly Bike Availability Prediction',
            //     legend: { position: 'bottom' },
            //     curveType: 'function',
            //     hAxis: { format: 'MM/dd HH:mm' },
            //     vAxis: { minValue: 0 },
            //     height: 300
            // };
            const options = {
                title: 'Predicted Available Bikes (Next 7 Days)',
                legend: { position: 'bottom' },
                curveType: 'function',
                hAxis: {
                    format: 'MMM/dd',
                    slantedText: true,
                    slantedTextAngle: 20,
                    textStyle: { fontSize: 10 },
                    gridlines: { count: 7 },
                },
                vAxis: { title: 'Available Bikes', minValue: 0 },
                height: 280
            };
            

            // Draw the chart in the designated HTML container
            const chart = new google.visualization.LineChart(
                document.getElementById('weeklyChart')
            );
            chart.draw(chartData, options);
        });
    });
}

// ===============================
// Function: toggleSection(section)
// Description: In prediction card, We allow user to select which way to predict the number of available bikes in the future.
// ===============================
export function toggleSection(section) {
    const single = document.getElementById('single-day-section');
    const weekly = document.getElementById('weekly-section');
  
    if (section === 'single-day') {
      single.classList.remove('d-none');
      weekly.classList.add('d-none');
    } else {
      single.classList.add('d-none');
      weekly.classList.remove('d-none');
  
      const stationId = document.getElementById("station_id").value;
      if (stationId) {
        drawWeeklyPredictionChart(stationId);
      } else {
        document.getElementById("weeklyChart").innerHTML = "<small class='text-muted'>Please enter a Station ID above.</small>";
      }
    }
  }
  
window.toggleSection = toggleSection;
window.predict = predict;