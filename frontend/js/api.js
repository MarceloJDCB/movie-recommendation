// API URL base
const API_BASE_URL = 'http://localhost:8000';

// Função para obter o token de autenticação armazenado
function getAuthToken() {
    return localStorage.getItem('authToken');
}

// Função para criar cabeçalhos de autenticação
function getAuthHeaders() {
    const token = getAuthToken();
    return {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'DENY',
        'X-XSS-Protection': '1; mode=block',
        'Content-Security-Policy': "default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; script-src 'self'",
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
        'Referrer-Policy': 'no-referrer-when-downgrade'
    };
}

// Função genérica para fazer requisições à API
async function apiRequest(endpoint, method = 'GET', data = null) {
    const url = `${API_BASE_URL}${endpoint}`;
    
    const options = {
        method,
        headers: getAuthHeaders(),
        mode: 'cors'
    };

    if (data) {
        options.body = JSON.stringify(data);
    }

    try {
        const response = await fetch(url, options);
        
        // Se a resposta é 401 (não autorizado), redirecionar para login
        if (response.status === 401) {
            localStorage.removeItem('authToken');
            window.location.href = 'index.html';
            return null;
        }
        
        // Para endpoints de login/cadastro que não retornam JSON em erro
        if (!response.ok && (endpoint === '/auth/login' || endpoint === '/auth/signup')) {
            const errorText = await response.text();
            throw new Error(errorText || 'Erro na requisição');
        }
        
        // Para outros endpoints, tentar parsear JSON
        const responseData = await response.json();
        
        if (!response.ok) {
            throw new Error(responseData.detail || 'Erro na requisição');
        }
        
        return responseData;
    } catch (error) {
        console.error('Erro na API:', error);
        throw error;
    }
}

// Funções específicas para cada endpoint da API

// Autenticação
const authAPI = {
    // Login
    login: async (username, password) => {
        const formData = new URLSearchParams();
        formData.append('username', username);
        formData.append('password', password);

        try {
            const response = await fetch(`${API_BASE_URL}/auth/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-Content-Type-Options': 'nosniff',
                    'X-Frame-Options': 'DENY',
                    'X-XSS-Protection': '1; mode=block',
                    'Content-Security-Policy': "default-src 'self'; img-src 'self' data:; style-src 'self' 'unsafe-inline'; script-src 'self'",
                    'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
                    'Referrer-Policy': 'no-referrer-when-downgrade'
                },
                body: formData
            });

            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(errorText || 'Falha no login');
            }

            return await response.json();
        } catch (error) {
            console.error('Erro no login:', error);
            throw error;
        }
    },

    // Cadastro
    signup: (userData) => apiRequest('/auth/signup', 'POST', userData),
    
    // Obter dados do usuário atual
    getCurrentUser: () => apiRequest('/users/me')
};

// Filmes
const moviesAPI = {
    // Listar filmes com suporte a paginação e busca
    async listMovies(skip = 0, limit = 12, search = '') {
        const url = new URL(`${API_BASE_URL}/movies`);
        
        // Adicionar parâmetros de paginação e busca
        url.searchParams.append('skip', skip);
        url.searchParams.append('limit', limit);
        
        // Adicionar parâmetro de busca apenas se existir
        if (search && search.trim() !== '') {
            url.searchParams.append('search', search.trim());
        }
        
        const response = await fetch(url, {
            headers: getAuthHeaders()
        });
        
        if (!response.ok) {
            throw new Error('Erro ao listar filmes');
        }
        
        return await response.json();
    },
    
    // Obter detalhes de um filme
    getMovie: (movieId) => apiRequest(`/movies/${movieId}`),
    
    // Criar avaliação
    createReview: (reviewData) => apiRequest('/movies/reviews', 'POST', reviewData),
    
    // Obter filmes similares
    getSimilarMovies: (movieId, limit = 5) => apiRequest(`/movies/recommendations/similar/${movieId}?limit=${limit}`),
    
    // Obter recomendações para o usuário atual
    getUserRecommendations: (limit = 10) => apiRequest(`/movies/recommendations/user?limit=${limit}`),
    
    // Obter filmes populares
    getPopularMovies: (limit = 10) => apiRequest(`/movies/recommendations/popular?limit=${limit}`)
};
