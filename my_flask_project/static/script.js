document.addEventListener("DOMContentLoaded", function() {
    console.log("JavaScript Loaded!");  // Debugging to check if JS is working

    // ✅ Form Validation
    const forms = document.querySelectorAll("form");

    forms.forEach(form => {
        form.addEventListener("submit", function(event) {
            let isValid = true;
            const inputs = form.querySelectorAll("input[required]");

            inputs.forEach(input => {
                if (input.value.trim() === "") {
                    isValid = false;
                    input.classList.add("error");
                    input.nextElementSibling?.remove(); // Remove existing error messages
                    let errorText = document.createElement("span");
                    errorText.className = "error-message";
                    errorText.innerText = `${input.placeholder} is required.`;
                    input.insertAdjacentElement("afterend", errorText);
                } else {
                    input.classList.remove("error");
                    let existingError = input.nextElementSibling;
                    if (existingError?.classList.contains("error-message")) {
                        existingError.remove();
                    }
                }
            });

            if (!isValid) {
                event.preventDefault(); // Prevent form submission
            }
        });
    });

    // ✅ Show/Hide Password Toggle
    document.querySelectorAll("input[type='password']").forEach(passwordField => {
        let toggleBtn = document.createElement("span");
        toggleBtn.innerText = "👁️";
        toggleBtn.classList.add("toggle-password");
        passwordField.parentNode.insertBefore(toggleBtn, passwordField.nextSibling);

        toggleBtn.addEventListener("click", function() {
            if (passwordField.type === "password") {
                passwordField.type = "text";
                toggleBtn.innerText = "🙈";
            } else {
                passwordField.type = "password";
                toggleBtn.innerText = "👁️";
            }
        });
    });

    // ✅ Flash Message Auto Hide (Success/Error Alerts)
    setTimeout(() => {
        document.querySelectorAll(".flash-message").forEach(message => {
            message.style.transition = "opacity 0.5s";
            message.style.opacity = "0";
            setTimeout(() => message.remove(), 500);
        });
    }, 5000);
});
