import { showPlotPanel, closePlotPanel } from './stationPlot.js';

// Declare the map variable globally so it can be accessed throughout the script
export let map;
let infoWindow; // Holds an instance of the InfoWindow for displaying bike station details

/**
 * Initializes the Google Map and fetches bike station data.
 * This function is called when the Google Maps API loads.
 */
export function initMap() {
    // Create a new Google Map instance centered on Dublin, Ireland
    map = new google.maps.Map(document.getElementById('map'), {
        center: { lat: 53.349805, lng: -6.26031 }, // Set initial center point (Dublin)
        zoom: 13 // Set default zoom level
    });

    // Create a new InfoWindow to display details when clicking on a marker
    infoWindow = new google.maps.InfoWindow();

    // Fetch bike station data from the server and add markers to the map
    fetch("/api/bike_stations")
        .then(response => response.json()) // Convert response to JSON format
        .then(stations => addMarkers(stations)) // Pass the station data to addMarkers function
        .catch(error => console.error("Error fetching bike stations:", error)); // Log errors if request fails
}

/**
 * Adds markers to the map for each bike station.
 * Each marker represents a bike station and is clickable to show details.
 *
 * @param {Array} stations - List of bike stations retrieved from the API.
 */
function addMarkers(stations) {
    stations.forEach(station => {
        // Create a marker at the station's position
        let marker = new google.maps.Marker({
            position: station.position, // Set marker position (latitude & longitude)
            map: map, // Attach marker to the existing map
            title: station.name, // Set the marker title to the station's name
            icon: {
                url: "/static/imgs/bike-marker.png", // the path of marer
                scaledSize: new google.maps.Size(35, 35), 
                anchor: new google.maps.Point(20, 40) 
              }
        });

        // Adding hover function and then simply display the current station information
        marker.addListener("mouseover", () => {
            const hoverContent = `
              <div class="custom-info-window">
                <h6><span class="marker-icon">📍</span>No.${station.number}: ${station.name}
                </h6>
                <div class="label">Available Bikes: ${station.available_bikes}</div>
                <div class="label">Available Stands: ${station.available_bike_stands}</div>
              </div>
            `;
            infoWindow.setContent(hoverContent);
            infoWindow.open(map, marker);
          });
        
        /**
         * Attach an event listener to each marker.
         * When clicked, it fetches weather data for that station and displays its details in an InfoWindow.
         */
        marker.addListener("click", function () {
            // Dynamically import the weather module to fetch weather data for the clicked station
            import("./weather.js").then(module => {
                module.fetchWeatherData(station);
            });

            showPlotPanel(station);

            //Show the bike prediction card and set the station_id
            const predictionCard = document.querySelector('#prediction-card');
            predictionCard.classList.remove('d-none');
            document.getElementById('station_id').value = station.number;


        });
    });
}
