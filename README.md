# Wachtwoordbeheerder

Deze repository bevat een eenvoudige wachtwoordbeheerder in Python. Deze applicatie maakt gebruik van encryptie en hashing om je wachtwoorden veilig op te slaan. 

## Belangrijk

**Momenteel is deze applicatie niet bedoeld voor publieke gebruikers.** Gebruik deze applicatie alleen voor educatieve doeleinden of als een proof of concept.

## Installatie

1. **Vereisten:**
   - Zorg ervoor dat je Python 3.x geïnstalleerd hebt.
   - Installeer de benodigde packages met pip:
     ```bash
     pip install cryptography argon2-cffi
     ```

2. **Hash het masterwachtwoord:**
   Voordat je de hoofdapplicatie uitvoert, moet je eerst het script `hash_password.py` uitvoeren om een gehashed bestand te maken voor je masterwachtwoord:
   ```bash
   python hash_password.py

3. **Voer de hoofdapplicate uit**
    Na het hash-en van je wachtwoord kun je de hoofdapplicatie `main.py` starten:
   ```bash
   python main.py

# Functionaliteiten

## Wachtwoord toevoegen:
Voeg een nieuwe service met bijbehorend gebruikersnaam en wachtwoord toe aan de database.

## Wachtwoorden bekijken: 
Bekijk opgeslagen wachtwoorden.

## Wachtwoord verwijderen:
Verwijder een specifiek opgeslagen wachtwoord.

## Twee-factor-authenticatie (2FA):
Ontvang een 2FA-code via e-mail om de toegang te beveiligen.

## Hoe het werkt

1. Voer je masterwachtwoord in.
2. Een 2FA-code wordt naar je e-mail verzonden.
3. Voer de 2FA-code in om toegang te krijgen tot de wachtwoordbeheerder.
4. Je kunt wachtwoorden toevoegen, bekijken en verwijderen.

## Veiligheid

- Wachtwoorden worden gehashed met de Argon2 hashing-algoritme.
- Gevoelige gegevens, zoals de .env-bestanden, worden versleuteld opgeslagen.
