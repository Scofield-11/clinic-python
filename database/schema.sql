CREATE TABLE IF NOT EXISTS TAI_KHOAN (
    AccountID INT AUTO_INCREMENT PRIMARY KEY,
    TenDangNhap VARCHAR(100) NOT NULL,
    MatKhau VARCHAR(255) NOT NULL,
    SoDienThoai VARCHAR(20),
    Email VARCHAR(100),
    VaiTro ENUM('BENH_NHAN', 'BAC_SI', 'ADMIN') NOT NULL,
    TrangThai TINYINT DEFAULT 1,
    UNIQUE KEY uq_TenDangNhap (TenDangNhap)
);

CREATE TABLE IF NOT EXISTS BENH_NHAN (
    PatientID INT AUTO_INCREMENT PRIMARY KEY,
    AccountID INT NOT NULL,
    HoTen VARCHAR(100) NOT NULL,
    NgaySinh DATE,
    GioiTinh ENUM('NAM', 'NU', 'KHAC'),
    DiaChi VARCHAR(255),
    FOREIGN KEY (AccountID) REFERENCES TAI_KHOAN(AccountID)
);

CREATE TABLE IF NOT EXISTS CHUYEN_KHOA (
    ChuyenKhoaID INT AUTO_INCREMENT PRIMARY KEY,
    TenChuyenKhoa VARCHAR(100) NOT NULL,
    MoTa TEXT
);

CREATE TABLE IF NOT EXISTS BAC_SI (
    BacSiID INT AUTO_INCREMENT PRIMARY KEY,
    AccountID INT NULL,
    ChuyenKhoaID INT NOT NULL,
    HoTen VARCHAR(100) NOT NULL,
    HocVan VARCHAR(255),
    KinhNghiemNam INT,
    SoDienThoai VARCHAR(20),
    TrangThai TINYINT DEFAULT 1,
    FOREIGN KEY (ChuyenKhoaID) REFERENCES CHUYEN_KHOA(ChuyenKhoaID),
    FOREIGN KEY (AccountID) REFERENCES TAI_KHOAN(AccountID)
);

CREATE TABLE IF NOT EXISTS LICH_HEN (
    LichHenID INT AUTO_INCREMENT PRIMARY KEY,
    PatientID INT NOT NULL,
    BacSiID INT NOT NULL,
    NgayKham DATE NOT NULL,
    GioKham TIME NOT NULL,
    LyDoKham VARCHAR(255),
    TrangThai ENUM('CHO_XAC_NHAN','DA_XAC_NHAN','HUY') DEFAULT 'CHO_XAC_NHAN',
    FOREIGN KEY (PatientID) REFERENCES BENH_NHAN(PatientID),
    FOREIGN KEY (BacSiID) REFERENCES BAC_SI(BacSiID)
);

CREATE INDEX idx_lichhen_bacsi_ngay_gio ON LICH_HEN (BacSiID, NgayKham, GioKham);

INSERT INTO CHUYEN_KHOA (TenChuyenKhoa, MoTa) VALUES
('Nội tổng quát', 'Khám và điều trị các bệnh nội khoa thường gặp'),
('Nhi', 'Khám và điều trị cho trẻ em'),
('Da liễu', 'Khám và điều trị các bệnh về da'),
('Răng Hàm Mặt', 'Khám và điều trị bệnh về răng hàm mặt'),
('Tim mạch', 'Khám và điều trị bệnh nhân bệnh tim');

INSERT INTO BAC_SI (ChuyenKhoaID, HoTen, HocVan, KinhNghiemNam, SoDienThoai) VALUES
(1, 'BS. Lê Văn Quang', 'BS Nội tổng quát', 5, '0903297940'),
(2, 'BS. Lê Thị Hồng Nhung', 'BS Nhi', 7, '0375112139'),
(3, 'BS. Trần Văn Phục', 'BS Da liễu', 4, '0912345678'),
(5, 'BS. Vũ Quang Du', 'BS Tim mạch', 8, '0342961367'),
(4, 'BS. Nguyễn Khắc Phát', 'BS Răng Hàm Mặt', 4, '0987654321');

INSERT INTO TAI_KHOAN (TenDangNhap, MatKhau, VaiTro, TrangThai) VALUES 
('admin', '11072006', 'ADMIN', 1),
('bs_quang', '123456', 'BAC_SI', 1),
('bs_nhung', '123456', 'BAC_SI', 1),
('bs_phuc',  '123456', 'BAC_SI', 1),
('bs_du',    '123456', 'BAC_SI', 1),
('bs_phat',  '123456', 'BAC_SI', 1);

UPDATE BAC_SI SET AccountID = (SELECT AccountID FROM TAI_KHOAN WHERE TenDangNhap = 'bs_quang') WHERE HoTen = 'BS. Lê Văn Quang';
UPDATE BAC_SI SET AccountID = (SELECT AccountID FROM TAI_KHOAN WHERE TenDangNhap = 'bs_nhung') WHERE HoTen = 'BS. Lê Thị Hồng Nhung';
UPDATE BAC_SI SET AccountID = (SELECT AccountID FROM TAI_KHOAN WHERE TenDangNhap = 'bs_phuc') WHERE HoTen = 'BS. Trần Văn Phục';
UPDATE BAC_SI SET AccountID = (SELECT AccountID FROM TAI_KHOAN WHERE TenDangNhap = 'bs_du') WHERE HoTen = 'BS. Vũ Quang Du';
UPDATE BAC_SI SET AccountID = (SELECT AccountID FROM TAI_KHOAN WHERE TenDangNhap = 'bs_phat') WHERE HoTen = 'BS. Nguyễn Khắc Phát';

ALTER TABLE LICH_HEN 
MODIFY COLUMN TrangThai ENUM('CHO_XAC_NHAN','DA_XAC_NHAN','DA_KHAM','HUY','VANG_MAT') DEFAULT 'CHO_XAC_NHAN';

ALTER TABLE LICH_HEN ADD COLUMN ChanDoan TEXT AFTER LyDoKham;
ALTER TABLE LICH_HEN ADD COLUMN ToaThuoc TEXT AFTER ChanDoan;

CREATE TABLE IF NOT EXISTS DANH_GIA (
    DanhGiaID INT AUTO_INCREMENT PRIMARY KEY,
    LichHenID INT NOT NULL,
    SoSao INT NOT NULL CHECK (SoSao >= 1 AND SoSao <= 5),
    BinhLuan TEXT,
    NgayDanhGia DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (LichHenID) REFERENCES LICH_HEN(LichHenID),
    UNIQUE KEY uq_LichHen_DanhGia (LichHenID)
);

ALTER TABLE BENH_NHAN ADD COLUMN NhanThongBao TINYINT DEFAULT 1;

ALTER TABLE BENH_NHAN ADD COLUMN ShareToken VARCHAR(100) UNIQUE DEFAULT NULL;