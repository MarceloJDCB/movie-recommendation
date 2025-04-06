// Estado da página
let currentPage = 0;
let pageSize = 12;
let totalMovies = 0;
let searchQuery = '';

// Inicializar a página de filmes
async function initMoviesPage() {
    // Verificar autenticação
    if (!requireAuth()) return;
    
    // Configurar busca
    setupSearch();
    
    // Inicializar paginação
    setupPagination();
    
    // Carregar filmes
    loadMovies();
}

// Configurar busca
function setupSearch() {
    const searchInput = document.getElementById('search-input');
    
    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            searchQuery = e.target.value;
            currentPage = 0; // Resetar para a primeira página
            loadMovies();
        });
    }
}

// Configurar paginação
function setupPagination() {
    const prevBtn = document.getElementById('prev-page');
    const nextBtn = document.getElementById('next-page');
    
    if (prevBtn && nextBtn) {
        prevBtn.addEventListener('click', () => {
            if (currentPage > 0) {
                currentPage--;
                loadMovies();
            }
        });
        
        nextBtn.addEventListener('click', () => {
            currentPage++;
            loadMovies();
        });
    }
}

// Carregar lista de filmes
async function loadMovies() {
    const moviesListEl = document.getElementById('movies-list');
    const prevBtn = document.getElementById('prev-page');
    const nextBtn = document.getElementById('next-page');
    const pageInfoEl = document.getElementById('page-info');
    
    if (!moviesListEl) return;
    
    // Mostrar indicador de carregamento
    moviesListEl.innerHTML = '<p class="loading">Carregando filmes...</p>';
    
    try {
        // Carregar filmes da API
        const skip = currentPage * pageSize;
        const movies = await moviesAPI.listMovies(skip, pageSize);
        
        // Atualizar informações de paginação
        prevBtn.disabled = currentPage === 0;
        
        // Supondo que se retornar menos do que o tamanho da página, estamos na última página
        nextBtn.disabled = movies.length < pageSize;
        
        pageInfoEl.textContent = `Página ${currentPage + 1}`;
        
        // Se não houver filmes
        if (movies.length === 0) {
            moviesListEl.innerHTML = '<p>Nenhum filme encontrado</p>';
            return;
        }
        
        // Renderizar filmes
        renderMovies(moviesListEl, movies);
        
    } catch (error) {
        console.error('Erro ao carregar filmes:', error);
        moviesListEl.innerHTML = '<p class="error">Erro ao carregar filmes</p>';
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

// Criar card de filme
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

// Inicializar quando o DOM estiver pronto
document.addEventListener('DOMContentLoaded', initMoviesPage);
