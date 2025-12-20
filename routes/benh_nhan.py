# routes/benh_nhan.py
from flask import Blueprint, render_template, request, redirect, url_for, session
from db import get_connection
from datetime import datetime
import uuid

benh_nhan_bp = Blueprint('benh_nhan', __name__)

# --- 1. TRANG CHỦ BỆNH NHÂN (Đã bỏ logic lấy Token) ---
@benh_nhan_bp.route("/trang-benh-nhan")
def trang_benh_nhan():
    if "account_id" not in session: return redirect(url_for("auth.dang_nhap"))
    
    account_id = session["account_id"]
    conn = get_connection()
    lich_hen = []
    thong_bao_nhac_lich = []
    cai_dat_thong_bao = 1
    # Đã bỏ share_token ở đây vì không cần hiển thị QR code tại dashboard nữa

    try:
        with conn.cursor() as cur:
            # Chỉ lấy cài đặt thông báo
            cur.execute("SELECT NhanThongBao FROM BENH_NHAN WHERE AccountID = %s", (account_id,))
            bn_info = cur.fetchone()
            if bn_info:
                cai_dat_thong_bao = bn_info["NhanThongBao"]

            # Lấy danh sách lịch hẹn
            sql = """
                SELECT lh.LichHenID, lh.NgayKham, lh.GioKham, lh.TrangThai,
                       bs.HoTen AS TenBacSi, dg.SoSao
                FROM LICH_HEN lh
                JOIN BENH_NHAN bn ON lh.PatientID = bn.PatientID
                JOIN BAC_SI bs ON lh.BacSiID = bs.BacSiID
                LEFT JOIN DANH_GIA dg ON lh.LichHenID = dg.LichHenID
                WHERE bn.AccountID = %s
                ORDER BY lh.NgayKham DESC, lh.GioKham DESC
            """
            cur.execute(sql, (account_id,))
            lich_hen = cur.fetchall()

            # Logic nhắc lịch
            if cai_dat_thong_bao == 1:
                now = datetime.now()
                for lh in lich_hen:
                    if lh["TrangThai"] == 'DA_XAC_NHAN':
                        gio_kham_time = (datetime.min + lh["GioKham"]).time()
                        thoi_gian_kham = datetime.combine(lh["NgayKham"], gio_kham_time)
                        diff = thoi_gian_kham - now
                        seconds_diff = diff.total_seconds()
                        if 0 <= seconds_diff <= 86400:
                            msg = f"Sắp đến lịch khám với {lh['TenBacSi']} ngày {lh['NgayKham'].strftime('%d/%m')} lúc {lh['GioKham']}."
                            thong_bao_nhac_lich.append(msg)

            for lh in lich_hen:
                if lh["NgayKham"]: lh["NgayKham"] = lh["NgayKham"].strftime("%d/%m/%Y")
            
    finally:
        conn.close()

    return render_template("trang_benh_nhan.html",
        lich_hen=lich_hen,
        thong_bao_nhac_lich=thong_bao_nhac_lich,
        cai_dat_thong_bao=cai_dat_thong_bao
    )

# --- 2. HÀM MỚI: QUẢN LÝ CHIA SẺ (Trang riêng) ---
@benh_nhan_bp.route("/quan-ly-chia-se")
def quan_ly_chia_se():
    if "account_id" not in session: return redirect(url_for("auth.dang_nhap"))
    
    conn = get_connection()
    share_token = None
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT ShareToken FROM BENH_NHAN WHERE AccountID = %s", (session["account_id"],))
            bn = cur.fetchone()
            if bn:
                share_token = bn["ShareToken"]
    finally:
        conn.close()
        
    return render_template("quan_ly_chia_se.html", share_token=share_token)


# --- 3. XỬ LÝ TẠO/HỦY LINK (Redirect về trang quản lý mới) ---
@benh_nhan_bp.route("/tao-lien-ket-chia-se", methods=["POST"])
def tao_lien_ket_chia_se():
    if "account_id" not in session: return redirect(url_for("auth.dang_nhap"))
    
    action = request.form.get("hanh_dong")
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            token = str(uuid.uuid4()) if action == "tao" else None
            cur.execute("UPDATE BENH_NHAN SET ShareToken = %s WHERE AccountID = %s", (token, session["account_id"]))
        conn.commit()
    finally:
        conn.close()
    
    # Quan trọng: Redirect về trang quản lý chia sẻ, KHÔNG phải trang bệnh nhân
    return redirect(url_for("benh_nhan.quan_ly_chia_se"))


@benh_nhan_bp.route("/dat-lich", methods=["GET", "POST"])
def dat_lich():
    if "account_id" not in session: return redirect(url_for("auth.dang_nhap"))
    account_id = session["account_id"]
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT PatientID FROM BENH_NHAN WHERE AccountID = %s", (account_id,))
            bn = cur.fetchone()
            if not bn: return "Lỗi: Không tìm thấy thông tin bệnh nhân."
            patient_id = bn["PatientID"]

            cur.execute("SELECT BacSiID, HoTen FROM BAC_SI WHERE TrangThai = 1")
            ds_bac_si = cur.fetchall()

            if request.method == "GET":
                return render_template("dat_lich.html", ds_bac_si=ds_bac_si)

            bac_si_id = request.form.get("bac_si")
            ngay_kham = request.form.get("ngay_kham")
            gio_kham = request.form.get("gio_kham")
            ly_do = request.form.get("ly_do")

            sql_insert = "INSERT INTO LICH_HEN (PatientID, BacSiID, NgayKham, GioKham, LyDoKham, TrangThai) VALUES (%s, %s, %s, %s, %s, 'CHO_XAC_NHAN')"
            cur.execute(sql_insert, (patient_id, bac_si_id, ngay_kham, gio_kham, ly_do))
            conn.commit()
            return redirect(url_for("benh_nhan.trang_benh_nhan"))
    finally:
        conn.close()

@benh_nhan_bp.route("/huy-lich/<int:lich_hen_id>", methods=["POST"])
def huy_lich(lich_hen_id):
    if "account_id" not in session: return redirect(url_for("auth.dang_nhap"))
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE LICH_HEN lh JOIN BENH_NHAN bn ON lh.PatientID = bn.PatientID
                SET lh.TrangThai = 'HUY'
                WHERE lh.LichHenID = %s AND bn.AccountID = %s AND lh.TrangThai IN ('CHO_XAC_NHAN', 'DA_XAC_NHAN')
            """, (lich_hen_id, session["account_id"]))
        conn.commit()
    finally:
        conn.close()
    return redirect(url_for("benh_nhan.trang_benh_nhan"))

@benh_nhan_bp.route("/danh-gia/<int:lich_hen_id>", methods=["GET", "POST"])
def danh_gia(lich_hen_id):
    if "account_id" not in session: return redirect(url_for("auth.dang_nhap"))
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT lh.LichHenID, bs.HoTen as TenBacSi, lh.NgayKham
                FROM LICH_HEN lh JOIN BENH_NHAN bn ON lh.PatientID = bn.PatientID JOIN BAC_SI bs ON lh.BacSiID = bs.BacSiID
                WHERE lh.LichHenID = %s AND bn.AccountID = %s AND lh.TrangThai = 'DA_KHAM'
            """, (lich_hen_id, session["account_id"]))
            lich = cur.fetchone()
            if not lich: return "Lỗi: Lịch hẹn không hợp lệ."

            if request.method == "GET":
                return render_template("danh_gia.html", lich=lich)

            so_sao = request.form.get("so_sao")
            binh_luan = request.form.get("binh_luan", "")
            cur.execute("INSERT INTO DANH_GIA (LichHenID, SoSao, BinhLuan) VALUES (%s, %s, %s)", (lich_hen_id, so_sao, binh_luan))
            conn.commit()
            return redirect(url_for("benh_nhan.trang_benh_nhan"))
    finally:
        conn.close()

@benh_nhan_bp.route("/cai-dat-thong-bao", methods=["POST"])
def xu_ly_cai_dat_thong_bao():
    if "account_id" not in session: return redirect(url_for("auth.dang_nhap"))
    trang_thai = 1 if request.form.get("nhan_thong_bao") == "on" else 0
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("UPDATE BENH_NHAN SET NhanThongBao = %s WHERE AccountID = %s", (trang_thai, session["account_id"]))
        conn.commit()
    finally:
        conn.close()
    return redirect(url_for("benh_nhan.trang_benh_nhan"))