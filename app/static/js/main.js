// Main JavaScript file for すみれ＆みあ

// Add any interactive features here
document.addEventListener('DOMContentLoaded', function () {
    console.log('✨ すみれ＆みあ app loaded!');

    // Auto-hide flash messages after 5 seconds
    setTimeout(function () {
        let alerts = document.querySelectorAll('.alert');
        alerts.forEach(function (alert) {
            let bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);
});
