import json
from backend.ai_core.client import generate_completion

def explore_location(user_action: str, case_data: dict) -> dict:
    setting = case_data.get("setting", "")
    hidden_factors = case_data.get("hidden_factors", [])
    
    system_prompt = f"""
    Lo adalah Informan dan Lingkungan dalam simulasi etnografi.
    Konteks: {setting}. Fakta di balik layar: {hidden_factors}.
    Tindakan User: "{user_action}"
    
    ATURAN MUTLAK:
    1. Berikan respons yang SANGAT LUWES, organik, dan seperti manusia nyata.
    2. Tentukan apakah dari tindakan user ini mereka berhasil menemukan secercah petunjuk penting atau celah rahasia terkait fakta tersembunyi.
    3. Output HANYA berupa objek JSON murni tanpa teks pengantar, markdown, atau backtick di luar JSON.
    
    STRUKTUR JSON WAJIB SEPERTI INI:
    {{
        "narasi": "Teks cerita interaksi atau respons lapangan (1-2 paragraf)",
        "is_clue": true atau false
    }}
    """
    
    try:
        raw_response = generate_completion(
            system_prompt=system_prompt,
            user_prompt="Gimana reaksi lapangan? Wajib format JSON murni.",
            response_format={"type": "json_object"},
            temperature=0.8
        )
        return json.loads(raw_response)
    except Exception as e:
        print(f"Error parsing JSON evidence: {e}")
        return {
            "narasi": "Sistem halusinasi. Warga menatapmu curiga dan mengusirmu karena situasinya terlalu abstrak.",
            "is_clue": False
        }