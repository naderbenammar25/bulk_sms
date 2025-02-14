document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('add-employee').addEventListener('click', function() {
        window.location.href = "/add_employee/";
    });

    function connectAsEmployee(employeeId) {
        window.location.href = "/accueil_MK_User/?employee_id=" + employeeId;
    }

    function editEmployee(employeeId) {
        window.location.href = "/edit_user/?user_id=" + employeeId;
    }

    function resetPassword(employeeId) {
        window.location.href = "/reset_password/?user_id=" + employeeId;
    }

    function toggleStatus(employeeId) {
        fetch("/toggle_user_status/" + employeeId + "/", {
            method: 'POST',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            }
        }).then(response => {
            if (response.ok) {
                location.reload();
            }
        });
    }

    document.getElementById('search').addEventListener('input', function() {
        const searchValue = this.value.toLowerCase();
        const rows = document.querySelectorAll('#employees-table tbody tr');
        rows.forEach(row => {
            const name = row.querySelector('td').textContent.toLowerCase();
            if (name.includes(searchValue)) {
                row.style.display = '';
            } else {
                row.style.display = 'none';
            }
        });
    });

    document.getElementById('employee-actions').addEventListener('change', function() {
        const employeeId = this.value;
        if (employeeId) {
            fetch(`/employee_actions/${employeeId}/`)
                .then(response => response.json())
                .then(data => {
                    // Afficher les actions de l'employé
                    console.log(data);
                });
        }
    });
});