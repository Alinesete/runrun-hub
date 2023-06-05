import os
from cryptography.fernet import Fernet

# Generate a random encryption key
encryption_key = Fernet.generate_key()

# Initialize the Fernet cipher with the encryption key
cipher = Fernet(encryption_key)

# Define the sensitive information
board_id = 000000
client_id = 000000

# Get user input for App_Token and User_Token
app_token = input("Enter the App_Token: ")
user_token = input("Enter the User_Token: ")

# Concatenate the information into a string
plaintext = f"board_id={board_id}\nclient_id={client_id}\nApp-Token={app_token}\nUser-Token={user_token}"

# Encrypt the plaintext
ciphertext = cipher.encrypt(plaintext.encode())

# Create the cache folder path outside the root folder
cache_folder = os.path.expanduser("~/runhub")

# Create the cache folder if it doesn't exist
if not os.path.exists(cache_folder):
    os.makedirs(cache_folder)

# Write the encrypted data to a file in the cache folder
cache_file = os.path.join(cache_folder, "encrypted_data")
with open(cache_file, "wb") as file:
    file.write(ciphertext)

# Write the encryption key to a separate file in the cache folder (keep it secure)
key_file = os.path.join(cache_folder, "encryption_key")
with open(key_file, "wb") as file:
    file.write(encryption_key)

print("Data encrypted and saved in the cache folder.")