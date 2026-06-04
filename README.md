# XOR-Vault-Password-manager-
An enterprise-inspired Python password manager featuring a dual-key trust model. Protects credentials by combining user-derived secrets and server-side entropy via bitwise XOR operations, ensuring database theft alone yields zero plaintext.


PASSWORD MANAGER - SPLIT KEY DESIGN (IMPROVED)

====================================
1. ACCOUNT CREATION
====================================

User creates:

    USERNAME
    MANAGER_PASSWORD
    MEMORY_KEY (custom phrase)

Example:

    USERNAME        = sha
    MANAGER_PASSWORD = 1234
    MEMORY_KEY      = hii (or any phrase)

System generates:

    RANDOM_SALT
    RANDOM_IV

====================================
2. MASTER KEY CREATION (SPLIT SYSTEM)
====================================

Step 1: User secret input

    USERNAME + MANAGER_PASSWORD + MEMORY_KEY

        ↓
    Argon2id

        ↓
    USER_KEY_PART

------------------------------------

Step 2: Server generates

    RANDOM_SERVER_SECRET

        ↓
    Stored securely in database

        ↓
    SERVER_KEY_PART

------------------------------------

Step 3: Combine both

    USER_KEY_PART + SERVER_KEY_PART
        ↓
    FINAL_MASTER_KEY

====================================
3. ENCRYPTION
====================================

User stores:

    WEBSITE_NAME
    WEBSITE_USERNAME
    WEBSITE_PASSWORD

Encrypt using:

    AES-256-GCM + FINAL_MASTER_KEY

Store in database:

    ENCRYPTED_DATA
    SALT
    IV
    SERVER_KEY_PART (labeled A or B)
    POINTER_ID (reference ID)

Do NOT store:

    FINAL_MASTER_KEY
    USER_KEY_PART
    PASSWORDS in plaintext

====================================
4. LOGIN PROCESS (2 STEP AUTH)
====================================

STEP 1 LOGIN:

User enters:

    USERNAME
    MANAGER_PASSWORD
    MEMORY_KEY

System generates:

    USER_KEY_PART

Verify user exists.

------------------------------------

STEP 2 CONFIRMATION:

User re-enters:

    USERNAME + MEMORY_KEY

System uses:

    DATABASE SERVER_KEY_PART (A/B reference)

Combine:

    USER_KEY_PART + SERVER_KEY_PART
        ↓
    FINAL_MASTER_KEY

====================================
5. DECRYPTION
====================================

FINAL_MASTER_KEY
        ↓
AES-256-GCM DECRYPT
        ↓
RECOVER:

    WEBSITE_NAME
    WEBSITE_USERNAME
    WEBSITE_PASSWORD

====================================
6. SECURITY MODEL
====================================

✔ Split key (user + server)
✔ Even database theft alone is useless
✔ Even user secrets alone are not enough
✔ Requires both halves to unlock vault
✔ AES-256-GCM protects stored data
✔ Argon2id protects against brute force

====================================
7. IMPORTANT RULE (FIXED IDEA)
====================================

You said:

    "first we find half key from login, then second half from database"

This is correct BUT:

✔ Server must NEVER store full key
✔ Server only stores random encrypted key part
✔ Both halves are REQUIRED every time

====================================
FINAL RESULT
====================================



