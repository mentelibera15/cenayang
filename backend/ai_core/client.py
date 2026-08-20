import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables dari file .env
load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("API Key OpenAI nggak ketemu! Lo udah isi file .env belum? Jangan males baca instruksi.")

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