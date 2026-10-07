import streamlit as st
import requests

API_KEY = "2b10b2XlSfeeAceuMozYsl2GO"
API_URL = f"https://my-api.plantnet.org/v2/identify/all?api-key={API_KEY}"

st.title("🌱 Endless Plantdex")

# 1. Inisialisasi memori penyimpanan (Endless Collection)
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
                        # Ambil data spesies terbaik
                        tebakan_terbaik = hasil['results'][0]
                        spesies = tebakan_terbaik['species']['scientificNameWithoutAuthor']
                        
                        # Coba ambil nama umumnya (jika tersedia di database)
                        nama_umum_list = tebakan_terbaik['species'].get('commonNames', [])
                        nama_umum = nama_umum_list[0] if nama_umum_list else "Spesies Eksotis"
                        
                        skor = tebakan_terbaik['score'] * 100
                        st.success(f"Spesies Ditemukan: **{spesies}** ({skor:.1f}%)")
                        
                        # 2. Logika Game: Cek apakah ini spesies baru
                        if spesies not in st.session_state.koleksi:
                            # Simpan ke dalam buku memori
                            st.session_state.koleksi[spesies] = {
                                'foto': foto.getvalue(),
                                'nama_umum': nama_umum
                            }
                            st.balloons() # Munculkan efek animasi balon!
                            st.info("✨ SPESIES BARU berhasil ditambahkan ke Plantdex!")
                        else:
                            st.info("Kamu sudah memiliki spesies tanaman ini di Plantdex.")
                    else:
                        st.warning("Gagal mengenali tanaman. Coba foto dari sudut yang lebih jelas.")
                else:
                    st.error("Gagal terhubung ke server Pl@ntNet. Cek kembali API Key.")

with tab2:
    st.header("Buku Koleksi Tanaman")
    
    # Menghitung total pencapaian
    total_koleksi = len(st.session_state.koleksi)
    st.write(f"🏆 Total Spesies Ditemukan: **{total_koleksi}**")
    st.divider()
    
    # 3. Menampilkan isi Plantdex secara dinamis
    if total_koleksi == 0:
        st.info("Koleksimu masih kosong. Ayo mulai memotret tanaman di sekitarmu!")
    else:
        # Menampilkan koleksi dalam grid 3 kolom
        cols = st.columns(3)
        for i, (spesies, data_tanaman) in enumerate(st.session_state.koleksi.items()):
            col = cols[i % 3]
            with col:
                st.image(data_tanaman['foto'], use_container_width=True)
                st.success(f"✅ {data_tanaman['nama_umum']}")
                st.caption(f"🧬 {spesies}")