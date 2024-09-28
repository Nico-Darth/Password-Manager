import os
import random
import smtplib
import string
from email.mime.text import MIMEText
from cryptography.fernet import Fernet
from argon2 import PasswordHasher

# Functie om een 2FA-code te genereren
def generate_2fa_code():
    letters = string.ascii_letters
    digits = string.digits

    # Zorg voor ten minste 3 letters en 3 cijfers
    code_letters = ''.join(random.choice(letters) for _ in range(3))
    code_digits = ''.join(random.choice(digits) for _ in range(3))

    # Vul aan tot 8 karakters
    remaining_length = 8 - (len(code_letters) + len(code_digits))
    all_characters = letters + digits
    code_remaining = ''.join(random.choice(all_characters) for _ in range(remaining_length))

    # Combineer en shuffle de code
    code = list(code_letters + code_digits + code_remaining)
    random.shuffle(code)
    return ''.join(code)

# Functie om e-mail te verzenden
def send_email(subject, body):
    sender_email = "niels.coert@gmail.com"
    receiver_email = "niels.coert@gmail.com"
    password = "tzuxzsvofozqosnw"  # Google App Password

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

# Stap 1: Vraag om het wachtwoord
password = input("Voer je wachtwoord in: ").encode()

# Stap 2: Laad de encryptiesleutel
with open('secret_enc.key', 'rb') as key_file:
    encryption_key = key_file.read()

# Stap 3: Laad de pepper uit het versleutelde .env.enc bestand
cipher = Fernet(encryption_key)

with open('.env.enc', 'rb') as enc_file:
    encrypted_data = enc_file.read()

decrypted_data = cipher.decrypt(encrypted_data)
# Verkrijg de pepper uit het gedecodeerde .env-inhoud
pepper_code = None
for line in decrypted_data.decode().splitlines():
    if line.startswith("PEPPER="):
        pepper_code = line.split('=')[1].strip()
        break

# Stap 4: Laad de opgeslagen gehashte waarde uit het password.hash bestand
with open('password.hash', 'rb') as hash_file:
    stored_hash = hash_file.read().decode()  # Decodeer naar string

# Stap 5: Voeg de pepper toe aan het ingevoerde wachtwoord
peppered_password = password + pepper_code.encode()

# Stap 6: Vergelijk het gehashte wachtwoord met de opgeslagen hash
ph = PasswordHasher()

try:
    # Verifieer het gehashte wachtwoord
    ph.verify(stored_hash, peppered_password.decode())  # Decodeer naar string voor verificatie
    print("Wachtwoord correct. Verstuur 2FA-code...")

    # Genereer en verzend de 2FA-code
    two_fa_code = generate_2fa_code()
    send_email("2FA Code", f"2FA Code: {two_fa_code}")

    # Vraag de gebruiker om de 2FA-code in te voeren
    user_code = input("Voer de 2FA-code in die naar je e-mail is verzonden: ")

    if user_code == two_fa_code:
        print("Access Granted")
    else:
        print("Access Denied: Ongeldige 2FA-code")
except Exception as e:
    print("Access Denied: Ongeldig wachtwoord")
