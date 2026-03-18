// Render chart from AJAX data
function renderChart(chartId, endpoint) {
    fetch(endpoint, {
            method: 'GET',
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            }
        })
        .then(response => response.json())
        .then(data => {
            // Use Chart.js or similar to render chart
            // Example:
            // new Chart(document.getElementById(chartId), { type: 'bar', data: data });
            console.log('Chart data:', data);
        })
        .catch(error => alert('Chart error: ' + error));
}