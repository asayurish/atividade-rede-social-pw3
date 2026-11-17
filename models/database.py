from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Instanciando o SQLAlchemy
db = SQLAlchemy()

class Usuario(db.Model):
    __tablename__ = 'usuario'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)  # Adicionado conforme requisito de cadastro
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha = db.Column(db.String(255), nullable=False)
    
    # Relacionamento 1 para N com Post (um usuário pode ter vários posts)
    posts = db.relationship('Post', backref='autor', lazy=True)
    
    def __init__(self, nome, email, senha):
        self.nome = nome
        self.email = email
        self.senha = senha


class Post(db.Model):
    __tablename__ = 'post'
    
    id = db.Column(db.Integer, primary_key=True)
    imagem = db.Column(db.String(255), nullable=False)
    legenda = db.Column(db.String(255), nullable=True)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Chave estrangeira ligada ao id do Usuario
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    
    def __init__(self, imagem, legenda, usuario_id):
        self.imagem = imagem
        self.legenda = legenda
        self.usuario_id = usuario_id