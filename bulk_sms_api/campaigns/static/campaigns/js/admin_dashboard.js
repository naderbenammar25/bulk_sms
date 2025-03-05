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

    // Ajouter une animation de chargement lors de la soumission du formulaire
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function (e) {
            e.preventDefault();
            const submitButton = form.querySelector('button[type="submit"]');
            submitButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> En cours...';
            setTimeout(() => {
                submitButton.innerHTML = 'Soumettre';
                alert('Formulaire soumis avec succès !');
            }, 2000);
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