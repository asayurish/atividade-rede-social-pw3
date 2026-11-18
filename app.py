
from flask import Flask
from flask_socketio import SocketIO
from controllers import routes, chat
from models.database import db
import os

# Inicializando o Flask
app = Flask(__name__, template_folder='views')

# Caminho principal do projeto
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

# Configurações do banco de dados
app.config['SQLALCHEMY_DATABASE_URI'] = (
    'sqlite:///' + os.path.join(BASE_DIR, 'models/rede_social.sqlite3')
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configurações de sessão
app.config['SECRET_KEY'] = 'chave_secreta_rede_social'
app.config['PERMANENT_SESSION_LIFETIME'] = 3600

# Configurações de upload
app.config['UPLOAD_FOLDER'] = os.path.join(BASE_DIR, 'static/uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# Criando a pasta de uploads
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Inicializando o banco de dados
db.init_app(app)

# Inicializando o SocketIO
socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    async_mode='threading'
)

# Registrando as rotas
routes.init_app(app)

# Registrando os eventos do chat
chat.init_app(socketio)

# Criando as tabelas
with app.app_context():
    db.create_all()
    print("Banco de dados e tabelas criados com sucesso!")

# Executando o servidor
if __name__ == '__main__':
    socketio.run(
        app,
        host='0.0.0.0',
        port=5000,
        debug=True
    )
