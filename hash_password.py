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

# --------- Vaste wachtwoord encryptie ---------

# Stap 8: Gebruik een vooraf gedefinieerd wachtwoord
fixed_password = "xxxxxxxxx".encode()

# Stap 9: Maak een encryptiesleutel
encryption_key = Fernet.generate_key()
cipher = Fernet(encryption_key)

# Stap 10: Versleutel het vaste wachtwoord
encrypted_fixed_password = cipher.encrypt(fixed_password)

# Stap 11: Sla het versleutelde wachtwoord op in fixed_password.enc bestand
with open('fixed_password.enc', 'wb') as fixed_enc_file:
    fixed_enc_file.write(encrypted_fixed_password)  # Opslaan als bytes

# Stap 12: Schrijf de pepper en salt naar een .env bestand
with open('.env', 'w') as env_file:
    env_file.write(f'PEPPER={pepper_code}\n')
    env_file.write(f'SALT={salt.hex()}\n')  # Schrijf salt als hex

# Stap 13: Versleutel de .env bestand
encrypt_file('.env', encryption_key)

# Stap 14: Bewaar de encryptiesleutel in een bestand
with open('secret_enc.key', 'wb') as key_file:
    key_file.write(encryption_key)

# Stap 15: Verwijder de originele .env file
os.remove('.env')

# Stap 16: Verwijder het script zelf
script_path = __file__
try:
    os.remove(script_path)
    print(f"Het script '{script_path}' is succesvol verwijderd.")
except Exception as e:
    print(f"Fout bij het verwijderen van het script: {e}")

print("Het wachtwoord is gehasht en opgeslagen in password.hash.")
print("Het vaste wachtwoord is versleuteld en opgeslagen in fixed_password.enc.")
