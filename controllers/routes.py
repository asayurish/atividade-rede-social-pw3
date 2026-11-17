# Importações necessárias
from flask import render_template, request, redirect, url_for, flash, session
from markupsafe import Markup
from models.database import db, Usuario, Post
from werkzeug.security import generate_password_hash, check_password_hash
import os
import uuid

def init_app(app):
    
    # Middleware para proteção de rotas (@app.before_request)
    @app.before_request
    def check_auth():
        # Rotas que não precisam de autenticação
        rotasPermitidas = ['login', 'cadastro', 'static']
        
        if request.endpoint in rotasPermitidas:
            return
        
        # Se o usuário não estiver logado, redireciona para o login
        if 'usuario_id' not in session:
            flash('Faça login para acessar esta página!', 'warning')
            return redirect(url_for('login'))

    # Rota raiz redireciona para o feed (se logado) ou login
    @app.route('/')
    def index():
        if 'usuario_id' in session:
            return redirect(url_for('feed'))
        return redirect(url_for('login'))

    # Rota de Cadastro de Usuário (com Nome, E-mail e Senha)
    @app.route('/cadastro', methods=['GET', 'POST'])
    def cadastro():
        if request.method == 'POST':
            nome = request.form['nome']
            email = request.form['email']
            senha = request.form['senha']
            
            # Verificando se o e-mail já existe
            usuario_existente = Usuario.query.filter_by(email=email).first()
            if usuario_existente:
                msg = Markup("E-mail já cadastrado. Faça o <a href='/login'>login</a>")
                flash(msg, 'danger')
                return redirect(url_for('cadastro'))
            
            # Criptografando a senha com scrypt conforme requisito
            senha_criptografada = generate_password_hash(senha, method='scrypt')
            
            # Salvando o novo usuário no banco
            novo_usuario = Usuario(nome=nome, email=email, senha=senha_criptografada)
            db.session.add(novo_usuario)
            db.session.commit()
            
            msgCad = Markup("Cadastro realizado com sucesso! Faça o <a href='/login'>login</a>")
            flash(msgCad, 'success')
            return redirect(url_for('cadastro'))
            
        return render_template('cadastro.html')
    
    # Rota de Login
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            email = request.form['email']
            senha = request.form['senha']
            
            usuario = Usuario.query.filter_by(email=email).first()
            
            if usuario and check_password_hash(usuario.senha, senha):
                # Salvando dados na sessão (incluindo o nome para o chat e feed)
                session['usuario_id'] = usuario.id
                session['usuario_nome'] = usuario.nome
                session['usuario_email'] = usuario.email
                
                flash('Login realizado com sucesso!', 'success')
                return redirect(url_for('feed'))
            else:
                flash('E-mail ou senha incorretos!', 'danger')
                return redirect(url_for('login'))
                 
        return render_template('login.html')

    # Rota de Logout
    @app.route('/logout')
    def logout():
        session.clear()
        flash('Você saiu da sua conta.', 'info')
        return redirect(url_for('login'))
    
    # Rota do Feed de Fotos e Postagens
    @app.route('/feed', methods=['GET', 'POST'])
    def feed():
        if request.method == 'POST':
            legenda = request.form.get('legenda')
            arquivo = request.files.get('file')
            
            if arquivo and arquivo.filename != '':
                # Extensões permitidas
                FILE_TYPES = {'png', 'jpg', 'jpeg', 'gif'}
                ext = arquivo.filename.rsplit('.', 1)[1].lower() if '.' in arquivo.filename else ''
                
                if ext in FILE_TYPES:
                    # Gerando nome único com UUID
                    filename = str(uuid.uuid4()) + '.' + ext
                    
                    # Salvando arquivo na pasta de uploads
                    arquivo.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    
                    # Salvando o post no banco de dados
                    novo_post = Post(
                        imagem=filename,
                        legenda=legenda,
                        usuario_id=session['usuario_id']
                    )
                    db.session.add(novo_post)
                    db.session.commit()
                    
                    flash('Postagem publicada com sucesso!', 'success')
                else:
                    flash('Formato de imagem inválido! Use apenas png, jpg, jpeg ou gif.', 'danger')
            else:
                flash('Selecione uma imagem para postar!', 'warning')
                
            return redirect(url_for('feed'))
        
        # Buscando todos os posts em ordem cronológica decrescente (do mais recente para o mais antigo)
        posts = Post.query.order_by(Post.data_criacao.desc()).all()
        return render_template('feed.html', posts=posts)

    # Rota de Chat em Tempo Real
    @app.route('/chat')
    def chat():
        return render_template('chat.html', nickname=session.get('usuario_nome'))