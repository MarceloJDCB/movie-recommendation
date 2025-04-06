// Inicializar página de perfil
async function initProfilePage() {
    // Verificar autenticação
    if (!requireAuth()) return;
    
    // Carregar informações do usuário
    loadUserProfile();
    
    // Carregar recomendações
    loadRecommendations();
    
    // Carregar filmes populares
    loadPopularMovies();
}

// Carregar perfil do usuário
async function loadUserProfile() {
    const profileContainer = document.getElementById('profile-info');
    
    if (!profileContainer) return;
    
    try {
        const userInfo = await authAPI.getCurrentUser();
        
        profileContainer.innerHTML = `
            <h2 class="user-name">${userInfo.username}</h2>
            <p class="user-email">${userInfo.email}</p>
            <p>Membro desde: ${formatDate(userInfo.created_at)}</p>
        `;
    } catch (error) {
        console.error('Erro ao carregar perfil:', error);
        profileContainer.innerHTML = '<p class="error">Erro ao carregar informações do perfil</p>';
    }
}

// Carregar recomendações para o usuário
async function loadRecommendations() {
    const recommendationsContainer = document.getElementById('recommendations-list');
    
    if (!recommendationsContainer) return;
    
    try {
        const movies = await moviesAPI.getUserRecommendations();
        
        if (movies.length === 0) {
            recommendationsContainer.innerHTML = '<p>Nenhuma recomendação disponível ainda. Avalie mais filmes para receber recomendações personalizadas.</p>';
            return;
        }
        
        renderMovies(recommendationsContainer, movies);
    } catch (error) {
        console.error('Erro ao carregar recomendações:', error);
        recommendationsContainer.innerHTML = '<p class="error">Erro ao carregar recomendações</p>';
    }
}

// Carregar filmes populares
async function loadPopularMovies() {
    const popularMoviesContainer = document.getElementById('popular-movies-list');
    
    if (!popularMoviesContainer) return;
    
    try {
        const movies = await moviesAPI.getPopularMovies();
        
        if (movies.length === 0) {
            popularMoviesContainer.innerHTML = '<p>Nenhum filme popular disponível.</p>';
            return;
        }
        
        renderMovies(popularMoviesContainer, movies);
    } catch (error) {
        console.error('Erro ao carregar filmes populares:', error);
        popularMoviesContainer.innerHTML = '<p class="error">Erro ao carregar filmes populares</p>';
    }
}

// Renderizar lista de filmes
function renderMovies(container, movies) {
    container.innerHTML = '';
    
    movies.forEach(movie => {
        const movieCard = createMovieCard(movie);
        container.appendChild(movieCard);
    });
}

// Criar card de filme (mesma função do movies.js)
function createMovieCard(movie) {
    const card = document.createElement('div');
    card.className = 'movie-card';
    
    // Definir imagem placeholder ou usar imagem do filme se disponível
    const imageUrl = movie.posterUrl || '';
    
    card.innerHTML = `
        <div class="movie-card-image">
            ${imageUrl ? `<img src="${imageUrl}" alt="${movie.title}">` : movie.title.charAt(0).toUpperCase()}
        </div>
        <div class="movie-card-content">
            <h3 class="movie-title">${movie.title}</h3>
            <p class="movie-genres">${movie.genres.join(', ')}</p>
            <p class="movie-director">Diretor: ${movie.director}</p>
            <div class="movie-actions">
                <a href="movie-details.html?id=${movie.id}">Ver detalhes</a>
            </div>
        </div>
    `;
    
    return card;
}

// Formatar data
function formatDate(dateString) {
    if (!dateString) return '';
    
    const date = new Date(dateString);
    return date.toLocaleDateString('pt-BR', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

// Inicializar quando o DOM estiver pronto
document.addEventListener('DOMContentLoaded', initProfilePage);
