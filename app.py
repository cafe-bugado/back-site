from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from flask_restx import Api, Resource, fields
import secrets
import os

app = Flask(__name__)

# CONFIGURAÇÕES
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL", 'sqlite:///site.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["JWT_SECRET_KEY"] = secrets.token_hex(32)

db = SQLAlchemy(app)
jwt = JWTManager(app)

# CONFIGURAÇÃO DO FLASK-RESTX (SWAGGER)
api = Api(app, version='1.0', title='API do Café Bugado',
          description='Documentação da API backend do projeto Café Bugado')

# MODELOS DE DADOS PARA SWAGGER (ENTRADA E SAÍDA)

usuario_model = api.model('Usuario', {
    'id': fields.Integer(readOnly=True, description='O identificador único do usuário'),
    'nome': fields.String(required=True, description='O nome do usuário'),
    'email': fields.String(required=True, description='O e-mail do usuário', unique=True),
    'imagem_url': fields.String(description='URL da imagem de perfil do usuário'),
    'stack': fields.String(description='Habilidades do usuário'),
    'linkedin_url': fields.String(description='URL do LinkedIn do usuário'),
    'twitter_url': fields.String(description='URL do Twitter do usuário'),
    'github_url': fields.String(description='URL do GitHub do usuário')
})

usuario_input_model = api.model('UsuarioInput', {
    'nome': fields.String(required=True, description='O nome do usuário'),
    'email': fields.String(required=True, description='O e-mail do usuário'),
    'password': fields.String(required=True, description='A senha do usuário'),
    'imagem_url': fields.String(description='URL da imagem de perfil do usuário'),
    'stack': fields.String(description='Habilidades do usuário'),
    'linkedin_url': fields.String(description='URL do LinkedIn do usuário'),
    'twitter_url': fields.String(description='URL do Twitter do usuário'),
    'github_url': fields.String(description='URL do GitHub do usuário')
})

login_model = api.model('LoginInput', {
    'email': fields.String(required=True, description='O e-mail do usuário'),
    'password': fields.String(required=True, description='A senha do usuário')
})

token_model = api.model('TokenResponse', {
    'access_token': fields.String(description='O token JWT para autenticação')
})

depoimento_model = api.model('Depoimento', {
    'id': fields.Integer(readOnly=True, description='O identificador único do depoimento'),
    'nome_autor': fields.String(required=True, description='O nome do autor do depoimento'),
    'texto': fields.String(required=True, description='O texto do depoimento'),
    'data_criacao': fields.String(readOnly=True, description='A data de criação do depoimento')
})

depoimento_input_model = api.model('DepoimentoInput', {
    'nome_autor': fields.String(required=True, description='O nome do autor do depoimento'),
    'texto': fields.String(required=True, description='O texto do depoimento')
})

stats_model = api.model('DashboardStats', {
    'total_usuarios': fields.Integer(description='Total de usuários'),
    'total_depoimentos': fields.Integer(description='Total de depoimentos')
})

# CLASES DE MODELOS (DO SQLAlchemy)
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(200), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    imagem_url = db.Column(db.String(500), nullable=True)
    stack = db.Column(db.String(200), nullable=True)
    linkedin_url = db.Column(db.String(200), nullable=True)
    twitter_url = db.Column(db.String(200), nullable=True)
    github_url = db.Column(db.String(200), nullable=True)

    def __repr__(self):
        return f"Usuario('{self.nome}', '{self.email}')"

    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'email': self.email,
            'imagem_url': self.imagem_url,
            'stack': self.stack,
            'linkedin_url': self.linkedin_url,
            'twitter_url': self.twitter_url,
            'github_url': self.github_url
        }

class Depoimento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome_autor = db.Column(db.String(100), nullable=False)
    texto = db.Column(db.Text, nullable=False)
    data_criacao = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"Depoimento('{self.nome_autor}', '{self.data_criacao}')"
    
    def to_dict(self):
        return {
            'id': self.id,
            'nome_autor': self.nome_autor,
            'texto': self.texto,
            'data_criacao': self.data_criacao.isoformat()
        }

# NAMESPACES PARA AGRUPAR AS ROTAS
ns_auth = api.namespace('auth', description='Rotas de Autenticação')
ns_users = api.namespace('usuarios', description='Rotas de Gerenciamento de Usuários')
ns_depoimentos = api.namespace('depoimentos', description='Rotas de Depoimentos')
ns_dashboard = api.namespace('dashboard', description='Rotas do Dashboard')

# ROTAS DA API

@ns_auth.route('/register')
class Register(Resource):
    @ns_auth.doc('register_usuario')
    @ns_auth.expect(usuario_input_model)
    def post(self):
        dados_usuario = request.json
        try:
            email = dados_usuario.get('email')
            password = dados_usuario.get('password')
            nome = dados_usuario.get('nome')
            if not email or not password or not nome:
                return {"message": "E-mail, senha e nome são obrigatórios"}, 400
            
            usuario_existente = Usuario.query.filter_by(email=email).first()
            if usuario_existente:
                return {"message": "Este E-mail já está registrado"}, 409
            
            hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
            
            novo_usuario = Usuario(
                email=email,
                password_hash=hashed_password,
                nome=nome,
                imagem_url=dados_usuario.get('imagem_url'),
                stack=dados_usuario.get('stack'),
                linkedin_url=dados_usuario.get('linkedin_url'),
                twitter_url=dados_usuario.get('twitter_url'),
                github_url=dados_usuario.get('github_url')
            )
            
            db.session.add(novo_usuario)
            db.session.commit()
            return {"message": "Usuário registrado com sucesso!"}, 201
        except Exception as e:
            db.session.rollback()
            return {"erro": "Erro ao registrar usuário", "details": str(e)}, 500

@ns_auth.route('/login')
class Login(Resource):
    @ns_auth.doc('login_usuario')
    @ns_auth.expect(login_model)
    @ns_auth.marshal_with(token_model)
    def post(self):
        try:
            dados_usuario = request.json
            email = dados_usuario.get('email')
            password = dados_usuario.get('password')
            if not email or not password:
                return {"message": "E-mail e senha são obrigatórios"}, 400
            
            busca_usuario = Usuario.query.filter_by(email=email).first()
            if busca_usuario and check_password_hash(busca_usuario.password_hash, password):
                access_token = create_access_token(identity=busca_usuario.id)
                return {'access_token': access_token}, 200
            else:
                return {"message": "E-mail ou senha inválidos"}, 401
        except Exception as e:
            return {"erro": "Erro ao entrar com o usuário", "error": str(e)}, 500

@ns_users.route('/')
class GerenciarUsuarios(Resource):
    @ns_users.doc('listar_usuarios')
    @ns_users.marshal_with(usuario_model, as_list=True)
    @jwt_required()
    def get(self):
        lista_usuarios = Usuario.query.all()
        return [usuario.to_dict() for usuario in lista_usuarios], 200

@ns_users.route('/<int:id>')
class BuscarUsuario(Resource):
    @ns_users.doc('buscar_usuario_por_id')
    @ns_users.marshal_with(usuario_model)
    @jwt_required()
    def get(self, id):
        usuario = Usuario.query.get_or_404(id)
        return usuario.to_dict(), 200

    @ns_users.doc('atualizar_usuario')
    @ns_users.expect(usuario_model)
    @ns_users.marshal_with(usuario_model)
    @jwt_required()
    def put(self, id):
        usuario = Usuario.query.get_or_404(id)
        try:
            dados_atualizacao = request.json
            if not dados_atualizacao:
                return {"message": "Nenhum dado fornecido para atualização"}, 400
            for key, value in dados_atualizacao.items():
                if hasattr(usuario, key) and key != 'id':
                    setattr(usuario, key, value)
            db.session.commit()
            return usuario.to_dict(), 200
        except Exception as e:
            db.session.rollback()
            return {"erro": "Erro ao atualizar o usuário", "error": str(e)}, 500

    @ns_users.doc('deletar_usuario')
    @jwt_required()
    def delete(self, id):
        usuario = Usuario.query.get_or_404(id)
        try:
            db.session.delete(usuario)
            db.session.commit()
            return '', 204
        except Exception as e:
            db.session.rollback()
            return {"erro": "Não foi possível deletar o usuário", "error": str(e)}, 500

@ns_depoimentos.route('/')
class GerenciarDepoimentos(Resource):
    @ns_depoimentos.doc('listar_depoimentos')
    @ns_depoimentos.marshal_with(depoimento_model, as_list=True)
    @jwt_required()
    def get(self):
        lista_depoimentos = Depoimento.query.all()
        return [depoimento.to_dict() for depoimento in lista_depoimentos], 200

    @ns_depoimentos.doc('adicionar_depoimento')
    @ns_depoimentos.expect(depoimento_input_model)
    @ns_depoimentos.marshal_with(depoimento_model)
    @jwt_required()
    def post(self):
        try:
            dados_depoimento = request.json
            if not dados_depoimento or 'nome_autor' not in dados_depoimento or 'texto' not in dados_depoimento:
                return {"message": "Dados inválidos. O nome e o texto são obrigatórios"}, 400
            novo_depoimento_obj = Depoimento(
                nome_autor=dados_depoimento['nome_autor'],
                texto=dados_depoimento['texto']
            )
            db.session.add(novo_depoimento_obj)
            db.session.commit()
            return novo_depoimento_obj.to_dict(), 201
        except Exception as e:
            db.session.rollback()
            return {"message": "Erro ao criar o depoimento", "error": str(e)}, 500

@ns_depoimentos.route('/<int:id>')
class BuscarDepoimento(Resource):
    @ns_depoimentos.doc('buscar_depoimento_por_id')
    @ns_depoimentos.marshal_with(depoimento_model)
    @jwt_required()
    def get(self, id):
        depoimento = Depoimento.query.get_or_404(id)
        return depoimento.to_dict(), 200

    @ns_depoimentos.doc('atualizar_depoimento')
    @ns_depoimentos.expect(depoimento_input_model)
    @ns_depoimentos.marshal_with(depoimento_model)
    @jwt_required()
    def put(self, id):
        depoimento = Depoimento.query.get_or_404(id)
        try:
            dados_atualizacao = request.json
            if not dados_atualizacao:
                return {"message": "Nenhum dado fornecido para atualização"}, 400
            for key, value in dados_atualizacao.items():
                if hasattr(depoimento, key) and key not in ['id', 'data_criacao']:
                    setattr(depoimento, key, value)
            db.session.commit()
            return depoimento.to_dict(), 200
        except Exception as e:
            db.session.rollback()
            return {"erro": "Erro ao atualizar o depoimento", "error": str(e)}, 500

    @ns_depoimentos.doc('deletar_depoimento')
    @jwt_required()
    def delete(self, id):
        depoimento = Depoimento.query.get_or_404(id)
        try:
            db.session.delete(depoimento)
            db.session.commit()
            return '', 204
        except Exception as e:
            db.session.rollback()
            return {"message": "Erro ao excluir o depoimento", "error": str(e)}, 500

@ns_dashboard.route('/stats')
class GetStats(Resource):
    @ns_dashboard.doc('get_dashboard_stats')
    @ns_dashboard.marshal_with(stats_model)
    @jwt_required()
    def get(self):
        total_usuarios = db.session.query(Usuario).count()
        total_depoimentos = db.session.query(Depoimento).count()
        stats = {
            "total_usuarios": total_usuarios,
            "total_depoimentos": total_depoimentos
        }
        return stats, 200