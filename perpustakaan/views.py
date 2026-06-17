from django.shortcuts import render, redirect
from django.db import connection
from django.contrib import messages
from django.utils import timezone 

def dictfetchall(cursor):
    "Mengubah hasil fetch cursor menjadi dictionary"
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]

# ================= DASHBOARD =================
def dashboard(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM buku")
        total_judul_buku = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM siswa")
        total_siswa = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM peminjaman WHERE status='Dipinjam'")
        total_dipinjam = cursor.fetchone()[0]
        cursor.execute("SELECT SUM(stok) FROM buku")
        total_stok_buku = cursor.fetchone()[0] or 0
    
    return render(request, 'dashboard.html', {
        'total_judul_buku': total_judul_buku,
        'total_siswa': total_siswa,
        'total_dipinjam': total_dipinjam,
        'total_stok_buku': total_stok_buku
    })

# ================= MODUL BUKU =================
def buku_list(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM buku ORDER BY id DESC")
        buku = dictfetchall(cursor)
    return render(request, 'buku_list.html', {'buku': buku})

def buku_detail(request, id):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM buku WHERE id=%s", [id])
        buku = dictfetchall(cursor)[0]  # Ambil baris pertama
    return render(request, 'buku_detail.html', {'buku': buku})

def buku_tambah(request):
    if request.method == 'POST':
        data = request.POST
        with connection.cursor() as cursor:
            cursor.execute('''
                INSERT INTO buku (judul, pengarang, kategori, penerbit, tahun_terbit, rak, stok, deskripsi)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ''', [data['judul'], data['pengarang'], data['kategori'], data['penerbit'], 
                  data['tahun_terbit'], data['rak'], data['stok'], data['deskripsi']])
        return redirect('buku_list')
    return render(request, 'buku_form.html')

def buku_edit(request, id):
    with connection.cursor() as cursor:
        if request.method == 'POST':
            data = request.POST
            cursor.execute('''
                UPDATE buku SET judul=%s, pengarang=%s, kategori=%s, penerbit=%s, 
                tahun_terbit=%s, rak=%s, stok=%s, deskripsi=%s WHERE id=%s
            ''', [data['judul'], data['pengarang'], data['kategori'], data['penerbit'], 
                  data['tahun_terbit'], data['rak'], data['stok'], data['deskripsi'], id])
            return redirect('buku_list')
        
        cursor.execute("SELECT * FROM buku WHERE id=%s", [id])
        buku = dictfetchall(cursor)[0]
    return render(request, 'buku_form.html', {'buku': buku})

def buku_hapus(request, id):
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM peminjaman WHERE buku_id=%s", [id])
        jumlah_pinjaman = cursor.fetchone()[0]
        
        if jumlah_pinjaman > 0:
            messages.error(request, "Gagal menghapus! Buku sedang dipinjam atau tercatat dalam riwayat peminjaman.")
            return redirect('buku_list')
        

        cursor.execute("DELETE FROM buku WHERE id=%s", [id])
        messages.success(request, "Data buku berhasil dihapus.")
        
    return redirect('buku_list')

# ================= MODUL SISWA =================
def siswa_list(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM siswa ORDER BY id DESC")
        siswa = dictfetchall(cursor)
    return render(request, 'siswa_list.html', {'siswa': siswa})

def siswa_detail(request, id):
    with connection.cursor() as cursor:
        # Mengambil data siswa
        cursor.execute("SELECT * FROM siswa WHERE id=%s", [id])
        siswa = dictfetchall(cursor)[0]
        
        # BONUS CERDAS: Ambil juga riwayat buku apa saja yang sedang/pernah dia pinjam
        cursor.execute('''
            SELECT b.judul, p.tanggal_pinjam, p.status 
            FROM peminjaman p
            JOIN buku b ON p.buku_id = b.id
            WHERE p.siswa_id = %s ORDER BY p.id DESC
        ''', [id])
        riwayat = dictfetchall(cursor)
        
    return render(request, 'siswa_detail.html', {'siswa': siswa, 'riwayat': riwayat})

def siswa_tambah(request):
    if request.method == 'POST':
        data = request.POST
        is_active = True if request.POST.get('is_active') == '1' else False
        with connection.cursor() as cursor:
            cursor.execute('''
                INSERT INTO siswa (nama, kelas, nis, is_active)
                VALUES (%s, %s, %s, %s)
            ''', [data['nama'], data['kelas'], data['nis'], is_active])
        return redirect('siswa_list')
    return render(request, 'siswa_form.html')

def siswa_edit(request, id):
    with connection.cursor() as cursor:
        if request.method == 'POST':
            data = request.POST
            is_active = True if request.POST.get('is_active') == '1' else False
            cursor.execute('''
                UPDATE siswa SET nama=%s, kelas=%s, nis=%s, is_active=%s WHERE id=%s
            ''', [data['nama'], data['kelas'], data['nis'], is_active, id])
            return redirect('siswa_list')
        
        cursor.execute("SELECT * FROM siswa WHERE id=%s", [id])
        siswa = dictfetchall(cursor)[0]
    return render(request, 'siswa_form.html', {'siswa': siswa})

def siswa_hapus(request, id):
    with connection.cursor() as cursor:
        # Cek apakah siswa ini masih memiliki riwayat peminjaman
        cursor.execute("SELECT COUNT(*) FROM peminjaman WHERE siswa_id=%s", [id])
        jumlah_pinjaman = cursor.fetchone()[0]
        
        if jumlah_pinjaman > 0:
            # Jika ada, batalkan penghapusan dan kirim pesan peringatan
            messages.error(request, "Gagal menghapus! Siswa memiliki riwayat transaksi di data peminjaman.")
            return redirect('siswa_list')
        
        # Jika bersih dari transaksi, baru izinkan hapus
        cursor.execute("DELETE FROM siswa WHERE id=%s", [id])
        messages.success(request, "Data siswa berhasil dihapus.")
        
    return redirect('siswa_list')

# ================= MODUL PEMINJAMAN =================
def peminjaman_list(request):
    with connection.cursor() as cursor:
        cursor.execute('''
            SELECT p.id, s.nama, b.judul, p.tanggal_pinjam, p.jatuh_tempo, p.keperluan, p.status 
            FROM peminjaman p
            JOIN siswa s ON p.siswa_id = s.id
            JOIN buku b ON p.buku_id = b.id
            ORDER BY p.id DESC
        ''')
        peminjaman = dictfetchall(cursor)
    
    # 🔴 PERBAIKAN: Ambil tanggal hari ini secara real-time dan kirim ke HTML lewat key 'now'
    hari_ini = timezone.now()
    
    return render(request, 'peminjaman_list.html', {
        'peminjaman': peminjaman,
        'now': hari_ini  # 🔴 Variabel 'now' sekarang resmi terdefinisi dan bisa dibaca HTML Anda!
    })

def peminjaman_tambah(request):
    with connection.cursor() as cursor:
        if request.method == 'POST':
            data = request.POST
            buku_id = data['buku_id']
            
            # FIX BUG 1: Validasi stok buku sebelum membolehkan peminjaman
            cursor.execute("SELECT stok FROM buku WHERE id=%s", [buku_id])
            stok_sekarang = cursor.fetchone()[0]
            
            if stok_sekarang <= 0:
                # Jika stok habis, form dikembalikan dengan pesan error
                cursor.execute("SELECT id, nama FROM siswa WHERE is_active=True")
                siswa = dictfetchall(cursor)
                cursor.execute("SELECT id, judul FROM buku WHERE stok > 0")
                buku = dictfetchall(cursor)
                return render(request, 'peminjaman_form.html', {
                    'siswa': siswa, 
                    'buku': buku, 
                    'error': 'Maaf, stok buku ini sedang kosong!'
                })
            
            # Jalankan transaksi penambahan peminjaman
            cursor.execute('''
                INSERT INTO peminjaman (siswa_id, buku_id, tanggal_pinjam, jatuh_tempo, keperluan, status)
                VALUES (%s, %s, %s, %s, %s, 'Dipinjam')
            ''', [data['siswa_id'], buku_id, data['tanggal_pinjam'], data['jatuh_tempo'], data['keperluan']])
            
            # FIX BUG 2: Otomatis memotong stok buku sebanyak 1 unit
            cursor.execute("UPDATE buku SET stok = stok - 1 WHERE id=%s", [buku_id])
            
            return redirect('peminjaman_list')
        
        # Mengambil data untuk Dropdown form tambah
        cursor.execute("SELECT id, nama FROM siswa WHERE is_active=True")
        siswa = dictfetchall(cursor)
        cursor.execute("SELECT id, judul FROM buku WHERE stok > 0")
        buku = dictfetchall(cursor)
        
    return render(request, 'peminjaman_form.html', {'siswa': siswa, 'buku': buku})

def peminjaman_ubah_status(request, id):
    with connection.cursor() as cursor:
        # Ambil status saat ini dan buku_id untuk validasi perubahan stok
        cursor.execute("SELECT status, buku_id FROM peminjaman WHERE id=%s", [id])
        peminjaman_data = cursor.fetchone()
        
        if peminjaman_data and peminjaman_data[0] == 'Dipinjam':
            buku_id = peminjaman_data[1]
            
            # Ubah status transaksi menjadi dikembalikan
            cursor.execute("UPDATE peminjaman SET status='Dikembalikan' WHERE id=%s", [id])
            
            # FIX BUG 3: Otomatis kembalikan/tambahkan stok buku kembali 1 unit ke rak
            cursor.execute("UPDATE buku SET stok = stok + 1 WHERE id=%s", [buku_id])
            
    return redirect('peminjaman_list')

def peminjaman_hapus(request, id):
    with connection.cursor() as cursor:
        # Ambil status dan buku_id untuk mengecek apakah stok perlu dikembalikan sebelum data dihapus
        cursor.execute("SELECT status, buku_id FROM peminjaman WHERE id=%s", [id])
        peminjaman_data = cursor.fetchone()
        
        if peminjaman_data:
            status = peminjaman_data[0]
            buku_id = peminjaman_data[1]
            
            # FIX BUG 4: Jika peminjaman yang dihapus statusnya masih 'Dipinjam', pulangkan stok bukunya
            if status == 'Dipinjam':
                cursor.execute("UPDATE buku SET stok = stok + 1 WHERE id=%s", [buku_id])
            
            # Hapus baris data dari tabel peminjaman
            cursor.execute("DELETE FROM peminjaman WHERE id=%s", [id])
            
    return redirect('peminjaman_list')
