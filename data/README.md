# Data publik pricelist Talented

- `refund.json` — ringkasan refund policy sekolah partner (Australia & New Zealand), dari dokumen resmi tiap sekolah. Diperbarui otomatis setiap bulan oleh Claude (jadwal tanggal 1). Status: Terverifikasi / Perlu konfirmasi / Tidak ditemukan. Website hanya menampilkan ringkasan untuk status Terverifikasi; status lain menampilkan `fallback_text`.

Dipakai oleh https://pricelist.talentededucationgroup.com (dibaca langsung, dengan cache-busting).

- `english.json` — syarat bahasa Inggris (IELTS/PTE) per sekolah partner (Australia & New Zealand) per jenjang + syarat umum visa 500 & NZQA (`general`). Dari sumber resmi sekolah. Diperbarui otomatis setiap bulan bersama refund. Status: Terverifikasi / Sebagian / Belum ditemukan; website memakai syarat umum bila sekolah belum ada.
- `jobs.json` — lowongan kerja pelajar dari Adzuna API (atribusi wajib "Jobs by Adzuna"), diperbarui setiap hari oleh GitHub Actions (`.github/workflows/update-jobs.yml`, `scripts/update_jobs.py`): hanya tanggal posting asli maks. 30 hari, masih tercantum di sumber, tanpa deskripsi lengkap; indikasi penipuan ditahan (`held_for_review`) dan admin diberi issue GitHub. Log: `jobs-log.json`. Butuh secret repo `ADZUNA_APP_ID` dan `ADZUNA_APP_KEY`.
- `accommodation.json` — direktori penyedia akomodasi pelajar resmi (ringkasan fakta + link, tanpa foto/logo), dicek ulang bulanan.
- `rules.json` — hak kerja visa pelajar AU & NZ dan aturan bond sewa per negara bagian/NZ, dari situs pemerintah (dengan tanggal cek).


## Terjemahan (12/11/2026)
- scholarships.json: setiap item wajib punya `i18n.en` (lihat field `maintenance`). Website: `i18n[lang]` -> `i18n.en` -> teks asli.
- accommodation.json: field `<nama>_<lang>` / `<nama>_en` wajib dipakai website (mis. `room_types_en`, `price_period_en`).
- panduan/manifest.json: setiap bab punya `title_en`; pertahankan saat video diperbarui.
