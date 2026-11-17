# comentário em Python
# importando o Flask na aplicação
from flask import Flask
from controllers import routes
# importando o chat
from controllers import chat, routes
import os
# importando o database e os models corretos
from models.database import db

# importando o flask-socketio
from flask_socketio import SocketIO

# carregando o Flask em uma variável
app = Flask(__name__, template_folder='views')

# Configurações do Banco de Dados (Utilizando SQLite conforme o guia de referência da atividade, ou MySQL se preferir)
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'models/rede_social.sqlite3')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# criando uma chave secreta (para flash messages e sessões)
app.config['SECRET_KEY'] = 'chave_secreta_rede_social'

# definindo o tempo da sessão
app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 hora

# definindo a pasta que receberá uploads
app.config['UPLOAD_FOLDER'] = os.path.join(BASE_DIR, 'static/uploads')

# definindo o tamanho máximo de arquivos de upload (16 MB)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 

# configurando o flask-socketio
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Enviando a variável APP (FLASK) para as rotas
routes.init_app(app)
# inicializando o SocketIO
chat.init_app(socketio)

# iniciando o servidor web
if __name__ == '__main__':
    # Cria a pasta de uploads caso não exista
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # inicializar o SQLAlchemy
    db.init_app(app=app)
    
    with app.app_context():
        # criando as tabelas no banco de dados
        db.create_all()
        print("Banco de dados e tabelas criados com sucesso!")
        
    # inicia o servidor com socketio
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)