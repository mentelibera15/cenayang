import psycopg2
import bcrypt
import os
from dotenv import load_dotenv

load_dotenv()
DB_URL = os.getenv("DATABASE_URL")

def get_db_connection():
    return psycopg2.connect(DB_URL)

def get_user_role(username: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT role FROM users WHERE username = %s", (username,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None

def verify_login(input_username: str, input_password: str) -> dict:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT password_hash, role FROM users WHERE username = %s", (input_username,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        return {"success": False, "role": None, "message": "Username lo nggak terdaftar. Jangan ngarang."}

    stored_hash, role = row
    input_pwd_bytes = input_password.encode('utf-8')

    try:
        if bcrypt.checkpw(input_pwd_bytes, stored_hash.encode('utf-8')):
            return {"success": True, "role": role, "message": "Login sukses."}
        else:
            return {"success": False, "role": None, "message": "Password salah."}
    except Exception as e:
        return {"success": False, "role": None, "message": f"Terjadi kesalahan internal bcrypt: {e}"}

def register_user(initiator_username: str, new_username: str, new_password: str, new_role: str) -> dict:
    if initiator_username != "galih":
        return {"success": False, "message": "Cuma Dewa Galih yang punya hak cipta akun!"}
    if new_role not in ["superadmin", "admin", "user"]:
        return {"success": False, "message": "Kasta (role) nggak valid."}

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        salt = bcrypt.gensalt()
        hash_pwd = bcrypt.hashpw(new_password.encode('utf-8'), salt).decode('utf-8')
        cursor.execute("INSERT INTO users (username, password_hash, role) VALUES (%s, %s, %s)", (new_username, hash_pwd, new_role))
        conn.commit()
        return {"success": True, "message": f"Akun {new_username} dengan kasta {new_role} berhasil dicetak."}
    except psycopg2.IntegrityError:
        return {"success": False, "message": "Username udah dipakai. Cari nama lain."}
    finally:
        conn.close()

def hijack_user(initiator_username: str, target_username: str) -> dict:
    if initiator_username != "galih":
        return {"success": False, "message": "Lo siapa berani-beraninya mau nge-hijack?"}
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT role FROM users WHERE username = %s", (target_username,))
    row = cursor.fetchone()
    conn.close()
    
    if not row:
        return {"success": False, "message": "User target nggak ketemu di database."}
    return {"success": True, "role": row[0], "message": f"Berhasil merasuki {target_username}."}

def delete_user(initiator_username: str, target_username: str) -> dict:
    initiator_role = get_user_role(initiator_username)
    if initiator_role not in ["superadmin", "admin"]:
        return {"success": False, "message": "Akses ditolak. Lo bukan admin."}
    if target_username == "galih":
        return {"success": False, "message": "Lo nggak bisa men-delete Dewa pencipta sistem."}
        
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE username = %s", (target_username,))
    conn.commit()
    affected = cursor.rowcount
    conn.close()
    
    if affected > 0:
        return {"success": True, "message": f"User {target_username} resmi dimusnahkan."}
    return {"success": False, "message": "User target tidak ditemukan."}

def change_user_password(initiator_username: str, target_username: str, new_password: str) -> dict:
    initiator_role = get_user_role(initiator_username)
    if initiator_role not in ["superadmin", "admin"]:
        return {"success": False, "message": "Otoritas lo kurang."}
    if target_username == "galih" and initiator_username != "galih":
        return {"success": False, "message": "Mimpi lo mau ganti password gue?"}
        
    salt = bcrypt.gensalt()
    hash_pwd = bcrypt.hashpw(new_password.encode('utf-8'), salt).decode('utf-8')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET password_hash = %s WHERE username = %s", (hash_pwd, target_username))
    conn.commit()
    affected = cursor.rowcount
    conn.close()
    
    if affected > 0:
        return {"success": True, "message": f"Password {target_username} berhasil diganti paksa."}
    return {"success": False, "message": "User tidak ditemukan."}