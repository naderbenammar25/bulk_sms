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


    document.getElementById('campaign-content').addEventListener('change', function() {
        var messageField = document.getElementById('campaign-message');
        if (this.value) {
            messageField.disabled = true;
        } else {
            messageField.disabled = false;
        }
    });

    

    document.querySelectorAll('.edit-button').forEach(function(button) {
        button.addEventListener('click', function() {
            var campaignId = this.dataset.id;
            var campaignTitle = this.dataset.title;
            var campaignContent = this.dataset.content;
            var campaignMessage = this.dataset.message;
            var targetGroups = this.dataset.groups;
            var launchDate = this.dataset.launch_date;
            var campaignStatus = this.dataset.status;

            document.getElementById('edit-campaign-id').value = campaignId;
            document.getElementById('edit-campaign-title').value = campaignTitle;
            document.getElementById('edit-campaign-content').value = campaignContent;
            document.getElementById('edit-campaign-message').value = campaignMessage;
            document.getElementById('edit-target-groups').value = targetGroups;
            document.getElementById('edit-launch-date').value = launchDate;
            document.getElementById('edit-campaign-status').value = campaignStatus;

            var form = document.getElementById('edit-campaign-form');
            form.style.display = 'block';
        });
    });


        document.getElementById('campaign-content').addEventListener('change', function() {
            var messageField = document.getElementById('campaign-message');
            if (this.value) {
                messageField.disabled = true;
            } else {
                messageField.disabled = false;
            }
        });

        document.getElementById('create-campaign-button').addEventListener('click', function() {
            var form = document.getElementById('create-campaign-form');
            if (form.style.display === 'none' || form.style.display === '') {
                form.style.display = 'block';
            } else {
                form.style.display = 'none';
            }
        });


        document.getElementById('edit-campaign-content').addEventListener('change', function() {
            var editMessageField = document.getElementById('edit-campaign-message');
            if (this.value) {
                editMessageField.disabled = true;
            } else {
                editMessageField.disabled = false;
            }
        });