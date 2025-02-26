document.addEventListener('DOMContentLoaded', function() {
    // Ajoutez ici les fonctionnalités JavaScript si nécessaire
    console.log('Dashboard chargé !');

    document.querySelectorAll('.edit-button').forEach(button => {
        button.addEventListener('click', function() {
            const input = this.previousElementSibling;
            input.disabled = !input.disabled;
            if (!input.disabled) {
                input.focus();
            }
        });
    });

    const timezoneAutoCheckbox = document.getElementById('timezone_auto');
    const timezoneSelect = document.getElementById('timezone');
    const detectedTimezoneInput = document.getElementById('detected_timezone');

    function detectTimezone() {
        const detectedTimezone = Intl.DateTimeFormat().resolvedOptions().timeZone;
        detectedTimezoneInput.value = detectedTimezone;
        let optionFound = false;
        for (let option of timezoneSelect.options) {
            if (option.value === detectedTimezone) {
                option.selected = true;
                optionFound = true;
                break;
            }
        }
        if (!optionFound) {
            const newOption = document.createElement('option');
            newOption.value = detectedTimezone;
            newOption.text = detectedTimezone;
            newOption.selected = true;
            timezoneSelect.add(newOption);
        }
    }

    timezoneAutoCheckbox.addEventListener('change', function() {
        timezoneSelect.disabled = this.checked;
        if (this.checked) {
            detectTimezone();
            timezoneSelect.classList.add('disabled');
        } else {
            timezoneSelect.classList.remove('disabled');
        }
    });

    if (timezoneAutoCheckbox.checked) {
        detectTimezone();
        timezoneSelect.classList.add('disabled');
    }
});