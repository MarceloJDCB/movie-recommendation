# BISO Movies - FastAPI com MongoDB

Projeto de API RESTful utilizando FastAPI com conexão ao MongoDB via Motor (driver assíncrono).

## Estrutura do Projeto

```
my_fastapi_mongo_project/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── dependencies.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── user.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── user.py
│   └── routers/
│       ├── __init__.py
│       └── users.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── Makefile
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

- `GET /`: Página inicial da API
- `POST /users/`: Criar um novo usuário
- `GET /users/`: Listar todos os usuários
- `POST /auth/login`: Autenticar um usuário
- `POST /auth/register`: Registrar um novo usuário

## Exemplos de uso

### Criar um novo usuário

```bash
curl -X 'POST' \
  'http://localhost:8000/users/' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "username": "exemplo",
  "email": "exemplo@email.com"
}'
```

### Listar todos os usuários

```bash
curl -X 'GET' \
  'http://localhost:8000/users/' \
  -H 'accept: application/json'
```

### Autenticar um usuário

```bash
curl -X 'POST' \
  'http://localhost:8000/auth/login' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "username": "exemplo",
  "password": "senha"
}'
```

### Registrar um novo usuário

```bash
curl -X 'POST' \
  'http://localhost:8000/auth/register' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "username": "exemplo",
  "email": "exemplo@email.com",
  "password": "senha"
}'
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