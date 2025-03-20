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

// Fonction pour afficher/masquer des sections
document.addEventListener('DOMContentLoaded', function () {
    const editButtons = document.querySelectorAll('.edit-button');
    const saveButtons = document.querySelectorAll('.save-button');

    editButtons.forEach(button => {
        button.addEventListener('click', function () {
            const section = this.closest('.section');
            const inputs = section.querySelectorAll('input, select');
            inputs.forEach(input => input.disabled = false);
            this.style.display = 'none';
            section.querySelector('.save-button').style.display = 'inline-block';
        });
    });

    saveButtons.forEach(button => {
        button.addEventListener('click', function () {
            const section = this.closest('.section');
            const inputs = section.querySelectorAll('input, select');
            inputs.forEach(input => input.disabled = true);
            this.style.display = 'none';
            section.querySelector('.edit-button').style.display = 'inline-block';
            alert('Modifications enregistrées avec succès !');
        });
    });

    
});

/* slider /////////////*/
document.addEventListener('DOMContentLoaded', function () {
    const slides = document.querySelector('.slides');
    const slideItems = document.querySelectorAll('.slide');
    const prevButton = document.querySelector('.prev');
    const nextButton = document.querySelector('.next');
    let currentIndex = 0;
    let autoSlideInterval;

    // Fonction pour passer à la slide suivante
    function nextSlide() {
        currentIndex = (currentIndex + 1) % slideItems.length;
        updateSlider();
    }

    // Fonction pour passer à la slide précédente
    function prevSlide() {
        currentIndex = (currentIndex - 1 + slideItems.length) % slideItems.length;
        updateSlider();
    }

    // Fonction pour mettre à jour le slider
    function updateSlider() {
        slides.style.transform = `translateX(-${currentIndex * 100}%)`;
    }

    // Défilement automatique
    function startAutoSlide() {
        autoSlideInterval = setInterval(nextSlide, 5000); // Change de slide toutes les 5 secondes
    }

    // Arrêt du défilement automatique au survol
    function stopAutoSlide() {
        clearInterval(autoSlideInterval);
    }

    // Événements pour les boutons de navigation
    prevButton.addEventListener('click', prevSlide);
    nextButton.addEventListener('click', nextSlide);

    // Événements pour le défilement automatique
    slides.addEventListener('mouseenter', stopAutoSlide);
    slides.addEventListener('mouseleave', startAutoSlide);

    // Démarrer le défilement automatique au chargement de la page
    startAutoSlide();
});






document.addEventListener('DOMContentLoaded', function () {
    const openCtx = document.getElementById('openChart').getContext('2d');
    const unsubscribeCtx = document.getElementById('unsubscribeChart').getContext('2d');
    const rateCtx = document.getElementById('rateChart').getContext('2d');
    const messageCtx = document.getElementById('messageChart').getContext('2d');

    const openData = {
        labels: Object.keys(openDistribution),
        datasets: [{
            label: 'Ouvertures',
            data: Object.values(openDistribution),
            backgroundColor: 'rgba(75, 192, 192, 0.2)',
            borderColor: 'rgba(75, 192, 192, 1)',
            borderWidth: 1
        }]
    };

    const unsubscribeData = {
        labels: Object.keys(unsubscribeDistribution),
        datasets: [{
            label: 'Désabonnements',
            data: Object.values(unsubscribeDistribution),
            backgroundColor: 'rgba(255, 99, 132, 0.2)',
            borderColor: 'rgba(255, 99, 132, 1)',
            borderWidth: 1
        }]
    };

    const rateData = {
        labels: ['Taux d\'Ouverture', 'Taux de Désabonnement'],
        datasets: [{
            label: 'Taux',
            data: [openRate, unsubscribeRate],
            backgroundColor: ['rgba(75, 192, 192, 0.2)', 'rgba(255, 99, 132, 0.2)'],
            borderColor: ['rgba(75, 192, 192, 1)', 'rgba(255, 99, 132, 1)'],
            borderWidth: 1
        }]
    };

    const messageData = {
        labels: ['Messages Envoyés', 'Messages Ouverts', 'Messages Désabonnés'],
        datasets: [{
            label: 'Messages',
            data: [totalSent, totalOpened, totalUnsubscribed],
            backgroundColor: ['rgba(54, 162, 235, 0.2)', 'rgba(75, 192, 192, 0.2)', 'rgba(255, 99, 132, 0.2)'],
            borderColor: ['rgba(54, 162, 235, 1)', 'rgba(75, 192, 192, 1)', 'rgba(255, 99, 132, 1)'],
            borderWidth: 1
        }]
    };

    new Chart(openCtx, {
        type: 'bar',
        data: openData,
        options: {
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });

    new Chart(unsubscribeCtx, {
        type: 'bar',
        data: unsubscribeData,
        options: {
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });

    new Chart(rateCtx, {
        type: 'pie',
        data: rateData,
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'top',
                }
            }
        }
    });

    new Chart(messageCtx, {
        type: 'doughnut',
        data: messageData,
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'top',
                }
            }
        }
    });
});