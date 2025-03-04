document.addEventListener('DOMContentLoaded', function() {
    function showStep(step) {
        const steps = ['step1', 'step2', 'step3', 'step4', 'confirmation-step'];
        steps.forEach(s => {
            const element = document.getElementById(s);
            if (element) {
                element.style.display = 'none';
            }
        });
        const currentStep = document.getElementById('step' + step) || document.getElementById(step);
        if (currentStep) {
            currentStep.style.display = 'block';
        }
    }

    // Initial call to show the first step
    showStep(1);

    // Add event listeners for the "Suivant" and "Précédent" buttons
    document.querySelectorAll('[data-next-step]').forEach(button => {
        button.addEventListener('click', function() {
            const nextStep = this.getAttribute('data-next-step');
            if (validateStep(nextStep - 1)) {
                showStep(nextStep);
            }
        });
    });

    document.querySelectorAll('[data-prev-step]').forEach(button => {
        button.addEventListener('click', function() {
            const prevStep = this.getAttribute('data-prev-step');
            showStep(prevStep);
        });
    });

    // Add event listener for campaign type change
    const campaignTypeElement = document.getElementById('campaign-type');
    if (campaignTypeElement) {
        campaignTypeElement.addEventListener('change', function() {
            const launchDateElement = document.getElementById('launch-date');
            const durationElement = document.getElementById('duration');
            const durationUnitElement = document.getElementById('duration-unit');
            const messagesPerPeriodElement = document.getElementById('messages-per-period');
            const periodUnitElement = document.getElementById('period-unit');
            if (this.value === 'lancement_rapide') {
                launchDateElement.disabled = true;
                launchDateElement.value = new Date().toISOString().slice(0, 16);
                durationElement.disabled = true;
                durationUnitElement.disabled = true;
                messagesPerPeriodElement.disabled = true;
                periodUnitElement.disabled = true;
            } else {
                launchDateElement.disabled = false;
                durationElement.disabled = false;
                durationUnitElement.disabled = false;
                messagesPerPeriodElement.disabled = false;
                periodUnitElement.disabled = false;
            }
        });
    }

    // Add event listener for campaign content change
    const campaignContentElement = document.getElementById('campaign-content');
    if (campaignContentElement) {
        campaignContentElement.addEventListener('change', function() {
            const campaignMessageElement = document.getElementById('campaign-message');
            if (this.value) {
                campaignMessageElement.disabled = true;
            } else {
                campaignMessageElement.disabled = false;
            }
        });
    }

    // Add event listener for finish button
    const finishButton = document.getElementById('finish-button');
    finishButton.addEventListener('click', function() {
        const type = document.getElementById('campaign-type').value;
        const title = document.getElementById('campaign-title').value;
        const message = document.getElementById('campaign-message').value;
        const launchDate = document.getElementById('launch-date').value;
        const campaignPreview = document.getElementById('campaign-preview');
        const confirmationMessage = document.getElementById('confirmation-message');

        if (type === 'lancement_rapide') {
            campaignPreview.innerHTML = `<strong>Titre:</strong> ${title}<br><strong>Message:</strong> ${message}`;
            confirmationMessage.innerHTML = "Êtes-vous sûr de vouloir lancer la campagne avec ce contenu ?";
            showStep('confirmation-step');
        } else if (type === 'planifié') {
            confirmationMessage.innerHTML = `Votre campagne sera lancée à la date ${launchDate}. Vous recevrez un rappel 12 heures avant cette date.`;
            showStep('confirmation-step');
        } else {
            document.getElementById('campaign-form').submit();
        }
    });

    // Add event listener for confirm button
    const confirmButton = document.getElementById('confirm-button');
    confirmButton.addEventListener('click', function() {
        const type = document.getElementById('campaign-type').value;
        if (type === 'lancement_rapide') {
            document.getElementById('campaign-form').submit();
        }
    });

    // Validate the current step
    function validateStep(step) {
        let valid = true;
        if (step === 1) {
            const title = document.getElementById('campaign-title').value.trim();
            if (!title) {
                alert('Le titre de la campagne est obligatoire.');
                valid = false;
            }
        }
        return valid;
    }

    // Add event listener for form submission
    const campaignForm = document.getElementById('campaign-form');
    campaignForm.addEventListener('submit', function(event) {
        const type = document.getElementById('campaign-type').value;
        if (type === 'lancement_rapide') {
            const launchDateInput = document.getElementById('launch-date');
            launchDateInput.value = new Date().toISOString().slice(0, 16);
        }
    });
});