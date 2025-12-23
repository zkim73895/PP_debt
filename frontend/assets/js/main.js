const API_BASE_URL = 'http://localhost:8000';

async function loadJobs() {
    try {
        const response = await fetch(`${API_BASE_URL}/api/jobs`);
        const jobs = await response.json();
        displayJobs(jobs);
    } catch (error) {
        console.error('Ошибка загрузки вакансий:', error);
        showError('Не удалось загрузить вакансии');
    }
}

function displayJobs(jobs) {
    const container = document.getElementById('jobs-container');
    if (!container) return;

    container.innerHTML = `
        <div class="col-12">
            <div class="alert alert-warning">
                <i class="bi bi-exclamation-triangle me-2"></i>
                Вакансии скоро появятся. API находится в разработке.
            </div>
        </div>
    `;
}

function showError(message) {
    const container = document.getElementById('jobs-container');
    if (container) {
        container.innerHTML = `
            <div class="col-12">
                <div class="alert alert-danger">
                    <i class="bi bi-x-circle me-2"></i>
                    ${message}
                </div>
            </div>
        `;
    }
}

document.addEventListener('DOMContentLoaded', function() {
    console.log('Campus Jobs frontend загружен');

    // Загружаем вакансии
    if (document.getElementById('jobs-container')) {
        setTimeout(loadJobs, 1000); // Имитация загрузки
    }
});