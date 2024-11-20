document.addEventListener("DOMContentLoaded", function() {
    // Handle weather map initialization
    if (weatherData && weatherData.lat && weatherData.lon) {
        // Initialize the map with the coordinates from the weather data
        var map = L.map('map').setView([weatherData.lat, weatherData.lon], 10);
        
        // Add the OpenStreetMap tiles to the map
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        }).addTo(map);

        // Add a marker for the city location
        L.marker([weatherData.lat, weatherData.lon]).addTo(map)
            .bindPopup('<b>' + weatherData.city + '</b>')
            .openPopup();
    } else {
        console.error("Weather data or coordinates are missing.");
    }

    // Initialize Typeahead.js for the city search input
    var citySearch = new Bloodhound({
        // Configure the API endpoint (GeoNames)
        remote: {
            url: 'http://api.geonames.org/searchJSON?formatted=true&lang=en&q=%QUERY%&maxRows=10&username=nuclearzombie',
            wildcard: '%QUERY%',
            filter: function(response) {
                // Return the formatted list of locations
                return response.geonames.map(function(location) {
                    return location.name + ', ' + location.countryName;
                });
            },
            // Adding a simple rate-limiting timeout to avoid too many requests
            rateLimitWait: 500
        },
        datumTokenizer: Bloodhound.tokenizers.whitespace,
        queryTokenizer: Bloodhound.tokenizers.whitespace
    });

    // Initialize Typeahead for the input field
    $('#city-search').typeahead(
        {
            minLength: 3,  // Start searching after 3 characters
            highlight: true
        },
        {
            name: 'city-search',
            source: citySearch
        }
    );

    // Handle city selection from Typeahead
    $('#city-search').on('typeahead:select', function(event, suggestion) {
        console.log('You selected: ' + suggestion);  // Log selected suggestion
        // You can perform actions based on the selection, like updating the map or making an API request for weather
    });
});
