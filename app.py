from flask import Flask, render_template, request, redirect, url_for, session
import pymysql
from datetime import datetime, date

app = Flask(__name__)
app.secret_key = "06081983"

def get_connection():
    conn = pymysql.connect(
        host="localhost",
        user="root",
        password="",
        database="clinic_db",
        cursorclass=pymysql.cursors.DictCursor
    )
    return conn

@app.route("/")
def trang_chu():
    return redirect(url_for("dang_nhap"))

@app.route("/dang-ky", methods=["GET", "POST"])
def dang_ky():
    if request.method == "GET":
        return render_template("dang_ky.html")

    ten_dang_nhap = request.form.get("ten_dang_nhap", "").strip()
    mat_khau = request.form.get("mat_khau", "")
    xac_nhan = request.form.get("xac_nhan_mat_khau", "")
    ho_ten = request.form.get("ho_ten", "").strip()
    so_dien_thoai = request.form.get("so_dien_thoai", "").strip()
    email = request.form.get("email", "").strip()
    ngay_sinh = request.form.get("ngay_sinh", None)
    gioi_tinh = request.form.get("gioi_tinh", None)
    dia_chi = request.form.get("dia_chi", "").strip()

    loi = []
    if not ten_dang_nhap:
        loi.append("Tên đăng nhập không được để trống.")
    if not ho_ten:
        loi.append("Họ tên không được để trống.")
    if not mat_khau or not xac_nhan:
        loi.append("Mật khẩu và xác nhận mật khẩu không được để trống.")
    if mat_khau and len(mat_khau) < 6:
        loi.append("Mật khẩu phải có ít nhất 6 ký tự.")
    if mat_khau != xac_nhan:
        loi.append("Mật khẩu và xác nhận mật khẩu không trùng khớp.")
    if not so_dien_thoai:
        loi.append("Số điện thoại không được để trống.")
    if not email:
        loi.append("Email không được để trống.")
    
    if loi:
        return render_template("dang_ky.html", loi=loi)

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT AccountID FROM TAI_KHOAN WHERE TenDangNhap=%s",
                (ten_dang_nhap,)
            )
            if cur.fetchone():
                loi.append("Tên đăng nhập đã tồn tại.")
                return render_template("dang_ky.html", loi=loi)

            cur.execute(
                "SELECT AccountID FROM TAI_KHOAN WHERE SoDienThoai=%s",
                (so_dien_thoai,)
            )
            if cur.fetchone():
                loi.append("Số điện thoại đã được sử dụng.")
                return render_template("dang_ky.html", loi=loi)

            cur.execute(
                "SELECT AccountID FROM TAI_KHOAN WHERE Email=%s",
                (email,)
            )
            if cur.fetchone():
                loi.append("Email đã được sử dụng.")
                return render_template("dang_ky.html", loi=loi)

            sql_tk = """
                INSERT INTO TAI_KHOAN 
                    (TenDangNhap, MatKhau, SoDienThoai, Email, VaiTro, TrangThai)
                VALUES (%s, %s, %s, %s, 'BENH_NHAN', 1)
            """
            cur.execute(sql_tk, (ten_dang_nhap, mat_khau, so_dien_thoai, email))
            account_id = cur.lastrowid

            sql_bn = """
                INSERT INTO BENH_NHAN (AccountID, HoTen, NgaySinh, GioiTinh, DiaChi)
                VALUES (%s, %s, %s, %s, %s)
            """
            cur.execute(sql_bn, (account_id, ho_ten, ngay_sinh, gioi_tinh, dia_chi))

        conn.commit()
    finally:
        conn.close()

    return redirect(url_for("dang_nhap"))



@app.route("/dang-nhap", methods=["GET", "POST"])
def dang_nhap():
    if request.method == "GET":
        return render_template("dang_nhap.html")

    ten_dang_nhap = request.form.get("ten_dang_nhap", "").strip()
    mat_khau = request.form.get("mat_khau", "")

    loi = []
    if not ten_dang_nhap or not mat_khau:
        loi.append("Vui lòng nhập đầy đủ tên đăng nhập và mật khẩu.")
        return render_template("dang_nhap.html", loi=loi)

    conn = get_connection()
    user = None
    try:
        with conn.cursor() as cur:
            sql = """
                SELECT AccountID, TenDangNhap, MatKhau, VaiTro, TrangThai
                FROM TAI_KHOAN
                WHERE TenDangNhap=%s
            """
            cur.execute(sql, (ten_dang_nhap,))
            user = cur.fetchone()
    finally:
        conn.close()

    if not user:
        loi.append("Sai tên đăng nhập hoặc mật khẩu.")
        return render_template("dang_nhap.html", loi=loi)

    if user["TrangThai"] != 1:
        loi.append("Tài khoản đã bị khóa. Vui lòng liên hệ phòng khám.")
        return render_template("dang_nhap.html", loi=loi)

    if user["MatKhau"] != mat_khau:
        loi.append("Sai tên đăng nhập hoặc mật khẩu.")
        return render_template("dang_nhap.html", loi=loi)

    # Lưu session
    session["account_id"] = user["AccountID"]
    session["ten_dang_nhap"] = user["TenDangNhap"]
    session["vai_tro"] = user["VaiTro"]

    return redirect(url_for("trang_benh_nhan"))



# -------- LOGOUT --------
@app.route("/dang-xuat")
def dang_xuat():
    session.clear()
    return redirect(url_for("dang_nhap"))

# -------- US03: XEM THÔNG TIN PHÒNG KHÁM & DANH SÁCH BÁC SĨ --------
@app.route("/thong-tin-phong-kham")
def thong_tin_phong_kham():
    conn = get_connection()
    ds_bac_si = []
    try:
        with conn.cursor() as cur:
            sql = """
                SELECT 
                    bs.BacSiID,
                    bs.HoTen,
                    bs.KinhNghiemNam,
                    bs.SoDienThoai,
                    ck.TenChuyenKhoa
                FROM BAC_SI bs
                JOIN CHUYEN_KHOA ck ON bs.ChuyenKhoaID = ck.ChuyenKhoaID
                WHERE bs.TrangThai = 1
                ORDER BY ck.TenChuyenKhoa, bs.HoTen
            """
            cur.execute(sql)
            ds_bac_si = cur.fetchall()
    finally:
        conn.close()

    thong_tin = {
        "ten": "Phòng khám Đa khoa Thuỷ Lợi",
        "dia_chi": "175 Tây Sơn, Đống Đa, Hà Nội",
        "so_dien_thoai": "0903297940",
        "gio_lam_viec": "Thứ 2 - Thứ 7: 7h30 - 17h00"
    }

    return render_template("thong_tin_phong_kham.html",
                           thong_tin=thong_tin,
                           ds_bac_si=ds_bac_si)

@app.route("/trang-benh-nhan")
def trang_benh_nhan():
    if "account_id" not in session:
        return redirect(url_for("dang_nhap"))

    account_id = session["account_id"]
    conn = get_connection()
    lich_hen = []
    try:
        with conn.cursor() as cur:
            sql = """
                SELECT lh.LichHenID, lh.NgayKham, lh.GioKham, lh.TrangThai,
                       bs.HoTen AS TenBacSi
                FROM LICH_HEN lh
                JOIN BENH_NHAN bn ON lh.PatientID = bn.PatientID
                JOIN BAC_SI bs ON lh.BacSiID = bs.BacSiID
                WHERE bn.AccountID = %s
                ORDER BY lh.NgayKham DESC, lh.GioKham DESC
            """
            cur.execute(sql, (account_id,))
            lich_hen = cur.fetchall()

            
    finally:
        conn.close()

    return render_template(
        "trang_benh_nhan.html",
        ten_dang_nhap=session.get("ten_dang_nhap"),
        lich_hen=lich_hen
    )


@app.route("/dat-lich", methods=["GET", "POST"])
def dat_lich():
    if "account_id" not in session:
        return redirect(url_for("dang_nhap"))

    account_id = session["account_id"]

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT PatientID FROM BENH_NHAN WHERE AccountID = %s",
                (account_id,)
            )
            bn = cur.fetchone()
            if not bn:
                return "Không tìm thấy thông tin bệnh nhân. Vui lòng liên hệ quản trị."
            patient_id = bn["PatientID"]

            cur.execute(
                "SELECT BacSiID, HoTen FROM BAC_SI WHERE TrangThai = 1"
            )
            ds_bac_si = cur.fetchall()

            if request.method == "GET":
                return render_template("dat_lich.html", ds_bac_si=ds_bac_si)

            bac_si_id = request.form.get("bac_si", "").strip()
            ngay_kham = request.form.get("ngay_kham", "").strip()
            gio_kham = request.form.get("gio_kham", "").strip()
            ly_do = request.form.get("ly_do", "").strip()

            loi = []

            if not bac_si_id:
                loi.append("Vui lòng chọn bác sĩ.")
            if not ngay_kham:
                loi.append("Vui lòng chọn ngày khám.")
            if not gio_kham:
                loi.append("Vui lòng chọn giờ khám.")

            ngay_obj = None
            if ngay_kham:
                try:
                    ngay_obj = datetime.strptime(ngay_kham, "%Y-%m-%d").date()
                    if ngay_obj < date.today():
                        loi.append("Ngày khám phải từ hôm nay trở về sau.")
                except ValueError:
                    loi.append("Ngày khám không hợp lệ.")

            if loi:
                return render_template(
                    "dat_lich.html",
                    ds_bac_si=ds_bac_si,
                    loi=loi
                )

            sql_check_bs = """
                SELECT LichHenID 
                FROM LICH_HEN
                WHERE BacSiID = %s 
                  AND NgayKham = %s 
                  AND GioKham = %s
                  AND TrangThai <> 'HUY'
            """
            cur.execute(sql_check_bs, (bac_si_id, ngay_kham, gio_kham))
            if cur.fetchone():
                loi.append("Khung giờ này bác sĩ đã có lịch. Vui lòng chọn giờ khác.")
                return render_template("dat_lich.html", ds_bac_si=ds_bac_si, loi=loi)

            sql_check_bn = """
                SELECT LichHenID 
                FROM LICH_HEN
                WHERE PatientID = %s
                  AND NgayKham = %s
                  AND GioKham = %s
                  AND TrangThai <> 'HUY'
            """
            cur.execute(sql_check_bn, (patient_id, ngay_kham, gio_kham))
            if cur.fetchone():
                loi.append("Bạn đã có lịch khám ở khung giờ này.")
                return render_template("dat_lich.html", ds_bac_si=ds_bac_si, loi=loi)

            sql_insert = """
                INSERT INTO LICH_HEN 
                    (PatientID, BacSiID, NgayKham, GioKham, LyDoKham, TrangThai)
                VALUES (%s, %s, %s, %s, %s, 'CHO_XAC_NHAN')
            """
            cur.execute(sql_insert, (patient_id, bac_si_id, ngay_kham, gio_kham, ly_do))
            conn.commit()

            return redirect(url_for("trang_benh_nhan"))

    finally:
        conn.close()

    return render_template("dat_lich.html", ds_bac_si=ds_bac_si)

@app.route("/huy-lich/<int:lich_hen_id>", methods=["POST"])
def huy_lich(lich_hen_id):
    if "account_id" not in session:
        return redirect(url_for("dang_nhap"))

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE LICH_HEN lh
                JOIN BENH_NHAN bn ON lh.PatientID = bn.PatientID
                SET lh.TrangThai = 'HUY'
                WHERE lh.LichHenID = %s
                  AND bn.AccountID = %s
                  AND lh.TrangThai IN ('CHO_XAC_NHAN', 'DA_XAC_NHAN')
            """, (lich_hen_id, session["account_id"]))

        conn.commit()
    finally:
        conn.close()

    return redirect(url_for("trang_benh_nhan"))

if __name__ == "__main__":
    app.run(debug=True)
