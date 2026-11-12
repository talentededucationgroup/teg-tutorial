# Generator soal mock test (sumber)

Skrip Python yang dipakai untuk membuat bank soal & audio latihan buatan Talented (bukan soal resmi).
Disimpan di sini sebagai sumber yang bisa diaudit; tidak dijalankan oleh website.

- `t3_n3.py`, `t3_n2.py`, `t3_n1.py` - isi soal JLPT N3/N2/N1; `t3_build.py bank|ssml <modul>` menyusun bagian ke `banks/jlpt.json` dan SSML audio 聴解.
- `t3_lis.py bank|ssml` - 発話表現 (N5-N3, ilustrasi `t3_svg.py` -> `img/jlpt/`) & 即時応答 (N5-N1); pilihan dibacakan di audio, urutan pilihan dikunci (`shuffle:false`, `aopts:true`). Jalankan **setelah** `t3_build.py` karena menimpa slot l4/l5.
- `t4_*.py` - perbesaran bank T4 Tahap 1 (JLPT N5/N4, HSK, TOPIK I, IELTS, PTE).
- `t4_split.py` - memotong audio TTS kelompok (SSML) di jeda panjang menjadi file per set; mono 24 kHz 64 kbps, loudnorm -18 LUFS. Env: `OUT`, `PRE`, `FOLD`, `GJ`, `SD` (ambang jeda detik).
- `*_groups.json` - daftar set per file audio kelompok.
Audio dibuat dengan Azure TTS (layanan TTS Talented), lalu divalidasi dengan `tools/validate_banks.py`.
Path absolut di skrip mengikuti lingkungan kerja pembuat; sesuaikan bila dijalankan ulang.
