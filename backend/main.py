from backend.auth import verify_login, register_user, hijack_user, delete_user, change_user_password
from backend.ai_core.case_agent import generate_new_case
from backend.ai_core.analysis_agent import generate_reasoning_analysis, generate_meta_analysis
from backend.ai_core.evidence import explore_location
from backend.database.db_manager import init_db, simpan_rapor, export_data_csv, get_riwayat_user, get_semua_user, hapus_riwayat_user
from backend.visualizer import buat_grafik_paradigma

def inisialisasi_sistem(): init_db()

# --- Fitur Autentikasi & Admin ---
def proses_login(user, pwd): return verify_login(user, pwd)
def proses_register(init_user, new_user, new_pwd, new_role): return register_user(init_user, new_user, new_pwd, new_role)
def proses_hijack(init_user, target): return hijack_user(init_user, target)
def proses_hapus_akun(init_user, target): return delete_user(init_user, target)
def proses_ganti_sandi(init_user, target, new_pwd): return change_user_password(init_user, target, new_pwd)

# --- Fitur Data & History ---
def tarik_semua_user(): return get_semua_user()
def tarik_riwayat(username): return get_riwayat_user(username)
def hapus_riwayat(username): return hapus_riwayat_user(username)
from backend.database.db_manager import export_data_csv
def tarik_data_csv(): return export_data_csv()

# --- Fitur Gameplay AI ---
def dapatkan_kasus_baru():
    sukses, data = generate_new_case()
    return data if sukses else {"error": "Gagal bikin kasus."}

def tindakan_interaktif(aksi, kasus):
    return explore_location(aksi, kasus)

def evaluasi_mahasiswa(user, log, hipotesis):
    rapor = generate_reasoning_analysis(log, hipotesis)
    simpan_rapor(user, log, hipotesis, rapor)
    return rapor

def proses_meta_analisis(username):
    riwayat = get_riwayat_user(username)
    if len(riwayat) < 4:
        kurang = 4 - len(riwayat)
        return {"status": "kurang", "pesan": f"Apa yang mau dianalisis bos! Selesaiin {kurang} simulasi lagi sana!"}
    
    hasil_meta = generate_meta_analysis(riwayat)
    return {"status": "sukses", "data": hasil_meta}

def generate_laporan_visual(daftar_paradigma, username):
    return buat_grafik_paradigma(daftar_paradigma, username)

if __name__ == "__main__":
    inisialisasi_sistem()

