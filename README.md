# API do Café Bugado

Esta é a API backend para o projeto **Café Bugado**. Ela foi desenvolvida com [Flask](https://flask.palletsprojects.com/) e fornece endpoints para autenticação, gerenciamento de usuários, depoimentos e estatísticas do dashboard.

## Tecnologias Utilizadas

- Flask 3.1
- Flask-RESTX
- Flask-JWT-Extended
- Flask-SQLAlchemy
- Secrets
- Werkzeug.security
- PostgreSQL
- Datetime

## Requisitos

- Python 3.12 ou superior
- `pip` para instalar as dependências

## Instalação

```bash
git clone https://github.com/cafe-bugado/back-site.git
cd back-site
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Inicializar o banco de dados

O projeto usa SQLite por padrão. Para criar o arquivo `site.db` com as tabelas necessárias, execute:

```python
from app import app, db
with app.app_context():
    db.create_all()
```

### Executar o servidor

```bash
python app.py
```

O servidor estará disponível em `http://127.0.0.1:5000/`.

### Documentação interativa

Com o servidor em execução, acesse `http://127.0.0.1:5000/` para visualizar a documentação gerada automaticamente pelo Swagger (Flask‑RESTX).

## Endpoints

Todos os endpoints abaixo, exceto os de autenticação, exigem um token JWT no cabeçalho `Authorization: Bearer <token>`.

### Autenticação

| Método | Rota            | Descrição                        |
| ------ | --------------- | -------------------------------- |
| POST   | `/auth/register`| Registra um novo usuário         |
| POST   | `/auth/login`   | Autentica e retorna um token JWT |

### Usuários

| Método | Rota                 | Descrição                     |
| ------ | -------------------- | ----------------------------- |
| GET    | `/usuarios/`         | Lista todos os usuários       |
| GET    | `/usuarios/<id>`     | Busca usuário por ID          |
| PUT    | `/usuarios/<id>`     | Atualiza usuário existente    |
| DELETE | `/usuarios/<id>`     | Remove usuário                |

### Depoimentos

| Método | Rota                      | Descrição                         |
| ------ | ------------------------- | --------------------------------- |
| GET    | `/depoimentos/`           | Lista depoimentos                 |
| POST   | `/depoimentos/`           | Cria novo depoimento              |
| GET    | `/depoimentos/<id>`       | Busca depoimento por ID           |
| PUT    | `/depoimentos/<id>`       | Atualiza depoimento               |
| DELETE | `/depoimentos/<id>`       | Remove depoimento                 |

### Dashboard

| Método | Rota                | Descrição                                         |
| ------ | ------------------- | ------------------------------------------------- |
| GET    | `/dashboard/stats`  | Retorna contagens de usuários e depoimentos       |

## Estrutura do Projeto

```
back-site/
├── app.py            # Código principal da API
├── requirements.txt  # Dependências do projeto
└── README.md
```

## Testes

Atualmente não há testes automatizados. Para verificar se o ambiente está configurado corretamente, execute:

```bash
pytest
```

O comando deve ser executado sem erros mesmo sem testes definidos.

