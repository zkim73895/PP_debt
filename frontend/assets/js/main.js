const API_BASE_URL = 'http://localhost:8000';
const FRONTEND_BASE_URL = 'http://localhost:3000';
let currentUser = null;
let currentJobId = null;

function saveToStorage(key, value) {
    localStorage.setItem(key, JSON.stringify(value));
}

function getFromStorage(key) {
    const item = localStorage.getItem(key);
    return item ? JSON.parse(item) : null;
}

function removeFromStorage(key) {
    localStorage.removeItem(key);
}

function showMessage(type, text, containerId = 'message-area') {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    const alertClass = {
        success: 'alert-success',
        error: 'alert-danger',
        warning: 'alert-warning',
        info: 'alert-info'
    }[type] || 'alert-info';
    
    container.innerHTML = `
        <div class="alert ${alertClass} alert-dismissible fade show" role="alert">
            ${text}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;

    setTimeout(() => {
        const alert = container.querySelector('.alert');
        if (alert) {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }
    }, 5000);
}

function formatDate(dateString) {
    if (!dateString) return 'Не указана';
    const date = new Date(dateString);
    return date.toLocaleDateString('ru-RU');
}

function checkAuth() {
    const user = getFromStorage('user');
    const token = getFromStorage('token');
    
    if (user && token) {
        currentUser = user;
        updateUIForAuth();
        return true;
    }
    return false;
}

function updateUIForAuth() {
    const loginSection = document.getElementById('login-section');
    const userSection = document.getElementById('user-section');
    const dashboardLink = document.getElementById('dashboard-link');
    const userEmail = document.getElementById('user-email');
    
    if (loginSection) loginSection.style.display = 'none';
    if (userSection) {
        userSection.style.display = 'block';
        if (userEmail && currentUser) {
            userEmail.textContent = currentUser.email;
        }
    }
    if (dashboardLink) dashboardLink.style.display = 'block';

    if (window.location.pathname.includes('login.html') && currentUser) {
        window.location.href = 'index.html';
    }
}

async function login(email, password) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/v1/auth/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ email, password })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            saveToStorage('user', data.user);
            saveToStorage('token', data.access_token);
            currentUser = data.user;
            
            showMessage('success', 'Вход выполнен успешно!');

            setTimeout(() => {
                updateUIForAuth();
                window.location.href = 'index.html';
            }, 1000);
            
            return true;
        } else {
            showMessage('error', data.detail || 'Ошибка входа');
            return false;
        }
    } catch (error) {
        console.error('Ошибка входа:', error);
        showMessage('error', 'Ошибка подключения к серверу');
        return false;
    }
}

function logout() {
    removeFromStorage('user');
    removeFromStorage('token');
    currentUser = null;

    const loginSection = document.getElementById('login-section');
    const userSection = document.getElementById('user-section');
    const dashboardLink = document.getElementById('dashboard-link');
    
    if (loginSection) loginSection.style.display = 'block';
    if (userSection) userSection.style.display = 'none';
    if (dashboardLink) dashboardLink.style.display = 'none';

    if (!window.location.pathname.includes('index.html')) {
        window.location.href = 'index.html';
    }
    
    showMessage('success', 'Вы успешно вышли из системы');
}

async function register(userData) {
    try {
        const response = await fetch(`${API_BASE_URL}/api/v1/auth/register`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(userData)
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showMessage('success', 'Регистрация успешна! Теперь войдите в систему.');

            const modal = bootstrap.Modal.getInstance(document.getElementById('registerModal'));
            if (modal) modal.hide();

            document.getElementById('email').value = userData.email;
            
            return true;
        } else {
            showMessage('error', data.detail || 'Ошибка регистрации', 'register-message');
            return false;
        }
    } catch (error) {
        console.error('Ошибка регистрации:', error);
        showMessage('error', 'Ошибка подключения к серверу', 'register-message');
        return false;
    }
}

async function loadJobs(categoryId = '', jobType = '') {
    const container = document.getElementById('jobs-container');
    if (!container) return;

    container.innerHTML = `
        <div class="col-12">
            <div class="text-center py-5">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Загрузка...</span>
                </div>
                <p class="mt-3">Загрузка вакансий...</p>
            </div>
        </div>
    `;
    
    try {
        let url = `${API_BASE_URL}/api/v1/jobs?limit=20`;
        if (categoryId) url += `&category_id=${categoryId}`;
        
        const response = await fetch(url);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const jobs = await response.json();
        
        if (jobs.length === 0) {
            container.innerHTML = `
                <div class="col-12">
                    <div class="alert alert-info">
                        <i class="bi bi-info-circle me-2"></i>
                        Пока нет доступных вакансий. Попробуйте позже.
                    </div>
                </div>
            `;
            return;
        }

        let filteredJobs = jobs;
        if (jobType) {
            filteredJobs = jobs.filter(job => job.job_type === jobType);
        }

        container.innerHTML = '';
        
        if (filteredJobs.length === 0) {
            container.innerHTML = `
                <div class="col-12">
                    <div class="alert alert-warning">
                        <i class="bi bi-exclamation-triangle me-2"></i>
                        Нет вакансий по выбранным фильтрам.
                    </div>
                </div>
            `;
            return;
        }
        
        filteredJobs.forEach(job => {
            const jobCard = createJobCard(job);
            container.appendChild(jobCard);
        });
        
    } catch (error) {
        console.error('Ошибка загрузки вакансий:', error);
        container.innerHTML = `
            <div class="col-12">
                <div class="alert alert-danger">
                    <i class="bi bi-x-circle me-2"></i>
                    Не удалось загрузить вакансии. Проверьте подключение к серверу.
                </div>
            </div>
        `;
    }
}

function createJobCard(job) {
    const col = document.createElement('div');
    col.className = 'col-lg-4 col-md-6 mb-4';
    
    // Определяем иконку по типу работы
    let icon = 'bi-briefcase';
    let typeText = 'Работа';
    if (job.job_type === 'internship') {
        icon = 'bi-mortarboard';
        typeText = 'Стажировка';
    } else if (job.job_type === 'part_time') {
        icon = 'bi-clock';
        typeText = 'Частичная';
    }
    
    col.innerHTML = `
        <div class="card job-card h-100" onclick="showJobDetails(${job.id})">
            <div class="card-body">
                <div class="d-flex justify-content-between align-items-start mb-2">
                    <h5 class="card-title job-title mb-0">${job.title}</h5>
                    <span class="badge bg-primary">${typeText}</span>
                </div>
                
                <p class="card-text text-muted small mb-3 text-ellipsis" style="max-height: 60px; overflow: hidden;">
                    ${job.description || 'Описание не указано'}
                </p>
                
                <div class="mt-auto">
                    <div class="d-flex justify-content-between align-items-center mb-2">
                        <span class="salary-badge text-success">
                            <i class="bi bi-cash"></i> ${job.salary || 'По договоренности'}
                        </span>
                        <small class="text-muted">
                            <i class="bi bi-calendar"></i> ${formatDate(job.created_at)}
                        </small>
                    </div>
                    
                    <div class="d-flex justify-content-between">
                        <span class="badge bg-secondary">
                            <i class="bi bi-tag"></i> ${job.category?.name || 'Без категории'}
                        </span>
                        <button class="btn btn-sm btn-outline-primary" onclick="event.stopPropagation(); showJobDetails(${job.id})">
                            <i class="bi bi-eye"></i> Подробнее
                        </button>
                    </div>
                </div>
            </div>
        </div>
    `;

    return col;
}

async function showJobDetails(jobId) {
    currentJobId = jobId;

    try {
        const response = await fetch(`${API_BASE_URL}/api/v1/jobs/${jobId}`);

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const job = await response.json();

        document.getElementById('modal-job-title').textContent = job.title;
        document.getElementById('modal-job-description').textContent = job.description || 'Не указано';
        document.getElementById('modal-job-requirements').textContent = job.requirements || 'Не указаны';
        document.getElementById('modal-job-salary').textContent = job.salary || 'По договоренности';
        document.getElementById('modal-job-department').textContent = job.department?.name || 'Не указан';
        document.getElementById('modal-job-category').textContent = job.category?.name || 'Без категории';

        const typeBadge = document.getElementById('modal-job-type');
        if (job.job_type === 'internship') {
            typeBadge.textContent = 'Стажировка';
            typeBadge.className = 'badge bg-info';
        } else if (job.job_type === 'part_time') {
            typeBadge.textContent = 'Частичная занятость';
            typeBadge.className = 'badge bg-warning';
        } else {
            typeBadge.textContent = 'Полная занятость';
            typeBadge.className = 'badge bg-primary';
        }

        const skillsContainer = document.getElementById('modal-job-skills');
        if (job.skills && job.skills.length > 0) {
            skillsContainer.innerHTML = job.skills.map(skill =>
                `<span class="skill-tag">${skill.name}</span>`
            ).join(' ');
        } else {
            skillsContainer.innerHTML = '<span class="text-muted">Навыки не указаны</span>';
        }

        const applyBtn = document.getElementById('apply-job-btn');
        if (currentUser) {
            applyBtn.disabled = false;
            applyBtn.textContent = 'Подать заявку';
        } else {
            applyBtn.disabled = true;
            applyBtn.textContent = 'Войдите для подачи заявки';
        }

        const modal = new bootstrap.Modal(document.getElementById('jobModal'));
        modal.show();

    } catch (error) {
        console.error('Ошибка загрузки деталей вакансии:', error);
        showMessage('error', 'Не удалось загрузить информацию о вакансии');
    }
}

async function applyForJob() {
    if (!currentUser) {
        showMessage('warning', 'Для подачи заявки необходимо войти в систему');
        return;
    }

    if (!currentJobId) {
        showMessage('error', 'Ошибка: не выбрана вакансия');
        return;
    }

    try {
        const response = await fetch(`${API_BASE_URL}/api/v1/applications`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                job_id: currentJobId,
                cover_letter: 'Я заинтересован в этой вакансии!'
            })
        });

        const data = await response.json();

        if (response.ok) {
            showMessage('success', 'Заявка успешно подана!');

            const modal = bootstrap.Modal.getInstance(document.getElementById('jobModal'));
            if (modal) modal.hide();

            updateApplicationsCount();

        } else {
            showMessage('error', data.detail || 'Ошибка при подаче заявки');
        }
    } catch (error) {
        console.error('Ошибка подачи заявки:', error);
        showMessage('error', 'Ошибка подключения к серверу');
    }
}

async function loadUserApplications() {
    const container = document.getElementById('applications-container');
    if (!container) return;

    if (!currentUser) {
        container.innerHTML = `
            <div class="alert alert-warning">
                <i class="bi bi-exclamation-triangle me-2"></i>
                Для просмотра заявок необходимо войти в систему.
            </div>
        `;
        return;
    }

    try {
        // Используем упрощенный эндпоинт
        const response = await fetch(`${API_BASE_URL}/api/v1/applications-simple`);

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const applications = await response.json();

        const userApplications = applications.filter(app => app.user_id === currentUser.id);

        if (userApplications.length === 0) {
            container.innerHTML = `
                <div class="text-center py-5">
                    <i class="bi bi-inbox fs-1 text-muted"></i>
                    <h5 class="mt-3">У вас пока нет заявок</h5>
                    <p class="text-muted">Найдите интересные вакансии и подайте заявку!</p>
                    <a href="index.html" class="btn btn-primary mt-2">
                        <i class="bi bi-search me-1"></i>Найти вакансии
                    </a>
                </div>
            `;

            updateStats(userApplications);
            return;
        }

        container.innerHTML = '';
        userApplications.forEach(app => {
            const appElement = createApplicationElement(app);
            container.appendChild(appElement);
        });

        updateStats(userApplications);

    } catch (error) {
        console.error('Ошибка загрузки заявок:', error);
        container.innerHTML = `
            <div class="alert alert-danger">
                <i class="bi bi-x-circle me-2"></i>
                Не удалось загрузить заявки. Проверьте подключение к серверу.
            </div>
        `;
    }
}

function createApplicationElement(application) {
    const div = document.createElement('div');
    div.className = 'card mb-3';

    // Определяем цвет статуса
    let statusClass = 'status-pending';
    let statusIcon = 'bi-clock';

    if (application.status === 'reviewed') {
        statusClass = 'status-reviewed';
        statusIcon = 'bi-eye';
    } else if (application.status === 'accepted') {
        statusClass = 'status-accepted';
        statusIcon = 'bi-check-circle';
    } else if (application.status === 'rejected') {
        statusClass = 'status-rejected';
        statusIcon = 'bi-x-circle';
    }

    div.innerHTML = `
        <div class="card-body">
            <div class="d-flex justify-content-between align-items-start">
                <div class="flex-grow-1">
                    <h5 class="card-title">${application.job?.title || 'Вакансия'}</h5>
                    <p class="card-text text-muted">
                        <i class="bi bi-calendar me-1"></i>
                        Подана: ${formatDate(application.created_at)}
                    </p>
                    
                    ${application.cover_letter ? `
                        <div class="mt-3">
                            <h6>Сопроводительное письмо:</h6>
                            <p class="card-text">${application.cover_letter}</p>
                        </div>
                    ` : ''}
                </div>
                
                <div class="text-end">
                    <span class="${statusClass} status-badge">
                        <i class="bi ${statusIcon} me-1"></i>
                        ${getStatusText(application.status)}
                    </span>
                    <div class="mt-2">
                        <small class="text-muted">ID: ${application.id}</small>
                    </div>
                </div>
            </div>
            
            <div class="mt-3">
                <a href="index.html" class="btn btn-sm btn-outline-primary">
                    <i class="bi bi-eye me-1"></i>Посмотреть вакансию
                </a>
            </div>
        </div>
    `;

    return div;
}

function updateStats(applications) {
    const total = applications.length;
    const pending = applications.filter(app => app.status === 'pending').length;
    const reviewed = applications.filter(app => app.status === 'reviewed').length;

    const totalEl = document.getElementById('total-applications');
    const pendingEl = document.getElementById('pending-applications');
    const reviewedEl = document.getElementById('reviewed-applications');

    if (totalEl) totalEl.textContent = total;
    if (pendingEl) pendingEl.textContent = pending;
    if (reviewedEl) reviewedEl.textContent = reviewed;
}

function getStatusText(status) {
    const statusMap = {
        'pending': 'На рассмотрении',
        'reviewed': 'Просмотрено',
        'accepted': 'Принято',
        'rejected': 'Отклонено'
    };

    return statusMap[status] || status;
}

async function updateApplicationsCount() {
    console.log('Applications count updated');
}

async function loadCategories() {
    const filter = document.getElementById('category-filter');
    if (!filter) return;

    try {
        const response = await fetch(`${API_BASE_URL}/api/v1/categories`);

        if (response.ok) {
            const categories = await response.json();

            filter.innerHTML = '<option value="">Все категории</option>';
            categories.forEach(category => {
                const option = document.createElement('option');
                option.value = category.id;
                option.textContent = category.name;
                filter.appendChild(option);
            });
        }
    } catch (error) {
        console.error('Ошибка загрузки категорий:', error);
    }
}

function applyFilters() {
    const categoryId = document.getElementById('category-filter').value;
    const jobType = document.getElementById('type-filter').value;

    loadJobs(categoryId, jobType);
}

function clearFilters() {
    document.getElementById('category-filter').value = '';
    document.getElementById('type-filter').value = '';
    loadJobs();
}

function refreshJobs() {
    loadJobs();
    showMessage('info', 'Список вакансий обновлен');
}

function loadUserInfo() {
    if (!currentUser) return;

    const fullNameEl = document.getElementById('user-full-name');
    const emailEl = document.getElementById('user-email');
    const typeEl = document.getElementById('user-type');
    const card = document.getElementById('user-info-card');

    if (fullNameEl) fullNameEl.textContent = currentUser.full_name;
    if (emailEl) emailEl.textContent = currentUser.email;
    if (typeEl) {
        typeEl.textContent = currentUser.user_type === 'student' ? 'Студент' : 'Работодатель';
    }
    if (card) card.style.display = 'block';
}

function fillTestCredentials() {
    document.getElementById('email').value = 'student@university.edu';
    document.getElementById('password').value = 'student123';
    showMessage('info', 'Тестовые данные заполнены. Нажмите "Войти" для продолжения.');
}

function showRegister() {
    const modal = new bootstrap.Modal(document.getElementById('registerModal'));
    modal.show();
}

function setupRegisterForm() {
    const form = document.getElementById('register-form');
    if (!form) return;

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const userData = {
            email: document.getElementById('register-email').value,
            password: document.getElementById('register-password').value,
            full_name: document.getElementById('register-name').value,
            user_type: document.getElementById('register-type').value
        };

        await register(userData);
    });
}

function setupLoginForm() {
    const form = document.getElementById('login-form');
    if (!form) return;

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const email = document.getElementById('email').value;
        const password = document.getElementById('password').value;

        await login(email, password);
    });
}

document.addEventListener('DOMContentLoaded', function() {
    console.log('Campus Jobs frontend загружен');

    checkAuth();

    setupLoginForm();
    setupRegisterForm();

    const path = window.location.pathname;

    if (path.includes('index.html') || path.endsWith('/') || path.endsWith('/frontend/')) {
        loadJobs();
        loadCategories();

    } else if (path.includes('dashboard.html')) {
        loadUserApplications();
        loadUserInfo();

    } else if (path.includes('login.html')) {
        console.log('Страница входа');
    }
});