import streamlit as st
import sys
import os
import json
from PIL import Image

# Memaksa Python mengenali folder root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from backend.main import (inisialisasi_sistem, proses_login, dapatkan_kasus_baru, 
                          tindakan_interaktif, evaluasi_mahasiswa, proses_meta_analisis,
                          tarik_riwayat, tarik_semua_user, export_excel, # export_excel adalah nama fungsi dari main.py lo sebelumnya
                          proses_register, proses_hijack, proses_hapus_akun, proses_ganti_sandi,
                          generate_laporan_visual)

# Inisialisasi Database (PostgreSQL)
inisialisasi_sistem()

# ================= KONFIGURASI HALAMAN & CSS =================
st.set_page_config(page_title="CENAYANG", page_icon="👁️", layout="wide")

# CSS Injeksi untuk Tombol WA Mengambang & Custom Chat
st.markdown("""
    <style>
    .wa-float {
        position: fixed;
        bottom: 40px;
        right: 40px;
        background-color: #25D366;
        color: #FFF;
        border-radius: 50px;
        text-align: center;
        font-size: 30px;
        width: 60px;
        height: 60px;
        line-height: 60px;
        z-index: 9999;
        text-decoration: none;
        box-shadow: 2px 2px 3px #999;
    }
    .wa-float:hover { color: #FFF; background-color: #128C7E; }
    </style>
    <a href="https://wa.me/628214927138" class="wa-float" target="_blank">💬</a>
""", unsafe_allow_html=True)

# ================= MANAJEMEN MEMORI SEMENTARA =================
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "username" not in st.session_state: st.session_state.username = ""
if "role" not in st.session_state: st.session_state.role = ""
if "kasus_aktif" not in st.session_state: st.session_state.kasus_aktif = {}
if "log_investigasi" not in st.session_state: st.session_state.log_investigasi = []
if "chat_history" not in st.session_state: st.session_state.chat_history = []
if "input_aksi_sementara" not in st.session_state: st.session_state.input_aksi_sementara = "" # Buat nampung chat

# ================= MODAL/POP-UP =================
@st.dialog("Rapor Paradigma Visual", width="large")
def tampilkan_rapor(rapor, path_gambar):
    st.markdown(f"### PARADIGMA DOMINAN: <span style='color:gold'>{rapor.get('Paradigma_Dominan', 'Unidentified').upper()}</span>", unsafe_allow_html=True)
    if path_gambar and os.path.exists(path_gambar):
        st.image(Image.open(path_gambar), use_container_width=True)
    else:
        st.error("Grafik gagal dimuat.")
    st.markdown("#### Catatan Dosen AI:")
    st.info(rapor.get("Overall_Feedback", ""))
    if st.button("Tutup & Kembali ke Dashboard"):
        st.session_state.kasus_aktif = {}
        st.rerun()

@st.dialog("Sabda Guru Besar: Meta-Analisis", width="large")
def tampilkan_meta(data_meta, path_gambar):
    st.markdown(f"### DEFAULT PARADIGMA: <span style='color:cyan'>{data_meta.get('Paradigma_Dominan_Default', 'Unidentified').upper()}</span>", unsafe_allow_html=True)
    if path_gambar and os.path.exists(path_gambar):
        st.image(Image.open(path_gambar), use_container_width=True)
    else:
        st.error("Grafik gagal dimuat.")
    st.markdown("#### Evaluasi Cara Berpikir Default Lo:")
    st.info(data_meta.get("Meta_Feedback", ""))

# ================= CALLBACK FUNGSI CHAT =================
def eksekusi_aksi_lapangan():
    aksi = st.session_state.input_aksi_sementara
    if not aksi: return
    
    # 1. Catat aksi user
    st.session_state.log_investigasi.append(aksi)
    st.session_state.chat_history.append({"role": "user", "text": aksi})
    
    # 2. Panggil AI untuk merespons
    res = tindakan_interaktif(aksi, st.session_state.kasus_aktif)
    is_clue = res.get('is_clue', False)
    role_balasan = "clue" if is_clue else "npc"
    st.session_state.chat_history.append({"role": role_balasan, "text": res.get('narasi', 'Hening.')})
    
    # 3. Bersihkan kolom input biar rapi
    st.session_state.input_aksi_sementara = ""

# ================= HALAMAN LOGIN =================
if not st.session_state.logged_in:
    kolom_tengah = st.columns([1, 2, 1])[1]
    with kolom_tengah:
        st.title("LOGIN CENAYANG")
        inp_user = st.text_input("Username")
        inp_pass = st.text_input("Password", type="password")
        if st.button("Masuk", use_container_width=True):
            res = proses_login(inp_user, inp_pass)
            if res["success"]:
                st.session_state.logged_in = True
                st.session_state.username = inp_user
                st.session_state.role = res["role"]
                st.rerun()
            else:
                st.error(res["message"])

# ================= DASHBOARD UTAMA =================
else:
    st.header(f"Dashboard: {st.session_state.username.upper()} (Kasta: {st.session_state.role.upper()})")
    
    # Render Tabs Dinamis
    tab_titles = ["Simulasi", "Riwayat", "Pengaturan"]
    if st.session_state.role in ["superadmin", "admin"]:
        tab_titles.append("Admin Panel")
    tabs = st.tabs(tab_titles)

    # --- TAB 1: SIMULASI ---
    with tabs[0]:
        if not st.session_state.kasus_aktif:
            col1, col2 = st.columns(2)
            if col1.button("Mulai Kasus Baru", use_container_width=True, type="primary"):
                with st.spinner("AI sedang merakit kasus lapangan..."):
                    kasus = dapatkan_kasus_baru()
                    if "error" not in kasus:
                        st.session_state.kasus_aktif = kasus
                        st.session_state.log_investigasi = []
                        awal = f"**SETTING:**\n{kasus.get('setting')}\n\n**MASALAH:**\n{kasus.get('visible_problem')}"
                        st.session_state.chat_history = [{"role": "sistem", "text": awal}]
                        st.rerun()
                    else:
                        st.error(kasus["error"])
            
            if col2.button("Meta-Analisis Paradigma Default", use_container_width=True):
                with st.spinner("Guru Besar sedang menganalisis..."):
                    res = proses_meta_analisis(st.session_state.username)
                    if res["status"] == "kurang":
                        st.warning(res["pesan"])
                    else:
                        data_meta = res["data"]
                        path_img = generate_laporan_visual(data_meta.get("Komposisi_Paradigma", []), f"Meta-Analisis {st.session_state.username}")
                        tampilkan_meta(data_meta, path_img)
        else:
            if st.button("Kembali / Batal", type="secondary"):
                st.session_state.kasus_aktif = {}
                st.rerun()
                
            col_kiri, col_kanan = st.columns([1.5, 1])
            
            with col_kiri:
                st.subheader(st.session_state.kasus_aktif.get('title', 'Kasus'))
                chat_box = st.container(height=500)
                with chat_box:
                    for chat in st.session_state.chat_history:
                        if chat["role"] == "sistem":
                            st.markdown(chat["text"])
                        elif chat["role"] == "user":
                            st.markdown(f"<span style='color:orange'>[{st.session_state.username.upper()}]: {chat['text']}</span>", unsafe_allow_html=True)
                        elif chat["role"] == "npc":
                            st.markdown(f"**[CENAYANG]:** {chat['text']}")
                        elif chat["role"] == "clue":
                            st.markdown(f"<span style='color:#25D366; font-weight:bold'>[PETUNJUK LAPANGAN DITEMUKAN]: {chat['text']}</span>", unsafe_allow_html=True)
            
            with col_kanan:
                st.markdown("**Tindakan Investigasi:**")
                
                # Menggunakan Callback biar input bersih otomatis setelah dienter/diklik
                st.text_input("Ketik langkah yang kamu ambil...", key="input_aksi_sementara", on_change=eksekusi_aksi_lapangan)
                st.button("Lakukan Aksi", on_click=eksekusi_aksi_lapangan)
                
                st.caption(f"Langkah tercatat: {len(st.session_state.log_investigasi)}")
                st.divider()
                
                hipo = st.text_area("Hipotesis Akhir:", height=150)
                if st.button("Submit Evaluasi", type="primary"):
                    if len(st.session_state.log_investigasi) < 5:
                        st.warning("Kurang Dalem, Bos! Turun lapangan minimal 5 kali aksi!")
                    elif not hipo.strip():
                        st.warning("Tulis kesimpulan akhir lo!")
                    else:
                        with st.spinner("Dosen AI sedang menganalisis insting lo..."):
                            rapor = evaluasi_mahasiswa(st.session_state.username, st.session_state.log_investigasi, hipo)
                            path_gambar = generate_laporan_visual(rapor.get("Daftar_Paradigma", []), st.session_state.username)
                            tampilkan_rapor(rapor, path_gambar)

    # --- TAB 2: RIWAYAT ---
    with tabs[1]:
        if st.button("Refresh Data"): st.rerun()
        riwayat = tarik_riwayat(st.session_state.username)
        if not riwayat:
            st.info("Belum ada riwayat simulasi.")
        else:
            for idx, row in enumerate(riwayat):
                with st.expander(f"Kasus {idx+1} | {row[0]} | Dominan: {row[3]}"):
                    st.markdown(f"**Log Aksi:** {row[1]}")
                    st.markdown(f"**Hipotesis:** {row[2]}")
                    try:
                        detail_p = "\n".join([f"- {p['nama']}: {p['skor']}%" for p in json.loads(row[4])])
                    except: detail_p = "Data usang"
                    st.markdown(f"**Detail Paradigma:**\n{detail_p}")
                    st.markdown(f"**Feedback:**\n> {row[5]}")

    # --- TAB 3: PENGATURAN ---
    with tabs[2]:
        csv_data = export_excel() # Panggil fungsi asli dari main.py lo
        if csv_data:
            st.download_button("Export Semua Rapor (CSV)", data=csv_data, file_name="Laporan_CENAYANG.csv", mime="text/csv", type="primary")
        else:
            st.error("Gagal menarik data CSV dari Database.")
        
        st.divider()
        st.subheader("Ganti Password Sendiri")
        new_pw = st.text_input("Password Baru", type="password", key="pw_sendiri")
        if st.button("Update Password") and new_pw:
            res = proses_ganti_sandi(st.session_state.username, st.session_state.username, new_pw)
            st.success(res["message"]) if res["success"] else st.error(res["message"])
            
        st.divider()
        if st.button("Logout", type="primary"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

    # --- TAB 4: ADMIN PANEL ---
    if st.session_state.role in ["superadmin", "admin"]:
        with tabs[3]:
            col_ad1, col_ad2 = st.columns(2)
            with col_ad1:
                st.subheader("Manajemen Kroco")
                adm_target = st.text_input("Target Username:")
                if st.button("Hapus User") and adm_target:
                    res = proses_hapus_akun(st.session_state.username, adm_target)
                    st.success(res["message"]) if res["success"] else st.error(res["message"])
                    
                adm_newpw = st.text_input("Password Baru Target", type="password")
                if st.button("Paksa Ganti PW") and adm_target and adm_newpw:
                    res = proses_ganti_sandi(st.session_state.username, adm_target, adm_newpw)
                    st.success(res["message"]) if res["success"] else st.error(res["message"])
            
            with col_ad2:
                if st.session_state.role == "superadmin":
                    st.markdown("### 👑 AREA DEWA")
                    hj_target = st.text_input("Username Korban Hijack:")
                    if st.button("Hijack Akun!") and hj_target:
                        res = proses_hijack(st.session_state.username, hj_target)
                        if res["success"]:
                            st.session_state.username = hj_target
                            st.session_state.role = res["role"]
                            st.rerun()
                        else:
                            st.error(res["message"])
                            
                    st.divider()
                    reg_user = st.text_input("New Username")
                    reg_pass = st.text_input("New Password", type="password")
                    reg_role = st.selectbox("Role", ["user", "admin", "superadmin"])
                    if st.button("Register User") and reg_user and reg_pass:
                        res = proses_register(st.session_state.username, reg_user, reg_pass, reg_role)
                        st.success(res["message"]) if res["success"] else st.error(res["message"])
                        
                    if st.button("Lihat Daftar Semua User"):
                        data = tarik_semua_user()
                        st.json([{"Username": u[0], "Role": u[1]} for u in data])