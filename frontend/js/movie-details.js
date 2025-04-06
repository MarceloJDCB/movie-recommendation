// Obter ID do filme da URL
function getMovieIdFromUrl() {
    const params = new URLSearchParams(window.location.search);
    return params.get('id');
}

// Inicializar página de detalhes do filme
async function initMovieDetailsPage() {
    // Verificar autenticação
    if (!requireAuth()) return;
    
    // Obter ID do filme
    const movieId = getMovieIdFromUrl();
    if (!movieId) {
        window.location.href = 'movies.html';
        return;
    }
    
    // Carregar detalhes do filme
    loadMovieDetails(movieId);
    
    // Carregar filmes similares
    loadSimilarMovies(movieId);
    
    // Configurar sistema de avaliação
    setupRatingSystem(movieId);
}

// Carregar detalhes do filme
async function loadMovieDetails(movieId) {
    const detailsContainer = document.getElementById('movie-details');
    
    if (!detailsContainer) return;
    
    try {
        const movie = await moviesAPI.getMovie(movieId);
        
        detailsContainer.innerHTML = `
            <h2 class="movie-title-large">${movie.title}</h2>
            <div class="movie-meta">
                <span><strong>Gêneros:</strong> ${movie.genres.join(', ')}</span>
                <span><strong>Diretor:</strong> ${movie.director}</span>
            </div>
            <div class="movie-actors">
                <h3>Elenco</h3>
                <p>${movie.actors.join(', ')}</p>
            </div>
        `;
        
        // Atualizar título da página
        document.title = `BISO Movies - ${movie.title}`;
        
    } catch (error) {
        console.error('Erro ao carregar detalhes do filme:', error);
        detailsContainer.innerHTML = '<p class="error">Erro ao carregar detalhes do filme</p>';
    }
}

// Carregar filmes similares
async function loadSimilarMovies(movieId) {
    const similarMoviesContainer = document.getElementById('similar-movies-list');
    
    if (!similarMoviesContainer) return;
    
    try {
        const movies = await moviesAPI.getSimilarMovies(movieId);
        
        if (movies.length === 0) {
            similarMoviesContainer.innerHTML = '<p>Nenhum filme similar encontrado</p>';
            return;
        }
        
        similarMoviesContainer.innerHTML = '';
        
        movies.forEach(movie => {
            const movieCard = createMovieCard(movie);
            similarMoviesContainer.appendChild(movieCard);
        });
        
    } catch (error) {
        console.error('Erro ao carregar filmes similares:', error);
        similarMoviesContainer.innerHTML = '<p class="error">Erro ao carregar filmes similares</p>';
    }
}

// Configurar sistema de avaliação
async function setupRatingSystem(movieId) {
    const stars = document.querySelectorAll('.star');
    const ratingInput = document.getElementById('rating-value');
    const reviewForm = document.getElementById('review-form');
    const messageEl = document.getElementById('review-message');
    
    // Configurar estrelas de avaliação
    stars.forEach(star => {
        star.addEventListener('click', () => {
            const value = parseInt(star.getAttribute('data-value'));
            ratingInput.value = value;
            
            // Atualizar display visual
            stars.forEach(s => {
                const starValue = parseInt(s.getAttribute('data-value'));
                if (starValue <= value) {
                    s.classList.add('active');
                } else {
                    s.classList.remove('active');
                }
            });
        });
        
        // Efeito hover
        star.addEventListener('mouseover', () => {
            const value = parseInt(star.getAttribute('data-value'));
            
            stars.forEach(s => {
                const starValue = parseInt(s.getAttribute('data-value'));
                if (starValue <= value) {
                    s.classList.add('hover');
                }
            });
        });
        
        star.addEventListener('mouseout', () => {
            stars.forEach(s => s.classList.remove('hover'));
        });
    });
    
    // Configurar envio do formulário
    if (reviewForm) {
        reviewForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const rating = parseFloat(ratingInput.value);
            const comment = document.getElementById('review-comment').value;
            
            // Validar avaliação
            if (!rating || rating < 1 || rating > 5) {
                messageEl.textContent = 'Por favor, selecione uma avaliação entre 1 e 5 estrelas';
                messageEl.className = 'message error';
                return;
            }
            
            try {
                messageEl.textContent = 'Enviando avaliação...';
                messageEl.className = 'message';
                
                // Criar dados da avaliação - não precisamos extrair o ID do usuário
                // já que a API usa o token para identificar o usuário atual
                const reviewData = {
                    movie_id: movieId,
                    rating,
                    comment
                };
                
                // Enviar avaliação
                await moviesAPI.createReview(reviewData);
                
                // Mostrar mensagem de sucesso
                messageEl.textContent = 'Avaliação enviada com sucesso!';
                messageEl.className = 'message success';
                
                // Resetar formulário
                reviewForm.reset();
                stars.forEach(s => s.classList.remove('active'));
                ratingInput.value = 0;
                
            } catch (error) {
                console.error('Erro ao enviar avaliação:', error);
                messageEl.textContent = error.message || 'Erro ao enviar avaliação';
                messageEl.className = 'message error';
            }
        });
    }
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

// Inicializar quando o DOM estiver pronto
document.addEventListener('DOMContentLoaded', initMovieDetailsPage);
