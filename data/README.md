# Data publik pricelist Talented

- `refund.json` — ringkasan refund policy sekolah partner (Australia & New Zealand), dari dokumen resmi tiap sekolah. Diperbarui otomatis setiap bulan oleh Claude (jadwal tanggal 1). Status: Terverifikasi / Perlu konfirmasi / Tidak ditemukan. Website hanya menampilkan ringkasan untuk status Terverifikasi; status lain menampilkan `fallback_text`.

Dipakai oleh https://pricelist.talentededucationgroup.com (dibaca langsung, dengan cache-busting).

- `english.json` — syarat bahasa Inggris (IELTS/PTE) per sekolah partner (Australia & New Zealand) per jenjang + syarat umum visa 500 & NZQA (`general`). Dari sumber resmi sekolah. Diperbarui otomatis setiap bulan bersama refund. Status: Terverifikasi / Sebagian / Belum ditemukan; website memakai syarat umum bila sekolah belum ada.
