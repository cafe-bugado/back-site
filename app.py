from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_jwt_extended import JWTManager, create_access_token, jwt_required
from werkzeug.security import generate_password_hash, check_password_hash
import secrets 

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["JWT_SECRET_KEY"] = secrets.token_hex(32)

db = SQLAlchemy(app)

jwt = JWTManager(app)

class Usuario(db.Model):
    password_hash = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(200), unique=True, nullable=False)
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    imagem_url = db.Column(db.String(500), nullable=True)
    stack = db.Column(db.String(200), nullable=True)
    linkedin_url = db.Column(db.String(200), nullable=True)
    twitter_url = db.Column(db.String(200), nullable=True)
    github_url = db.Column(db.String(200), nullable=True)

    def __repr__(self):
        return f"Usuario('{self.nome}', '{self.email}')"

    def to_dict(self):
        return {
            'email': self.email,
            'id': self.id,
            'nome': self.nome,
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


@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "Bem-vindo à API do Café Bugado!"})


@app.route("/usuarios", methods=["GET"])
@jwt_required()
def gerenciar_usuarios():
    lista_usuarios = Usuario.query.all()
    lista_usuarios_json = [usuario.to_dict() for usuario in lista_usuarios]
    return jsonify(lista_usuarios_json), 200


@app.route("/depoimentos", methods=["POST"])
@jwt_required()
def adicionar_depoimentos():
    try:
        dados_depoimento = request.json
        if not dados_depoimento or 'nome_autor' not in dados_depoimento or 'texto' not in dados_depoimento:
            return jsonify({"message": "Dados inválidos. O nome é obrigatório"}), 400
        novo_depoimento_obj = Depoimento(
            nome_autor=dados_depoimento['nome_autor'],
            texto=dados_depoimento['texto']
        )
        db.session.add(novo_depoimento_obj)
        db.session.commit()
        return jsonify(novo_depoimento_obj.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Erro ao criar o depoimento", "error": str(e)}), 500
    

@app.route("/depoimentos", methods=["GET"])
@jwt_required()
def listar_depoimentos():
    lista_depoimentos = Depoimento.query.all()
    lista_depoimentos_json = [depoimento.to_dict() for depoimento in lista_depoimentos]
    return jsonify(lista_depoimentos_json), 200
            

@app.route("/usuarios/<int:id>", methods=["GET", "PUT", "DELETE"])
@jwt_required()
def buscar_usuario_por_id(id):
    usuario = Usuario.query.get_or_404(id)
    if request.method == "GET":
        return jsonify(usuario.to_dict()), 200
    elif request.method == "PUT":
        try:
            dados_atualizacao = request.json
            if not dados_atualizacao:
                return jsonify({"message": "Nenhum dado fornecido para atualização"}), 400
            for key, value in dados_atualizacao.items():
                if hasattr(usuario, key) and key != 'id':
                    setattr(usuario, key, value)
            db.session.commit()
            return jsonify(usuario.to_dict()), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"erro": "Erro ao atualizar o usuário", "error": str(e)}), 500
    elif request.method == "DELETE":
        try:
            db.session.delete(usuario)
            db.session.commit()
            return '', 204
        except Exception as e:
            db.session.rollback()
            return jsonify({"erro": "Não foi possível deletar o usuário", "error": str(e)}), 500


@app.route("/depoimentos/<int:id>", methods=["GET", "PUT", "DELETE"])
@jwt_required()
def buscar_depoimento_por_id(id):
    depoimento = Depoimento.query.get_or_404(id)
    if request.method == "GET":
        depoimento = depoimento.to_dict()
        return jsonify(depoimento), 200
    elif request.method == "PUT":
        try:
            dados_atualizacao = request.json
            if not dados_atualizacao:
                return jsonify({"message": "Nenhum dado fornecido para atualização"}), 400
            for key, value in dados_atualizacao.items():
                if hasattr(depoimento, key) and key not in ['id', 'data_criacao']:
                    setattr(depoimento, key, value)
            db.session.commit()
            return jsonify(depoimento.to_dict()), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"erro": "Erro ao atualizar o depoimento", "error": str(e)}), 500
    elif request.method == "DELETE":
        try:
            db.session.delete(depoimento)
            db.session.commit()
            return '', 204
        except Exception as e:
            db.session.rollback()
            return jsonify({"message": "Erro ao excluir o depoimento", "error": str(e)}), 500   
        

@app.route("/dashboard/stats", methods=["GET"])
@jwt_required()
def get_dashboard_stats():
    total_usuarios = db.session.query(Usuario).count()
    total_depoimentos = db.session.query(Depoimento).count()
    stats = {
        "total_usuarios": total_usuarios,
        "total_depoimentos": total_depoimentos
    }
    return jsonify(stats), 200


@app.route("/register", methods=["POST"])
def register():
    dados_usuario = request.json
    try:
        email = dados_usuario.get('email')
        password = dados_usuario.get('password')
        nome = dados_usuario.get('nome')
        if not email or not password or not nome:
            return jsonify({"message": "E-mail, senha e nome são obrigatórios"}), 400
        usuario_existente = Usuario.query.filter_by(email=email).first()
        if usuario_existente:
            return jsonify({"message": "Este E-mail já está registrado"}), 409
        hashed_password = generate_password_hash(password, method='sha256')                 
        novo_usuario = Usuario(
            email=email,
            password_hash=hashed_password,
            nome=nome,
            imagem_url=dados_usuario.get('imagem_url'),
            stack=dados_usuario.get('stack')
        )
        db.session.add(novo_usuario)
        db.session.commit()
        return jsonify({"message": "Usuário registrado com sucesso!"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"erro": "Erro ao registrar usuário", "details": str(e)}), 500
        

@app.route("/login", methods=["POST"])
def login():
    try:
        dados_usuario = request.json
        email = dados_usuario.get('email')
        password = dados_usuario.get('password')
        if not email or not password:   
            return jsonify({"message": "E-mail e senha são obrigatórios"}), 400
        busca_usuario = Usuario.query.filter_by(email=email).first()
        if busca_usuario and check_password_hash(busca_usuario.password_hash, password):
            access_token = create_access_token(identity=busca_usuario.id)
            return jsonify(access_token=access_token), 200
        else:
            return jsonify({"message": "E-mail ou senha inválidos"}), 401
    except Exception as e:
        return jsonify({"erro": "Erro ao entrar com o usuário", "error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)