#đăng ký
if email:
    import re
    pattern = r"^[^@]+@[^@]+\.[^@]+$"
    if not re.match(pattern, email):
        loi.append("Email không hợp lệ.")
else:
    loi.append("Email không được để trống.")

elif len(so_dien_thoai) < 9 or len(so_dien_thoai) > 11:
        loi.append("Số điện thoại không hợp lệ (9–11 số).")


#đăng nhập
from werkzeug.security import generate_password_hash, check_password_hash
mat_khau_hash = generate_password_hash(mat_khau)

# kiểm tra mật khẩu đã mã hóa
    if not check_password_hash(user["MatKhau"], mat_khau):
        loi.append("Sai tên đăng nhập hoặc mật khẩu.")
        return render_template("dang_nhap.html", loi=loi)

#trang benh nhan
# ĐỔI ĐỊNH DẠNG NGÀY: YYYY-MM-DD -> DD/MM/YYYY
    for lh in lich_hen:
        if lh["NgayKham"]:
            lh["NgayKham"] = lh["NgayKham"].strftime("%d/%m/%Y")

#đặt lịch
gio_obj = None
if gio_kham:
    try:
        gio_obj = datetime.strptime(gio_kham, "%H:%M").time()
    except ValueError:
        loi.append("Giờ khám không hợp lệ.")