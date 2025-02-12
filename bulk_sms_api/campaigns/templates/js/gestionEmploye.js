e.js
function toggleStatus(userId) {
    fetch(`/api/employees/${userId}/toggle_status/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        const statusCell = document.getElementById(`status-${data.id}`);
        const button = document.getElementById(`toggle-button-${data.id}`);
        if (data.is_active) {
            statusCell.textContent = 'Actif';
            button.textContent = 'Désactiver';
        } else {
            statusCell.textContent = 'Inactif';
            button.textContent = 'Activer';
        }
    })
    .catch(error => console.error('There was an error toggling the status!', error));
}