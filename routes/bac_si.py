# routes/bac_si.py
from flask import Blueprint, render_template, request, redirect, url_for, session
from db import get_connection

bac_si_bp = Blueprint('bac_si', __name__)

@bac_si_bp.route("/quan-ly-lich-hen")
def quan_ly_lich_hen():
    if "account_id" not in session or session["vai_tro"] not in ['ADMIN', 'BAC_SI']:
        return "Bạn không có quyền truy cập."

    conn = get_connection()
    ds_lich_hen = []
    try:
        with conn.cursor() as cur:
            sql = """
                SELECT lh.LichHenID, lh.NgayKham, lh.GioKham, lh.LyDoKham, lh.TrangThai,
                       bn.HoTen AS TenBenhNhan, bn.GioiTinh, bn.NgaySinh, bs.HoTen AS TenBacSi
                FROM LICH_HEN lh
                JOIN BENH_NHAN bn ON lh.PatientID = bn.PatientID
                JOIN BAC_SI bs ON lh.BacSiID = bs.BacSiID
            """
            if session["vai_tro"] == 'BAC_SI':
                cur.execute("SELECT BacSiID FROM BAC_SI WHERE AccountID = %s", (session["account_id"],))
                bs_info = cur.fetchone()
                if bs_info: 
                    sql += f" WHERE lh.BacSiID = {bs_info['BacSiID']}"
            
            sql += " ORDER BY lh.NgayKham DESC, lh.GioKham ASC"
            cur.execute(sql)
            ds_lich_hen = cur.fetchall()
    finally:
        conn.close()
    return render_template("quan_ly_lich_hen.html", ds_lich_hen=ds_lich_hen)

@bac_si_bp.route("/cap-nhat-trang-thai/<int:lich_hen_id>/<trang_thai>", methods=["POST"])
def cap_nhat_trang_thai(lich_hen_id, trang_thai):
    if "account_id" not in session or session["vai_tro"] not in ['ADMIN', 'BAC_SI']:
        return redirect(url_for("auth.dang_nhap"))
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("UPDATE LICH_HEN SET TrangThai = %s WHERE LichHenID = %s", (trang_thai, lich_hen_id))
        conn.commit()
    finally:
        conn.close()
    return redirect(url_for("bac_si.quan_ly_lich_hen"))

@bac_si_bp.route("/luu-ket-qua-kham", methods=["POST"])
def luu_ket_qua_kham():
    if "account_id" not in session or session["vai_tro"] not in ['ADMIN', 'BAC_SI']:
        return redirect(url_for("auth.dang_nhap"))
    lich_hen_id = request.form.get("lich_hen_id")
    chan_doan = request.form.get("chan_doan")
    toa_thuoc = request.form.get("toa_thuoc")
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("UPDATE LICH_HEN SET ChanDoan=%s, ToaThuoc=%s, TrangThai='DA_KHAM' WHERE LichHenID=%s", 
                        (chan_doan, toa_thuoc, lich_hen_id))
        conn.commit()
    finally:
        conn.close()
    return redirect(url_for("bac_si.quan_ly_lich_hen"))