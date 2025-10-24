import mysql.connector
import tkinter as tk
from tkinter import messagebox, ttk, simpledialog
import hashlib


DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'uas'
}


def hash_password(pw: str) -> str:
    return hashlib.sha256(pw.encode('utf-8')).hexdigest()


class DB:
    def __init__(self):
        self.conn = None
        self.connect()
    def connect(self):
        self.conn = mysql.connector.connect(**DB_CONFIG)
    def fetchone(self, query, params=None):
        cur = self.conn.cursor(dictionary=True)
        cur.execute(query, params or ())
        r = cur.fetchone()
        cur.close()
        return r
    def fetchall(self, query, params=None):
        cur = self.conn.cursor(dictionary=True)
        cur.execute(query, params or ())
        r = cur.fetchall()
        cur.close()
        return r
    def execute(self, query, params=None):
        cur = self.conn.cursor()
        cur.execute(query, params or ())
        self.conn.commit()
        cur.close()
        return True

DBM = DB()

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Sistem Bimbingan Skripsi')
        self.geometry('900x600')
        self.user = None
        self.frame = None
        self.show_login()

    def clear_frame(self):
        if self.frame:
            self.frame.destroy()

    def show_login(self):
        self.clear_frame()
        self.frame = LoginFrame(self, on_login=self.on_login)
        self.frame.pack(fill='both', expand=True)

    def on_login(self, user_row):
        # user_row: dict from tb_users
        self.user = user_row
        role = user_row['role']
        if role == 'admin':
            self.show_admin()
        elif role == 'dosen':
            self.show_dosen()
        elif role == 'mahasiswa':
            self.show_mahasiswa()

    def logout(self):
        self.user = None
        self.show_login()

    def show_admin(self):
        self.clear_frame()
        self.frame = AdminFrame(self, self.logout)
        self.frame.pack(fill='both', expand=True)

    def show_dosen(self):
        self.clear_frame()
        self.frame = DosenFrame(self, self.logout)
        self.frame.pack(fill='both', expand=True)

    def show_mahasiswa(self):
        self.clear_frame()
        self.frame = MahasiswaFrame(self, self.logout)
        self.frame.pack(fill='both', expand=True)

class LoginFrame(tk.Frame):
    def __init__(self, master, on_login):
        super().__init__(master)
        self.on_login = on_login
        tk.Label(self, text='Login Sistem Bimbingan', font=('Arial',16)).pack(pady=20)
        frm = tk.Frame(self)
        frm.pack()
        tk.Label(frm, text='Username').grid(row=0, column=0, sticky='e')
        tk.Label(frm, text='Password').grid(row=1, column=0, sticky='e')
        self.ent_user = tk.Entry(frm)
        self.ent_pass = tk.Entry(frm, show='*')
        self.ent_user.grid(row=0, column=1)
        self.ent_pass.grid(row=1, column=1)
        tk.Button(self, text='Login', command=self.login).pack(pady=10)

    def login(self):
        u = self.ent_user.get().strip()
        p = self.ent_pass.get().strip()
        if not u or not p:
            messagebox.showwarning('Error','Isi username & password')
            return
        # ambil user
        # NOTE: in seed we used plain passwords; try both hashed and plain for convenience
        row = DBM.fetchone('SELECT * FROM tb_users WHERE username=%s', (u,))
        if not row:
            messagebox.showerror('Error','User tidak ditemukan')
            return
        # periksa hash
        hashed = hash_password(p)
        if row['password_hash'] == p or row['password_hash'] == hashed:
            self.on_login(row)
        else:
            messagebox.showerror('Error','Password salah')

class AdminFrame(tk.Frame):
    def __init__(self, master, logout_cb):
        super().__init__(master)
        tk.Label(self, text='Dashboard Admin', font=('Arial',16)).pack(pady=10)
        btn_frm = tk.Frame(self)
        btn_frm.pack()
        tk.Button(btn_frm, text='Kelola Dosen', command=self.kelola_dosen).grid(row=0,column=0,padx=5)
        tk.Button(btn_frm, text='Kelola Mahasiswa', command=self.kelola_mahasiswa).grid(row=0,column=1,padx=5)
        tk.Button(btn_frm, text='Lihat Pengajuan', command=self.lihat_pengajuan).grid(row=0,column=2,padx=5)
        tk.Button(btn_frm, text='Logout', command=logout_cb).grid(row=0,column=3,padx=5)
        self.content = tk.Frame(self)
        self.content.pack(fill='both', expand=True, pady=10)

    def kelola_dosen(self):
        for w in self.content.winfo_children(): w.destroy()
        DosenManage(self.content)

    def kelola_mahasiswa(self):
        for w in self.content.winfo_children(): w.destroy()
        MahasiswaManage(self.content)

    def lihat_pengajuan(self):
        for w in self.content.winfo_children(): w.destroy()
        PengajuanList(self.content)

class DosenFrame(tk.Frame):
    def __init__(self, master, logout_cb):
        super().__init__(master)
        tk.Label(self, text='Dashboard Dosen', font=('Arial',16)).pack(pady=10)
        btn_frm = tk.Frame(self)
        btn_frm.pack()
        tk.Button(btn_frm, text='Buat Jadwal', command=self.buat_jadwal).grid(row=0,column=0,padx=5)
        tk.Button(btn_frm, text='Lihat Pengajuan', command=self.lihat_pengajuan).grid(row=0,column=1,padx=5)
        tk.Button(btn_frm, text='Logout', command=logout_cb).grid(row=0,column=2,padx=5)
        self.content = tk.Frame(self)
        self.content.pack(fill='both', expand=True, pady=10)

    def buat_jadwal(self):
        for w in self.content.winfo_children(): w.destroy()
        JadwalCreate(self.content, nidn=self._get_nidn())

    def lihat_pengajuan(self):
        for w in self.content.winfo_children(): w.destroy()
        PengajuanDosenList(self.content, nidn=self._get_nidn())

    def _get_nidn(self):
        # ambil nidn berdasarkan user
        user_id = self.master.user['id_user']
        r = DBM.fetchone('SELECT nidn FROM dosen WHERE id_user=%s', (user_id,))
        return r['nidn'] if r else None

class MahasiswaFrame(tk.Frame):
    def __init__(self, master, logout_cb):
        super().__init__(master)
        tk.Label(self, text='Dashboard Mahasiswa', font=('Arial',16)).pack(pady=10)
        btn_frm = tk.Frame(self)
        btn_frm.pack()
        tk.Button(btn_frm, text='Lihat Jadwal Dosen', command=self.lihat_jadwal).grid(row=0,column=0,padx=5)
        tk.Button(btn_frm, text='Ajukan Bimbingan', command=self.ajukan_bimbingan).grid(row=0,column=1,padx=5)
        tk.Button(btn_frm, text='Riwayat Bimbingan', command=self.riwayat).grid(row=0,column=2,padx=5)
        tk.Button(btn_frm, text='Logout', command=logout_cb).grid(row=0,column=3,padx=5)
        self.content = tk.Frame(self)
        self.content.pack(fill='both', expand=True, pady=10)

    def lihat_jadwal(self):
        for w in self.content.winfo_children(): w.destroy()
        JadwalList(self.content)

    def ajukan_bimbingan(self):
        for w in self.content.winfo_children(): w.destroy()
        AjukanForm(self.content, nim=self._get_nim())

    def riwayat(self):
        for w in self.content.winfo_children(): w.destroy()
        RiwayatList(self.content, nim=self._get_nim())

    def _get_nim(self):
        user_id = self.master.user['id_user']
        r = DBM.fetchone('SELECT nim FROM mahasiswa WHERE id_user=%s', (user_id,))
        return r['nim'] if r else None


class DosenManage(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.pack(fill='both', expand=True)
        tk.Button(self, text='Tambah Dosen', command=self.tambah).pack(pady=5)
        self.tree = ttk.Treeview(self, columns=('nidn','nama','departemen'), show='headings')
        for c in ('nidn','nama','departemen'):
            self.tree.heading(c, text=c)
        self.tree.pack(fill='both', expand=True)
        self.load()

    def load(self):
        for r in self.tree.get_children(): self.tree.delete(r)
        rows = DBM.fetchall('SELECT nidn,nama,departemen FROM dosen')
        for row in rows:
            self.tree.insert('', 'end', values=(row['nidn'], row['nama'], row['departemen']))

    def tambah(self):
        nidn = simpledialog.askstring('NIDN','NIDN:')
        nama = simpledialog.askstring('Nama','Nama:')
        dept = simpledialog.askstring('Departemen','Departemen:')
        if nidn and nama:
            # buat user untuk dosen
            username = nidn
            # default password = nidn (hash)
            pw_hash = nidn
            DBM.execute('INSERT INTO tb_users (username,password_hash,role) VALUES (%s,%s,%s)', (username,pw_hash,'dosen'))
            uid = DBM.fetchone('SELECT id_user FROM tb_users WHERE username=%s',(username,))['id_user']
            DBM.execute('INSERT INTO dosen (nidn,nama,departemen,id_user) VALUES (%s,%s,%s,%s)', (nidn,nama,dept,uid))
            messagebox.showinfo('OK','Dosen ditambahkan')
            self.load()


class MahasiswaManage(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.pack(fill='both', expand=True)
        tk.Button(self, text='Tambah Mahasiswa', command=self.tambah).pack(pady=5)
        self.tree = ttk.Treeview(self, columns=('nim','nama','prodi'), show='headings')
        for c in ('nim','nama','prodi'):
            self.tree.heading(c, text=c)
        self.tree.pack(fill='both', expand=True)
        self.load()

    def load(self):
        for r in self.tree.get_children(): self.tree.delete(r)
        rows = DBM.fetchall('SELECT nim,nama,prodi FROM mahasiswa')
        for row in rows:
            self.tree.insert('', 'end', values=(row['nim'], row['nama'], row['prodi']))

    def tambah(self):
        nim = simpledialog.askstring('NIM','NIM:')
        nama = simpledialog.askstring('Nama','Nama:')
        prodi = simpledialog.askstring('Prodi','Prodi:')
        if nim and nama:
            username = nim
            pw_hash = nim
            DBM.execute('INSERT INTO tb_users (username,password_hash,role) VALUES (%s,%s,%s)', (username,pw_hash,'mahasiswa'))
            uid = DBM.fetchone('SELECT id_user FROM tb_users WHERE username=%s',(username,))['id_user']
            DBM.execute('INSERT INTO mahasiswa (nim,nama,prodi,id_user) VALUES (%s,%s,%s,%s)', (nim,nama,prodi,uid))
            messagebox.showinfo('OK','Mahasiswa ditambahkan')
            self.load()


class JadwalCreate(tk.Frame):
    def __init__(self, master, nidn=None):
        super().__init__(master)
        self.pack(fill='both', expand=True)
        tk.Label(self, text=f'Buat jadwal untuk {nidn}').pack()
        frm = tk.Frame(self)
        frm.pack(pady=10)
        tk.Label(frm, text='Hari').grid(row=0,column=0)
        tk.Label(frm, text='Jam Mulai (HH:MM)').grid(row=1,column=0)
        tk.Label(frm, text='Jam Selesai (HH:MM)').grid(row=2,column=0)
        self.nidn = nidn
        self.ent_hari = ttk.Combobox(frm, values=['Senin','Selasa','Rabu','Kamis','Jumat','Sabtu','Minggu'])
        self.ent_jam_mulai = tk.Entry(frm)
        self.ent_jam_selesai = tk.Entry(frm)
        self.ent_hari.grid(row=0,column=1)
        self.ent_jam_mulai.grid(row=1,column=1)
        self.ent_jam_selesai.grid(row=2,column=1)
        tk.Button(self, text='Simpan', command=self.simpan).pack(pady=5)

    def simpan(self):
        hari = self.ent_hari.get()
        jm = self.ent_jam_mulai.get()
        js = self.ent_jam_selesai.get()
        try:
            DBM.execute('INSERT INTO jadwal_dosen (nidn,hari,jam_mulai,jam_selesai) VALUES (%s,%s,%s,%s)', (self.nidn,hari,jm+':00',js+':00'))
            messagebox.showinfo('OK','Jadwal tersimpan')
        except Exception as e:
            messagebox.showerror('Error',str(e))

class JadwalList(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.pack(fill='both', expand=True)
        self.tree = ttk.Treeview(self, columns=('id','nidn','hari','jam'), show='headings')
        for c in ('id','nidn','hari','jam'):
            self.tree.heading(c, text=c)
        self.tree.pack(fill='both', expand=True)
        tk.Button(self, text='Refresh', command=self.load).pack(pady=5)
        self.load()
    def load(self):
        for r in self.tree.get_children(): self.tree.delete(r)
        rows = DBM.fetchall('SELECT id_jadwal,nidn,CONCAT(hari," ",TIME_FORMAT(jam_mulai, "%H:%i")) AS jam FROM jadwal_dosen WHERE status=%s', ('tersedia',))
        for row in rows:
            self.tree.insert('', 'end', values=(row['id_jadwal'], row['nidn'], row['jam'].split()[0], row['jam'].split()[1]))

class AjukanForm(tk.Frame):
    def __init__(self, master, nim=None):
        super().__init__(master)
        self.pack(fill='both', expand=True)
        self.nim = nim
        tk.Label(self, text='Ajukan Bimbingan').pack()
        tk.Button(self, text='Pilih jadwal dari daftar', command=self.pilih_jadwal).pack(pady=5)
        tk.Button(self, text='Ajukan manual (isi dosen & tanggal)', command=self.ajukan_manual).pack(pady=5)

    def pilih_jadwal(self):
        rows = DBM.fetchall('SELECT id_jadwal,nidn,hari, TIME_FORMAT(jam_mulai, "%H:%i") AS jam FROM jadwal_dosen WHERE status=%s', ('tersedia',))
        if not rows:
            messagebox.showinfo('Info','Tidak ada jadwal tersedia')
            return
        choices = [f"{r['id_jadwal']} - {r['nidn']} - {r['hari']} {r['jam']}" for r in rows]
        sel = simpledialog.askstring('Pilih','Ketik ID jadwal yang ingin diajukan:\n' + '\n'.join(choices))
        if not sel: return
        idj = int(sel.split()[0])
        # insert pengajuan
        DBM.execute('INSERT INTO bimbingan (nim,nidn,id_jadwal,status) VALUES (%s,%s,%s,%s)', (self.nim, DBM.fetchone('SELECT nidn FROM jadwal_dosen WHERE id_jadwal=%s',(idj,))['nidn'], idj, 'menunggu'))
        messagebox.showinfo('OK','Pengajuan dikirim')

    def ajukan_manual(self):
        nidn = simpledialog.askstring('NIDN','NIDN dosen:')
        tanggal = simpledialog.askstring('Tanggal','Tanggal (YYYY-MM-DD):')
        jam = simpledialog.askstring('Jam','Jam (HH:MM):')
        if nidn and tanggal and jam:
            DBM.execute('INSERT INTO bimbingan (nim,nidn,tanggal,jam,status) VALUES (%s,%s,%s,%s,%s)', (self.nim,nidn,tanggal,jam+':00','menunggu'))
            messagebox.showinfo('OK','Pengajuan manual dikirim')

class PengajuanList(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.pack(fill='both', expand=True)
        self.tree = ttk.Treeview(self, columns=('id','nim','nidn','status','created'), show='headings')
        for c in ('id','nim','nidn','status','created'):
            self.tree.heading(c, text=c)
        self.tree.pack(fill='both', expand=True)
        tk.Button(self, text='Refresh', command=self.load).pack(pady=5)
        tk.Button(self, text='Set Diterima (manual)', command=self.set_diterima).pack(pady=5)
        self.load()
    def load(self):
        for r in self.tree.get_children(): self.tree.delete(r)
        rows = DBM.fetchall('SELECT id_bimbingan,nim,nidn,status,created_at FROM bimbingan ORDER BY created_at DESC')
        for row in rows:
            self.tree.insert('', 'end', values=(row['id_bimbingan'],row['nim'],row['nidn'],row['status'],row['created_at']))
    def set_diterima(self):
        sel = self.tree.selection()
        if not sel: return
        item = self.tree.item(sel[0])['values']
        idb = item[0]
        # ubah status jadi diterima
        DBM.execute('UPDATE bimbingan SET status=%s WHERE id_bimbingan=%s', ('diterima', idb))
        messagebox.showinfo('OK','Status diubah ke diterima')
        self.load()

class PengajuanDosenList(tk.Frame):
    def __init__(self, master, nidn=None):
        super().__init__(master)
        self.nidn = nidn
        tk.Label(self, text=f'Pengajuan untuk {nidn}').pack()
        self.tree = ttk.Treeview(self, columns=('id','nim','tanggal','jam','status'), show='headings')
        for c in ('id','nim','tanggal','jam','status'):
            self.tree.heading(c, text=c)
        self.tree.pack(fill='both', expand=True)
        tk.Button(self, text='Refresh', command=self.load).pack(pady=5)
        tk.Button(self, text='Terima', command=self.terima).pack(pady=5)
        tk.Button(self, text='Tolak', command=self.tolak).pack(pady=5)
        self.load()
    def load(self):
        for r in self.tree.get_children(): self.tree.delete(r)
        rows = DBM.fetchall('SELECT id_bimbingan,nim,tanggal, TIME_FORMAT(jam, "%H:%i") AS jam,status FROM bimbingan WHERE nidn=%s ORDER BY created_at DESC', (self.nidn,))
        for row in rows:
            self.tree.insert('', 'end', values=(row['id_bimbingan'],row['nim'],row['tanggal'] or '-',row['jam'] or '-',row['status']))
    def terima(self):
        sel = self.tree.selection()
        if not sel: return
        idb = self.tree.item(sel[0])['values'][0]
        # set diterima
        DBM.execute('UPDATE bimbingan SET status=%s WHERE id_bimbingan=%s', ('diterima', idb))
        messagebox.showinfo('OK','Pengajuan diterima')
        self.load()
    def tolak(self):
        sel = self.tree.selection()
        if not sel: return
        idb = self.tree.item(sel[0])['values'][0]
        DBM.execute('UPDATE bimbingan SET status=%s WHERE id_bimbingan=%s', ('ditolak', idb))
        messagebox.showinfo('OK','Pengajuan ditolak')
        self.load()


class RiwayatList(tk.Frame):
    def __init__(self, master, nim=None):
        super().__init__(master)
        self.nim = nim
        tk.Label(self, text=f'Riwayat bimbingan {nim}').pack()
        self.tree = ttk.Treeview(self, columns=('id','nidn','tanggal','jam','status','catatan'), show='headings')
        for c in ('id','nidn','tanggal','jam','status','catatan'):
            self.tree.heading(c, text=c)
        self.tree.pack(fill='both', expand=True)
        tk.Button(self, text='Refresh', command=self.load).pack(pady=5)
        self.load()
    def load(self):
        for r in self.tree.get_children(): self.tree.delete(r)
        rows = DBM.fetchall('SELECT id_bimbingan,nidn,tanggal, TIME_FORMAT(jam, "%H:%i") AS jam,status,catatan FROM bimbingan WHERE nim=%s ORDER BY created_at DESC', (self.nim,))
        for row in rows:
            self.tree.insert('', 'end', values=(row['id_bimbingan'],row['nidn'],row['tanggal'] or '-',row['jam'] or '-',row['status'], (row['catatan'] or '')[:50]))


if __name__ == '__main__':
    app = App()
    app.mainloop()
