import os
import random
import smtplib
import string
import sqlite3
from email.mime.text import MIMEText
from cryptography.fernet import Fernet
from argon2 import PasswordHasher
from getpass import getpass  # Voeg getpass toe

# Functie om een 2FA-code te genereren
def generate_2fa_code():
    letters = string.ascii_letters
    digits = string.digits

    code_letters = ''.join(random.choice(letters) for _ in range(3))
    code_digits = ''.join(random.choice(digits) for _ in range(3))
    remaining_length = 8 - (len(code_letters) + len(code_digits))
    all_characters = letters + digits
    code_remaining = ''.join(random.choice(all_characters) for _ in range(remaining_length))
    
    code = list(code_letters + code_digits + code_remaining)
    random.shuffle(code)
    return ''.join(code)

# Functie om e-mail te verzenden
def send_email(subject, body, password):
    sender_email = "niels.coert@gmail.com"
    receiver_email = "niels.coert@gmail.com"

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = receiver_email

    try:
        with smtplib.SMTP_SSL('142.250.27.108', 465) as server:
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, msg.as_string())
        print("E-mail met 2FA-code verzonden.")
    except Exception as e:
        print(f"Fout bij het verzenden van e-mail: {e}")

# Functie om verbinding te maken met de database
def init_db():
    conn = sqlite3.connect('saved-passwords.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS passwords (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        service TEXT NOT NULL,
                        username TEXT NOT NULL,
                        password BLOB NOT NULL
                    )''')
    conn.commit()
    return conn

# Functie om wachtwoord toe te voegen
def add_password(conn, fernet):
    service = input("Voer de naam van de service in (bijv. Google): ")
    username = input("Voer je gebruikersnaam in: ")
    password = getpass("Voer het wachtwoord in: ").encode()  # Gebruik getpass

    encrypted_password = fernet.encrypt(password)
    
    cursor = conn.cursor()
    cursor.execute("INSERT INTO passwords (service, username, password) VALUES (?, ?, ?)",
                   (service, username, encrypted_password))
    conn.commit()
    print(f"Wachtwoord voor {service} succesvol toegevoegd.")

# Functie om wachtwoorden te bekijken
def view_passwords(conn, fernet):
    cursor = conn.cursor()
    cursor.execute("SELECT service, username, password FROM passwords")
    rows = cursor.fetchall()

    if not rows:
        print("Geen wachtwoorden gevonden.")
        return

    for row in rows:
        service, username, encrypted_password = row
        decrypted_password = fernet.decrypt(encrypted_password).decode()
        print(f"Service: {service}, Gebruikersnaam: {username}, Wachtwoord: {decrypted_password}")

# Functie om een wachtwoord te verwijderen
def delete_password(conn):
    service = input("Voer de naam van de service in waarvan je het wachtwoord wilt verwijderen: ")
    
    cursor = conn.cursor()
    cursor.execute("DELETE FROM passwords WHERE service = ?", (service,))
    
    if cursor.rowcount == 0:
        print(f"Geen wachtwoord gevonden voor {service}.")
    else:
        conn.commit()
        print(f"Wachtwoord voor {service} succesvol verwijderd.")

# Stap 1: Vraag om het wachtwoord
password = getpass("Voer je wachtwoord in: ").encode()  # Gebruik getpass voor wachtwoord

# Stap 2: Laad de encryptiesleutel
with open('secret_enc.key', 'rb') as key_file:
    encryption_key = key_file.read()

# Stap 3: Laad de pepper uit het versleutelde .env.enc bestand
cipher = Fernet(encryption_key)

with open('.env.enc', 'rb') as enc_file:
    encrypted_data = enc_file.read()

decrypted_data = cipher.decrypt(encrypted_data)
pepper_code = None
for line in decrypted_data.decode().splitlines():
    if line.startswith("PEPPER="):
        pepper_code = line.split('=')[1].strip()
        break

# Stap 4: Laad het versleutelde vaste wachtwoord
with open('fixed_password.enc', 'rb') as fixed_enc_file:
    encrypted_fixed_password = fixed_enc_file.read()

# Ontsleutel het vaste wachtwoord
decrypted_fixed_password = cipher.decrypt(encrypted_fixed_password).decode()

# Stap 5: Laad de opgeslagen gehashte waarde uit het password.hash bestand
with open('password.hash', 'rb') as hash_file:
    stored_hash = hash_file.read().decode()

# Stap 6: Voeg de pepper toe aan het ingevoerde wachtwoord
peppered_password = password + pepper_code.encode()

# Stap 7: Verifieer het wachtwoord met Argon2
ph = PasswordHasher()
try:
    ph.verify(stored_hash, peppered_password.decode())
    print("Wachtwoord correct. Verstuur 2FA-code...")

    # Genereer en verzend de 2FA-code
    two_fa_code = generate_2fa_code()
    send_email("2FA Code", f"2FA Code: {two_fa_code}", decrypted_fixed_password)

    # Vraag de gebruiker om de 2FA-code in te voeren
    user_code = input("Voer de 2FA-code in die naar je e-mail is verzonden: ")

    if user_code == two_fa_code:
        print("Access Granted")

        # Verbinding met de database
        conn = init_db()

        # Laad de Fernet-cipher voor encryptie/decryptie
        fernet = Fernet(encryption_key)

        while True:
            print("\n1. Wachtwoord toevoegen")
            print("2. Wachtwoorden bekijken")
            print("3. Wachtwoord verwijderen")
            print("4. Afsluiten")

            keuze = input("Kies een optie: ")

            if keuze == '1':
                add_password(conn, fernet)
            elif keuze == '2':
                view_passwords(conn, fernet)
            elif keuze == '3':
                delete_password(conn)
            elif keuze == '4':
                conn.close()
                print("Afsluiten...")
                break
            else:
                print("Ongeldige optie. Probeer opnieuw.")
    else:
        print("Access Denied: Ongeldige 2FA-code")
except Exception as e:
    print("Access Denied: Ongeldig wachtwoord")
