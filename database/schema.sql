CREATE TABLE TAI_KHOAN (
    AccountID INT AUTO_INCREMENT PRIMARY KEY,
    TenDangNhap VARCHAR(100) NOT NULL,   -- email hoặc SĐT
    MatKhau VARCHAR(255) NOT NULL,
    SoDienThoai VARCHAR(20),
    Email VARCHAR(100),
    VaiTro ENUM('BENH_NHAN', 'BAC_SI', 'ADMIN') NOT NULL,
    TrangThai TINYINT DEFAULT 1,         -- 1: hoạt động, 0: khóa
    NgayTao DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_TenDangNhap (TenDangNhap)
);

CREATE TABLE BENH_NHAN (
    PatientID INT AUTO_INCREMENT PRIMARY KEY,
    AccountID INT NOT NULL,
    HoTen VARCHAR(100) NOT NULL,
    NgaySinh DATE,
    GioiTinh ENUM('NAM', 'NU', 'KHAC'),
    DiaChi VARCHAR(255),
    FOREIGN KEY (AccountID) REFERENCES TAI_KHOAN(AccountID)
);

CREATE TABLE CHUYEN_KHOA (
    ChuyenKhoaID INT AUTO_INCREMENT PRIMARY KEY,
    TenChuyenKhoa VARCHAR(100) NOT NULL,
    MoTa TEXT
);

CREATE TABLE BAC_SI (
    BacSiID INT AUTO_INCREMENT PRIMARY KEY,
    AccountID INT NULL,  -- nếu sau này cho bác sĩ đăng nhập
    ChuyenKhoaID INT NOT NULL,
    HoTen VARCHAR(100) NOT NULL,
    HocVan VARCHAR(255),
    KinhNghiemNam INT,
    SoDienThoai VARCHAR(20),
    TrangThai TINYINT DEFAULT 1,
    FOREIGN KEY (ChuyenKhoaID) REFERENCES CHUYEN_KHOA(ChuyenKhoaID),
    FOREIGN KEY (AccountID) REFERENCES TAI_KHOAN(AccountID)
);

CREATE TABLE LICH_HEN (
    LichHenID INT AUTO_INCREMENT PRIMARY KEY,
    PatientID INT NOT NULL,
    BacSiID INT NOT NULL,
    NgayKham DATE NOT NULL,
    GioKham TIME NOT NULL,
    LyDoKham VARCHAR(255),
    TrangThai ENUM('CHO_XAC_NHAN','DA_XAC_NHAN','DA_KHAM','HUY') DEFAULT 'CHO_XAC_NHAN',
    NgayTao DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (PatientID) REFERENCES BENH_NHAN(PatientID),
    FOREIGN KEY (BacSiID) REFERENCES BAC_SI(BacSiID),
    CONSTRAINT uq_LichHen UNIQUE (BacSiID, NgayKham, GioKham)
);

INSERT INTO CHUYEN_KHOA (TenChuyenKhoa, MoTa) VALUES
('Nội tổng quát', 'Khám và điều trị các bệnh nội khoa thường gặp'),
('Nhi', 'Khám và điều trị cho trẻ em'),
('Da liễu', 'Khám và điều trị các bệnh về da');

INSERT INTO BAC_SI (ChuyenKhoaID, HoTen, HocVan, KinhNghiemNam, SoDienThoai)
VALUES
(1, 'BS. Lê Văn Quang', 'BS Nội tổng quát', 5, '0909000001'),
(2, 'BS. Lê Thị Hồng Nhung', 'BS Nhi', 7, '0909000002'),
(3, 'BS. Trần Văn Phục', 'BS Da liễu', 4, '0909000003'),
(3, 'BS. Vũ Quang Du', 'BS Da liễu', 4, '0909000004'),
(3, 'BS. Nguyễn Khắc Phát', 'BS Da liễu', 4, '0909000005');