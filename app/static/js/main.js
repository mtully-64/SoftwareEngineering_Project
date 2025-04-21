import { initMap } from "./map.js";

let mapLoaded = false; // Flag to track whether the Google Maps API has been loaded
const mapElement = document.getElementById('map');

/**
 * Fetches the Google Maps API key securely from the backend.
 */
async function getGoogleMapsKey() {
    try {
        const response = await fetch("/api/google-maps-key");
        const data = await response.json();
        return data.apiKey;
    } catch (error) {
        console.error("Error fetching Google Maps API key:", error);
        return null;
    }
}

/**
 * Creates an Intersection Observer to detect when the map element is visible in the viewport.
 * If the map enters the viewport and has not been loaded yet, dynamically loads the Google Maps JavaScript API.
 */
const observer = new IntersectionObserver(async (entries) => {
    entries.forEach(async (entry) => {
        if (entry.isIntersecting && !mapLoaded) { // Check if the map is visible and has not been loaded
            const apiKey = await getGoogleMapsKey(); // Get API key from backend
            if (!apiKey) {
                console.error("Google Maps API key is missing!");
                return;
            }

            // Dynamically create and append the Google Maps API script
            const script = document.createElement("script");
            script.src = `https://maps.googleapis.com/maps/api/js?key=${apiKey}&callback=initMap`;
            script.async = true; // Load asynchronously to avoid blocking rendering
            script.defer = true; // Defer execution until the page has fully loaded
            document.body.appendChild(script);

            // Prevent multiple script injections
            mapLoaded = true;
        }
    });
});

// Start observing the map element to trigger the API loading when it comes into view
if (mapElement) {
    observer.observe(mapElement);
}

/**
 * Exposes the `initMap` function globally so that it can be called as a callback 
 * by the Google Maps API after the script loads.
 */
window.initMap = initMap;

// Logout function
window.logout = function () {
    fetch("/logout", { credentials: "include" })
        .then(response => {
            if (response.ok) {
                window.location.href = "/login"; // Redirect to login after logout
            } else {
                console.error("Logout failed:", response.status);
            }
        })
        .catch(error => console.error("Error logging out:", error));
};