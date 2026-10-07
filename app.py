import streamlit as st
import requests

API_KEY = "2b10b2XlSfeeAceuMozYsl2GO"
API_URL = f"https://my-api.plantnet.org/v2/identify/all?api-key={API_KEY}"

import streamlit as st
import requests
import json
import io
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload

# Konfigurasi Dasar
API_KEY = "2b10b2XlSfeeAceuMozYsl2GO"
API_URL = f"https://my-api.plantnet.org/v2/identify/all?api-key={API_KEY}"
FOLDER_ID = "1vIfPjGqHCEinbBRR_HEkolAvIUoKbUdH" # Folder ID Google Drive-mu

# Menghubungkan ke Akun Robot Google Drive
@st.cache_resource
def get_drive_service():
    creds_json = json.loads(st.secrets["GCP_CREDENTIALS"])
    credentials = service_account.Credentials.from_service_account_info(creds_json)
    return build('drive', 'v3', credentials=credentials)

drive_service = get_drive_service()

def simpan_ke_drive(file_bytes, nama_file):
    media = MediaIoBaseUpload(io.BytesIO(file_bytes), mimetype='image/jpeg', resumable=True)
    file_metadata = {'name': nama_file, 'parents': [FOLDER_ID]}
    file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    return file.get('id')

st.title("🌱 Endless Plantdex")

if 'koleksi' not in st.session_state:
    st.session_state.koleksi = {}

tab1, tab2 = st.tabs(["🔍 Pindai Tanaman", "📖 Buku Koleksi"])

with tab1:
    st.write("Temukan spesies baru di sekitarmu dan tambahkan ke koleksimu!")
    foto = st.file_uploader("Unggah foto daun, bunga, atau buah", type=["jpg", "jpeg", "png"])
    
    if foto is not None:
        st.image(foto, caption="Menunggu pemindaian...", width=300)
        
        if st.button("Deteksi & Tangkap!"):
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
                        
                        st.success(f"Spesies Ditemukan: **{spesies}** ({skor:.1f}%)")
                        
                        if spesies not in st.session_state.koleksi:
                            # 1. Simpan ke memori web
                            st.session_state.koleksi[spesies] = {
                                'foto': foto.getvalue(),
                                'nama_umum': nama_umum
                            }
                            # 2. Simpan foto fisik ke Google Drive
                            nama_file_drive = f"{spesies} - {nama_umum}.jpg"
                            simpan_ke_drive(foto.getvalue(), nama_file_drive)
                            
                            st.balloons()
                            st.info("✨ SPESIES BARU ditambahkan ke Plantdex & Google Drive!")
                        else:
                            st.info("Kamu sudah memiliki spesies tanaman ini di Plantdex.")
                    else:
                        st.warning("Gagal mengenali tanaman.")
                else:
                    st.error("Gagal terhubung ke server Pl@ntNet.")

with tab2:
    st.header("Buku Koleksi Tanaman")
    total_koleksi = len(st.session_state.koleksi)
    st.write(f"🏆 Total Spesies Ditemukan: **{total_koleksi}**")
    st.divider()
    
    if total_koleksi == 0:
        st.info("Koleksimu masih kosong. Ayo mulai memotret tanaman di sekitarmu!")
    else:
        cols = st.columns(3)
        for i, (spesies, data_tanaman) in enumerate(st.session_state.koleksi.items()):
            col = cols[i % 3]
            with col:
                st.image(data_tanaman['foto'], use_container_width=True)
                st.success(f"✅ {data_tanaman['nama_umum']}")
                st.caption(f"🧬 {spesies}")