import os
from cryptography.fernet import Fernet

encryption_key = Fernet.generate_key()
cipher = Fernet(encryption_key)

board_id = 000000
client_id = 000000

app_token = input("Enter the App_Token: ")
user_token = input("Enter the User_Token: ")

plaintext = f"board_id={board_id}\nclient_id={client_id}\nApp-Token={app_token}\nUser-Token={user_token}"

ciphertext = cipher.encrypt(plaintext.encode())

cache_folder = os.path.expanduser("~/runhub")

if not os.path.exists(cache_folder):
    os.makedirs(cache_folder)

cache_file = os.path.join(cache_folder, "encrypted_data")
with open(cache_file, "wb") as file:
    file.write(ciphertext)

key_file = os.path.join(cache_folder, "encryption_key")
with open(key_file, "wb") as file:
    file.write(encryption_key)

print("Data encrypted and saved in the cache folder.")