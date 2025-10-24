-- nama db: user
CREATE TABLE tb_users (
  id_user INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(50) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  role ENUM('admin','dosen','mahasiswa') NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE dosen (
  nidn VARCHAR(20) PRIMARY KEY,
  nama VARCHAR(100) NOT NULL,
  departemen VARCHAR(100),
  id_user INT UNIQUE,
  FOREIGN KEY (id_user) REFERENCES tb_users(id_user) ON DELETE SET NULL
);

CREATE TABLE mahasiswa (
  nim VARCHAR(20) PRIMARY KEY,
  nama VARCHAR(100) NOT NULL,
  prodi VARCHAR(100),
  id_user INT UNIQUE,
  FOREIGN KEY (id_user) REFERENCES tb_users(id_user) ON DELETE SET NULL
);

CREATE TABLE jadwal_dosen (
  id_jadwal INT AUTO_INCREMENT PRIMARY KEY,
  nidn VARCHAR(20) NOT NULL,
  hari ENUM('Senin','Selasa','Rabu','Kamis','Jumat','Sabtu','Minggu') NOT NULL,
  jam_mulai TIME NOT NULL,
  jam_selesai TIME NOT NULL,
  kapasitas INT DEFAULT 1,
  status ENUM('tersedia','penuh','nonaktif') DEFAULT 'tersedia',
  FOREIGN KEY (nidn) REFERENCES dosen(nidn) ON DELETE CASCADE
);


CREATE TABLE bimbingan (
  id_bimbingan INT AUTO_INCREMENT PRIMARY KEY,
  nim VARCHAR(20) NOT NULL,
  nidn VARCHAR(20) NOT NULL,
  id_jadwal INT DEFAULT NULL,
  tanggal DATE DEFAULT NULL,
  jam TIME DEFAULT NULL,
  status ENUM('menunggu','diterima','ditolak','selesai') DEFAULT 'menunggu',
  catatan TEXT,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (nim) REFERENCES mahasiswa(nim) ON DELETE CASCADE,
  FOREIGN KEY (nidn) REFERENCES dosen(nidn) ON DELETE CASCADE,
  FOREIGN KEY (id_jadwal) REFERENCES jadwal_dosen(id_jadwal) ON DELETE SET NULL
);

INSERT INTO tb_users (username, password_hash, role) VALUES
('admin01', 'adminpass', 'admin'),
('dosen01', 'dosenpass', 'dosen'),
('mhs01', 'mhspass', 'mahasiswa');


INSERT INTO dosen (nidn, nama, departemen, id_user) VALUES
('D001','Dr. Andi','Teknik Informatika', 2);

INSERT INTO mahasiswa (nim, nama, prodi, id_user) VALUES
('M001','Naufal Khn','Sistem Informasi', 3);


INSERT INTO jadwal_dosen (nidn, hari, jam_mulai, jam_selesai, kapasitas) VALUES
('D001','Senin','10:00:00','11:00:00',1),
('D001','Rabu','14:00:00','15:00:00',1);
