import json
import random
from backend.ai_core.client import generate_completion

def generate_new_case(domain="random"):
    themes = [
        "Komersialisasi Artefak Suci (Pengrajin lokal memproduksi massal duplikat benda ritual dari tanah liat untuk turis, memicu kemarahan tetua adat namun di sisi lain menghidupi ekonomi desa)",
        "Sinkretisme dan Hegemoni (Perebutan posisi juru kunci situs keramat antara keturunan asli dan elit politik yang menggunakan kerangka agama dominan untuk memonopoli donasi peziarah)",
        "Ekologi Politik & Mitos (Perusahaan tambang menggunakan narasi kutukan roh hutan untuk menakuti warga agar pindah, sementara warga sipil mencoba membongkar konspirasinya)",
        "Pergeseran Kekerabatan Berdarah (Konflik hak waris tanah yang berujung kekerasan karena benturan antara hukum negara yang patriarkis dan tradisi lokal matrilineal)"
    ]
    
    chosen_theme = random.choice(themes)

    system_prompt = f"""
    Lo adalah Sutradara Kasus Etnografi untuk simulasi CENAYANG.
    TEMA KASUS: {chosen_theme}
    
    ATURAN MUTLAK:
    1. Hasilkan kasus yang terasa seperti catatan lapangan antropologis nyata. Penuh intrik sosial, perebutan kuasa, dan benturan makna budaya.
    2. Haram pakai setting corporate/perusahaan/kantor.
    3. Output HANYA berupa objek JSON murni tanpa teks pengantar, markdown, atau backtick di luar JSON.
    
    STRUKTUR JSON WAJIB SEPERTI INI:
    {{
        "title": "Judul Kasus Etnografis",
        "setting": "Deskripsi atmosfer sosial dan lokasi yang sangat mendetail",
        "visible_problem": "Masalah di permukaan yang dilihat warga awam",
        "hidden_factors": ["Struktur kuasa tersembunyi", "Makna budaya yang dimanipulasi"],
        "actors": [
            {{ "name": "Nama tokoh", "role": "Peran sosial", "bias": "Fanatisme/cara pandangnya" }}
        ]
    }}
    """
    
    try:
        raw_response = generate_completion(
            system_prompt=system_prompt,
            user_prompt="Bikin kasus antropologis baru. Wajib format JSON murni.",
            response_format={"type": "json_object"},
            temperature=0.7
        )
        return True, json.loads(raw_response)
    except Exception as e:
        print(f"Kasus gagal dibikin, error JSON parsing: {e}")
        return False, None