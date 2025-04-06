// Verificar se o usuário está logado
function isAuthenticated() {
    return localStorage.getItem('authToken') !== null;
}

// Redirecionar para a página de login se não estiver autenticado
function requireAuth() {
    if (!isAuthenticated()) {
        window.location.href = 'index.html';
        return false;
    }
    return true;
}

// Redirecionar para a página de filmes se já estiver autenticado
function redirectIfAuthenticated() {
    if (isAuthenticated()) {
        window.location.href = 'movies.html';
        return true;
    }
    return false;
}

// Inicializar página de login
function initLoginPage() {
    // Se já estiver autenticado, redirecionar para movies.html
    if (redirectIfAuthenticated()) return;
    
    // Botões de alternância entre abas
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');
    
    // Adicionar listeners para alternância de abas
    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const tabId = btn.getAttribute('data-tab');
            
            // Remover classe active de todas as abas e conteúdos
            tabBtns.forEach(b => b.classList.remove('active'));
            tabContents.forEach(c => c.classList.remove('active'));
            
            // Adicionar classe active ao botão e conteúdo correspondente
            btn.classList.add('active');
            document.getElementById(tabId).classList.add('active');
        });
    });
    
    // Formulário de login
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const username = document.getElementById('login-username').value;
            const password = document.getElementById('login-password').value;
            const messageEl = document.getElementById('login-message');
            
            try {
                messageEl.textContent = 'Autenticando...';
                messageEl.className = 'message';
                
                const response = await authAPI.login(username, password);
                
                // Armazenar token
                localStorage.setItem('authToken', response.access_token);
                
                // Redirecionar para a página de filmes
                window.location.href = 'movies.html';
            } catch (error) {
                messageEl.textContent = 'Usuário ou senha incorretos';
                messageEl.className = 'message error';
            }
        });
    }
    
    // Formulário de cadastro
    const signupForm = document.getElementById('signup-form');
    if (signupForm) {
        signupForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const username = document.getElementById('signup-username').value;
            const email = document.getElementById('signup-email').value;
            const password = document.getElementById('signup-password').value;
            const messageEl = document.getElementById('signup-message');
            
            try {
                messageEl.textContent = 'Criando conta...';
                messageEl.className = 'message';
                
                await authAPI.signup({ username, email, password });
                
                // Mostrar mensagem de sucesso
                messageEl.textContent = 'Conta criada com sucesso! Faça login para continuar.';
                messageEl.className = 'message success';
                
                // Limpar o formulário
                signupForm.reset();
                
                // Mudar para a aba de login após 2 segundos
                setTimeout(() => {
                    document.querySelector('[data-tab="login"]').click();
                }, 2000);
            } catch (error) {
                messageEl.textContent = error.message || 'Erro ao criar conta';
                messageEl.className = 'message error';
            }
        });
    }
}

// Inicializar funcionalidade de logout
function initLogout() {
    const logoutBtn = document.getElementById('logout-btn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', (e) => {
            e.preventDefault();
            localStorage.removeItem('authToken');
            window.location.href = 'index.html';
        });
    }
}

// Executar quando o DOM estiver pronto
document.addEventListener('DOMContentLoaded', () => {
    // Verificar se estamos na página de login
    const isLoginPage = window.location.pathname.endsWith('index.html') || 
                        window.location.pathname === '/' || 
                        window.location.pathname === '/frontend/';
    
    if (isLoginPage) {
        initLoginPage();
    } else {
        // Verificar autenticação para outras páginas
        requireAuth();
        initLogout();
    }
});
