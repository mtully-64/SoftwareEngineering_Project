// Fetch weather data for a specific bike station
export function fetchWeatherData(station) {
    const lat = station.position.lat;
    const lon = station.position.lng;

    fetch(`/api/weather?lat=${lat}&lon=${lon}`)
        .then(response => response.json())
        .then(weatherData => updateWeatherInfo(weatherData, station))
        .catch(error => console.error("Error fetching weather data:", error));
}

// Function to update weather info on the page
function updateWeatherInfo(weatherData, station) {
    document.getElementById("temp-here").textContent = `${weatherData.main.temp}°C`;
    document.getElementById("wind-here").textContent = `${weatherData.wind.speed} m/s`;
    document.getElementById("cond-here").textContent = weatherData.weather[0].main;

    //And loads bike station onto page
    const bikeInfo = document.querySelector(".bike-info");
    bikeInfo.innerHTML = `
        <h2>Station No: ${station.number}</h2>
        <ul>
            <li><strong>Address:</strong> ${station.address}</li>
            <li><strong>Total Bikes:</strong> ${station.bike_stands}</li>
            <li><strong>Available Bikes:</strong> ${station.available_bikes}</li>
            <li><strong>Available Stands:</strong> ${station.available_bike_stands}</li>
        </ul>
    `;
}
