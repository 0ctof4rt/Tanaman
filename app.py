import streamlit as st
import requests
import base64
from datetime import datetime

# 1. Konfigurasi Halaman (HARUS DI BARIS PALING ATAS setelah import)
st.set_page_config(
    page_title="Jurnal Plantdex",
    page_icon="🌿",
    layout="centered", # Bisa diubah ke "wide" kalau ingin lebar penuh
    initial_sidebar_state="expanded"
)

# 2. CSS Khusus untuk menyembunyikan menu bawaan Streamlit dan mempercantik tombol
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            /* Mempercantik tampilan font dan jarak */
            .css-18e3th9 {
                padding-top: 2rem;
            }
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# --- (LANJUTKAN DENGAN KODE API_KEY_KAMU DAN SETERUSNYA DI SINI) ---

# Konfigurasi Dasar
API_KEY = "2b10b2XlSfeeAceuMozYsl2GO" 
API_URL = f"https://my-api.plantnet.org/v2/identify/all?api-key={API_KEY}"
GAS_URL = "https://script.google.com/macros/s/AKfycbwHaXZp9EftsYg9J4KyB2hJYzGNI9I3Gkz3ETREGSk22_ouQOYkELXdUelL5oZ2H5Z5/exec" # Paste Web app URL dari Tahap 1 di sini

def simpan_ke_drive(file_bytes, nama_file):
    try:
        file_b64 = base64.b64encode(file_bytes).decode('utf-8')
        payload = {
            "fileName": nama_file,
            "fileData": file_b64
        }
        response = requests.post(GAS_URL, data=payload)
        if response.json().get("status") == "sukses":
            return True
        return False
    except Exception as e:
        st.error(f"Gagal mengirim ke Drive: {e}")
        return False

st.title("🌱 Jurnal Pemantauan Tanaman")

# Struktur memori diubah untuk menyimpan "list" (daftar) foto per spesies
if 'koleksi' not in st.session_state:
    st.session_state.koleksi = {}

tab1, tab2 = st.tabs(["🔍 Pindai Tanaman", "📖 Buku Jurnal"])

with tab1:
    st.write("Pantau pertumbuhan tanamanmu atau catat penemuan baru!")
    foto = st.file_uploader("Unggah foto daun, bunga, atau buah", type=["jpg", "jpeg", "png"])
    
    if foto is not None:
        st.image(foto, caption="Menunggu pemindaian...", width=300)
        
        if st.button("Deteksi & Catat!"):
            with st.spinner("Menganalisis DNA tanaman..."):
                files = {'images': (foto.name, foto.getvalue(), foto.type)}
                data = {'organs': ['auto']}
                
                response = requests.post(API_URL, files=files, data=data)
                
                if response.status_code == 200:
                    hasil = response.json()
                    if hasil.get('results'):
                        tebakan_terbaik = hasil['results'][0]
                        spesies = tebakan_terbaik['species']['scientificNameWithoutAuthor']
                        nama_umum = tebakan_terbaik['species'].get('commonNames', ["Spesies Eksotis"])[0]
                        skor = tebakan_terbaik['score'] * 100
                        
                        st.success(f"Dikenali sebagai: **{spesies}** ({skor:.1f}%)")
                        
                        # Membuat stempel waktu agar nama file di Drive selalu unik
                        waktu_catat = datetime.now().strftime("%Y%m%d_%H%M%S")
                        nama_file_drive = f"{spesies} - {waktu_catat}.jpg"
                        
                        is_spesies_baru = False
                        
                        # Logika Jurnal: Buat album baru ATAU tambah ke album lama
                        if spesies not in st.session_state.koleksi:
                            st.session_state.koleksi[spesies] = {
                                'nama_umum': nama_umum,
                                'fotos': [foto.getvalue()] # Menyimpan dalam bentuk album (list)
                            }
                            is_spesies_baru = True
                        else:
                            st.session_state.koleksi[spesies]['fotos'].append(foto.getvalue())
                        
                        # Simpan ke Google Drive
                        berhasil = simpan_ke_drive(foto.getvalue(), nama_file_drive)
                        
                        if berhasil:
                            if is_spesies_baru:
                                st.balloons()
                                st.info("✨ SPESIES BARU berhasil ditambahkan ke Jurnal & Drive!")
                            else:
                                st.success("📸 Catatan foto baru berhasil ditambahkan ke album spesies ini!")
                        else:
                            st.warning("Tercatat di web, tapi gagal dikirim ke Drive.")
                    else:
                        st.warning("Gagal mengenali tanaman.")
                else:
                    st.error("Gagal terhubung ke server Pl@ntNet.")

with tab2:
    st.header("Jurnal Koleksi Tanaman")
    total_spesies = len(st.session_state.koleksi)
    st.write(f"🏆 Total Spesies Dipantau: **{total_spesies}**")
    st.divider()
    
    if total_spesies == 0:
        st.info("Jurnalmu masih kosong. Ayo mulai potret tanaman di sekitarmu!")
    else:
        # Menampilkan album menggunakan sistem "Expander" (Menu lipat) agar halamannya rapi
        for spesies, data_tanaman in st.session_state.koleksi.items():
            jumlah_foto = len(data_tanaman['fotos'])
            
            with st.expander(f"🌿 {data_tanaman['nama_umum']} ({jumlah_foto} Catatan)"):
                st.caption(f"Nama Ilmiah: {spesies}")
                
                # Menampilkan rentetan foto di dalam album tersebut (3 kolom)
                cols = st.columns(3)
                for idx, foto_bytes in enumerate(data_tanaman['fotos']):
                    col_index = idx % 3
                    with cols[col_index]:
                        st.image(foto_bytes, use_container_width=True, caption=f"Catatan #{idx+1}")