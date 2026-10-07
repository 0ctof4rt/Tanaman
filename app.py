import streamlit as st
import requests

API_KEY = "2b10b2XlSfeeAceuMozYsl2GO"
API_URL = f"https://my-api.plantnet.org/v2/identify/all?api-key={API_KEY}"

# 1. Tentukan Daftar Target Plantdex (Bisa kamu tambah/ubah nanti)
TARGET_PLANTS = [
    "Monstera deliciosa", 
    "Sansevieria trifasciata", 
    "Aloe vera", 
    "Epipremnum aureum",
    "Bougainvillea spectabilis"
]
NAMA_UMUM = {
    "Monstera deliciosa": "Janda Bolong", 
    "Sansevieria trifasciata": "Lidah Mertua", 
    "Aloe vera": "Lidah Buaya", 
    "Epipremnum aureum": "Sirih Gading",
    "Bougainvillea spectabilis": "Bunga Kertas"
}

# 2. Siapkan "Memori Sementara" untuk percobaan tampilan
if 'koleksi' not in st.session_state:
    st.session_state.koleksi = {}

st.title("🌱 Plantdex Collector")

# 3. Membuat Dua Tab (Halaman)
tab1, tab2 = st.tabs(["🔍 Pindai Tanaman", "📖 Buka Plantdex"])

with tab1:
    st.write("Unggah foto tanaman untuk mendeteksinya dan memasukkannya ke Plantdex!")
    foto = st.file_uploader("Pilih foto dari Galeri/Kamera", type=["jpg", "jpeg", "png"])
    
    if foto is not None:
        st.image(foto, caption="Foto siap dipindai...", width=300)
        
        if st.button("Deteksi & Tangkap!"):
            with st.spinner("Sistem sedang menganalisis foto..."):
                files = {'images': (foto.name, foto.getvalue(), foto.type)}
                data = {'organs': ['auto']}
                response = requests.post(API_URL, files=files, data=data)
                
                if response.status_code == 200:
                    hasil = response.json()
                    if hasil.get('results'):
                        # Ambil nama ilmiah hasil tebakan terbaik
                        spesies = hasil['results'][0]['species']['scientificNameWithoutAuthor']
                        skor = hasil['results'][0]['score'] * 100
                        
                        st.success(f"Ditemukan: **{spesies}** (Kecocokan: {skor:.1f}%)")
                        
                        # Simpan gambar ke dalam koleksi jika tebakan ada di dalam target Plantdex kita
                        # atau kita simpan saja apa pun yang ditemukan
                        st.session_state.koleksi[spesies] = foto.getvalue()
                        st.info("Buka tab '📖 Buka Plantdex' untuk melihat koleksimu yang baru!")
                    else:
                        st.warning("Tanaman tidak dikenali. Coba foto dari sudut lain.")
                else:
                    st.error("Gagal menghubungi server Pl@ntNet.")

with tab2:
    st.header("Buku Koleksi Tanaman")
    st.write("Kumpulkan semua tanaman target di bawah ini!")
    st.divider()
    
    # Menampilkan Plantdex dalam bentuk Grid (3 kolom)
    cols = st.columns(3)
    for i, target in enumerate(TARGET_PLANTS):
        col = cols[i % 3] # Membagi tampilan secara rata ke 3 kolom
        with col:
            # Jika tanaman target sudah ada di dalam koleksi
            if target in st.session_state.koleksi:
                st.image(st.session_state.koleksi[target], use_container_width=True)
                st.success(f"✅ {NAMA_UMUM.get(target, target)}")
                st.caption(f"Spesies: {target}")
            # Jika tanaman target belum ditemukan (Berbayang/Kosong)
            else:
                # Menampilkan kotak abu-abu (emoji kotak sebagai placeholder)
                st.markdown("<div style='text-align: center; padding: 20px; background-color: #333333; border-radius: 10px; color: gray;'><h1>?</h1></div>", unsafe_allow_html=True)
                st.error(f"❌ Belum Ditemukan")
                st.caption(NAMA_UMUM.get(target, target))