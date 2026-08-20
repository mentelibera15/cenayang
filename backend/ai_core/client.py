import os
from openai import OpenAI
from dotenv import load_dotenv

# Fungsi ini cuma jalan kalau lo nge-run di laptop lokal
load_dotenv()

# Usaha pertama: Tarik dari OS / Environment Variables lokal
api_key = os.getenv("OPENAI_API_KEY")

# Usaha kedua: Jaring Pengaman Khusus Cloud Streamlit
if not api_key:
    try:
        import streamlit as st
        # Secara paksa narik data langsung dari brankas rahasia Streamlit
        api_key = st.secrets["OPENAI_API_KEY"]
    except Exception:
        pass

# Kalau dua-duanya gagal, berarti lo yang salah masukin API Key di dashboard
if not api_key:
    raise ValueError("API Key OpenAI nggak ketemu! Cek file .env lokal atau menu Secrets di Streamlit Cloud!")

# Inisialisasi client
client = OpenAI(api_key=api_key)

def generate_completion(system_prompt: str, user_prompt: str, model: str = "gpt-4o-mini", response_format=None, temperature: float = 0.7) -> str:
    try:
        kwargs = {
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": temperature
        }
        
        if response_format:
            kwargs["response_format"] = response_format

        response = client.chat.completions.create(**kwargs)
        return response.choices[0].message.content

    except Exception as e:
        print(f"Gagal manggil AI, nih errornya: {e}")
        return "{}" if response_format else "Terjadi kesalahan pada sistem AI. Cek koneksi atau limit saldo lo."
