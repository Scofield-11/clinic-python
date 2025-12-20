from flask import Blueprint, render_template, request, redirect, url_for, session
from db import get_connection

auth_bp = Blueprint('auth', __name__)

@auth_bp.route("/")
def trang_chu():
    return redirect(url_for("auth.dang_nhap"))

@auth_bp.route("/dang-ky", methods=["GET", "POST"])
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
        loi.append("Mật khẩu không được để trống.")
    if mat_khau and len(mat_khau) < 6:
        loi.append("Mật khẩu phải có ít nhất 6 ký tự.")
    if mat_khau != xac_nhan: 
        loi.append("Mật khẩu không khớp.")
    if not so_dien_thoai: 
        loi.append("Số điện thoại không được để trống.")
    if not email: 
        loi.append("Email không được để trống.")
    
    if loi: 
        return render_template("dang_ky.html", loi=loi)

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT AccountID FROM TAI_KHOAN WHERE TenDangNhap=%s", (ten_dang_nhap,))
            if cur.fetchone():
                return render_template("dang_ky.html", loi=["Tên đăng nhập đã tồn tại."])
            
            sql_tk = "INSERT INTO TAI_KHOAN (TenDangNhap, MatKhau, SoDienThoai, Email, VaiTro, TrangThai) VALUES (%s, %s, %s, %s, 'BENH_NHAN', 1)"
            cur.execute(sql_tk, (ten_dang_nhap, mat_khau, so_dien_thoai, email))
            account_id = cur.lastrowid
            
            sql_bn = "INSERT INTO BENH_NHAN (AccountID, HoTen, NgaySinh, GioiTinh, DiaChi) VALUES (%s, %s, %s, %s, %s)"
            cur.execute(sql_bn, (account_id, ho_ten, ngay_sinh, gioi_tinh, dia_chi))
        conn.commit()
    finally:
        conn.close()

    return redirect(url_for("auth.dang_nhap"))

@auth_bp.route("/dang-nhap", methods=["GET", "POST"])
def dang_nhap():
    if request.method == "GET":
        return render_template("dang_nhap.html")

    ten_dang_nhap = request.form.get("ten_dang_nhap", "").strip()
    mat_khau = request.form.get("mat_khau", "")
    conn = get_connection()
    user = None
    try:
        with conn.cursor() as cur:
            sql = "SELECT AccountID, TenDangNhap, MatKhau, VaiTro, TrangThai FROM TAI_KHOAN WHERE TenDangNhap=%s"
            cur.execute(sql, (ten_dang_nhap,))
            user = cur.fetchone()
            if user:
                user["HoTen"] = user["TenDangNhap"]
                if user["VaiTro"] == "BAC_SI":
                    cur.execute("SELECT HoTen FROM BAC_SI WHERE AccountID = %s", (user["AccountID"],))
                    bs = cur.fetchone()
                    if bs: 
                        user["HoTen"] = bs["HoTen"]
                elif user["VaiTro"] == "BENH_NHAN":
                    cur.execute("SELECT HoTen FROM BENH_NHAN WHERE AccountID = %s", (user["AccountID"],))
                    bn = cur.fetchone()
                    if bn: 
                        user["HoTen"] = bn["HoTen"]
    finally:
        conn.close()

    if not user or user["MatKhau"] != mat_khau:
        return render_template("dang_nhap.html", loi=["Sai tên đăng nhập hoặc mật khẩu."])
    
    if user["TrangThai"] != 1:
        return render_template("dang_nhap.html", loi=["Tài khoản đã bị khóa."])

    session["account_id"] = user["AccountID"]
    session["ten_dang_nhap"] = user["TenDangNhap"]
    session["vai_tro"] = user["VaiTro"]
    session["ho_ten"] = user["HoTen"]

    if user["VaiTro"] == "BENH_NHAN":
        return redirect(url_for("benh_nhan.trang_benh_nhan"))
    else:
        return redirect(url_for("bac_si.quan_ly_lich_hen"))

@auth_bp.route("/dang-xuat")
def dang_xuat():
    session.clear()
    return redirect(url_for("auth.dang_nhap"))