# BISO Movies - Sistema de Recomendação de Filmes

Projeto de API RESTful utilizando FastAPI com conexão ao MongoDB via Motor (driver assíncrono) para um sistema completo de recomendação de filmes baseado em preferências de usuários.

## Estrutura do Projeto

```
movie-recommendation/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── dependencies.py
│   ├── config.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base_model.py
│   │   ├── movie.py
│   │   ├── review.py
│   │   └── user.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── movie.py
│   │   ├── review.py
│   │   └── user.py
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── movies.py
│   │   └── users.py
│   ├── repositories/
│   │   ├── base_repository.py
│   │   └── movie_repository.py
│   ├── services/
│   │   └── recommendation_service.py
│   └── utils/
│       ├── __init__.py
│       ├── auth.py
│       ├── recommendation.py
│       └── validation.py
├── frontend/
│   ├── index.html
│   ├── movies.html
│   ├── movie-details.html
│   ├── profile.html
│   ├── css/
│   │   └── styles.css
│   └── js/
│       ├── api.js
│       ├── auth.js
│       ├── movie-details.js
│       ├── movies.js
│       └── profile.js
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── requirements_test.txt
│   └── test_movies.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── Makefile
├── data_generator.py
├── load_data.py
└── README.md
```

## Pré-requisitos

- Python 3.7+
- Docker e Docker Compose
- Make (para usar os comandos do Makefile)

## Instalação e Execução

### Usando Make

1. Clone o repositório ou crie os arquivos conforme a estrutura acima.

2. Crie e ative um ambiente virtual:

```bash
# Windows
make setup

# Linux/macOS
make setup
```

3. Instale as dependências:

```bash
pip install -r requirements.txt
```

4. Inicie os contêineres:

```bash
make up
```

5. A API estará disponível em: http://localhost:8000

6. Para parar os contêineres:

```bash
make down
```

7. Para limpar todo o ambiente (contêineres, volumes e imagens):

```bash
make clean
```

8. Para resetar apenas o banco de dados MongoDB:

```bash
make clean-mongo
```

### Windows sem Make

1. Clone o repositório ou crie os arquivos conforme a estrutura acima.

2. Crie e ative um ambiente virtual:

```bash
python -m venv venv
venv\Scripts\activate
```

3. Instale as dependências:

```bash
pip install -r requirements.txt
```

4. Inicie os contêineres:

```bash
docker-compose up -d
```

5. A API estará disponível em: http://localhost:8000

6. Para parar os contêineres:

```bash
docker-compose down
```

7. Para limpar todo o ambiente (contêineres, volumes e imagens):

```bash
docker-compose down -v --rmi all
```

8. Para resetar apenas o banco de dados MongoDB:

```bash
docker-compose down -v
docker-compose up -d
```

## Populando o Banco de Dados

### Usando Make

Os seguintes comandos estão disponíveis para popular o banco de dados:

```bash
# Carregar conjunto padrão de dados
make load-data          # 50 filmes, 10 usuários, 100 avaliações

# Carregar conjunto pequeno de dados para testes
make load-test-data    # 20 filmes, 5 usuários, 30 avaliações

# Carregar grande volume de dados
make load-large-data   # 200 filmes, 50 usuários, 500 avaliações

# Carregar pequeno volume de dados
make load-small-data   # 10 filmes, 5 usuários, 20 avaliações

# Limpar banco de dados
make clean-db
```

### Windows sem Make

Para Windows sem Make, use o script Python diretamente:

```bash
# Carregar conjunto padrão de dados
python load_data.py

# Carregar conjunto pequeno de dados para testes
python load_data.py --movies 20 --users 5 --reviews 30

# Carregar grande volume de dados
python load_data.py --movies 200 --users 50 --reviews 500

# Carregar pequeno volume de dados
python load_data.py --movies 10 --users 5 --reviews 20

# Limpar banco de dados antes de inserir dados
python load_data.py --clean

# Exemplo com todas as opções
python load_data.py --mongo-url mongodb://localhost:27017 --database myfastapidb --movies 100 --users 20 --reviews 200 --clean
```

Parâmetros disponíveis para o script load_data.py:
- `--mongo-url`: URL de conexão com o MongoDB (padrão: mongodb://localhost:27017)
- `--database`: Nome do banco de dados (padrão: myfastapidb)
- `--movies`: Número de filmes a serem gerados (padrão: 50)
- `--users`: Número de usuários a serem gerados (padrão: 10)
- `--reviews`: Número de avaliações a serem geradas (padrão: 100)
- `--clean`: Limpar coleções antes de inserir novos dados

## Endpoints disponíveis

### Autenticação
- `POST /auth/login`: Autenticar um usuário
- `POST /auth/register`: Registrar um novo usuário

### Usuários
- `GET /users/`: Listar todos os usuários
- `GET /users/{user_id}`: Obter informações de um usuário específico
- `POST /users/`: Criar um novo usuário
- `PUT /users/{user_id}`: Atualizar informações de um usuário
- `DELETE /users/{user_id}`: Excluir um usuário

### Filmes
- `GET /movies/`: Listar todos os filmes com paginação e filtros
- `GET /movies/{movie_id}`: Obter detalhes de um filme específico
- `POST /movies/`: Adicionar um novo filme
- `PUT /movies/{movie_id}`: Atualizar informações de um filme
- `DELETE /movies/{movie_id}`: Excluir um filme

### Avaliações
- `GET /movies/reviews`: Listar avaliações de filmes
- `POST /movies/reviews`: Criar uma nova avaliação para um filme
- `PUT /movies/reviews/{review_id}`: Atualizar uma avaliação
- `DELETE /movies/reviews/{review_id}`: Excluir uma avaliação

### Recomendações
- `GET /movies/{user_id}/recommendations`: Obter recomendações personalizadas para um usuário
- `GET /movies/recommendations/similar/{movie_id}`: Obter filmes similares a um filme específico
- `GET /movies/popular`: Obter lista de filmes populares

## Sistema de Recomendação

O BISO Movies implementa um sistema de recomendação sofisticado que utiliza técnicas de filtragem baseada em conteúdo e análise de preferências dos usuários.

### Tipos de Recomendação

1. **Recomendações Personalizadas**
   - Baseadas no histórico de avaliações do usuário
   - Considerando gêneros favoritos, diretores e atores
   - Utilizando algoritmo TF-IDF e similaridade de cosseno

2. **Filmes Similares**
   - Recomendações de filmes similares a um filme específico
   - Baseadas em características como gênero, diretor e elenco

3. **Filmes Populares**
   - Para usuários novos sem histórico de avaliações
   - Baseados em popularidade geral e avaliações médias

### Como Funciona

O algoritmo de recomendação segue os seguintes passos:

1. Analisa o histórico de avaliações do usuário para identificar filmes bem avaliados (≥ 4.0)
2. Extrai características desses filmes (gêneros, diretores, atores)
3. Identifica os gêneros preferidos do usuário
4. Aplica técnicas de processamento de linguagem natural (TF-IDF) para comparar filmes
5. Calcula a similaridade de cosseno entre filmes avaliados e potenciais recomendações
6. Ordena os resultados e retorna os mais relevantes

### Exemplos de Uso

#### Obter recomendações personalizadas

```bash
curl -X 'GET' \
  'http://localhost:8000/movies/6507ed3a1f1d4a5b2c3d4e5f/recommendations' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer {seu_token}'
```

#### Obter filmes similares

```bash
curl -X 'GET' \
  'http://localhost:8000/movies/recommendations/similar/6507ed3a1f1d4a5b2c3d4e5f' \
  -H 'accept: application/json'
```

#### Avaliar um filme

```bash
curl -X 'POST' \
  'http://localhost:8000/movies/reviews' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer {seu_token}' \
  -d '{
  "movie_id": "6507ed3a1f1d4a5b2c3d4e5f",
  "rating": 4.5,
  "comment": "Excelente filme, recomendo!"
}'
```

## Exemplos de uso da API

### Usuários

#### Criar um novo usuário

```bash
curl -X 'POST' \
  'http://localhost:8000/users/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "username": "exemplo",
  "email": "exemplo@email.com",
  "password": "senha123"
}'
```

#### Listar todos os usuários

```bash
curl -X 'GET' \
  'http://localhost:8000/users/' \
  -H 'accept: application/json' \
  -H 'Authorization: Bearer {seu_token}'
```

### Autenticação

#### Login de usuário

```bash
curl -X 'POST' \
  'http://localhost:8000/auth/login' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "username": "exemplo",
  "password": "senha123"
}'
```

#### Registrar um novo usuário

```bash
curl -X 'POST' \
  'http://localhost:8000/auth/register' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "username": "exemplo",
  "email": "exemplo@email.com",
  "password": "senha123"
}'
```

### Filmes

#### Listar filmes com paginação e filtros

```bash
curl -X 'GET' \
  'http://localhost:8000/movies/?skip=0&limit=10&search=matrix&genre=sci-fi' \
  -H 'accept: application/json'
```

#### Obter detalhes de um filme

```bash
curl -X 'GET' \
  'http://localhost:8000/movies/6507ed3a1f1d4a5b2c3d4e5f' \
  -H 'accept: application/json'
```

## Documentação da API

A documentação Swagger/OpenAPI está disponível em: http://localhost:8000/docs

## Visualização básica de frontend

O BISO Movies inclui uma interface básica de usuário que pode ser acessada simplesmente abrindo o arquivo index.html em qualquer navegador web moderno:

```bash
# Abrir no navegador padrão
# No Windows
start frontend/index.html

# No macOS
open frontend/index.html

# No Linux
xdg-open frontend/index.html
```

Não é necessário nenhum servidor web para visualizar a interface - basta abrir o arquivo HTML diretamente. O front-end se conectará à API em execução no endereço http://localhost:8000 para buscar e exibir dados.

A interface inclui:
- Lista de filmes populares
- Busca de filmes por título, gênero ou ano
- Visualização detalhada de filmes 
- Login/registro de usuários
- Área de perfil do usuário com filmes favoritos e avaliações

Para funcionar corretamente, a API deve estar em execução e acessível antes de abrir a interface.

## Pontos de Melhoria Futura

O BISO Movies tem um grande potencial para expansão. Aqui estão alguns pontos de melhoria para desenvolvimento futuro:

### Backend
1. **Cache**: Implementar Redis ou outra solução de cache para melhorar performance em consultas frequentes
2. **Algoritmo de Recomendação Avançado**: Expandir o algoritmo atual para incluir técnicas de Machine Learning mais avançadas
3. **Escalabilidade**: Implementar sharding no MongoDB para suportar grandes volumes de dados
4. **Logging Estruturado**: Adicionar sistema de logging para monitoramento e depuração

### Frontend
1. **Framework Moderno**: Migrar para React, Vue.js ou Angular para melhor manutenibilidade
2. **Estado Global**: Implementar gerenciamento de estado com Redux ou Vuex
3. **Testes de UI**: Adicionar testes automatizados para a interface com Jest, Cypress ou Playwright
4. **Experiência Mobile**: Melhorar responsividade e/ou criar app móvel dedicado
5. **Acessibilidade**: Melhorar a conformidade com padrões WCAG para acessibilidade

### Funcionalidades
1. **Integração com APIs Externas**: Conectar com TMDb ou OMDB para obter informações reais de filmes
2. **Recursos Sociais**: Adicionar comentários, discussões e compartilhamento de listas de filmes
3. **Listas Personalizadas**: Permitir que usuários criem listas de "Para assistir" e outras categorias personalizadas
4. **Histórico de Visualização**: Rastrear filmes assistidos por usuário
5. **Notificações**: Sistema de notificações para novos lançamentos baseados nas preferências do usuário

### DevOps
1. **CI/CD**: Implementar pipeline completo para integração e deploy contínuos
2. **Infraestrutura como Código**: Usar Terraform ou similar para definir infraestrutura
3. **Monitoramento**: Adicionar Prometheus/Grafana para monitoramento de desempenho
4. **Segurança**: Realizar auditorias de segurança e implementar proteções adicionais
5. **Backup e Recuperação**: Estratégia robusta de backup e recuperação de dados