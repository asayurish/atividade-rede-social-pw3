
from flask import render_template, request, redirect, url_for, flash, session
from markupsafe import Markup
from models.database import db, Usuario, Post
from werkzeug.security import generate_password_hash, check_password_hash
import os
import uuid


def init_app(app):

    # Proteção das páginas
    @app.before_request
    def check_auth():

        rotas_permitidas = [
            'index',
            'login',
            'cadastro',
            'static'
        ]

        if request.endpoint in rotas_permitidas:
            return

        if 'usuario_id' not in session:
            flash('Faça login para continuar!', 'warning')
            return redirect(url_for('login'))

    # Página inicial
    @app.route('/')
    def index():

        if 'usuario_id' in session:
            return redirect(url_for('feed'))

        return render_template('index.html')

    # Cadastro
    @app.route('/cadastro', methods=['GET', 'POST'])
    def cadastro():

        if request.method == 'POST':

            nome = request.form.get('nome', '').strip()
            email = request.form.get('email', '').strip()
            senha = request.form.get('senha', '')

            if not nome or not email or not senha:
                flash('Preencha todos os campos!', 'warning')
                return redirect(url_for('cadastro'))

            usuario_existente = Usuario.query.filter_by(
                email=email
            ).first()

            if usuario_existente:
                flash('Este e-mail já está cadastrado!', 'danger')
                return redirect(url_for('cadastro'))

            senha_criptografada = generate_password_hash(
                senha,
                method='scrypt'
            )

            novo_usuario = Usuario(
                nome=nome,
                email=email,
                senha=senha_criptografada
            )

            db.session.add(novo_usuario)
            db.session.commit()

            flash('Cadastro realizado com sucesso! Faça seu login.', 'success')

            return redirect(url_for('login'))

        return render_template('cadastro.html')

    # Login
    @app.route('/login', methods=['GET', 'POST'])
    def login():

        if request.method == 'POST':

            email = request.form.get('email', '').strip()
            senha = request.form.get('senha', '')

            usuario = Usuario.query.filter_by(email=email).first()

            if usuario and check_password_hash(usuario.senha, senha):

                session['usuario_id'] = usuario.id
                session['usuario_nome'] = usuario.nome
                session['usuario_email'] = usuario.email

                flash('Login realizado com sucesso!', 'success')

                return redirect(url_for('feed'))

            flash('E-mail ou senha incorretos!', 'danger')
            return redirect(url_for('login'))

        return render_template('login.html')

    # Logout
    @app.route('/logout')
    def logout():

        session.clear()

        flash('Você saiu da sua conta.', 'info')

        return redirect(url_for('index'))

    # Feed
    @app.route('/feed', methods=['GET', 'POST'])
    def feed():

        if request.method == 'POST':

            legenda = request.form.get('legenda', '')
            arquivo = request.files.get('file')

            if not arquivo or arquivo.filename == '':
                flash('Selecione uma imagem!', 'warning')
                return redirect(url_for('feed'))

            extensoes_permitidas = {'png', 'jpg', 'jpeg', 'gif'}

            ext = (
                arquivo.filename.rsplit('.', 1)[1].lower()
                if '.' in arquivo.filename else ''
            )

            if ext not in extensoes_permitidas:
                flash('Formato de imagem inválido!', 'danger')
                return redirect(url_for('feed'))

            filename = str(uuid.uuid4()) + '.' + ext

            arquivo.save(
                os.path.join(app.config['UPLOAD_FOLDER'], filename)
            )

            novo_post = Post(
                imagem=filename,
                legenda=legenda,
                usuario_id=session['usuario_id']
            )

            db.session.add(novo_post)
            db.session.commit()

            flash('Publicação realizada com sucesso!', 'success')

            return redirect(url_for('feed'))

        posts = Post.query.order_by(
            Post.data_criacao.desc()
        ).all()

        return render_template('feed.html', posts=posts)

    # Chat
    @app.route('/chat')
    def chat():

        return render_template(
            'chat.html',
            nickname=session.get('usuario_nome')
        )
