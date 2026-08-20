import customtkinter as ctk
from tkinter import messagebox
from PIL import Image
import sys
import os
import json
import webbrowser

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from backend.main import (inisialisasi_sistem, proses_login, dapatkan_kasus_baru, 
                          tindakan_interaktif, evaluasi_mahasiswa, proses_meta_analisis,
                          tarik_riwayat, export_excel, tarik_semua_user,
                          proses_register, proses_hijack, proses_hapus_akun, proses_ganti_sandi,
                          generate_laporan_visual)

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class CenayangApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("CENAYANG - Mesin Evaluasi Nalar Antropologis (v2.0 RBAC)")
        self.geometry("1100x800")
        
        self.nama_aktif = ""
        self.role_aktif = ""
        self.kasus_aktif = {}
        self.log_investigasi = []
        
        inisialisasi_sistem()
        
        self.container = ctk.CTkFrame(self)
        self.container.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.tampilkan_login()
        
        # TOMBOL FLOATING WHATSAPP
        # Nempel langsung ke 'self', jadi nggak akan ikut terhapus saat frame diganti
        self.btn_wa = ctk.CTkButton(
            self, 
            text="💬", 
            width=70, 
            height=50, 
            corner_radius=25, 
            fg_color="#25D366", 
            hover_color="#128C7E", 
            font=("Arial", 16, "bold"),
            command=self.buka_wa
        )
        # Taruh di pojok kanan bawah
        self.btn_wa.place(relx=0.97, rely=0.97, anchor="se")

    def buka_wa(self):
        """Fungsi babu buat ngelempar user ke browser buka link WA lo."""
        webbrowser.open("https://wa.me/628214927138")

    def bersihkan_layar(self):
        for widget in self.container.winfo_children():
            widget.destroy()

    # ================= LOGIN =================
    def tampilkan_login(self):
        self.bersihkan_layar()
        frame = ctk.CTkFrame(self.container, width=400, height=400)
        frame.place(relx=0.5, rely=0.5, anchor="center")
        
        ctk.CTkLabel(frame, text="LOGIN CENAYANG", font=("Arial", 24, "bold")).pack(pady=(40, 10))
        self.inp_user = ctk.CTkEntry(frame, placeholder_text="Username", width=250)
        self.inp_user.pack(pady=10)
        self.inp_pass = ctk.CTkEntry(frame, placeholder_text="Password", show="*", width=250)
        self.inp_pass.pack(pady=10)
        ctk.CTkButton(frame, text="Masuk", command=self.handle_login, width=250).pack(pady=20)

    def handle_login(self):
        user = self.inp_user.get()
        pwd = self.inp_pass.get()
        res = proses_login(user, pwd)
        
        if res["success"]:
            self.nama_aktif = user
            self.role_aktif = res["role"]
            self.tampilkan_dashboard()
        else:
            messagebox.showerror("Ditolak", res["message"])

    def handle_logout(self):
        self.nama_aktif = ""
        self.role_aktif = ""
        self.tampilkan_login()

    # ================= DASHBOARD =================
    def tampilkan_dashboard(self):
        self.bersihkan_layar()
        ctk.CTkLabel(self.container, text=f"Dashboard: {self.nama_aktif.upper()} (Kasta: {self.role_aktif.upper()})", font=("Arial", 18, "bold")).pack(pady=10)
        
        self.tabs = ctk.CTkTabview(self.container)
        self.tabs.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.tabs.add("Simulasi")
        self.tabs.add("Riwayat")
        self.tabs.add("Pengaturan")
        if self.role_aktif in ["superadmin", "admin"]:
            self.tabs.add("Admin Panel")
            
        self.setup_tab_simulasi()
        self.setup_tab_riwayat()
        self.setup_tab_pengaturan()
        if self.role_aktif in ["superadmin", "admin"]:
            self.setup_tab_admin()

    # --- TAB 1: SIMULASI ---
    def setup_tab_simulasi(self):
        tab = self.tabs.tab("Simulasi")
        ctk.CTkButton(tab, text="Mulai Kasus Baru", command=self.mulai_tes, height=50, width=300).pack(pady=30)
        ctk.CTkButton(tab, text="Meta-Analisis Paradigma Default", command=self.handle_meta, height=50, width=300, fg_color="purple", hover_color="darkviolet").pack(pady=10)

    def handle_meta(self):
        res = proses_meta_analisis(self.nama_aktif)
        if res["status"] == "kurang":
            messagebox.showwarning("Kurang Syarat", res["pesan"])
        else:
            data_meta = res["data"]
            komposisi = data_meta.get("Komposisi_Paradigma", [])
            dominan = data_meta.get("Paradigma_Dominan_Default", "Unidentified")
            esai = data_meta.get("Meta_Feedback", "")
            
            path_gambar = generate_laporan_visual(komposisi, f"Meta-Analisis {self.nama_aktif}")
            
            jendela_meta = ctk.CTkToplevel(self)
            jendela_meta.title("Sabda Guru Besar: Meta-Analisis")
            jendela_meta.geometry("800x750")
            jendela_meta.grab_set()
            
            ctk.CTkLabel(jendela_meta, text=f"DEFAULT PARADIGMA:\n{dominan.upper()}", font=("Arial", 20, "bold"), text_color="cyan").pack(pady=15)
            
            if path_gambar and os.path.exists(path_gambar):
                img = ctk.CTkImage(light_image=Image.open(path_gambar), dark_image=Image.open(path_gambar), size=(600, 350))
                lbl_img = ctk.CTkLabel(jendela_meta, image=img, text="")
                lbl_img.pack(pady=10)
            else:
                ctk.CTkLabel(jendela_meta, text="(Grafik gagal dimuat karena data kosong)", text_color="red").pack(pady=10)
                
            ctk.CTkLabel(jendela_meta, text="Evaluasi Cara Berpikir Default Kamu:", font=("Arial", 14, "bold")).pack(pady=(10, 5))
            txt_esai = ctk.CTkTextbox(jendela_meta, height=130, wrap="word")
            txt_esai.pack(fill="x", padx=20, pady=5)
            txt_esai.insert("1.0", esai)
            txt_esai.configure(state="disabled")
            
            ctk.CTkButton(jendela_meta, text="Tutup", command=jendela_meta.destroy, fg_color="darkred").pack(pady=15)

    # --- TAB 2: RIWAYAT ---
    def setup_tab_riwayat(self):
        tab = self.tabs.tab("Riwayat")
        ctk.CTkButton(tab, text="Refresh Data", command=self.refresh_riwayat).pack(pady=10)
        self.box_riwayat = ctk.CTkTextbox(tab, wrap="word")
        self.box_riwayat.pack(fill="both", expand=True, padx=10, pady=10)
        self.refresh_riwayat()

    def refresh_riwayat(self):
        data = tarik_riwayat(self.nama_aktif)
        self.box_riwayat.configure(state="normal")
        self.box_riwayat.delete("1.0", "end")
        if not data:
            self.box_riwayat.insert("end", "Belum ada riwayat simulasi.")
        else:
            for idx, row in enumerate(data):
                try: 
                    detail_p = "\n  ".join([f"{p['nama']}: {p['skor']}%" for p in json.loads(row[4])])
                except: detail_p = "Data usang"
                self.box_riwayat.insert("end", f"[{idx+1}] Waktu: {row[0]}\nLog: {row[1]}\nHipotesis: {row[2]}\nParadigma Dominan: {row[3]}\nDetail:\n  {detail_p}\nFeedback: {row[5]}\n" + "-"*50 + "\n")
        self.box_riwayat.configure(state="disabled")

    # --- TAB 3: PENGATURAN ---
    def setup_tab_pengaturan(self):
        tab = self.tabs.tab("Pengaturan")
        ctk.CTkButton(tab, text="Export Semua Rapor (Excel)", command=lambda: messagebox.showinfo("Export", "Sukses!") if export_excel() else messagebox.showerror("Gagal", "Error!"), fg_color="green").pack(pady=20)
        ctk.CTkLabel(tab, text="Ganti Password Sendiri:").pack()
        self.inp_new_pw = ctk.CTkEntry(tab, show="*")
        self.inp_new_pw.pack(pady=5)
        ctk.CTkButton(tab, text="Update Password", command=self.update_own_pw).pack(pady=10)
        ctk.CTkButton(tab, text="Logout", command=self.handle_logout, fg_color="darkred").pack(pady=40)

    def update_own_pw(self):
        new_pw = self.inp_new_pw.get()
        if not new_pw: return
        res = proses_ganti_sandi(self.nama_aktif, self.nama_aktif, new_pw)
        messagebox.showinfo("Info", res["message"])

    # --- TAB 4: ADMIN PANEL ---
    def setup_tab_admin(self):
        tab = self.tabs.tab("Admin Panel")
        
        form_frame = ctk.CTkFrame(tab)
        form_frame.pack(fill="x", padx=10, pady=10)
        
        ctk.CTkLabel(form_frame, text="Target Username:").grid(row=0, column=0, padx=5, pady=5)
        self.adm_target = ctk.CTkEntry(form_frame)
        self.adm_target.grid(row=0, column=1, padx=5, pady=5)
        
        ctk.CTkButton(form_frame, text="Hapus User", command=self.adm_hapus).grid(row=0, column=2, padx=5, pady=5)
        
        self.adm_newpw = ctk.CTkEntry(form_frame, placeholder_text="Password Baru Target")
        self.adm_newpw.grid(row=1, column=1, padx=5, pady=5)
        ctk.CTkButton(form_frame, text="Paksa Ganti PW", command=self.adm_gantipw).grid(row=1, column=2, padx=5, pady=5)

        if self.role_aktif == "superadmin":
            dewa_frame = ctk.CTkFrame(tab, border_width=2, border_color="gold")
            dewa_frame.pack(fill="x", padx=10, pady=20)
            ctk.CTkLabel(dewa_frame, text="=== AREA DEWA (SUPERADMIN) ===", text_color="gold").pack(pady=5)
            
            hijack_frame = ctk.CTkFrame(dewa_frame, fg_color="transparent")
            hijack_frame.pack(pady=5)
            self.hj_target = ctk.CTkEntry(hijack_frame, placeholder_text="Username Korban")
            self.hj_target.pack(side="left", padx=5)
            ctk.CTkButton(hijack_frame, text="Hijack Akun!", command=self.adm_hijack, fg_color="purple").pack(side="left", padx=5)
            
            reg_frame = ctk.CTkFrame(dewa_frame, fg_color="transparent")
            reg_frame.pack(pady=5)
            self.reg_user = ctk.CTkEntry(reg_frame, placeholder_text="New Username")
            self.reg_user.pack(side="left", padx=2)
            self.reg_pass = ctk.CTkEntry(reg_frame, placeholder_text="New Password")
            self.reg_pass.pack(side="left", padx=2)
            self.reg_role = ctk.CTkOptionMenu(reg_frame, values=["user", "admin", "superadmin"])
            self.reg_role.pack(side="left", padx=2)
            ctk.CTkButton(reg_frame, text="Register User", command=self.adm_register).pack(side="left", padx=2)
            
            ctk.CTkButton(dewa_frame, text="Lihat Daftar Semua User", command=self.adm_list_user).pack(pady=10)

    def adm_hapus(self):
        res = proses_hapus_akun(self.nama_aktif, self.adm_target.get())
        messagebox.showinfo("Info", res["message"])
        
    def adm_gantipw(self):
        res = proses_ganti_sandi(self.nama_aktif, self.adm_target.get(), self.adm_newpw.get())
        messagebox.showinfo("Info", res["message"])

    def adm_hijack(self):
        target = self.hj_target.get()
        res = proses_hijack(self.nama_aktif, target)
        if res["success"]:
            messagebox.showwarning("HIJACK BERHASIL", res["message"])
            self.nama_aktif = target
            self.role_aktif = res["role"]
            self.tampilkan_dashboard()
        else:
            messagebox.showerror("Gagal", res["message"])

    def adm_register(self):
        res = proses_register(self.nama_aktif, self.reg_user.get(), self.reg_pass.get(), self.reg_role.get())
        messagebox.showinfo("Info", res["message"])

    def adm_list_user(self):
        data = tarik_semua_user()
        teks = "Daftar Akun:\n\n" + "\n".join([f"- {u[0]} ({u[1]})" for u in data])
        messagebox.showinfo("Database User", teks)

    # ================= GAMEPLAY / SIMULASI =================
    def mulai_tes(self):
        self.kasus_aktif = dapatkan_kasus_baru()
        if "error" in self.kasus_aktif:
            messagebox.showerror("Error AI", self.kasus_aktif["error"])
            return
            
        self.log_investigasi = []
        self.bersihkan_layar()
        
        ctk.CTkButton(self.container, text="Kembali ke Dashboard", command=self.tampilkan_dashboard, fg_color="darkred").pack(anchor="nw", pady=5)
        
        panel_kiri = ctk.CTkFrame(self.container, width=500)
        panel_kiri.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        ctk.CTkLabel(panel_kiri, text=self.kasus_aktif.get('title', 'Kasus'), font=("Arial", 16, "bold")).pack(pady=5)
        
        self.txt_kasus = ctk.CTkTextbox(panel_kiri, wrap="word")
        self.txt_kasus.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.txt_kasus._textbox.tag_config("user_tag", foreground="orange")
        self.txt_kasus._textbox.tag_config("npc_tag", foreground="white")
        self.txt_kasus._textbox.tag_config("sys_tag", foreground="red")
        self.txt_kasus._textbox.tag_config("clue_tag", foreground="green")
        
        awal_teks = f"SETTING: {self.kasus_aktif.get('setting')}\n\nMASALAH: {self.kasus_aktif.get('visible_problem')}\n\n"
        self.txt_kasus.insert("end", awal_teks)
        self.txt_kasus.configure(state="disabled")
        
        panel_kanan = ctk.CTkFrame(self.container, width=400)
        panel_kanan.pack(side="right", fill="both", expand=True, padx=5, pady=5)
        
        ctk.CTkLabel(panel_kanan, text="Tindakan Investigasi:").pack(pady=5)
        self.inp_aksi = ctk.CTkEntry(panel_kanan, width=300)
        self.inp_aksi.pack(pady=5)
        ctk.CTkButton(panel_kanan, text="Lakukan Aksi", command=self.kirim_aksi).pack(pady=5)
        
        self.lbl_log = ctk.CTkLabel(panel_kanan, text="Langkah: 0")
        self.lbl_log.pack(pady=5)
        
        ctk.CTkLabel(panel_kanan, text="Hipotesis Akhir:").pack(pady=(20, 5))
        self.inp_hipo = ctk.CTkTextbox(panel_kanan, height=100)
        self.inp_hipo.pack(fill="x", padx=10)
        ctk.CTkButton(panel_kanan, text="Submit Evaluasi", command=self.submit_evaluasi, fg_color="purple").pack(pady=15)

    def kirim_aksi(self):
        aksi = self.inp_aksi.get()
        if not aksi: return
        
        self.log_investigasi.append(aksi)
        self.lbl_log.configure(text=f"Langkah: {len(self.log_investigasi)}")
        self.inp_aksi.delete(0, 'end')
        
        self.txt_kasus.configure(state="normal")
        
        self.txt_kasus.insert("end", f"\n[{self.nama_aktif.upper()}]: {aksi}\n", "user_tag")
        self.txt_kasus.insert("end", "[CENAYANG]: Sedang memantau...\n", "sys_tag")
        self.txt_kasus.see("end")
        self.update()
        
        res = tindakan_interaktif(aksi, self.kasus_aktif)
        narasi = res.get('narasi', 'Hening.')
        is_clue = res.get('is_clue', False)
        
        self.txt_kasus.delete("end-2l", "end-1l")
        
        tag_pengecoran = "clue_tag" if is_clue else "npc_tag"
        prefix = "[PETUNJUK LAPANGAN DITEMUKAN]: " if is_clue else "[CENAYANG]: "
        
        self.txt_kasus.insert("end", f"{prefix}{narasi}\n", tag_pengecoran)
        self.txt_kasus.see("end")
        self.txt_kasus.configure(state="disabled")

    def submit_evaluasi(self):
        hipo = self.inp_hipo.get("1.0", "end-1c").strip()
        if len(self.log_investigasi) < 5:
            messagebox.showwarning("Kurang Dalem, Bos!", "Turun lapangan kok nanyanya kurang dari 5 kali? Kamu kira ini sensus penduduk? Gali data dan interaksi lebih dalam sebelum narik kesimpulan!")
            return
        if not hipo:
            messagebox.showwarning("Kosong", "Tulis kesimpulan akhirmu!")
            return
            
        messagebox.showinfo("Proses", "Dosen AI sedang menganalisis insting kamu. Tunggu bentar...")
        rapor = evaluasi_mahasiswa(self.nama_aktif, self.log_investigasi, hipo)
        
        daftar_paradigma = rapor.get("Daftar_Paradigma", [])
        paradigma_dominan = rapor.get("Paradigma_Dominan", "Unidentified")
        feedback = rapor.get("Overall_Feedback", "")
        
        path_gambar = generate_laporan_visual(daftar_paradigma, self.nama_aktif)
        
        jendela_rapor = ctk.CTkToplevel(self)
        jendela_rapor.title("Rapor Paradigma Visual")
        jendela_rapor.geometry("750x700")
        jendela_rapor.grab_set() 
        
        ctk.CTkLabel(jendela_rapor, text=f"PARADIGMA DOMINAN:\n{paradigma_dominan.upper()}", font=("Arial", 20, "bold"), text_color="gold").pack(pady=15)
        
        if path_gambar and os.path.exists(path_gambar):
            img = ctk.CTkImage(light_image=Image.open(path_gambar), dark_image=Image.open(path_gambar), size=(600, 350))
            lbl_img = ctk.CTkLabel(jendela_rapor, image=img, text="")
            lbl_img.pack(pady=10)
        else:
            ctk.CTkLabel(jendela_rapor, text="(Grafik gagal dimuat)", text_color="red").pack(pady=10)
            
        ctk.CTkLabel(jendela_rapor, text="Catatan Dosen AI:", font=("Arial", 14, "bold")).pack(pady=(10, 5))
        txt_feedback = ctk.CTkTextbox(jendela_rapor, height=120, wrap="word")
        txt_feedback.pack(fill="x", padx=20, pady=5)
        txt_feedback.insert("1.0", feedback)
        txt_feedback.configure(state="disabled")
        
        ctk.CTkButton(jendela_rapor, text="Tutup & Kembali ke Dashboard", command=lambda: [jendela_rapor.destroy(), self.tampilkan_dashboard()], fg_color="darkred").pack(pady=15)

if __name__ == "__main__":
    app = CenayangApp()
    app.mainloop()
