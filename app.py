import streamlit as st
import requests

# Ganti dengan API Key Pl@ntNet milikmu
API_KEY = "2b10b2XlSfeeAceuMozYsl2GO"
API_URL = f"https://my-api.plantnet.org/v2/identify/all?api-key={API_KEY}"

st.title("🌱 Pendeteksi Jenis Tanaman Otomatis")
st.write("Unggah foto tanamanmu untuk mengetahui jenis spesiesnya!")

# Tombol untuk upload foto
foto = st.file_uploader("Pilih foto tanaman", type=["jpg", "jpeg", "png"])

if foto is not None:
    # Tampilkan foto yang diunggah
    st.image(foto, caption="Foto Tanamanmu", use_container_width=True)
    
    if st.button("Deteksi Tanaman"):
        with st.spinner("Sedang menganalisis foto..."):
            # Siapkan data gambar untuk dikirim ke API
            files = {
                'images': (foto.name, foto.getvalue(), foto.type)
            }
            # Kita set 'auto' agar AI sendiri yang menebak apakah itu daun, bunga, atau buah
            data = {
                'organs': ['auto'] 
            }
            
            # Mengirim permintaan ke server Pl@ntNet
            response = requests.post(API_URL, files=files, data=data)
            
            if response.status_code == 200:
                hasil = response.json()
                
                # Mengambil tebakan terbaik (urutan pertama)
                if hasil.get('results'):
                    tebakan_terbaik = hasil['results'][0]
                    nama_ilmiah = tebakan_terbaik['species']['scientificNameWithoutAuthor']
                    nama_umum = tebakan_terbaik['species'].get('commonNames', ['Tidak ada nama umum'])[0]
                    skor = tebakan_terbaik['score'] * 100
                    
                    st.success(f"Berhasil dideteksi! Ini kemungkinan besar adalah: **{nama_ilmiah}** ({nama_umum})")
                    st.info(f"Tingkat kecocokan: {skor:.2f}%")
                else:
                    st.warning("Spesies tanaman tidak ditemukan di database.")
            else:
                st.error("Terjadi kesalahan saat menghubungi server Pl@ntNet. Cek kembali API Key-mu.")