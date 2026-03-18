// AJAX fetch for dashboard data
function loadDashboard(endpoint) {
    fetch(endpoint, {
            method: 'GET',
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            // Render dashboard data
            // Example: update table or chart
            console.log(data);
        })
        .catch(error => alert('Dashboard error: ' + error));
}