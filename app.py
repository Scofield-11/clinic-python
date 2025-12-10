from flask import Flask, render_template, request, redirect, url_for, session
import pymysql

app = Flask(__name__)
app.secret_key = "bi_mat_cua_ban"  # sau này có thể đổi

# Hàm kết nối MySQL
def get_connection():
    conn = pymysql.connect(
        host="localhost",
        user="root",        # sửa nếu MySQL khác
        password="",        # sửa nếu có mật khẩu
        database="clinic_db",
        cursorclass=pymysql.cursors.DictCursor
    )
    return conn


# Trang gốc: chuyển tới đăng nhập
@app.route("/")
def trang_chu():
    return redirect(url_for("dang_nhap"))


# -------- ĐĂNG KÝ --------
@app.route("/dang-ky", methods=["GET", "POST"])
def dang_ky():
    if request.method == "GET":
        return render_template("dang_ky.html")

    # POST: xử lý dữ liệu form
    ten_dang_nhap = request.form.get("ten_dang_nhap", "").strip()
    mat_khau = request.form.get("mat_khau", "")
    xac_nhan = request.form.get("xac_nhan_mat_khau", "")
    ho_ten = request.form.get("ho_ten", "").strip()
    so_dien_thoai = request.form.get("so_dien_thoai", "").strip()
    ngay_sinh = request.form.get("ngay_sinh", None)
    gioi_tinh = request.form.get("gioi_tinh", None)
    dia_chi = request.form.get("dia_chi", "").strip()

    loi = []
    if not ten_dang_nhap:
        loi.append("Tên đăng nhập không được để trống.")
    if not so_dien_thoai:
        loi.append("Số điện thoại không được để trống.")
    elif len(so_dien_thoai) < 9 or len(so_dien_thoai) > 11:
        loi.append("Số điện thoại không hợp lệ (9-11 số).")
    if not ho_ten:
        loi.append("Họ tên không được để trống.")
    if not mat_khau or not xac_nhan:
        loi.append("Mật khẩu và xác nhận mật khẩu không được để trống.")
    if mat_khau and len(mat_khau) < 6:
        loi.append("Mật khẩu phải có ít nhất 6 ký tự.")
    if mat_khau != xac_nhan:
        loi.append("Mật khẩu và xác nhận mật khẩu không trùng khớp.")

    if loi:
        # render lại form + danh sách lỗi
        return render_template("dang_ky.html", loi=loi)

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # kiểm tra trùng tên đăng nhập
            cur.execute(
                "SELECT AccountID FROM TAI_KHOAN WHERE TenDangNhap=%s",
                (ten_dang_nhap,)
            )
            if cur.fetchone():
                loi.append("Tên đăng nhập đã tồn tại.")
                return render_template("dang_ky.html", loi=loi)

            # Đơn giản: lưu mật khẩu dạng plain text cho dễ (thực tế nên hash)
            sql_tk = """
                INSERT INTO TAI_KHOAN (TenDangNhap, MatKhau, SoDienThoai, VaiTro, TrangThai)
                VALUES (%s, %s, %s, 'BENH_NHAN', 1)
            """
            cur.execute(sql_tk, (ten_dang_nhap, mat_khau, so_dien_thoai))
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


# -------- ĐĂNG NHẬP --------
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
                SELECT AccountID, TenDangNhap, MatKhau, VaiTro
                FROM TAI_KHOAN
                WHERE TenDangNhap=%s AND MatKhau=%s AND TrangThai=1
            """
            cur.execute(sql, (ten_dang_nhap, mat_khau))
            user = cur.fetchone()
    finally:
        conn.close()

    if not user:
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


# -------- TRANG BỆNH NHÂN --------
@app.route("/trang-benh-nhan")
def trang_benh_nhan():
    if "account_id" not in session:
        return redirect(url_for("dang_nhap"))

    account_id = session["account_id"]

    # Lấy danh sách lịch hẹn của bệnh nhân
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


# -------- ĐẶT LỊCH KHÁM --------
@app.route("/dat-lich", methods=["GET", "POST"])
def dat_lich():
    if "account_id" not in session:
        return redirect(url_for("dang_nhap"))

    account_id = session["account_id"]

    conn = get_connection()
    # Lấy PatientID từ AccountID
    patient_id = None
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT PatientID FROM BENH_NHAN WHERE AccountID=%s",
                (account_id,)
            )
            row = cur.fetchone()
            if not row:
                return "Không tìm thấy bệnh nhân."
            patient_id = row["PatientID"]

            # Lấy danh sách bác sĩ
            cur.execute(
                "SELECT BacSiID, HoTen FROM BAC_SI WHERE TrangThai=1"
            )
            ds_bac_si = cur.fetchall()

            if request.method == "POST":
                bac_si_id = request.form.get("bac_si")
                ngay_kham = request.form.get("ngay_kham")
                gio_kham = request.form.get("gio_kham")
                ly_do = request.form.get("ly_do", "").strip()

                loi = []
                if not bac_si_id:
                    loi.append("Vui lòng chọn bác sĩ.")
                if not ngay_kham:
                    loi.append("Vui lòng chọn ngày khám.")
                if not gio_kham:
                    loi.append("Vui lòng chọn giờ khám.")

                if loi:
                    return render_template(
                        "dat_lich.html",
                        ds_bac_si=ds_bac_si,
                        loi=loi
                    )

                # Kiểm tra trùng lịch
                sql_check = """
                    SELECT LichHenID FROM LICH_HEN
                    WHERE BacSiID=%s AND NgayKham=%s AND GioKham=%s
                """
                cur.execute(sql_check, (bac_si_id, ngay_kham, gio_kham))
                if cur.fetchone():
                    loi.append("Khung giờ này bác sĩ đã có lịch, vui lòng chọn giờ khác.")
                    return render_template("dat_lich.html", ds_bac_si=ds_bac_si, loi=loi)

                # Insert lịch hẹn
                sql_insert = """
                    INSERT INTO LICH_HEN (PatientID, BacSiID, NgayKham, GioKham, LyDoKham, TrangThai)
                    VALUES (%s, %s, %s, %s, %s, 'CHO_XAC_NHAN')
                """
                cur.execute(sql_insert, (patient_id, bac_si_id, ngay_kham, gio_kham, ly_do))
                conn.commit()

                return redirect(url_for("trang_benh_nhan"))

    finally:
        conn.close()

    # GET: hiện form
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT BacSiID, HoTen FROM BAC_SI WHERE TrangThai=1"
            )
            ds_bac_si = cur.fetchall()
    finally:
        conn.close()

    return render_template("dat_lich.html", ds_bac_si=ds_bac_si)


if __name__ == "__main__":
    app.run(debug=True)
