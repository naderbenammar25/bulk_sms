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


        document.addEventListener('DOMContentLoaded', function() {
            const statusSelect = document.getElementById('campaign-status');
            const launchDateInput = document.getElementById('launch-date');
            const durationInput = document.getElementById('duration');
        
            if (statusSelect && launchDateInput && durationInput) {
                function toggleDateFields() {
                    if (statusSelect.value === 'brouillon') {
                        launchDateInput.disabled = true;
                        durationInput.disabled = true;
                    } else {
                        launchDateInput.disabled = false;
                        durationInput.disabled = false;
                    }
                }
        
                statusSelect.addEventListener('change', toggleDateFields);
                toggleDateFields(); // Initial call to set the correct state
            }
        
            const editButtons = document.querySelectorAll('.edit-button');
            const editForm = document.getElementById('edit-campaign-form');
            const editCampaignId = document.getElementById('edit-campaign-id');
            const editCampaignTitle = document.getElementById('edit-campaign-title');
            const editCampaignContent = document.getElementById('edit-campaign-content');
            const editCampaignMessage = document.getElementById('edit-campaign-message');
            const editTargetGroups = document.getElementById('edit-target-groups');
            const editLaunchDate = document.getElementById('edit-launch-date');
            const editDuration = document.getElementById('edit-duration');
            const editMessagesPerPeriod = document.getElementById('edit-messages-per-period');
        
            if (editButtons && editForm && editCampaignId && editCampaignTitle && editCampaignContent && editCampaignMessage && editTargetGroups && editLaunchDate && editDuration && editMessagesPerPeriod) {
                editButtons.forEach(button => {
                    button.addEventListener('click', function() {
                        const campaignId = this.getAttribute('data-id');
                        const campaignTitle = this.getAttribute('data-title');
                        const campaignContent = this.getAttribute('data-content');
                        const campaignMessage = this.getAttribute('data-message');
                        const targetGroups = this.getAttribute('data-groups');
                        const launchDate = this.getAttribute('data-launch_date');
                        const duration = this.getAttribute('data-duration');
                        const messagesPerPeriod = this.getAttribute('data-messages_per_period');
        
                        editCampaignId.value = campaignId;
                        editCampaignTitle.value = campaignTitle;
                        editCampaignContent.value = campaignContent;
                        editCampaignMessage.value = campaignMessage;
                        editTargetGroups.value = targetGroups;
                        editLaunchDate.value = launchDate;
                        editDuration.value = duration;
                        editMessagesPerPeriod.value = messagesPerPeriod;
        
                        editForm.style.display = 'block';
                    });
                });
            }
        });