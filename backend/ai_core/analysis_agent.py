import json
from backend.ai_core.client import generate_completion

def generate_reasoning_analysis(user_logs: list, final_hypothesis: str) -> dict:
    log_text = "\n".join([f"- {log}" for log in user_logs]) if user_logs else "Nggak ada aksi."
    system_prompt = f"""
    Lo adalah Dosen Antropologi di CENAYANG. Baca log penelitian dan kesimpulan ini:
    Log: \n{log_text}
    Hipotesis: "{final_hypothesis}"
    
    TUGAS LO: Tentukan sendiri paradigma antropologi apa yang paling dominan dipakai mahasiswa ini.
    
    ATURAN MUTLAK: Output HANYA berupa objek JSON murni tanpa teks pengantar, markdown, atau backtick.
    
    STRUKTUR JSON WAJIB SEPERTI INI:
    {{
        "Paradigma_Dominan": "Nama paradigma utama",
        "Daftar_Paradigma": [
            {{"nama": "Nama Paradigma A", "skor": 85}}
        ],
        "Overall_Feedback": "Kritik dosen yang tajam."
    }}
    """
    try:
        # BUG FIXED: Menggunakan Keyword Arguments secara eksplisit!
        raw = generate_completion(
            system_prompt=system_prompt, 
            user_prompt="Analisis paradigmanya. Wajib JSON murni.", 
            response_format={"type": "json_object"}, 
            temperature=0.4
        )
        return json.loads(raw)
    except Exception as e:
        return {"Paradigma_Dominan": "Unidentified", "Daftar_Paradigma": [], "Overall_Feedback": f"Error: {e}"}

def generate_meta_analysis(riwayat_data: list) -> dict:
    kompilasi = "\n".join([f"Kasus {i+1}: Hipo: {k[2]} | Dominan saat itu: {k[3]}" for i, k in enumerate(riwayat_data)])
    system_prompt = f"""
    Lo adalah Guru Besar Antropologi. User ini telah menyelesaikan {len(riwayat_data)} simulasi.
    Berikut rekam jejak mereka: 
    {kompilasi}
    
    Tugas lo: Lakukan meta-analisis. Bongkar 'Cara Berpikir Default' mereka secara menyeluruh.
    
    ATURAN MUTLAK: Output HANYA berupa objek JSON murni.
    
    STRUKTUR JSON WAJIB:
    {{
        "Paradigma_Dominan_Default": "Satu paradigma paling melekat di otaknya",
        "Komposisi_Paradigma": [
            {{"nama": "Paradigma X", "skor": 70}},
            {{"nama": "Paradigma Y", "skor": 30}}
        ],
        "Meta_Feedback": "Esai tajam akademis (2 paragraf) membongkar cara pikir mereka secara keseluruhan."
    }}
    """
    try:
        # BUG FIXED: Menggunakan Keyword Arguments secara eksplisit!
        raw = generate_completion(
            system_prompt=system_prompt, 
            user_prompt="Bongkar paradigma defaultnya. Wajib JSON murni.", 
            response_format={"type": "json_object"}, 
            temperature=0.6
        )
        return json.loads(raw)
    except Exception as e:
        return {"Paradigma_Dominan_Default": "Error", "Komposisi_Paradigma": [], "Meta_Feedback": f"Gagal: {e}"}