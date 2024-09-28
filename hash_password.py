import os
import secrets
from getpass import getpass
from cryptography.fernet import Fernet
from argon2 import PasswordHasher

# Functie om de inhoud van een bestand te versleutelen
def encrypt_file(filename, key):
    cipher = Fernet(key)
    with open(filename, 'rb') as file:
        data = file.read()
    encrypted_data = cipher.encrypt(data)
    with open(f"{filename}.enc", 'wb') as enc_file:
        enc_file.write(encrypted_data)

# Stap 1: Genereren van een 32-byte lange pepper code
pepper_code = secrets.token_hex(32)  # 64 hexadecimale karakters (32 bytes)

# Stap 2: Genereren van een 32-byte lange salt code
salt = secrets.token_bytes(32)  # 32 bytes

# Stap 3: Vraag om het wachtwoord met getpass
password = getpass("Voer je wachtwoord in: ").encode()

# Stap 4: Combineer het wachtwoord met de pepper
peppered_password = password + pepper_code.encode()

# Stap 5: Maak een instance van de PasswordHasher met een tijdfactor van 16
ph = PasswordHasher(time_cost=16)

# Stap 6: Hash het peppered wachtwoord
hashed_password = ph.hash(peppered_password.decode())  # Decodeer naar string

# Stap 7: Sla de gehashte waarde op in password.hash bestand
with open('password.hash', 'wb') as hash_file:
    hash_file.write(hashed_password.encode())  # Encodeer naar bytes

# Stap 8: Maak een encryptiesleutel en versleutel de .env bestand
encryption_key = Fernet.generate_key()
cipher = Fernet(encryption_key)

# Stap 9: Schrijf de pepper en salt naar een .env bestand
with open('.env', 'w') as env_file:
    env_file.write(f'PEPPER={pepper_code}\n')
    env_file.write(f'SALT={salt.hex()}\n')  # Schrijf salt als hex

# Stap 10: Versleutel de .env bestand
encrypt_file('.env', encryption_key)

# Stap 11: Bewaar de encryptiesleutel in een bestand
with open('secret_enc.key', 'wb') as key_file:
    key_file.write(encryption_key)

# Stap 12: Verwijder de originele .env file
os.remove('.env')

print("Het wachtwoord is gehasht en opgeslagen in password.hash.")
