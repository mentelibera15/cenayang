import matplotlib.pyplot as plt
import os

def buat_grafik_paradigma(daftar_paradigma: list, username: str) -> str:
    """
    Tukang gambar grafik. Menerima array JSON dari AI, mengubahnya jadi Bar Chart,
    lalu menyimpannya sebagai file gambar sementara.
    """
    if not daftar_paradigma:
        return None

    # Ekstraksi data dari JSON
    labels = [item.get("nama", "Unknown") for item in daftar_paradigma]
    scores = [item.get("skor", 0) for item in daftar_paradigma]

    # Mengatur kanvas (ukuran dan warna)
    plt.figure(figsize=(7, 4), facecolor='#2b2b2b')
    ax = plt.axes()
    ax.set_facecolor('#2b2b2b')
    
    # Kustomisasi warna teks biar nggak nyaru sama background gelap UI CustomTkinter
    ax.tick_params(colors='white')
    ax.xaxis.label.set_color('white')
    ax.title.set_color('white')
    
    # Menggambar grafik batang horizontal
    warna_bar = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']
    plt.barh(labels, scores, color=warna_bar[:len(labels)])
    
    plt.xlabel('Persentase Dominasi (%)')
    plt.title(f'Komposisi Cara Berpikir: {username.upper()}')
    plt.xlim(0, 100)
    plt.tight_layout()

    # Menyimpan ke file sementara di root folder
    jalur_output = os.path.join(os.path.dirname(__file__), '..', 'temp_chart.png')
    plt.savefig(jalur_output, dpi=100)
    plt.close() # Tutup kanvas biar memori laptop lo nggak jebol
    
    return jalur_output