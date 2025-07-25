# API do Café Bugado

Esta é a API backend desenvolvida para o projeto "Café Bugado". Ela gerencia usuários, depoimentos e dados de um dashboard, oferecendo endpoints seguros para autenticação e manipulação de recursos.

---

## Tecnologias

- **Python:** Linguagem de programação principal.
- **Flask:** Framework web para construir a API.
- **Flask-SQLAlchemy:** Ferramenta para interagir com o banco de dados.
- **Flask-JWT-Extended:** Para autenticação e geração de tokens de acesso.
- **Werkzeug:** Para criptografia de senhas.
- **SQLite:** Banco de dados simples para desenvolvimento.

---

## Instalação e Configuração

Siga estes passos para configurar e rodar o projeto localmente:

1.  Clone o repositório:
    ```bash
    git clone https://github.com/seu-usuario/seu-repositorio.git
    cd seu-repositorio
    ```

2.  Crie e ative o ambiente virtual:
    ```bash
    python -m venv venv
    source venv/bin/activate
    ```
    *(No Windows, use `venv\Scripts\activate`)*

3.  Instale as dependências:
    ```bash
    pip install -r requirements.txt
    ```

4.  Inicialize o banco de dados:
    ```bash
    # (Se necessário, dependendo da sua configuração)
    flask shell
    >>> from app import db
    >>> db.create_all()
    >>> exit()
    ```

---

## Como Rodar a API

No mesmo terminal, com o ambiente virtual ativado, inicie o servidor:

```bash
python app.py
A API estará disponível em http://127.0.0.1:5000.

Endpoints da API
Aqui estão os principais endpoints que você pode usar para interagir com a API:

Método	Endpoint	Descrição	Autenticação
POST	/register	Registra um novo usuário.	Não
POST	/login	Autentica um usuário e retorna um token JWT.	Não
GET	/usuarios	Lista todos os usuários.	Sim
GET	/usuarios/<id>	Obtém detalhes de um usuário específico.	Sim
PUT	/usuarios/<id>	Atualiza um usuário existente.	Sim
DELETE	/usuarios/<id>	Exclui um usuário.	Sim
POST	/depoimentos	Cria um novo depoimento.	Sim
GET	/depoimentos	Lista todos os depoimentos.	Sim
GET	/depoimentos/<id>	Obtém detalhes de um depoimento específico.	Sim
PUT	/depoimentos/<id>	Atualiza um depoimento.	Sim
DELETE	/depoimentos/<id>	Exclui um depoimento.	Sim
GET	/dashboard/stats	Retorna o total de usuários e depoimentos.	Sim

Exportar para as Planilhas
Exemplo de Requisição para Login
Requisição (JSON):

JSON

{
  "email": "teste@exemplo.com",
  "password": "senha123"
}
Resposta (JSON):

JSON

{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}

Depois de salvar o arquivo `README.md` com este conteúdo, use `git add README.md`, `git commit` e `git push` para que a versão formatada apareça no seu repositório.