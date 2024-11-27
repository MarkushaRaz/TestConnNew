from flask import Flask, render_template, request, jsonify
import socket
import threading
from kivy.core.audio import SoundLoader

# Инициализация Flask-приложения
app = Flask(__name__)

# Настройка аудио
sound = SoundLoader.load('Zvezda.mp3')
if sound:
    sound.play()

# Настройка сокета
host = '0.0.0.0'
port = 12345
clients = []

try:
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen()
    print("> Successful new server")
except PermissionError:
    print("> Error new server")

# Функция обработки данных от клиента
def handle_client(client_socket):
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if not message:
                break
            print(f"Received: {message}")
        except ConnectionResetError:
            print("> Client disconnected")
            break

    client_socket.close()

# Поток для обработки клиентов
def accept_clients():
    while True:
        client, address = server.accept()
        clients.append(client)
        client_thread = threading.Thread(target=handle_client, args=(client,))
        client_thread.start()
        print(f"> Successful connections: {len(clients)}")

threading.Thread(target=accept_clients, daemon=True).start()

# Роуты Flask
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/send_command', methods=['POST'])
def send_command():
    command = request.json.get('command')
    if command:
        for client in clients:
            try:
                client.send(command.encode('utf-8'))
            except Exception as e:
                print(f"Error sending command: {e}")
        return jsonify({"status": "Command sent", "command": command})
    return jsonify({"status": "No command received"}), 400

# Запуск приложения
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
