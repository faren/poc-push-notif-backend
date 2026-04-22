import os
import random
import time
from datetime import datetime, timedelta

import pymssql

# ─── Config ───────────────────────────────────────────────────────────────────
DB_HOST     = os.getenv("DB_HOST", "sqlserver")
DB_PASSWORD = os.getenv("DB_PASSWORD", "BpjsSimul@si2026")
DB_NAME     = os.getenv("DB_NAME", "DBMobile")

DAYS_BACK   = 30
BATCH_SIZE  = 2000

# ─── Status distribution (index = status value) ───────────────────────────────
# 0=Baru, 1=Berhasil Dikirim, 2=Gagal-Token, 3=Gagal-Server, 4=Diterima, 5=Dibaca
STATUS_VALUES  = [0,  1,  2,  3,  4,  5]
STATUS_WEIGHTS = [3,  5,  18, 2,  50, 22]

# ─── Jenis Notifikasi ─────────────────────────────────────────────────────────
JENIS = [
    (1,  7),   # Tagihan Iuran
    (5,  20),  # Rating Pelayanan
    (13, 30),  # Info Kepesertaan
    (15, 25),  # Antrean
    (16, 3),   # Info Pelayanan
    (21, 15),  # Pengaduan / Keluhan
]
JENIS_CODES   = [j[0] for j in JENIS]
JENIS_WEIGHTS = [j[1] for j in JENIS]

# ─── Content per KdJnsNotif ───────────────────────────────────────────────────
JUDUL = {
    1:  ["Tagihan Iuran BPJS Kesehatan",
         "Pengingat Pembayaran Iuran",
         "Konfirmasi Pembayaran Iuran"],
    5:  ["Evaluasi Layanan Fasilitas Kesehatan",
         "Penilaian Layanan Dokter",
         "Rating Pelayanan Faskes"],
    13: ["Info Kepesertaan",
         "Rencana Non Aktif Peserta PBI",
         "Info Penonaktifan Peserta",
         "Perubahan Status Kepesertaan"],
    15: ["Pendaftaran Antrean Berhasil",
         "Pembatalan Antrean",
         "Pengingat Jadwal Antrean",
         "Konfirmasi Jadwal Antrean"],
    16: ["Info Pelayanan Konsultasi Dokter",
         "Informasi Layanan BPJS",
         "Update Kebijakan Layanan"],
    21: ["Tindak Lanjut Pengaduan",
         "Update Status Pengaduan",
         "Konfirmasi Pengaduan Diterima"],
}

PESAN = {
    1:  ["Iuran BPJS Kesehatan Anda belum dibayarkan. Segera lakukan pembayaran untuk menghindari penonaktifan kepesertaan.",
         "Pengingat: Iuran BPJS Kesehatan Anda akan jatuh tempo. Pastikan pembayaran tepat waktu."],
    5:  ["Bagaimana pengalaman layanan Anda? Berikan penilaian melalui aplikasi Mobile JKN.",
         "Kami mengundang Anda untuk memberikan penilaian atas layanan yang telah Anda terima. Klik untuk memberi rating."],
    13: ["Status kepesertaan BPJS Kesehatan Anda berpotensi akan dinonaktifkan. Silakan hubungi kantor BPJS terdekat.",
         "Kepesertaan BPJS Kesehatan Anda telah aktif kembali. Anda dapat menggunakan layanan kesehatan seperti biasa.",
         "Terdapat perubahan status kepesertaan Anda. Silakan cek detail melalui aplikasi Mobile JKN."],
    15: ["Pendaftaran antrean Anda berhasil. Harap datang tepat waktu sesuai jadwal yang ditentukan.",
         "Antrean Anda telah dibatalkan. Silakan daftar kembali melalui aplikasi Mobile JKN jika diperlukan.",
         "Pengingat: Jadwal antrean Anda adalah hari ini. Pastikan Anda membawa kartu BPJS Kesehatan."],
    16: ["Jadwal dokter spesialis di fasilitas kesehatan Anda telah diperbarui. Cek aplikasi Mobile JKN untuk detail.",
         "BPJS Kesehatan telah memperbarui kebijakan layanan. Silakan baca informasi terbaru melalui aplikasi."],
    21: ["Pengaduan Anda sedang dalam proses penanganan. Tim kami akan segera menghubungi Anda.",
         "Pengaduan Anda telah berhasil diterima. Estimasi penyelesaian 3-5 hari kerja.",
         "Tindak lanjut pengaduan Anda telah diperbarui. Silakan cek status melalui aplikasi Mobile JKN."],
}

FCM_ERRORS = {
    2: [
        "Exactly one of token, topic or condition must be specified",
        "The registration token is not a valid FCM registration token",
        "Requested entity was not found.",
        "The provided registration token is not registered.",
    ],
    3: [
        "Internal Server Error",
        "Service temporarily unavailable. Please try again",
        "Quota exceeded for quota metric 'clouderrorreporting.googleapis.com'",
    ],
}

# Hourly send distribution (index = hour 0-23)
HOUR_WEIGHTS = [1,1,1,1,1,2,3,5,8,9,8,7,8,7,7,7,6,5,6,6,5,4,3,2]


# ─── Helpers ──────────────────────────────────────────────────────────────────
def random_nokapst():
    return str(random.randint(1000000000, 9999999999))

def random_userid():
    return random.randint(100_000, 9_999_999)

def random_fdate(base_date):
    hour   = random.choices(range(24), weights=HOUR_WEIGHTS)[0]
    minute = random.randint(0, 59)
    second = random.randint(0, 59)
    return base_date + timedelta(hours=hour, minutes=minute, seconds=second)

def build_row(base_date):
    kd_jns = random.choices(JENIS_CODES, weights=JENIS_WEIGHTS)[0]
    status = random.choices(STATUS_VALUES, weights=STATUS_WEIGHTS)[0]
    fdate  = random_fdate(base_date)

    send_date = (fdate + timedelta(seconds=random.randint(3, 30))) if status > 0 else None
    response  = random.choice(FCM_ERRORS[status]) if status in FCM_ERRORS else None

    return (
        random_nokapst(),               # Nokapst
        kd_jns,                         # KdJnsNotif
        random.choice(PESAN[kd_jns]),   # Pesan
        status,                         # Status
        0,                              # FUser (0 = system)
        fdate,                          # FDate
        send_date,                      # SendDate
        random.choice(JUDUL[kd_jns]),   # Judul
        response,                       # Response
        fdate,                          # Schedule
        None,                           # Parameter
        random_userid(),                # UserID
    )


# ─── DB connection with retry ─────────────────────────────────────────────────
def connect_with_retry(max_attempts=30, delay=5):
    for attempt in range(1, max_attempts + 1):
        try:
            conn = pymssql.connect(
                server=DB_HOST, user="sa",
                password=DB_PASSWORD, database=DB_NAME,
                timeout=10
            )
            print(f"[generator] Connected to SQL Server ({DB_HOST})")
            return conn
        except Exception as e:
            print(f"[generator] Attempt {attempt}/{max_attempts}: {e}")
            time.sleep(delay)
    raise RuntimeError("Could not connect to SQL Server after all retries")


# ─── Main ─────────────────────────────────────────────────────────────────────
INSERT_SQL = """
INSERT INTO [dbo].[Notifikasi]
    (Nokapst, KdJnsNotif, Pesan, Status, FUser, FDate, SendDate,
     Judul, Response, Schedule, Parameter, UserID)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
"""

def main():
    conn   = connect_with_retry()
    cursor = conn.cursor()

    today         = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    total_inserted = 0

    for day_offset in range(DAYS_BACK, -1, -1):
        base_date = today - timedelta(days=day_offset)
        weekday   = base_date.weekday()

        # Higher volume on weekdays, lower on weekends
        daily_count = (
            random.randint(40_000, 80_000) if weekday < 5
            else random.randint(15_000, 35_000)
        )

        print(f"[generator] {base_date.strftime('%Y-%m-%d')} ({['Mon','Tue','Wed','Thu','Fri','Sat','Sun'][weekday]}) → {daily_count:,} rows")

        for offset in range(0, daily_count, BATCH_SIZE):
            batch = [build_row(base_date) for _ in range(min(BATCH_SIZE, daily_count - offset))]
            cursor.executemany(INSERT_SQL, batch)
            conn.commit()
            total_inserted += len(batch)

    cursor.close()
    conn.close()
    print(f"\n[generator] Done. Total inserted: {total_inserted:,}")


if __name__ == "__main__":
    main()
