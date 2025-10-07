import streamlit as st
import pandas as pd
import os
from datetime import datetime
import json
import io
import os 
from dotenv import load_dotenv
import random


load_dotenv()

# ================================
# KONFIGURASI
# ================================

# Password untuk mengakses aplikasi
APP_PASSWORD = st.secrets["APP_PASSWORD"]  # Ganti dengan password yang diinginkan

# File untuk menyimpan data
DATA_FILE = st.secrets["DATA_FILE"]
BACKUP_FILE = st.secrets["BACKUP_FILE"]

# Google Sheets URL untuk sync (optional)
GOOGLE_SHEET_URL = st.secrets["GOOGLE_SHEET_URL"]  # Ganti dengan URL sheet Anda

# ================================
# FUNGSI AUTHENTICATION
# ================================

def check_password():
    """Cek apakah user sudah login atau belum"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    
    if not st.session_state.authenticated:
        st.title("🔐 Login - Inventory Management System")
        st.markdown("---")
        
        with st.form("login_form"):
            password = st.text_input("Password:", type="password", placeholder="Masukkan password")
            submit_button = st.form_submit_button("Login")
            
            if submit_button:
                if password == APP_PASSWORD:
                    st.session_state.authenticated = True
                    st.success("✅ Login berhasil!")
                    st.rerun()
                else:
                    st.error("❌ Password salah!")
        
        st.info("💡 **Petunjuk:** Masukkan password untuk mengakses sistem inventory")
        return False
    
    return True

def logout():
    """Logout user"""
    st.session_state.authenticated = False
    st.rerun()

# ================================
# FUNGSI DATA MANAGEMENT
# ================================

def init_data_file():
    """Inisialisasi file data jika belum ada"""
    if not os.path.exists(DATA_FILE):
        # Buat DataFrame kosong dengan struktur yang benar
        columns = [
            "ID", "Nama Barang", "Kategori", "Stok", 
            "Harga Satuan", "Lokasi", "Tanggal Ditambah", 
            "Tanggal Update", "Keterangan"
        ]
        df = pd.DataFrame(columns=columns)
        df.to_csv(DATA_FILE, index=False)
        
        # # Buat juga sample data
        # sample_data = {
        #     "ID": [1, 2, 3],
        #     "Nama Barang": ["Laptop Dell Inspiron", "Mouse Wireless Logitech", "Meja Kantor Kayu"],
        #     "Kategori": ["Elektronik", "Elektronik", "Furniture"], 
        #     "Stok": [5, 25, 10],
        #     "Harga Satuan": [8500000, 350000, 1200000],
        #     "Lokasi": ["Gudang A - Rak 1", "Gudang A - Rak 2", "Gudang B - Area 1"],
        #     "Tanggal Ditambah": ["2024-10-06 18:00:00", "2024-10-06 18:05:00", "2024-10-06 18:10:00"],
        #     "Tanggal Update": ["2024-10-06 18:00:00", "2024-10-06 18:05:00", "2024-10-06 18:10:00"],
        #     "Keterangan": ["Laptop untuk kantor", "Mouse wireless dengan battery tahan lama", "Meja kantor ukuran 120x60 cm"]
        # }
        # sample_df = pd.DataFrame(sample_data)
        # sample_df.to_csv(DATA_FILE, index=False)
        
        return df
    return None

def load_data():
    """Load data dari CSV file"""
    try:
        if os.path.exists(DATA_FILE):
            df = pd.read_csv(DATA_FILE)
            # Pastikan kolom numerik dalam format yang benar
            if 'Stok' in df.columns:
                df['Stok'] = pd.to_numeric(df['Stok'], errors='coerce').fillna(0)
            if 'Harga Satuan' in df.columns:
                df['Harga Satuan'] = pd.to_numeric(df['Harga Satuan'], errors='coerce').fillna(0)
            return df
        else:
            return init_data_file()
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return pd.DataFrame()

def save_data(df):
    """Simpan data ke CSV file"""
    try:
        # Backup data lama
        if os.path.exists(DATA_FILE):
            df_backup = pd.read_csv(DATA_FILE)
            df_backup.to_csv(BACKUP_FILE, index=False)
        
        # Simpan data baru
        df.to_csv(DATA_FILE, index=False)
        return True
    except Exception as e:
        st.error(f"Error saving data: {str(e)}")
        return False

def get_next_id(df):
    """Generate ID baru"""
    if len(df) == 0:
        return 1
    return int(df['ID'].max()) + 1

def add_item(item_data):
    """Tambah item baru"""
    try:
        df = load_data()
        new_id = get_next_id(df)
        
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        new_row = {
            "ID": new_id,
            "Nama Barang": item_data['nama'],
            "Kategori": item_data['kategori'],
            "Stok": item_data['stok'],
            "Harga Satuan": item_data['harga'],
            "Lokasi": item_data['lokasi'],
            "Tanggal Ditambah": now,
            "Tanggal Update": now,
            "Keterangan": item_data['keterangan']
        }
        
        # Tambah row baru
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        
        # Simpan data
        if save_data(df):
            return True, new_id
        else:
            return False, None
            
    except Exception as e:
        st.error(f"Error adding item: {str(e)}")
        return False, None

def update_item(item_id, item_data):
    """Update item yang sudah ada"""
    try:
        df = load_data()
        
        # Find row dengan ID yang sesuai
        row_index = df[df['ID'] == item_id].index
        
        if len(row_index) == 0:
            return False
        
        # Update data
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        idx = row_index[0]
        
        df.loc[idx, 'Nama Barang'] = item_data['nama']
        df.loc[idx, 'Kategori'] = item_data['kategori']
        df.loc[idx, 'Stok'] = item_data['stok']
        df.loc[idx, 'Harga Satuan'] = item_data['harga']
        df.loc[idx, 'Lokasi'] = item_data['lokasi']
        df.loc[idx, 'Tanggal Update'] = now
        df.loc[idx, 'Keterangan'] = item_data['keterangan']
        
        # Simpan data
        return save_data(df)
        
    except Exception as e:
        st.error(f"Error updating item: {str(e)}")
        return False

def delete_item(item_id):
    """Hapus item"""
    try:
        df = load_data()
        
        # Filter out item dengan ID yang sesuai
        df_filtered = df[df['ID'] != item_id]
        
        if len(df_filtered) == len(df):
            return False  # Item tidak ditemukan
        
        # Simpan data
        return save_data(df_filtered)
        
    except Exception as e:
        st.error(f"Error deleting item: {str(e)}")
        return False

# ================================
# FUNGSI EXPORT/IMPORT
# ================================

def export_to_csv():
    """Export data ke CSV untuk download"""
    try:
        df = load_data()
        return df.to_csv(index=False)
    except Exception as e:
        st.error(f"Error exporting data: {str(e)}")
        return None

def export_to_excel():
    """Export data ke Excel untuk download"""
    try:
        df = load_data()
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Inventory', index=False)
        return output.getvalue()
    except Exception as e:
        st.error(f"Error exporting to Excel: {str(e)}")
        return None

def import_from_csv(uploaded_file):
    """Import data dari CSV file"""
    try:
        df = pd.read_csv(uploaded_file)
        
        # Validasi kolom yang diperlukan
        required_columns = ["ID", "Nama Barang", "Kategori", "Stok", "Harga Satuan"]
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            st.error(f"Missing columns: {missing_columns}")
            return False
        
        # Pastikan kolom numerik
        df['Stok'] = pd.to_numeric(df['Stok'], errors='coerce').fillna(0)
        df['Harga Satuan'] = pd.to_numeric(df['Harga Satuan'], errors='coerce').fillna(0)
        
        # Pastikan semua kolom ada
        all_columns = [
            "ID", "Nama Barang", "Kategori", "Stok", 
            "Harga Satuan", "Lokasi", "Tanggal Ditambah", 
            "Tanggal Update", "Keterangan"
        ]
        
        for col in all_columns:
            if col not in df.columns:
                if col in ["Tanggal Ditambah", "Tanggal Update"]:
                    df[col] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                else:
                    df[col] = ""
        
        # Reorder columns
        df = df[all_columns]
        
        # Simpan data
        return save_data(df)
        
    except Exception as e:
        st.error(f"Error importing data: {str(e)}")
        return False

# ================================
# MAIN APPLICATION
# ================================

def main():
    """Aplikasi utama"""
    
    # Initialize data file
    init_data_file()
    
    # Cek authentication
    if not check_password():
        return
    
    # Header aplikasi
    st.title("📦 Inventory Management System")
    # st.markdown("### Sistem Manajemen Inventory - Full CRUD + Local Storage")
    
    # Sidebar untuk logout dan info
    with st.sidebar:
        st.markdown("### Menu")
        if st.button("🚪 Logout", width='stretch'):
            logout()
        
        st.markdown("---")
        st.markdown("**Status:** ✅ Ready")
        st.markdown("**Storage:** 📁 Local CSV File")
        st.markdown("**Mode:** 🔄 Full CRUD")
        
        # Data info
        df = load_data()
        st.markdown("---")
        st.markdown("### 📊 Data Info")
        st.write(f"**Total Items:** {len(df)}")
        if os.path.exists(DATA_FILE):
            file_size = os.path.getsize(DATA_FILE)
            st.write(f"**File Size:** {file_size} bytes")
            
        # Export section
        st.markdown("---")
        st.markdown("### 📤 Export Data")
        
        col1, col2 = st.columns(2)
        with col1:
            csv_data = export_to_csv()
            if csv_data:
                st.download_button(
                    label="📄 CSV",
                    data=csv_data,
                    file_name=f"inventory_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    width='stretch'
                )
        
        with col2:
            excel_data = export_to_excel()
            if excel_data:
                st.download_button(
                    label="📊 Excel",
                    data=excel_data,
                    file_name=f"inventory_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    width='stretch'
                )
    
    # Tab menu
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📋 Lihat Inventory", "➕ Tambah Barang", "✏️ Edit Barang", "🗑️ Hapus Barang", "📊 Import/Export"])
    
    # Tab 1: Lihat Inventory
    with tab1:
        st.header("📋 Daftar Inventory")
        
        # Load dan tampilkan data
        df = load_data()
        
        if len(df) > 0:
            # Filter dan search
            col1, col2 = st.columns(2)
            
            with col1:
                search_term = st.text_input("🔍 Cari barang:", placeholder="Masukkan nama barang...")
            
            with col2:
                categories = ['Semua'] + list(df['Kategori'].unique()) if 'Kategori' in df.columns else ['Semua']
                selected_category = st.selectbox("📂 Filter kategori:", categories)
            
            # Apply filters
            filtered_df = df.copy()
            
            if search_term:
                filtered_df = filtered_df[
                    filtered_df['Nama Barang'].str.contains(search_term, case=False, na=False)
                ]
            
            if selected_category != 'Semua':
                filtered_df = filtered_df[filtered_df['Kategori'] == selected_category]
            
            # Tampilkan statistik
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Item", len(df))
            
            with col2:
                total_stok = df['Stok'].sum() if 'Stok' in df.columns else 0
                st.metric("Total Stok", f"{total_stok:,.0f}")
            
            with col3:
                stok_rendah = len(df[df['Stok'] <= 10]) if 'Stok' in df.columns else 0
                st.metric("Stok Rendah (≤10)", stok_rendah, delta=-stok_rendah if stok_rendah > 0 else None)
            
            with col4:
                if 'Harga Satuan' in df.columns and 'Stok' in df.columns:
                    total_nilai = (df['Harga Satuan'] * df['Stok']).sum()
                    st.metric("Total Nilai", f"Rp {total_nilai:,.0f}")
            
            st.markdown("---")
            
            # Tampilkan tabel
            if len(filtered_df) > 0:
                st.dataframe(
                    filtered_df,
                    width='stretch',
                    hide_index=True,
                    column_config={
                        "ID": st.column_config.NumberColumn("ID", width="small"),
                        "Harga Satuan": st.column_config.NumberColumn(
                            "Harga Satuan",
                            format="Rp %.0f"
                        ),
                        "Stok": st.column_config.NumberColumn("Stok"),
                    }
                )
            else:
                st.info("📝 Tidak ada data yang sesuai dengan filter.")
        
        else:
            st.info("📝 Belum ada data inventory. Silakan tambah barang baru di tab 'Tambah Barang'.")
    
    # Tab 2: Tambah Barang
    with tab2:
        st.header("➕ Tambah Barang Baru")
        
        with st.form("add_item_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                nama = st.text_input("Nama Barang *", placeholder="Contoh: Laptop Dell")
                kategori = st.selectbox(
                    "Kategori *", 
                    ["Elektronik", "Furniture", "Kabel", "Keyboard", "Mouse", "Lainnya"]
                )
                stok = st.number_input("Stok *", min_value=0, step=1, value=0)  
            
            with col2:
                harga = st.number_input("Harga Satuan (Rp) *", min_value=0, step=1000, value=0)
                lokasi = st.text_input("Lokasi", placeholder="Contoh: Gudang A - Rak 1")
                keterangan = st.text_area("Keterangan", placeholder="Deskripsi atau catatan tambahan")
            
            submitted = st.form_submit_button("➕ Tambah Barang", width='stretch')
            
            if submitted:
                if nama and kategori and stok >= 0 and harga >= 0:
                    item_data = {
                        'nama': nama,
                        'kategori': kategori,
                        'stok': stok,
                        'harga': harga,
                        'lokasi': lokasi,
                        'keterangan': keterangan
                    }
                    
                    with st.spinner('Menambahkan barang...'):
                        success, new_id = add_item(item_data)
                        if success:
                            st.success(f"✅ Barang '{nama}' berhasil ditambahkan dengan ID {new_id}!")
                            st.balloons()
                            st.rerun()
                        else:
                            st.error("❌ Gagal menambahkan barang.")
                else:
                    st.error("❌ Mohon isi semua field yang wajib (*)")
    
    # Tab 3: Edit Barang
    with tab3:
        st.header("✏️ Edit Barang")
        
        df = load_data()
        
        if len(df) > 0:
            # Select item to edit
            item_options = []
            for _, row in df.iterrows():
                item_options.append(f"{int(row['ID'])} - {row['Nama Barang']}")
            
            selected_item = st.selectbox("Pilih barang yang akan diedit:", ["Pilih barang..."] + item_options)
            
            if selected_item != "Pilih barang...":
                item_id = int(selected_item.split(" - ")[0])
                selected_row = df[df['ID'] == item_id].iloc[0]
                
                st.markdown(f"**Edit barang:** {selected_row['Nama Barang']}")
                
                with st.form("edit_item_form"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        nama = st.text_input("Nama Barang *", value=selected_row['Nama Barang'])
                        kategori = st.selectbox(
                            "Kategori *", 
                            ["Elektronik", "Furniture", "Kabel", "Keyboard", "Mouse", "Lainnya"],
                            index=["Elektronik", "Furniture", "Kabel", "Keyboard", "Mouse", "Lainnya"].index(selected_row['Kategori']) if selected_row['Kategori'] in ["Elektronik", "Furniture", "Kabel", "Keyboard", "Mouse", "Lainnya"] else 0
                        )
                        stok = st.number_input("Stok *", min_value=0, step=1, value=int(selected_row['Stok']))
                    
                    with col2:
                        harga = st.number_input("Harga Satuan (Rp) *", min_value=0, step=1000, value=int(selected_row['Harga Satuan']))
                        lokasi = st.text_input("Lokasi", value=selected_row['Lokasi'] if pd.notna(selected_row['Lokasi']) else "")
                        keterangan = st.text_area("Keterangan", value=selected_row['Keterangan'] if pd.notna(selected_row['Keterangan']) else "")
                    
                    submitted = st.form_submit_button("💾 Simpan Perubahan", width='stretch')
                    
                    if submitted:
                        if nama and kategori and stok >= 0 and harga >= 0:
                            item_data = {
                                'nama': nama,
                                'kategori': kategori,
                                'stok': stok,
                                'harga': harga,
                                'lokasi': lokasi,
                                'keterangan': keterangan
                            }
                            
                            with st.spinner('Menyimpan perubahan...'):
                                if update_item(item_id, item_data):
                                    st.success(f"✅ Barang '{nama}' berhasil diperbarui!")
                                    st.rerun()
                                else:
                                    st.error("❌ Gagal memperbarui barang.")
                        else:
                            st.error("❌ Mohon isi semua field yang wajib (*)")
        else:
            st.info("📝 Belum ada data untuk diedit.")
    
    # Tab 4: Hapus Barang
    with tab4:
        st.header("🗑️ Hapus Barang")
        
        df = load_data()
        
        if len(df) > 0:
            # Select item to delete
            item_options = []
            for _, row in df.iterrows():
                item_options.append(f"{int(row['ID'])} - {row['Nama Barang']} (Stok: {int(row['Stok'])})")
            
            selected_item = st.selectbox("Pilih barang yang akan dihapus:", ["Pilih barang..."] + item_options)
            
            if selected_item != "Pilih barang...":
                item_id = int(selected_item.split(" - ")[0])
                selected_row = df[df['ID'] == item_id].iloc[0]
                
                st.markdown("### ⚠️ Konfirmasi Penghapusan")
                st.warning(f"Anda akan menghapus: **{selected_row['Nama Barang']}**")
                
                # Show item details
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**ID:** {int(selected_row['ID'])}")
                    st.write(f"**Kategori:** {selected_row['Kategori']}")
                    st.write(f"**Stok:** {int(selected_row['Stok'])}")
                
                with col2:
                    st.write(f"**Harga:** Rp {selected_row['Harga Satuan']:,.0f}")
                    st.write(f"**Lokasi:** {selected_row['Lokasi'] if pd.notna(selected_row['Lokasi']) else '-'}")
                
                st.markdown("---")
                
                # Confirmation
                confirm = st.checkbox("✅ Saya yakin ingin menghapus barang ini")
                
                if confirm:
                    if st.button("🗑️ Hapus Barang", type="secondary", width='stretch'):
                        with st.spinner('Menghapus barang...'):
                            if delete_item(item_id):
                                st.success(f"✅ Barang '{selected_row['Nama Barang']}' berhasil dihapus!")
                                st.rerun()
                            else:
                                st.error("❌ Gagal menghapus barang.")
        else:
            st.info("📝 Belum ada data untuk dihapus.")
    
    # Tab 5: Import/Export
    with tab5:
        st.header("📊 Import/Export Data")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📤 Export Data")
            st.markdown("Download data inventory dalam berbagai format:")
            
            # CSV Export
            csv_data = export_to_csv()
            if csv_data:
                st.download_button(
                    label="📄 Download CSV",
                    data=csv_data,
                    file_name=f"inventory_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    width='stretch'
                )
            
            # Excel Export  
            excel_data = export_to_excel()
            if excel_data:
                st.download_button(
                    label="📊 Download Excel",
                    data=excel_data,
                    file_name=f"inventory_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    width='stretch'
                )
            
            # Google Sheets link
            st.markdown("---")
            st.markdown("**📋 Google Sheets Integration:**")
            st.info("""
            1. Download CSV dari tombol di atas
            2. Buka Google Sheets
            3. File → Import → Upload CSV
            4. Pilih "Replace spreadsheet"
            5. Share spreadsheet dengan tim
            """)
            
            if GOOGLE_SHEET_URL != "https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID/edit":
                st.markdown(f"[🔗 Buka Google Sheets]({GOOGLE_SHEET_URL})")
        
        with col2:
            st.subheader("📥 Import Data")
            st.markdown("Upload file CSV untuk mengganti data inventory:")
            
            uploaded_file = st.file_uploader("Pilih file CSV", type=['csv'])
            
            if uploaded_file is not None:
                st.markdown("**Preview data yang akan diimport:**")
                
                # Preview uploaded data
                try:
                    preview_df = pd.read_csv(uploaded_file)
                    st.dataframe(preview_df.head(), width='stretch')
                    
                    st.markdown(f"**Total rows:** {len(preview_df)}")
                    st.markdown(f"**Columns:** {', '.join(preview_df.columns)}")
                    
                    # Reset file pointer
                    uploaded_file.seek(0)
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if st.button("✅ Import Data", width='stretch'):
                            with st.spinner('Importing data...'):
                                if import_from_csv(uploaded_file):
                                    st.success("✅ Data berhasil diimport!")
                                    st.rerun()
                                else:
                                    st.error("❌ Gagal import data.")
                    
                    with col2:
                        if st.button("❌ Batal", width='stretch'):
                            st.rerun()
                            
                except Exception as e:
                    st.error(f"Error reading file: {str(e)}")
            
            st.markdown("---")
            st.markdown("**📋 Format CSV yang diperlukan:**")
            st.code("""
ID,Nama Barang,Kategori,Stok,Harga Satuan,Lokasi,Tanggal Ditambah,Tanggal Update,Keterangan
1,Laptop Dell,Elektronik,5,8500000,Labor 1.3 Thehok,2024-10-06 18:00:00,2024-10-06 18:00:00,Laptop kantor
            """)

# ================================
# SETUP PAGE CONFIG
# ================================

st.set_page_config(
    page_title="Inventory Management System",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ================================
# RUN APPLICATION
# ================================

if __name__ == "__main__":
    main()
