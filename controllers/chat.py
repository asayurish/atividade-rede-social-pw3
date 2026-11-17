from flask import request
from flask_socketio import emit


#evento quando o usuario conecta
def init_app(socketio):
    @socketio.on('connect')
    def handle_connect():
        print(f"O usuário com a ID: {request.sid} conectou!")
        
    #evento quando o usuario desconecta
    @socketio.on('disconnect')
    def handle_disconnect():
        print(f"O usuário com a ID: {request.sid} desconectou!")
    
    # evento quando o usuario entra no chat
    @socketio.on('join')
    def handle_join(data):
        print(f"{data['nickname']} entrou no chat.")
        emit("join", data, broadcast=True)
        
    #evento quando o usuario envia uma mensagem
    @socketio.on('msg')
    def handle_msg(data):
        emit("showmsg", data, broadcast=True)