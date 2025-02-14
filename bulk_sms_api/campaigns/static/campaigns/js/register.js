document.addEventListener("DOMContentLoaded", function () {
    const canvas = document.getElementById("colorWheel");
    const ctx = canvas.getContext("2d");
    const radius = canvas.width / 2;

    const primaryInput = document.getElementById("primary_color");
    const secondaryInput = document.getElementById("secondary_color");
    const tertiaryInput = document.getElementById("tertiary_color");

    const colorInputs = [primaryInput, secondaryInput, tertiaryInput];
    let selectedInput = primaryInput;

    // Définir des couleurs formelles par défaut
    const defaultColors = ["#F4EDDE", "#2A303D", "#808080"];

    function drawColorWheel() {
        for (let angle = 0; angle < 360; angle += 1) {
            for (let r = 0; r < radius; r += 1) {
                const x = radius + r * Math.cos(angle * Math.PI / 180);
                const y = radius + r * Math.sin(angle * Math.PI / 180);

                const hue = angle;
                const saturation = (r / radius) * 100;
                const lightness = 100 - (r / radius) * 50;

                ctx.fillStyle = `hsl(${hue}, ${saturation}%, ${lightness}%)`;
                ctx.fillRect(x, y, 1, 1);
            }
        }
    }

    function getColorFromCanvas(x, y) {
        const imageData = ctx.getImageData(x, y, 1, 1).data;
        const r = imageData[0];
        const g = imageData[1];
        const b = imageData[2];
        return `#${((1 << 24) + (r << 16) + (g << 8) + b).toString(16).slice(1).toUpperCase()}`;
    }

    canvas.addEventListener("click", function (event) {
        const rect = canvas.getBoundingClientRect();
        const x = event.clientX - rect.left;
        const y = event.clientY - rect.top;
        const hexColor = getColorFromCanvas(x, y);

        if (selectedInput) {
            selectedInput.value = hexColor;
            selectedInput.style.backgroundColor = hexColor;
            selectedInput.style.color = getContrastColor(hexColor);
        }
    });

    colorInputs.forEach(input => {
        input.addEventListener("focus", function () {
            selectedInput = this;
        });

        input.addEventListener("input", function () {
            if (/^#([0-9A-F]{3}){1,2}$/i.test(this.value)) {
                this.style.backgroundColor = this.value;
                this.style.color = getContrastColor(this.value);
            } else {
                this.style.backgroundColor = "";
                this.style.color = "";
            }
        });
    });

    function getContrastColor(hex) {
        const r = parseInt(hex.substr(1, 2), 16);
        const g = parseInt(hex.substr(3, 2), 16);
        const b = parseInt(hex.substr(5, 2), 16);
        return (r * 0.299 + g * 0.587 + b * 0.114) > 186 ? "#000000" : "#FFFFFF";
    }

    function applyDefaultColors() {
        colorInputs.forEach((input, index) => {
            if (!/^#([0-9A-F]{3}){1,2}$/i.test(input.value)) {
                input.value = defaultColors[index];
                input.style.backgroundColor = defaultColors[index];
                input.style.color = getContrastColor(defaultColors[index]);
            }
        });
    }

    document.querySelector("form").addEventListener("submit", function (event) {
        applyDefaultColors();
    });

    drawColorWheel();
});



document.addEventListener("DOMContentLoaded", function () {
    const mailContainer = document.querySelector(".floating-mails-container");

    function createFloatingMail() {
        const mail = document.createElement("div");
        mail.classList.add("floating-mail");
        
        // Position aléatoire
        const startX = Math.random() * window.innerWidth;
        mail.style.left = `${startX}px`;

        // Taille aléatoire
        const size = Math.random() * 20 + 20; // Entre 20px et 40px
        mail.style.width = `${size}px`;
        mail.style.height = `${size * 0.75}px`;

        // Durée d'animation aléatoire
        const duration = Math.random() * 5 + 5; // Entre 5s et 10s
        mail.style.animationDuration = `${duration}s`;

        // Variation de la trajectoire horizontale
        const randomX = Math.random() * 2 - 1; // Entre -1 et 1
        mail.style.setProperty('--random-x', randomX);

        // Rotation aléatoire
        mail.style.transform = `rotate(${Math.random() * 360}deg)`;

        // Opacité aléatoire
        mail.style.opacity = Math.random() * 0.5 + 0.5; // Entre 0.5 et 1

        mailContainer.appendChild(mail);

        // Supprimer l'élément une fois l'animation terminée
        setTimeout(() => {
            mail.remove();
        }, duration * 1000);
    }

    // Générer des mails en continu avec un délai aléatoire
    function generateMailWithDelay() {
        createFloatingMail();
        const delay = Math.random() * 1000 + 500; // Entre 500ms et 1500ms
        setTimeout(generateMailWithDelay, delay);
    }

    generateMailWithDelay();
});