import imaplib
import email
from email.header import decode_header
import configparser
import time
import os

def load_config():
    config = configparser.ConfigParser()
    config.read("config.ini")
    return config["EMAIL"]



def email_body(msg):
    
    for part in msg.walk():# проход по письму
        if part.get_content_type() == "text/plain":
            return part.get_payload(decode=True).decode() #получаем текст письма
    

def load_processed_uids(file_path):
    if not os.path.exists(file_path):
        return set()
    with open(file_path, "r", encoding="utf-8") as file:
        return set(file.read().splitlines())

def save_processed_uids(file_path, uids):
    
    with open(file_path, "a", encoding="utf-8") as file: # дописываем
        for uid in uids:
            file.write(f"{uid}\n")

def check_email():
    config = load_config()
    admin_email = config["EMAIL_LOGIN"]
    admin_password = config["EMAIL_PASSWORD"]
    imap_host = config["IMAP_HOST"]
    imap_port = config["IMAP_PORT"]
    period_check = int(config["PERIOD_CHECK"])

    processed_uids_file = "processed_uids.log"
    processed_uids = load_processed_uids(processed_uids_file)

    while True:
        try:
            with imaplib.IMAP4_SSL(imap_host, imap_port) as mail:
                mail.login(admin_email, admin_password)
                mail.select("inbox")

                
                status, messages = mail.uid("search", None, "ALL")# Ищем все письма в почтовом ящике
                new_uids = set(messages[0].split()) - processed_uids

                for uid in new_uids:
                    status, msg_data = mail.uid("fetch", uid, "(RFC822)")
                    for response_part in msg_data:
                        if isinstance(response_part, tuple):
                            msg = email.message_from_bytes(response_part[1])
                            subject = decode_header(msg["Subject"])[0][0]
                            if isinstance(subject, bytes):
                                subject = subject.decode()

                            body = email_body(msg)
                           

                            
                            if "[Ticket #" in subject:
                                with open("success_request.log", "a", encoding="utf-8") as log:
                                    log.write(f"ID: {subject}\n")
                                    log.write(f"Текст: {body}\n\n")
                            else:
                                with open("error_request.log", "a", encoding="utf-8") as log:
                                    log.write(f"Unknown subject: {subject}\n")
                                    log.write(f"Текст: {body}\n\n")

                    
                    processed_uids.add(uid)

                
                save_processed_uids(processed_uids_file, new_uids)

        except Exception as e:
            print(f"Ошибка проверки писем: {e}")
        time.sleep(period_check)


check_email()
