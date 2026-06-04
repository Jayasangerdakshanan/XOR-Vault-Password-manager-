import base64
import os
import json  # Added to allow saving data to a file
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

# --- RECOVERY STORAGE ---
DATA_FILE = "vault.json"
GLOBAL_SALT = b'SplitKeySalt!' 
global_user_key_part = None

def load_database():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_database(db_data):
    with open(DATA_FILE, "w") as f:
        json.dump(db_data, f, indent=4)

# Load existing data right at startup
DATABASE = load_database()


# 1. Welcome Screen
print("""         =======================================================
         +++++++++++++++ WELCOME TO LOGIN PAGE +++++++++++++++++
         =======================================================""")

def user_input():
    global global_user_key_part
    username = input("++Enter user name :- ")
    password = input("++Enter password :- ")
    key = input("++Enter your KEY :- ")

    print("\n--- Login Data Saved ---")
    print("Username:", username)
    print("Password:", password)
    print("Key:", key)

    # Turn the login inputs into your USER_KEY_PART bytes
    combined = f"{username}{password}{key}".encode()
    kdf = PBKDF2HMAC(algorithm=hashes.SHA256(), length=16, salt=GLOBAL_SALT, iterations=100_000)
    global_user_key_part = kdf.derive(combined)

# Call your login function to run it first

user_input()
mode = input("""\nSelect mode:
If you need to add password please type -a
If you need to view password please type -o
-> """).strip()

def Web_input():
    # As requested before: We can combine these 3 into one line later, 
    # but let's keep your 3 inputs for this test run!
    website_name = input("\n++Enter Website name :- ")
    website_password = input("++Enter Website Password :- ")
    website_username = input("++Enter Website user name :- ")

    print("\n--- Website Details Saved ---")
    print("Website Name:", website_name)
    print("Website Username:", website_username)
    print("Website Password:", website_password)

    # Generate the server half key and unique IV
    iv = os.urandom(12) 
    server_key_part = os.urandom(16)
    
    # Mix user part + server part to make the AES-256 key
    final_master_key = global_user_key_part + server_key_part
    
    # Encrypt the data using AES-256-GCM
    aesgcm = AESGCM(final_master_key)
    payload = f"{website_name}|{website_username}|{website_password}".encode()
    encrypted_data = aesgcm.encrypt(iv, payload, None)

    # Convert raw binary bytes into text strings so they can be saved in a standard JSON file
    DATABASE[website_name.lower()] = {
        "encrypted_data": base64.b64encode(encrypted_data).decode('utf-8'),
        "iv": base64.b64encode(iv).decode('utf-8'),
        "server_key_part": base64.b64encode(server_key_part).decode('utf-8')
    }
    
    # Commit changes permanently to your computer's disk
    save_database(DATABASE)
    print(f"✔ [SYSTEM]: Encrypted & saved data permanently to disk for {website_name}!")

    new_web_info = input("Please enter Y to add new info or enter N [Y/N] :- ").strip()
    
    # If they press Y, we call Web_input() again to loop it!
    if new_web_info == "Y" or new_web_info == "y":
        Web_input()
    else:
        print("\nExiting data entry mode...")

def Web_open():
    print('================VALUT Opening=================-')
    print("Checking keys... Decrypting your passwords...")

    target_site = input("++Enter Website name to decrypt :- ").strip().lower()
    
    if target_site in DATABASE:
        record = DATABASE[target_site]
        
        # Convert text strings back into operational raw binary bytes
        encrypted_data = base64.b64decode(record["encrypted_data"])
        iv = base64.b64decode(record["iv"])
        server_key_part = base64.b64decode(record["server_key_part"])
        
        # Combine the user's login key with this record's unique server part
        final_master_key = global_user_key_part + server_key_part
        
        try:
            # Decrypt using AES-256-GCM
            aesgcm = AESGCM(final_master_key)
            decrypted_bytes = aesgcm.decrypt(iv, encrypted_data, None)
            
            # Split back into the original 3 values
            web_name, web_user, web_pass = decrypted_bytes.decode().split("|")
            
            print("\n ===]-->> Decryption Successful <<--[=== ")
            print("Website:", web_name)
            print("Username:", web_user)
            print("Password:", web_pass)
        except Exception:
            print(" XXXXXX Decryption Failed! Invalid cryptographic integrity check XXXX")
    else:
        print("! XX ==Error: Website record not found in database== XX !")

# 2. FIXED: Use input() instead of print() so the user can actually type their choice


if mode == "-a":
    print("\n[+++++++++++++== PLEASE ADD NEW INFO ==+++++++++++++]")
    Web_input()
elif mode == "-o":
    print("\n[+++++++++++++== OPENING VAULT ==+++++++++++++]")
    # We will build the decryption/view function here later!
    Web_open()
else:
    print("Invalid option selected.")
