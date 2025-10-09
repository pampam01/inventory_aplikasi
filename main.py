import streamlit as st
import pandas as pd
import os
from datetime import datetime
import json
import io
import os 
# from dotenv import load_dotenv
import random



# ================================
# KONFIGURASI
# ================================

# st.write(st.secrets["nonexistent_key"])

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
            "ID", "Tanggal", "Nama Komponen", "Deskripsi", 
            "Jumlah Masuk", "Jumlah Keluar", "Stok Akhir", 
            "Lokasi Penyimpanan", "Keterangan"
        ]
        df = pd.DataFrame(columns=columns)
        df.to_csv(DATA_FILE, index=False)
        
        return df
    return None

def load_data():
    """Load data dari CSV file"""
    try:
        if os.path.exists(DATA_FILE):
            df = pd.read_csv(DATA_FILE)
            # Pastikan kolom numerik dalam format yang benar
            if 'Jumlah Masuk' in df.columns:
                df['Jumlah Masuk'] = pd.to_numeric(df['Jumlah Masuk'], errors='coerce').fillna(0)
            if 'Jumlah Keluar' in df.columns:
                df['Jumlah Keluar'] = pd.to_numeric(df['Jumlah Keluar'], errors='coerce').fillna(0)
            if 'Stok Akhir' in df.columns:
                df['Stok Akhir'] = pd.to_numeric(df['Stok Akhir'], errors='coerce').fillna(0)
            return df
        else:
            return init_data_file()
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return pd.DataFrame()

def load_backup_data():
    """Load data dari backup file"""
    try:
        if os.path.exists(BACKUP_FILE):
            df = pd.read_csv(BACKUP_FILE)
            # Pastikan kolom numerik dalam format yang benar
            if 'Jumlah Masuk' in df.columns:
                df['Jumlah Masuk'] = pd.to_numeric(df['Jumlah Masuk'], errors='coerce').fillna(0)
            if 'Jumlah Keluar' in df.columns:
                df['Jumlah Keluar'] = pd.to_numeric(df['Jumlah Keluar'], errors='coerce').fillna(0)
            if 'Stok Akhir' in df.columns:
                df['Stok Akhir'] = pd.to_numeric(df['Stok Akhir'], errors='coerce').fillna(0)
            return df
        else:
            return pd.DataFrame()
    except Exception as e:
        st.error(f"Error loading backup data: {str(e)}")
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
            "Tanggal": now,
            "Nama Komponen": item_data['nama'],
            "Deskripsi": item_data['deskripsi'],
            "Jumlah Masuk": item_data['jumlah_masuk'],
            "Jumlah Keluar": item_data['jumlah_keluar'],
            "Stok Akhir": item_data['stok_akhir'],
            "Lokasi Penyimpanan": item_data['lokasi'],
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
        
        df.loc[idx, 'Tanggal'] = now
        df.loc[idx, 'Nama Komponen'] = item_data['nama']
        df.loc[idx, 'Deskripsi'] = item_data['deskripsi']
        df.loc[idx, 'Jumlah Masuk'] = item_data['jumlah_masuk']
        df.loc[idx, 'Jumlah Keluar'] = item_data['jumlah_keluar']
        df.loc[idx, 'Stok Akhir'] = item_data['stok_akhir']
        df.loc[idx, 'Lokasi Penyimpanan'] = item_data['lokasi']
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
        required_columns = ["ID", "Nama Komponen", "Jumlah Masuk", "Jumlah Keluar", "Stok Akhir"]
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            st.error(f"Missing columns: {missing_columns}")
            return False
        
        # Pastikan kolom numerik
        df['Jumlah Masuk'] = pd.to_numeric(df['Jumlah Masuk'], errors='coerce').fillna(0)
        df['Jumlah Keluar'] = pd.to_numeric(df['Jumlah Keluar'], errors='coerce').fillna(0)
        df['Stok Akhir'] = pd.to_numeric(df['Stok Akhir'], errors='coerce').fillna(0)
        
        # Pastikan semua kolom ada
        all_columns = [
            "ID", "Tanggal", "Nama Komponen", "Deskripsi", 
            "Jumlah Masuk", "Jumlah Keluar", "Stok Akhir", 
            "Lokasi Penyimpanan", "Keterangan"
        ]
        
        for col in all_columns:
            if col not in df.columns:
                if col == "Tanggal":
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
    st.title("📦 Inventory Management System - Komponen")
    st.markdown("### Sistem Manajemen Inventory Komponen - Full CRUD + Local Storage")
    
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
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["📋 Lihat Inventory", "➕ Tambah Barang", "✏️ Edit Barang", "🗑️ Hapus Barang", "📊 Import/Export", "💾 Backup Data"])
    
    # Tab 1: Lihat Inventory
    with tab1:
        st.header("📋 Daftar Inventory Komponen")
        
        # Load dan tampilkan data
        df = load_data()
        
        if len(df) > 0:
            # Filter dan search
            col1, col2 = st.columns(2)
            
            with col1:
                search_term = st.text_input("🔍 Cari komponen:", placeholder="Masukkan nama komponen...")
            
            with col2:
                lokasi_options = ['Semua'] + list(df['Lokasi Penyimpanan'].unique()) if 'Lokasi Penyimpanan' in df.columns else ['Semua']
                selected_lokasi = st.selectbox("📍 Filter lokasi:", lokasi_options)
            
            # Apply filters
            filtered_df = df.copy()
            
            if search_term:
                filtered_df = filtered_df[
                    filtered_df['Nama Komponen'].str.contains(search_term, case=False, na=False)
                ]
            
            if selected_lokasi != 'Semua':
                filtered_df = filtered_df[filtered_df['Lokasi Penyimpanan'] == selected_lokasi]
            
            # Tampilkan statistik
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Item", len(df))
            
            with col2:
                total_stok_akhir = df['Stok Akhir'].sum() if 'Stok Akhir' in df.columns else 0
                st.metric("Total Stok Akhir", f"{total_stok_akhir:,.0f}")
            
            with col3:
                stok_rendah = len(df[df['Stok Akhir'] <= 10]) if 'Stok Akhir' in df.columns else 0
                st.metric("Stok Rendah (≤10)", stok_rendah, delta=-stok_rendah if stok_rendah > 0 else None)
            
            with col4:
                total_masuk = df['Jumlah Masuk'].sum() if 'Jumlah Masuk' in df.columns else 0
                st.metric("Total Masuk", f"{total_masuk:,.0f}")
            
            st.markdown("---")
            
            # Tampilkan tabel
            if len(filtered_df) > 0:
                st.dataframe(
                    filtered_df,
                    width='stretch',
                    hide_index=True,
                    column_config={
                        "ID": st.column_config.NumberColumn("ID", width="small"),
                        "Jumlah Masuk": st.column_config.NumberColumn("Jumlah Masuk"),
                        "Jumlah Keluar": st.column_config.NumberColumn("Jumlah Keluar"),
                        "Stok Akhir": st.column_config.NumberColumn("Stok Akhir"),
                    }
                )
            else:
                st.info("📝 Tidak ada data yang sesuai dengan filter.")
        
        else:
            st.info("📝 Belum ada data inventory. Silakan tambah komponen baru di tab 'Tambah Barang'.")
    
    # Tab 2: Tambah Barang
    with tab2:
        st.header("➕ Tambah Komponen Baru")
        
        with st.form("add_item_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                nama = st.text_input("Nama Komponen *", placeholder="Contoh: Motherboard ASUS")
                deskripsi = st.text_area("Deskripsi", placeholder="Deskripsi detail komponen")
                jumlah_masuk = st.number_input("Jumlah Masuk *", min_value=0, step=1, value=0)
                jumlah_keluar = st.number_input("Jumlah Keluar", min_value=0, step=1, value=0)
            
            with col2:
                stok_akhir = st.number_input("Stok Akhir *", min_value=0, step=1, value=0)
                lokasi = st.text_input("Lokasi Penyimpanan", placeholder="Contoh: Gudang A - Rak 1")
                keterangan = st.text_area("Keterangan", placeholder="Catatan tambahan")
            
            submitted = st.form_submit_button("➕ Tambah Komponen", width='stretch')
            
            if submitted:
                if nama and jumlah_masuk >= 0 and stok_akhir >= 0:
                    item_data = {
                        'nama': nama,
                        'deskripsi': deskripsi,
                        'jumlah_masuk': jumlah_masuk,
                        'jumlah_keluar': jumlah_keluar,
                        'stok_akhir': stok_akhir,
                        'lokasi': lokasi,
                        'keterangan': keterangan
                    }
                    
                    with st.spinner('Menambahkan komponen...'):
                        success, new_id = add_item(item_data)
                        if success:
                            st.success(f"✅ Komponen '{nama}' berhasil ditambahkan dengan ID {new_id}!")
                            st.balloons()
                            st.rerun()
                        else:
                            st.error("❌ Gagal menambahkan komponen.")
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
                item_options.append(f"{int(row['ID'])} - {row['Nama Komponen']}")
            
            selected_item = st.selectbox("Pilih komponen yang akan diedit:", ["Pilih komponen..."] + item_options)
            
            if selected_item != "Pilih komponen...":
                item_id = int(selected_item.split(" - ")[0])
                selected_row = df[df['ID'] == item_id].iloc[0]
                
                st.markdown(f"**Edit komponen:** {selected_row['Nama Komponen']}")
                
                with st.form("edit_item_form"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        nama = st.text_input("Nama Komponen *", value=selected_row['Nama Komponen'])
                        deskripsi = st.text_area("Deskripsi", value=selected_row['Deskripsi'] if pd.notna(selected_row['Deskripsi']) else "")
                        jumlah_masuk = st.number_input("Jumlah Masuk *", min_value=0, step=1, value=int(selected_row['Jumlah Masuk']))
                        jumlah_keluar = st.number_input("Jumlah Keluar", min_value=0, step=1, value=int(selected_row['Jumlah Keluar']))
                    
                    with col2:
                        stok_akhir = st.number_input("Stok Akhir *", min_value=0, step=1, value=int(selected_row['Stok Akhir']))
                        lokasi = st.text_input("Lokasi Penyimpanan", value=selected_row['Lokasi Penyimpanan'] if pd.notna(selected_row['Lokasi Penyimpanan']) else "")
                        keterangan = st.text_area("Keterangan", value=selected_row['Keterangan'] if pd.notna(selected_row['Keterangan']) else "")
                    
                    submitted = st.form_submit_button("💾 Simpan Perubahan", width='stretch')
                    
                    if submitted:
                        if nama and jumlah_masuk >= 0 and stok_akhir >= 0:
                            item_data = {
                                'nama': nama,
                                'deskripsi': deskripsi,
                                'jumlah_masuk': jumlah_masuk,
                                'jumlah_keluar': jumlah_keluar,
                                'stok_akhir': stok_akhir,
                                'lokasi': lokasi,
                                'keterangan': keterangan
                            }
                            
                            with st.spinner('Menyimpan perubahan...'):
                                if update_item(item_id, item_data):
                                    st.success(f"✅ Komponen '{nama}' berhasil diperbarui!")
                                    st.rerun()
                                else:
                                    st.error("❌ Gagal memperbarui komponen.")
                        else:
                            st.error("❌ Mohon isi semua field yang wajib (*)")
        else:
            st.info("📝 Belum ada data komponen untuk diedit.")
    
    # Tab 4: Hapus Barang
    with tab4:
        st.header("🗑️ Hapus Barang")
        
        df = load_data()
        
        if len(df) > 0:
            # Select item to delete
            item_options = []
            for _, row in df.iterrows():
                item_options.append(f"{int(row['ID'])} - {row['Nama Komponen']} (Stok: {int(row['Stok Akhir'])})")
            
            selected_item = st.selectbox("Pilih komponen yang akan dihapus:", ["Pilih komponen..."] + item_options)
            
            if selected_item != "Pilih komponen...":
                item_id = int(selected_item.split(" - ")[0])
                selected_row = df[df['ID'] == item_id].iloc[0]
                
                st.markdown("### ⚠️ Konfirmasi Penghapusan")
                st.warning(f"Anda akan menghapus: **{selected_row['Nama Komponen']}**")
                
                # Show item details
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**ID:** {int(selected_row['ID'])}")
                    st.write(f"**Deskripsi:** {selected_row['Deskripsi'] if pd.notna(selected_row['Deskripsi']) else '-'}")
                    st.write(f"**Stok Akhir:** {int(selected_row['Stok Akhir'])}")
                
                with col2:
                    st.write(f"**Jumlah Masuk:** {int(selected_row['Jumlah Masuk'])}")
                    st.write(f"**Jumlah Keluar:** {int(selected_row['Jumlah Keluar'])}")
                    st.write(f"**Lokasi:** {selected_row['Lokasi Penyimpanan'] if pd.notna(selected_row['Lokasi Penyimpanan']) else '-'}")
                
                st.markdown("---")
                
                # Confirmation
                confirm = st.checkbox("✅ Saya yakin ingin menghapus komponen ini")
                
                if confirm:
                    if st.button("🗑️ Hapus Komponen", type="secondary", width='stretch'):
                        with st.spinner('Menghapus komponen...'):
                            if delete_item(item_id):
                                st.success(f"✅ Komponen '{selected_row['Nama Komponen']}' berhasil dihapus!")
                                st.rerun()
                            else:
                                st.error("❌ Gagal menghapus komponen.")
        else:
            st.info("📝 Belum ada data komponen untuk dihapus.")
    
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
ID,Tanggal,Nama Komponen,Deskripsi,Jumlah Masuk,Jumlah Keluar,Stok Akhir,Lokasi Penyimpanan,Keterangan
1,2024-10-06 18:00:00,Motherboard ASUS,ASUS B450M Pro4,10,2,8,Labor 1.3 Thehok,Komponen utama PC
            """)
    
    # Tab 6: Backup Data
    with tab6:
        st.header("💾 Backup Data Management")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 Lihat Data Backup")
            st.markdown("Data backup dari file `inventory_backup.csv`:")
            
            backup_df = load_backup_data()
            if len(backup_df) > 0:
                st.dataframe(
                    backup_df,
                    width='stretch',
                    hide_index=True,
                    column_config={
                        "ID": st.column_config.NumberColumn("ID", width="small"),
                        "Jumlah Masuk": st.column_config.NumberColumn("Jumlah Masuk"),
                        "Jumlah Keluar": st.column_config.NumberColumn("Jumlah Keluar"),
                        "Stok Akhir": st.column_config.NumberColumn("Stok Akhir"),
                    }
                )
                
                # Backup statistics
                col1_stat, col2_stat, col3_stat = st.columns(3)
                with col1_stat:
                    st.metric("Total Item Backup", len(backup_df))
                with col2_stat:
                    total_stok_backup = backup_df['Stok Akhir'].sum() if 'Stok Akhir' in backup_df.columns else 0
                    st.metric("Total Stok Backup", f"{total_stok_backup:,.0f}")
                with col3_stat:
                    total_masuk_backup = backup_df['Jumlah Masuk'].sum() if 'Jumlah Masuk' in backup_df.columns else 0
                    st.metric("Total Masuk Backup", f"{total_masuk_backup:,.0f}")
            else:
                st.info("📝 Tidak ada data backup yang tersedia.")
        
        with col2:
            st.subheader("🔄 Restore dari Backup")
            st.markdown("Pulihkan data dari backup file:")
            
            if len(backup_df) > 0:
                st.markdown("**Preview data backup:**")
                st.dataframe(backup_df.head(3), width='stretch')
                
                st.markdown("---")
                st.markdown("**⚠️ Peringatan:** Restore akan mengganti semua data saat ini!")
                
                col1_restore, col2_restore = st.columns(2)
                
                with col1_restore:
                    if st.button("🔄 Restore dari Backup", type="secondary", width='stretch'):
                        with st.spinner('Restoring data from backup...'):
                            if save_data(backup_df):
                                st.success("✅ Data berhasil dipulihkan dari backup!")
                                st.rerun()
                            else:
                                st.error("❌ Gagal memulihkan data dari backup.")
                
                with col2_restore:
                    if st.button("📋 Lihat Detail Backup", width='stretch'):
                        st.markdown("**Detail Backup File:**")
                        st.write(f"- **File:** {BACKUP_FILE}")
                        st.write(f"- **Total Records:** {len(backup_df)}")
                        if os.path.exists(BACKUP_FILE):
                            file_size = os.path.getsize(BACKUP_FILE)
                            st.write(f"- **File Size:** {file_size} bytes")
                        st.write(f"- **Last Modified:** {datetime.fromtimestamp(os.path.getmtime(BACKUP_FILE)).strftime('%Y-%m-%d %H:%M:%S') if os.path.exists(BACKUP_FILE) else 'N/A'}")
            else:
                st.info("📝 Tidak ada data backup untuk dipulihkan.")
            
            st.markdown("---")
            st.markdown("**📁 Backup File Info:**")
            if os.path.exists(BACKUP_FILE):
                st.success(f"✅ Backup file ditemukan: `{BACKUP_FILE}`")
                file_size = os.path.getsize(BACKUP_FILE)
                st.write(f"- **Size:** {file_size} bytes")
                st.write(f"- **Modified:** {datetime.fromtimestamp(os.path.getmtime(BACKUP_FILE)).strftime('%Y-%m-%d %H:%M:%S')}")
            else:
                st.warning(f"⚠️ Backup file tidak ditemukan: `{BACKUP_FILE}`")

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
