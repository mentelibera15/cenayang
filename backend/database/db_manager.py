import os
import json
from datetime import datetime
import bcrypt
import psycopg2
from dotenv import load_dotenv
import io
import csv

# Tarik URL dari file .env
load_dotenv()
DB_URL = os.getenv("DATABASE_URL")

def get_db_connection(): 
    return psycopg2.connect(DB_URL)

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    # Sintaks Postgres: SERIAL bukan AUTOINCREMENT
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (id SERIAL PRIMARY KEY, username TEXT UNIQUE NOT NULL, password_hash TEXT NOT NULL, role TEXT NOT NULL CHECK(role IN ('superadmin', 'admin', 'user')))''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS rapor_paradigma (id SERIAL PRIMARY KEY, username TEXT NOT NULL, waktu_tes TEXT NOT NULL, log_aksi TEXT, hipotesis TEXT, paradigma_dominan TEXT, data_analisis TEXT, feedback_dosen TEXT, FOREIGN KEY(username) REFERENCES users(username))''')
    
    cursor.execute("SELECT * FROM users WHERE username='galih'")
    if not cursor.fetchone():
        salt = bcrypt.gensalt()
        hash_pwd = bcrypt.hashpw(b"mahardika", salt).decode('utf-8')
        # Sintaks Postgres: Pakai %s bukan ?
        cursor.execute("INSERT INTO users (username, password_hash, role) VALUES (%s, %s, 'superadmin')", ('galih', hash_pwd))
    conn.commit()
    conn.close()

def simpan_rapor(nama_user: str, log_aksi: list, hipotesis: str, hasil_ai: dict):
    log_teks = " | ".join(log_aksi) if log_aksi else "Tidak ada aksi."
    waktu = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    paradigma_dominan = hasil_ai.get("Paradigma_Dominan", "Tidak Terbaca")
    data_analisis = json.dumps(hasil_ai.get("Daftar_Paradigma", []))
    feedback = hasil_ai.get("Overall_Feedback", "Tidak ada feedback.")
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('INSERT INTO rapor_paradigma (username, waktu_tes, log_aksi, hipotesis, paradigma_dominan, data_analisis, feedback_dosen) VALUES (%s, %s, %s, %s, %s, %s, %s)', (nama_user, waktu, log_teks, hipotesis, paradigma_dominan, data_analisis, feedback))
        conn.commit()
        conn.close()
        return True
    except Exception as e: 
        print(f"Error DB: {e}")
        return False

def get_riwayat_user(username: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT waktu_tes, log_aksi, hipotesis, paradigma_dominan, data_analisis, feedback_dosen FROM rapor_paradigma WHERE username = %s ORDER BY id DESC', (username,))
    data = cursor.fetchall()
    conn.close()
    return data

def get_semua_user():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT username, role FROM users')
    data = cursor.fetchall()
    conn.close()
    return data

def hapus_riwayat_user(username: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM rapor_paradigma WHERE username = %s', (username,))
    conn.commit()
    affected = cursor.rowcount
    conn.close()
    return affected > 0

# FUNGSI BARU UNTUK WEB (Melempar data sebagai memory buffer, bukan simpan ke C:)
def export_data_csv():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM rapor_paradigma')
        data = cursor.fetchall()
        kolom = [desc[0] for desc in cursor.description]
        conn.close()
        
        output = io.StringIO()
        writer = csv.writer(output, delimiter=';')
        writer.writerow(kolom)
        writer.writerows(data)
        return output.getvalue()
    except Exception as e:
        print(f"Error tarik CSV: {e}")
        return None