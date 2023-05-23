from cryptography.fernet import Fernet
import ctypes

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


# Write the encrypted data to a file
with open("😨", "wb") as file:
    file.write(ciphertext)

# Write the encryption key to a separate file (keep it secure)
with open("./assets/data", "wb") as file:
    file.write(encryption_key)
