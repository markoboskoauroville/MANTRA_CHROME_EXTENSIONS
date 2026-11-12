document.addEventListener('DOMContentLoaded', function() {
    const goButton = document.getElementById('go');
    const outDiv = document.getElementById('out');

    if (goButton && outDiv) {
        goButton.addEventListener('click', function() {
            outDiv.textContent = 'done';
        });
    }
});
