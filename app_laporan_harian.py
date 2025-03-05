import streamlit as st
import pandas as pd
import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.ticker import FuncFormatter
from datetime import datetime 

# File untuk menyimpan data
DATA_FILE = "rekap_data.csv"

# Load data jika ada, jika tidak buat DataFrame kosong
def load_data():
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
        # Jika kolom 'Total Akhir' tidak ada, tambahkan kolom tersebut dengan nilai default 0
        if 'Total Akhir' not in df.columns:
            df['Total Akhir'] = 0
        return df
    else:
        # Data kosong tanpa total akhir
        return pd.DataFrame(columns=["Tanggal", "Tipe", "Jumlah", "Keterangan", "Total Akhir"])

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

def export_pdf(df):
    pdf_file = "rekap_harian.pdf"
    document = SimpleDocTemplate(pdf_file, pagesize=letter)
    
    # Menyiapkan data untuk tabel
    data = [["Tanggal", "Tipe", "Jumlah", "Keterangan", "Total Akhir"]]  # Header tabel
    
    # Menambahkan setiap baris data
    for index, row in df.iterrows():
        data.append([row['Tanggal'], row['Tipe'], f"Rp{row['Jumlah']:,.0f}", row['Keterangan'], f"Rp{row['Total Akhir']:,.0f}"])

    # Membuat tabel
    table = Table(data)

    # Menambahkan style pada tabel
    style = TableStyle([
        ('TEXTCOLOR', (0, 0), (-1, 0), (0, 0, 0)),  # Warna teks header
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Penataan teks ke tengah
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  # Gaya font untuk header
        ('BACKGROUND', (0, 0), (-1, 0), (0.6, 0.6, 0.6)),  # Latar belakang header
        ('GRID', (0, 0), (-1, -1), 1, (0, 0, 0)),  # Menambahkan grid
        ('FONTSIZE', (0, 0), (-1, -1), 10),  # Ukuran font untuk semua sel
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),  # Padding untuk header
        ('TOPPADDING', (0, 1), (-1, -1), 5),  # Padding untuk baris data
    ])

    table.setStyle(style)

    # Menyusun dokumen PDF
    elements = [table]
    document.build(elements)

    st.success("PDF berhasil dibuat! Cek file rekap_harian.pdf")

# Set Streamlit page layout to wide mode
st.set_page_config(layout="wide")
# Applying the custom CSS to the title

# Custom CSS for centering and glowing underline effect
st.markdown("""
    <style>
    /* Centering the title */
    .title {
        text-align: center;
        font-size: 40px;
        font-weight: bold;
        color: #f56f81;
        position: relative;
    }

    /* Animation for glowing underline */
    .title::after {
        content: '';
        position: absolute;
        bottom: -5px; /* Distance between text and the underline */
        left: 0;
        width: 100%;
        height: 4px; /* Thickness of the underline */
        background: linear-gradient(90deg, #ff00ff, #00ffff, #ff00ff);
        animation: glowingUnderline 3s ease-in-out infinite; /* Perpanjang durasi animasi */
    }

    /* Keyframes for glowing underline */
    @keyframes glowingUnderline {
        0% { 
            transform: scaleX(0); 
            opacity: 0.5;
        }
        50% { 
            transform: scaleX(1);
            opacity: 1;
        }
        100% { 
            transform: scaleX(0); 
            opacity: 0.5;
        }
    }
    </style>
""", unsafe_allow_html=True)

# Applying the custom CSS to the title
st.markdown('<div class="title">FINANCIAL TRACKER</div>', unsafe_allow_html=True)

data = load_data()

# Jika data kosong, kita mulai dari 0
if data.empty:
    total_akhir = 0
else:
    total_akhir = data["Total Akhir"].iloc[-1]  # Ambil total akhir terakhir


# Hitung total pemasukan dan pengeluaran
total_pemasukan = data[data["Tipe"] == "Pemasukan"]["Jumlah"].sum() if not data.empty else 0
total_pengeluaran = data[data["Tipe"] == "Pengeluaran"]["Jumlah"].sum() if not data.empty else 0

#Menggunakan columns untuk menyusun informasi secara horizontal
colA, colB, colC = st.columns(3)

with colA:
    st.markdown(f"### 💰 Saldo Saat Ini:\n Rp{total_akhir:,.0f}")

with colB:
    st.markdown(f"### 📈 Total Pemasukan:\n Rp{total_pemasukan:,.0f}")

with colC:
    st.markdown(f"### 📉 Total Pengeluaran:\n Rp{total_pengeluaran:,.0f}")

tanggal = st.date_input("Tanggal")
tipe = st.radio("Tipe Transaksi", ["Pemasukan", "Pengeluaran"])
jumlah = st.number_input("Jumlah (Rp)", min_value=0, step=1000)
keterangan = st.text_input("Keterangan")

# Layout with columns
col1, col2, col3, col4 = st.columns([1, 1, 1, 1])

# Add buttons inside each column
with col1:
    if st.button("Tambah Transaksi"):
        if tipe == "Pemasukan":
            total_akhir += jumlah
        elif tipe == "Pengeluaran":
            total_akhir -= jumlah
            
        # Pastikan data yang dimasukkan tidak kosong
        if not keterangan or jumlah == 0:
            st.warning("Keterangan dan jumlah harus diisi dengan benar!")
        else:
            new_data = pd.DataFrame([[tanggal, tipe, jumlah, keterangan, total_akhir]], 
                                    columns=["Tanggal", "Tipe", "Jumlah", "Keterangan", "Total Akhir"])
            data = pd.concat([data, new_data], ignore_index=True)
            save_data(data)
            
            # Setelah transaksi ditambahkan, reset kolom Jumlah dan Keterangan
            jumlah = 0  # Reset jumlah
            keterangan = ""  # Reset keterangan
            
            st.success(f"Transaksi berhasil ditambahkan! Total Akhir sekarang: Rp{total_akhir:,.2f}")

# Tombol untuk mencetak PDF
with col2:
    if st.button("Cetak PDF"):
        st.write("Mencetak PDF...")
        export_pdf(data)

with col3:
    if st.button("Hapus Data Terakhir"):
        if not data.empty:
            data = data.iloc[:-1]
            save_data(data)
            st.success("Data terakhir berhasil dihapus!")
        else:
            st.warning("Tidak ada data untuk dihapus!")

with col4:
    if st.button("Hapus Semua Data"):
        # Menghapus semua data dan mereset total_akhir menjadi 0
        data = pd.DataFrame(columns=["Tanggal", "Tipe", "Jumlah", "Keterangan", "Total Akhir"])
        total_akhir = 0  # Reset total akhir menjadi 0 setelah data dihapus
        save_data(data)
        st.success("Semua data berhasil dihapus! Total Akhir telah direset.")

st.write("## Data Rekap")

# Display data in a container with full width
with st.container():
    st.dataframe(data)



# # Group by date and transaction type, then sum the amounts
data_grouped = data.groupby(['Tanggal', 'Tipe'])['Jumlah'].sum().unstack().fillna(0)

# Cek apakah ada data yang tersedia untuk divisualisasikan
if not data_grouped.empty:
    st.write("## Visualisasi Jumlah Pemasukan dan Pengeluaran per Hari")
    fig, ax = plt.subplots(figsize=(10, 6))
    data_grouped.plot(kind='bar', stacked=False, ax=ax, color=['#b5d2c3', '#f7909e'])

    # Customizing the chart
    ax.set_title("Pemasukan vs Pengeluaran per Hari")
    ax.set_xlabel("Tanggal")
    ax.set_ylabel("Jumlah (Rp)")

    # Formatting the y-axis to show values in thousands
    def thousand_formatter(x, pos):
        return f'Rp{x*1e-3:.0f}K'

    ax.yaxis.set_major_formatter(FuncFormatter(thousand_formatter))

    ax.legend(title="Tipe Transaksi", labels=["Pemasukan", "Pengeluaran"])
    plt.xticks(rotation=45, ha="right")

    # Display the plot
    st.pyplot(fig)
else:
    # Jika tidak ada data, tidak tampilkan grafik apapun
    st.write("## Visualisasi Jumlah Pemasukan dan Pengeluaran per Hari")
    st.write("Tidak ada data untuk ditampilkan.")

st.markdown("""
    <style>
    .cover-container {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 2cm;  /* Set the height to 2cm */
        background-color: #f1f1f1;
        flex-direction: column;
        text-align: center;
        font-family: 'Arial', sans-serif;
        margin: 0;  /* Remove default margins */
    }

    .by-agian {
        font-size: 12px;  /* Adjust font size */
        font-style: italic;
        color: #888;
        margin-top: 5px;  /* Adjust margin to fit inside 2cm height */
    }

    .cover-link {
        font-size: 14px;  /* Adjust font size */
        color: #00f;
        text-decoration: none;
        margin-top: 5px;
    }

    .cover-link:hover {
        text-decoration: underline;
    }
    </style>
    <div class="cover-container">
        <div class="by-agian">Cover By Agian</div>
    </div>
""", unsafe_allow_html=True)
