// AJAX upload for dataset
function uploadDataset(formId, endpoint) {
    const form = document.getElementById(formId);
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        const formData = new FormData(form);
        fetch(endpoint, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('Upload successful!');
                } else {
                    alert('Upload failed: ' + (data.error || 'Unknown error'));
                }
            })
            .catch(error => alert('Error: ' + error));
    });
}