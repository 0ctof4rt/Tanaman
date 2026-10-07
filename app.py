import streamlit as st
import requests
import base64

# Konfigurasi Dasar
API_KEY = "2b10b2XlSfeeAceuMozYsl2GO" 
API_URL = f"https://my-api.plantnet.org/v2/identify/all?api-key={API_KEY}"
GAS_URL = "https://script.google.com/macros/s/AKfycbwHaXZp9EftsYg9J4KyB2hJYzGNI9I3Gkz3ETREGSk22_ouQOYkELXdUelL5oZ2H5Z5/exec" # Paste Web app URL dari Tahap 1 di sini

def simpan_ke_drive(file_bytes, nama_file):
    try:
        # Mengubah foto menjadi teks (base64) agar mudah dikirim lewat internet
        file_b64 = base64.b64encode(file_bytes).decode('utf-8')
        payload = {
            "fileName": nama_file,
            "fileData": file_b64
        }
        # Mengirim ke Jembatan Google Apps Script
        response = requests.post(GAS_URL, data=payload)
        if response.json().get("status") == "sukses":
            return True
        return False
    except Exception as e:
        st.error(f"Gagal mengirim ke Drive: {e}")
        return False

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
                            st.session_state.koleksi[spesies] = {
                                'foto': foto.getvalue(),
                                'nama_umum': nama_umum
                            }
                            
                            # Simpan fisik ke Google Drive melalui Apps Script
                            nama_file_drive = f"{spesies} - {nama_umum}.jpg"
                            berhasil = simpan_ke_drive(foto.getvalue(), nama_file_drive)
                            
                            if berhasil:
                                st.balloons()
                                st.info("✨ SPESIES BARU ditambahkan ke Plantdex & Google Drive!")
                            else:
                                st.warning("Spesies masuk ke Plantdex, tapi gagal disimpan ke Drive.")
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