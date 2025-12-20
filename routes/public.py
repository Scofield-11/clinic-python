from flask import Blueprint, render_template
from db import get_connection

public_bp = Blueprint('public', __name__)

@public_bp.route("/thong-tin-phong-kham")
def thong_tin_phong_kham():
    conn = get_connection()
    ds_bac_si = []
    try:
        with conn.cursor() as cur:
            sql = """
                SELECT bs.BacSiID, bs.HoTen, bs.KinhNghiemNam, bs.SoDienThoai, ck.TenChuyenKhoa,
                    COUNT(dg.DanhGiaID) as LuotDanhGia, IFNULL(AVG(dg.SoSao), 0) as DiemTrungBinh
                FROM BAC_SI bs
                JOIN CHUYEN_KHOA ck ON bs.ChuyenKhoaID = ck.ChuyenKhoaID
                LEFT JOIN LICH_HEN lh ON bs.BacSiID = lh.BacSiID
                LEFT JOIN DANH_GIA dg ON lh.LichHenID = dg.LichHenID
                WHERE bs.TrangThai = 1
                GROUP BY bs.BacSiID
                ORDER BY DiemTrungBinh DESC
            """
            cur.execute(sql)
            ds_bac_si = cur.fetchall()
            for bs in ds_bac_si: 
                bs['DiemTrungBinh'] = round(bs['DiemTrungBinh'], 1)
    finally:
        conn.close()

    thong_tin = {
        "ten": "Phòng khám Đa khoa Thuỷ Lợi",
        "dia_chi": "175 Tây Sơn, Đống Đa, Hà Nội",
        "so_dien_thoai": "0903297940",
        "gio_lam_viec": "Thứ 2 - Thứ 7: 7h30 - 17h00"
    }
    return render_template("thong_tin_phong_kham.html", thong_tin=thong_tin, ds_bac_si=ds_bac_si)

@public_bp.route("/ho-so-y-te/<token>")
def xem_ho_so_cong_khai(token):
    conn = get_connection()
    benh_nhan = None
    lich_su_kham = []
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT HoTen, GioiTinh, NgaySinh, DiaChi FROM BENH_NHAN WHERE ShareToken = %s", (token,))
            benh_nhan = cur.fetchone()
            if not benh_nhan: 
                return "Liên kết không tồn tại."
            
            if benh_nhan['NgaySinh']: 
                benh_nhan['NgaySinh'] = benh_nhan['NgaySinh'].strftime("%d/%m/%Y")

            sql_ls = """
                SELECT lh.NgayKham, lh.LyDoKham, lh.ChanDoan, lh.ToaThuoc, bs.HoTen as TenBacSi, ck.TenChuyenKhoa
                FROM LICH_HEN lh
                JOIN BENH_NHAN bn ON lh.PatientID = bn.PatientID
                JOIN BAC_SI bs ON lh.BacSiID = bs.BacSiID
                JOIN CHUYEN_KHOA ck ON bs.ChuyenKhoaID = ck.ChuyenKhoaID
                WHERE bn.ShareToken = %s AND lh.TrangThai = 'DA_KHAM'
                ORDER BY lh.NgayKham DESC
            """
            cur.execute(sql_ls, (token,))
            lich_su_kham = cur.fetchall()
            for ls in lich_su_kham:
                if ls['NgayKham']: ls['NgayKham'] = ls['NgayKham'].strftime("%d/%m/%Y")
    finally:
        conn.close()
    return render_template("ho_so_public.html", bn=benh_nhan, ls=lich_su_kham)