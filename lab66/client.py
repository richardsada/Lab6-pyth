
import pickle


import socket

def main():
    host = '127.0.0.1'  # Адрес сервера
    port = 12345         # Порт сервера

    while True:
        email = input("Введите email: ")
        message = input("Введите текст сообщения: ")
        data = f"{email}|{message}"

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            try:
                client_socket.connect((host, port))
                client_socket.sendall(data.encode())
                response = client_socket.recv(1024).decode()
                if response == "OK":
                    print("Сообщение успешно отправлено!")
                    break
                else:
                    print(f"Ошибка: {response}")
            except Exception as e:
                print(f"Не удалось подключиться к серверу: {e}")


main()
