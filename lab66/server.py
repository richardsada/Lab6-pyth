import socket
import smtplib
import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import configparser
import random

def load_config():
    config = configparser.ConfigParser()
    config.read("config.ini")
    return config["EMAIL"]

def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email) 

def send_email(admin_email, admin_password, smtp_host, smtp_port, recipient, message, ticket_id):
    try:
        msg = MIMEMultipart()
        msg['From'] = admin_email
        msg['To'] = recipient
        msg['Subject'] = f"[Ticket #{ticket_id}] Mailer"
        msg.attach(MIMEText(message, 'plain')) # добавляет к сообщению неформатир текст

        with smtplib.SMTP_SSL(smtp_host, smtp_port) as server:
            server.login(admin_email, admin_password)
            server.send_message(msg)
    except Exception as e:
        return str(e)
    try:
        msg = MIMEMultipart()
        msg['From'] = admin_email
        msg['To'] = admin_email
        msg['Subject'] = f"[Ticket #{ticket_id}] Mailer"
        msg.attach(MIMEText(message, 'plain'))

        with smtplib.SMTP_SSL(smtp_host, smtp_port) as server:
            server.login(admin_email, admin_password)
            server.send_message(msg)
    except Exception as e:
        return str(e)
    return "OK"

def main():
    config = load_config()
    admin_email = config["EMAIL_LOGIN"]
    admin_password = config["EMAIL_PASSWORD"]
    smtp_host = config["SMTP_HOST"]
    smtp_port = int(config["SMTP_PORT"])

    host = '127.0.0.1'
    port = 12345

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind((host, port))# подключаемся к порту
        server_socket.listen(5)
        print("Сервер запущен и ожидает подключения...")

        while True:
            conn, addr = server_socket.accept()
            with conn:
                print(f"Подключение от {addr}")
                data = conn.recv(1024).decode()
                if not data:
                    continue
                email, message = data.split("|", 1)

                if not is_valid_email(email):
                    conn.sendall("Некорректный email".encode())
                    continue

                ticket_id = random.randint(10000, 99999)
                result = send_email(admin_email, admin_password, smtp_host, smtp_port, email, message, ticket_id)
                
                if result == "OK":
                    conn.sendall("OK".encode())
                    print("Сообщение отправлено")
                    break
                else:
                    conn.sendall(f"Ошибка: {result}".encode())
                


main()
