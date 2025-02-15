document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('add-employee').addEventListener('click', function() {
        window.location.href = "/add_employee/";
    });

    document.querySelectorAll('.edit-employee').forEach(button => {
        button.addEventListener('click', function() {
            const employeeId = this.dataset.employeeId;
            window.location.href = "/edit_user/" + employeeId + "/";
        });
    });

    document.querySelectorAll('.reset-password').forEach(button => {
        button.addEventListener('click', function() {
            const employeeId = this.dataset.employeeId;
            window.location.href = "/reset_password/" + employeeId + "/";
        });
    });

    document.querySelectorAll('.toggle-status').forEach(button => {
        button.addEventListener('click', function() {
            const employeeId = this.dataset.employeeId;
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
        });
    });

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