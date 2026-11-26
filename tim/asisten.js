/* Kit Tim – Asisten (Jawab Cepat + Cek Student). Tanpa server, tanpa data pribadi tersimpan di server. */
(function () {
const EV = null; const evLookup = () => null; const evCountry = () => 2; const evCombined = () => null;
const KARTU = {"checked": "21 Nov 2026", "kurs": 12330, "sumber": "Home Affairs (500, 485, 600, skilled occupation list), pricelist Talented, situs resmi Le Cordon Bleu", "items": [{"t": "Biaya", "q": "Biaya visa student berapa?", "a": "Tarif standar AUD 2.500. Paspor Indonesia dapat tarif konsesi ASEAN, sekitar *AUD 2.050 (± Rp 25,3 juta)*.", "s": "warn", "src": "Konsesi ASEAN RESMI · angka 2.050 SEKUNDER", "k": "vac visa fee 500"}, {"t": "Biaya", "q": "Dana di rekening harus berapa?", "a": "Rumusnya: biaya hidup AUD 29.710 + tuition tahun pertama + tiket ± AUD 2.000.\nContoh tuition AUD 15.400 → *± AUD 47.110 (± Rp 580,9 juta)*.\nBawa pasangan +AUD 10.394, per anak +AUD 4.449.", "s": "ok", "src": "RESMI (tiket: perkiraan)", "k": "rekening koran bank statement saldo financial capacity"}, {"t": "Biaya", "q": "Biaya hidup per bulan berapa?", "a": "Patokan pemerintah AUD 29.710 per tahun ≈ *AUD 2.476 per bulan (± Rp 30,5 juta)*, sudah termasuk tempat tinggal. Perth/Adelaide biasanya lebih hemat dari Sydney/Melbourne.", "s": "ok", "src": "RESMI", "k": "living cost sewa makan"}, {"t": "Biaya", "q": "OSHC (asuransi) berapa?", "a": "Untuk single sekitar *AUD 55–60 per bulan* (ahm AUD 55,02 sampai nib AUD 60,48). Harus menutup seluruh masa visa.", "s": "ok", "src": "Pricelist, 18 Nov 2026", "k": "asuransi kesehatan insurance"}, {"t": "Biaya", "q": "Ada diskon dari Talented?", "a": "Beberapa sekolah ada potongan khusus Talented, tandanya 💰 Special discount di pricelist. Sebut angkanya hanya kalau tercantum, jangan janjikan diskon lain sebelum dikonfirmasi.", "s": "ok", "src": "Pricelist", "k": "promo potongan beasiswa"}, {"t": "Bahasa", "q": "PTE / IELTS minimal untuk student visa?", "a": "Tanpa ELICOS: *IELTS 6.0 / PTE 47*.\nDengan ELICOS ≥10 minggu: IELTS 5.5 / PTE 39.\nDengan ELICOS ≥20 minggu: IELTS 5.0 / PTE 31.\nSekolah bisa minta lebih tinggi, cek Programme details di pricelist.", "s": "ok", "src": "RESMI", "k": "english toefl skor"}, {"t": "Proses", "q": "Kapan CoE keluar?", "a": "Setelah semua syarat di offer letter terpenuhi (termasuk hasil PTE/IELTS), offer ditandatangani, lalu biaya awal dan OSHC dibayar. Setelah CoE keluar, baru visa diajukan.", "s": "ok", "src": "Proses standar", "k": "coe offer letter dokumen"}, {"t": "Proses", "q": "Bisa apply student visa dari Australia?", "a": "Sejak 2 Okt 2026 umumnya *harus dari luar Australia*. Pemegang visa turis, WHV, dan 485 tidak bisa ganti ke student visa di Australia.", "s": "ok", "src": "RESMI", "k": "onshore offshore ganti visa"}, {"t": "Proses", "q": "Boleh pindah sekolah?", "a": "Dari 2 Okt 2026 sampai 30 Jun 2027, umumnya harus menyelesaikan *12 bulan* di sekolah pertama dulu. Mulai 1 Jul 2027 kembali jadi 6 bulan.", "s": "ok", "src": "RESMI", "k": "transfer provider release"}, {"t": "Kerja", "q": "Boleh kerja berapa jam?", "a": "*48 jam per 2 minggu* saat kuliah berjalan, bebas saat libur resmi sekolah.", "s": "ok", "src": "RESMI", "k": "part time work rights"}, {"t": "Keluarga", "q": "Boleh bawa pasangan atau anak?", "a": "Boleh, paspor Indonesia termasuk pengecualian. Syaratnya: dimasukkan *sejak aplikasi pertama*, tidak bisa ditambah setelah visa keluar, dan semua harus berada di lokasi yang sama saat apply.\nTambah dana: pasangan AUD 10.394, per anak AUD 4.449 per tahun.", "s": "ok", "src": "RESMI", "k": "dependant suami istri keluarga"}, {"t": "Visa lain", "q": "Ikut kursus pakai visa turis?", "a": "Bisa, *maksimal 3 bulan* belajar, tidak boleh kerja. Biaya visa *AUD 250 (± Rp 3,1 juta)*. Cocok untuk short course non-akreditasi (contoh Le Cordon Bleu Sydney 6 minggu AUD 3.180–3.339).", "s": "ok", "src": "RESMI · harga LCB situs resmi", "k": "visitor 600 tourist short course"}, {"t": "Visa lain", "q": "Working Holiday (WHV 462) Indonesia?", "a": "Biaya *AUD 840*, usia 18–30, minimal D3 atau 2 tahun S1, IELTS 4.5 / PTE 24, dana ± AUD 5.000, perlu surat rekomendasi Imigrasi RI. Visa pertama lewat sistem *ballot* (dibuka diperkirakan akhir 2026).", "s": "ok", "src": "RESMI", "k": "whv work and holiday"}, {"t": "485", "q": "Lulus Diploma bisa Graduate Visa 485?", "a": "Bisa (jalur Post-Vocational) kalau: total studi ≥ *92 minggu CRICOS* selesai dalam ≥16 bulan, usia ≤35, *IELTS 6.5 / PTE 55*, bidangnya ada di *MLTSSL* + skills assessment.\nBiaya *AUD 5.750*, tinggal sampai 18 bulan, apply dari Australia.", "s": "ok", "src": "RESMI", "k": "graduate visa pvew advanced diploma"}, {"t": "485", "q": "Patisserie / Cookery bisa 485?", "a": "*Cookery (Chef) bisa*, karena Chef 351311 ada di MLTSSL.\n*Patisserie (Pastrycook) dan Cook TIDAK bisa* 485 jalur Diploma, karena bukan MLTSSL.\nKalau target 485, arahkan ke Commercial Cookery + Kitchen Management, lalu konsultasi registered migration agent.", "s": "bad", "src": "RESMI, penting", "k": "pastrycook chef cook mltssl"}, {"t": "Sensitif", "q": "\"Visanya pasti keluar kan?\"", "a": "Keputusan visa sepenuhnya dari pemerintah Australia, jadi tidak ada yang bisa menjamin. Yang kami bantu: dokumen lengkap, jujur, dan sesuai syarat, supaya peluangnya sebaik mungkin.", "s": "ok", "src": "Aturan Talented", "k": "jamin janji approve"}, {"t": "Sensitif", "q": "Pernah ditolak visa sebelumnya?", "a": "Wajib dicantumkan dengan jujur di aplikasi. Untuk kasus seperti ini kami arahkan konsultasi dengan registered migration agent sebelum apply.", "s": "warn", "src": "CEK agen migrasi", "k": "refusal ditolak cancel"}, {"t": "Sensitif", "q": "Kalau visa ditolak, uang kembali?", "a": "Mengikuti refund policy sekolah di offer letter. Umumnya sebagian biaya dikembalikan dengan potongan. Cek bagian \"Refund policy\" di Programme details pricelist, atau di offer letter.", "s": "warn", "src": "CEK offer letter", "k": "refund pengembalian"}, {"t": "Sensitif", "q": "Bisa dibuatkan GS / dokumen?", "a": "GS harus ditulis sendiri oleh student sesuai kondisi aslinya. Kami bantu jelaskan apa yang perlu ada dan cek kelengkapannya, tapi tidak menulis atau mengubah dokumen.", "s": "ok", "src": "Aturan Talented", "k": "genuine student statement joki palsu"}, {"t": "Cek harga", "q": "Cara cepat cek harga di pricelist", "a": "1. Pilih Country dan Offshore/Onshore.\n2. Ketik nama sekolah/jurusan di \"Search programmes or schools\".\n3. Pilih City, lalu Sort → \"Upfront cost\" atau \"Total study cost\".\n4. Klik \"Programme details\" untuk rincian, lalu \"Send WA (PDF)\" untuk kirim ke student.", "s": "ok", "src": "pricelist.talentededucationgroup.com", "k": "pricelist harga cara"}, {"t": "Visa", "q": "Indonesia evidence level berapa?", "a": "Per 30 Sep 2026 Indonesia di *Country Assessment Level 2*. Kombinasi dengan level sekolah menentukan dokumen: sekolah Level 1 → biasanya *streamlined*; sekolah Level 2–3 → *regular* (wajib bukti dana & English).\nCek pasti di Document Checklist Tool Home Affairs. Default Talented: selalu siapkan bukti dana & English.", "s": "warn", "src": "Dokumen internal 30 Sep 2026 · cek Document Checklist Tool", "k": "evidence assessment level negara streamlined regular dokumen"}, {"t": "Visa", "q": "Cara cek level sekolah", "a": "Level per sekolah ada di versi internal Kit Tim (setelah aplikasi dikunci login). Sementara: tanya konsultan senior atau cek di *Document Checklist Tool* Home Affairs.\nSekolah Level 3 = pemeriksaan dokumen paling ketat; untuk student berisiko, bandingkan sekolah Level 1–2 di bidang & kota yang sama.", "s": "ok", "src": "App Tim", "k": "level sekolah provider evidence"}]};
const PRICELIST = "https://pricelist.talentededucationgroup.com/";
const AS_FIELDS = [
  {g: "Profil", f: [
    {id: "ini", l: "Inisial student", t: "text", ph: "mis. KN (tanpa nama lengkap)"},
    {id: "usia", l: "Usia", t: "number", ph: "tahun"},
    {id: "lokasi", l: "Posisi sekarang", t: "select", o: ["Indonesia", "Australia – Student visa", "Australia – Visitor/turis", "Australia – WHV", "Australia – 485", "Negara lain"]},
    {id: "keluarga", l: "Yang ikut", t: "select", o: ["Sendiri", "Pasangan", "Pasangan + anak", "Anak saja"]},
    {id: "anak", l: "Jumlah anak ikut", t: "number", ph: "0"},
  ]},
  {g: "Pendidikan & kerja", f: [
    {id: "pend", l: "Pendidikan terakhir", t: "select", o: ["SMA/SMK", "D3", "S1", "S2", "Lainnya"]},
    {id: "jur", l: "Jurusan terakhir", t: "text", ph: "mis. IPA, Akuntansi"},
    {id: "lulus", l: "Tahun lulus terakhir", t: "number", ph: "mis. 2022"},
    {id: "kerja", l: "Pengalaman kerja (tahun)", t: "number", ph: "0"},
    {id: "bidker", l: "Bidang kerja", t: "text", ph: "mis. F&B, admin"},
  ]},
  {g: "Rencana studi", f: [
    {id: "negara", l: "Negara tujuan", t: "select", o: ["Australia", "New Zealand", "United Kingdom", "United States", "Lainnya"]},
    {id: "jenjang", l: "Jenjang tujuan", t: "select", o: ["ELICOS saja", "Certificate III/IV", "Diploma / Adv. Diploma", "Bachelor", "Master", "Lainnya"]},
    {id: "bidang", l: "Bidang tujuan", t: "text", ph: "mis. Commercial Cookery"},
    {id: "kota", l: "Kota", t: "text", ph: "mis. Perth"},
    {id: "tuition", l: "Tuition tahun pertama (AUD)", t: "number", ph: "lihat tab Harga"},
    {id: "sekolah", l: "Sekolah / provider tujuan", t: "text", ph: "mis. Le Cordon Bleu, APSI"},
    {id: "paspor", l: "Paspor", t: "text", ph: "Indonesia"},
    {id: "jalur", l: "Jalur yang diinginkan", t: "select", o: ["Harus VET", "VET atau universitas", "Universitas (HE)"]},
    {id: "split", l: "Mau mulai 1 tahun di Asia dulu (1+2)?", t: "select", o: ["Ya", "Belum tahu", "Tidak"]},
    {id: "tujuan_akhir", l: "Negara tujuan akhir", t: "select", o: ["Australia", "United States", "New Zealand", "United Kingdom"]},
    {id: "tujuan", l: "Rencana setelah lulus", t: "select", o: ["Kembali berkarier di Indonesia", "Karier internasional, belum pasti", "Ingin menetap / PR", "Belum jelas"]},
  ]},
  {g: "Bahasa Inggris", f: [
    {id: "tes", l: "Tes", t: "select", o: ["Belum tes", "PTE Academic", "IELTS"]},
    {id: "skor", l: "Skor overall", t: "number", ph: "mis. 47 atau 6.0"},
    {id: "bahasa", l: "Bahasa lain yang dikuasai", t: "multi", o: ["Mandarin", "Jepang", "Korea"]},
  ]},
  {g: "Dana", f: [
    {id: "sponsor", l: "Sponsor", t: "select", o: ["Orang tua", "Diri sendiri", "Pasangan", "Beasiswa", "Keluarga lain"]},
    {id: "dana", l: "Dana siap dibuktikan (AUD)", t: "number", ph: "mis. 50000"},
    {id: "dana_rp", l: "atau Dana (Rp juta)", t: "number", ph: "mis. 300"},
    {id: "riwayat", l: "Riwayat saldo", t: "select", o: ["Stabil ≥ 3 bulan", "Ada setoran besar baru", "Belum tahu"]},
    {id: "income", l: "Penghasilan sponsor", t: "select", o: ["Jelas & ada dokumennya", "Ada, dokumen kurang", "Belum tahu"]},
  ]},
  {g: "Riwayat visa & ikatan di Indonesia", f: [
    {id: "tolak", l: "Pernah ditolak visa?", t: "select", o: ["Tidak pernah", "Pernah – Australia", "Pernah – negara lain"]},
    {id: "overstay", l: "Pernah overstay / langgar visa?", t: "select", o: ["Tidak", "Ya"]},
    {id: "travel", l: "Riwayat ke luar negeri", t: "select", o: ["Belum pernah", "Pernah, selalu pulang tepat waktu"]},
    {id: "isu", l: "Isu kesehatan / karakter yang harus diungkap?", t: "select", o: ["Tidak ada", "Ada"]},
    {id: "ikatan", l: "Ikatan di Indonesia (pilih yang ada)", t: "multi", o: ["Pekerjaan menunggu", "Usaha keluarga", "Aset/properti", "Keluarga yang bergantung", "Rencana karier jelas di Indonesia"]},
    {id: "catatan", l: "Catatan konsultan (tanpa data pribadi)", t: "area", ph: "mis. ingin buka bakery di Bandung setelah lulus"},
  ]},
];
const AS_RANK_P = {"SMA/SMK": 1, "D3": 2, "S1": 3, "S2": 4};
const AS_RANK_T = {"ELICOS saja": 0, "Certificate III/IV": 1, "Diploma / Adv. Diploma": 2, "Bachelor": 3, "Master": 4};
const AS_LIVE = {student: 29710, partner: 10394, child: 4449, travel: 2000};


function assess(p, year) {
  if (!p.dana && Number(p.dana_rp)) p = {...p, dana: Math.round(Number(p.dana_rp) * 1e6 / 12330)};
  const A = [], miss = [];
  const has = k => p[k] !== undefined && p[k] !== null && String(p[k]).trim() !== "" && !(Array.isArray(p[k]) && !p[k].length && k !== "ikatan");
  const area = (n, s, notes, acts) => A.push({n, s, notes, acts});
  const need = (k, q) => { if (!has(k)) miss.push(q); };
  need("usia", "Berapa usiamu sekarang?"); need("pend", "Pendidikan terakhirmu apa?"); need("lulus", "Lulus tahun berapa?");
  need("jur", "Jurusan terakhirmu apa?"); need("bidang", "Mau ambil bidang apa dan kenapa tertarik di bidang itu?");
  need("tujuan", "Setelah lulus rencananya kerja apa dan di mana?"); need("dana", "Kira-kira dana yang siap dibuktikan berapa?");
  need("sponsor", "Siapa yang membiayai (sponsor)?"); need("tolak", "Pernah ditolak visa negara mana pun?");
  if (!has("tes") || p.tes === "Belum tes") miss.push("Sudah pernah tes PTE/IELTS? Kalau sudah, berapa skornya?");
  if (has("kerja") && Number(p.kerja) > 0 && !has("bidker")) miss.push("Pengalaman kerjamu di bidang apa?");
  if (!p.ikatan || !p.ikatan.length) miss.push("Ada pekerjaan, usaha keluarga, atau rencana karier yang menunggu di Indonesia?");
  if (!has("income") || p.income === "Belum tahu") miss.push("Pekerjaan/penghasilan sponsor apa, dan ada slip gaji atau dokumen usahanya?");

  // 1. Jalur & lokasi
  const lok = p.lokasi || "Indonesia";
  if (/Visitor|WHV|485/.test(lok)) area("Jalur aplikasi", "bad", ["Sejak 2 Okt 2026, pemegang visa ini tidak bisa apply Student visa dari dalam Australia."], ["Rencanakan apply dari luar Australia (mis. pulang ke Indonesia).", "Rujuk ke registered migration agent untuk timing."]);
  else if (/Student visa/.test(lok)) area("Jalur aplikasi", "warn", ["Student visa baru dari dalam Australia hanya boleh untuk pengecualian tertentu (mis. naik jenjang AQF di provider yang sesuai).", "Pindah provider: wajib selesai 12 bulan principal course (2 Okt 2026–30 Jun 2027)."], ["Cek apakah kasusnya masuk pengecualian onshore sebelum memberi offer."]);
  else area("Jalur aplikasi", "ok", ["Apply dari luar Australia: sesuai aturan sejak 2 Okt 2026."], []);

  // 2. Akademik & GS logika studi
  const notes = [], acts = []; let s = "ok";
  const gap = has("lulus") ? year - Number(p.lulus) : null;
  const rp = AS_RANK_P[p.pend], rt = AS_RANK_T[p.jenjang];
  if (rp && rt !== undefined && rt < rp - 1) { s = "warn"; notes.push(`Turun jenjang (${p.pend} → ${p.jenjang}).`); acts.push("GS harus menjelaskan kenapa jenjang ini masuk akal untuk kariernya (mis. ganti karier ke bidang vokasi yang dibutuhkan)."); }
  if (gap !== null && gap >= 3) { if (s === "ok") s = "warn"; notes.push(`Jeda studi ${gap} tahun.`); acts.push(Number(p.kerja) > 0 ? "Siapkan bukti kerja selama jeda (surat kerja, slip gaji) dan kaitkan dengan bidang studi." : "Siapkan penjelasan kegiatan selama jeda dan buktinya."); }
  if (has("jur") && has("bidang")) notes.push(`Bidang lama "${p.jur}" → bidang baru "${p.bidang}": pastikan alasan perpindahan logis.`);
  if (has("usia") && Number(p.usia) < 18) { s = "warn"; notes.push("Di bawah 18 tahun: wajib ada pengaturan kesejahteraan (wali/CAAW)."); acts.push("Siapkan wali atau welfare arrangement dari sekolah."); }
  if (!has("pend") || !has("lulus") || !has("jenjang")) { if (s === "ok") s = "warn"; notes.push("Data pendidikan/jenjang tujuan belum lengkap."); }
  if (!notes.length) notes.push("Kesinambungan studi terlihat wajar.");
  area("Akademik & alur studi", s, notes, acts);

  // 3. Bahasa Inggris
  const sk = Number(p.skor);
  if (!has("tes") || p.tes === "Belum tes" || !has("skor")) area("Bahasa Inggris", "warn", ["Belum ada skor tes."], ["Jadwalkan PTE Academic. Target visa: 47 tanpa ELICOS, 39 dengan ELICOS ≥10 minggu, 31 dengan ELICOS ≥20 minggu.", "Cek syarat sekolah (Bachelor/Master biasanya lebih tinggi)."]);
  else {
    const pte = p.tes === "PTE Academic", [a, b, c] = pte ? [47, 39, 31] : [6, 5.5, 5];
    if (sk >= a) area("Bahasa Inggris", "ok", [`${p.tes} ${sk}: memenuhi minimum visa tanpa ELICOS.`], ["Pastikan juga memenuhi syarat sekolah dan tes masih berlaku (maks 2 tahun)."]);
    else if (sk >= b) area("Bahasa Inggris", "warn", [`${p.tes} ${sk}: perlu paket ELICOS ≥10 minggu.`], ["Tawarkan paket ELICOS + course utama, atau tes ulang untuk capai " + a + "."]);
    else if (sk >= c) area("Bahasa Inggris", "warn", [`${p.tes} ${sk}: perlu paket ELICOS ≥20 minggu.`], ["Tawarkan paket ELICOS ≥20 minggu, atau persiapan tes dulu."]);
    else area("Bahasa Inggris", "bad", [`${p.tes} ${sk}: di bawah minimum visa.`], ["Ikut kursus persiapan (mis. Victory Scholars Academy) lalu tes ulang sebelum apply."]);
  }

  // 4. Dana
  const nChild = p.keluarga === "Pasangan + anak" || p.keluarga === "Anak saja" ? Math.max(Number(p.anak) || 1, 1) : 0;
  const partner = /Pasangan/.test(p.keluarga || "");
  const tui = Number(p.tuition) || 0;
  const needAUD = AS_LIVE.student + tui + AS_LIVE.travel + (partner ? AS_LIVE.partner + AS_LIVE.travel : 0) + nChild * (AS_LIVE.child + AS_LIVE.travel);
  const fN = [`Perlu dibuktikan ± AUD ${needAUD.toLocaleString("id-ID")}${tui ? "" : " + tuition tahun pertama (belum diisi)"} (biaya hidup ${AS_LIVE.student.toLocaleString("id-ID")}${partner ? " + pasangan " + AS_LIVE.partner.toLocaleString("id-ID") : ""}${nChild ? ` + ${nChild} anak × ${AS_LIVE.child.toLocaleString("id-ID")}` : ""} + tiket).`];
  const fA = []; let fs = "ok";
  if (nChild) fN.push("Anak usia sekolah: tambah biaya sekolah ± AUD 13.502/tahun.");
  if (!has("dana")) { fs = "warn"; fA.push("Tanyakan total dana yang siap dibuktikan."); }
  else if (Number(p.dana) < needAUD) {
    const gap = needAUD - Number(p.dana), near = Number(p.dana) >= needAUD * 0.85;
    fs = near ? "warn" : "bad";
    fN.push(`Dana AUD ${Number(p.dana).toLocaleString("id-ID")} ${near ? "hampir cukup" : "masih kurang"}: kurang ± AUD ${gap.toLocaleString("id-ID")} (± Rp ${Math.round(gap * 12330 / 1e6).toLocaleString("id-ID")} juta) dari minimum resmi.`);
    fA.push(near ? "Bisa ditutup: tambah tabungan beberapa bulan, sponsor keluarga yang sah, beasiswa/diskon yang berlaku, atau sekolah/kota sedikit lebih hemat." : "Solusi: pilih kota/sekolah lebih hemat, jalur 1+2 Asia, mulai kursus bahasa dulu sambil menabung, atau sponsor keluarga yang sah.");
  }
  else fN.push(`Dana AUD ${Number(p.dana).toLocaleString("id-ID")}: cukup.`);
  if (p.riwayat === "Ada setoran besar baru") { if (fs === "ok") fs = "warn"; fA.push("Siapkan bukti asal dana yang sah (jual aset, pencairan deposito, warisan, dll.). Jangan meminjam dana sementara."); }
  if (p.income !== "Jelas & ada dokumennya") { if (fs === "ok") fs = "warn"; fA.push("Kumpulkan bukti penghasilan sponsor (slip gaji, SPT, izin usaha, laporan keuangan)."); }
  area("Dana", fs, fN, fA);

  // 5. Genuine Student (ikatan & tujuan)
  const ik = (p.ikatan || []).length, gN = [], gA = []; let gs = ik >= 2 ? "ok" : "warn";
  gN.push(ik ? `Ikatan di Indonesia: ${p.ikatan.join(", ")}.` : "Belum ada ikatan di Indonesia yang tercatat.");
  if (p.tujuan === "Ingin menetap / PR") { gs = "warn"; gN.push("Ingin menetap boleh disampaikan jujur, tapi tujuan utama visa harus studi yang sungguh-sungguh."); gA.push("Rencana migrasi dibahas dengan registered migration agent, bukan dijanjikan konsultan."); }
  if (p.tujuan === "Belum jelas" || !has("tujuan")) { gs = "warn"; gA.push("Gali rencana karier yang realistis dan sesuai bidang studi; student menulis GS sendiri."); }
  if (ik < 2) gA.push("Kumpulkan bukti ikatan yang ada (surat kerja/cuti, usaha keluarga, rencana karier dengan riset gaji di Indonesia).");
  if (p.travel === "Pernah, selalu pulang tepat waktu") gN.push("Riwayat perjalanan baik: poin positif.");
  area("Genuine Student (GS)", gs, gN, gA);

  // 6. Riwayat imigrasi & karakter
  const rN = [], rA = []; let rs = "ok";
  if (/Pernah/.test(p.tolak || "")) { rs = "bad"; rN.push(`${p.tolak}.`); rA.push("Wajib diungkapkan di aplikasi. Analisa alasan penolakan sebelumnya bersama registered migration agent sebelum apply."); }
  if (p.overstay === "Ya") { rs = "bad"; rN.push("Riwayat overstay/pelanggaran visa."); rA.push("Rujuk ke registered migration agent sebelum memberi offer."); }
  if (p.isu === "Ada") { rs = rs === "bad" ? "bad" : "warn"; rN.push("Ada isu kesehatan/karakter yang harus diungkap."); rA.push("Jangan dicatat detailnya di sini. Rujuk ke registered migration agent."); }
  if (!has("tolak")) { rs = "warn"; rN.push("Belum ditanyakan riwayat penolakan visa."); }
  if (!rN.length) rN.push("Tidak ada catatan penolakan atau pelanggaran.");
  area("Riwayat visa & karakter", rs, rN, rA);

  // 6b. Evidence level (negara paspor × provider)
  if ((p.negara || "Australia") === "Australia") {
    const nc = evCountry(p.paspor), pv = p.sekolah ? evLookup(p.sekolah) : null, eN = [], eA = []; let es = "ok";
    eN.push(`Negara paspor ${p.paspor || "Indonesia"}: ${nc ? "Level " + nc : "level belum ada di data"} (per 30 Sep 2026).`);
    if (!p.sekolah) { es = "warn"; eN.push("Sekolah tujuan belum diisi."); }
    else if (!pv) { es = "warn"; eN.push(`Level "${p.sekolah}" belum ada di data.`); eA.push("Cek kombinasi negara + provider di Document Checklist Tool Home Affairs."); }
    else {
      eN.push(`${pv.nama}: Level ${pv.level ?? "?"} (${pv.tanggal}).` + (pv.catatan ? " " + pv.catatan : ""));
      const cb = evCombined(nc, pv.level);
      if (cb) eN.push(`Perkiraan kombinasi: ${cb} evidence.`);
      if (pv.level === 3) { es = "bad"; eA.push("Provider Level 3: pemeriksaan dokumen paling ketat. Untuk kasus berisiko, bandingkan provider Level 1–2 di bidang & kota yang sama."); }
      else if (cb === "Regular") { es = "warn"; eA.push("Regular evidence: wajib bukti keuangan & English lengkap sesuai Document Checklist Tool."); }
      if (pv.catatan) { if (es === "ok") es = "warn"; eA.push("Sumber data berbeda untuk sekolah ini: konfirmasi ke provider / Document Checklist Tool."); }
    }
    eA.push("Default Talented: walau streamlined, tetap siapkan bukti English dan keuangan.");
    area("Evidence level (dokumen)", es, eN, eA);
  }

  // 7. Prospek setelah lulus (485)
  const bid = (p.bidang || "").toLowerCase(), pN = [], pA = []; let ps = "ok";
  if (/patis|pastry|bak(er|ing)/.test(bid)) { ps = "warn"; pN.push("Patisserie/Pastrycook bukan MLTSSL: tidak bisa 485 jalur Diploma."); pA.push("Jangan janjikan 485. Bila student ingin 485, diskusikan paket Commercial Cookery (Chef)."); }
  else if (/cook|chef|kitchen|culinary/.test(bid)) pN.push("Chef ada di MLTSSL: 485 jalur Diploma dimungkinkan (≥92 minggu CRICOS + skills assessment TRA).");
  if (has("usia") && Number(p.usia) > 35) { ps = "warn"; pN.push("Usia di atas 35: umumnya tidak memenuhi syarat 485."); }
  if (!pN.length) pN.push("Cek kesesuaian bidang dengan daftar okupasi bila student menanyakan 485 (IELTS 6.5/PTE 55, usia ≤35).");
  area("Prospek setelah lulus", ps, pN, pA);

  if (has("negara") && p.negara !== "Australia") area("Negara tujuan", "warn", [`Aturan di atas berbasis Australia. Untuk ${p.negara}, syarat visa, dana, dan bahasa berbeda.`], ["Cek ke sumber resmi negara tersebut atau tanyakan ke konsultan senior."]);
  const order = {bad: 0, warn: 1, ok: 2};
  return {areas: A, missing: miss, needAUD, top: [...A].sort((x, y) => order[x.s] - order[y.s])};
}


/* ---------- Jalur & solusi saat kasus "mentok" ---------- */
function paths(p, r) {
  const O = [], bad = r.areas.filter(a => a.s === "bad").map(a => a.n), warn = r.areas.filter(a => a.s === "warn").map(a => a.n);
  const stuck = bad.length > 0 || warn.length >= 3;
  const vet = /Certificate|Diploma/.test(p.jenjang || ""), mau = p.jalur || "";
  const dest = p.tujuan_akhir || p.negara || "Australia";
  const has = n => bad.includes(n) || warn.includes(n);
  const bid = (p.bidang || "").toLowerCase();
  const add = (id, judul, cocok, kenapa, langkah, cek) => O.push({id, judul, cocok, kenapa, langkah, cek});

  if (/Pernah/.test(p.tolak || "") || p.overstay === "Ya")
    add("agen", "Analisa dulu bersama registered migration agent", "Wajib sebelum memilih jalur mana pun",
      ["Riwayat penolakan/pelanggaran harus diungkap jujur di setiap aplikasi, di negara mana pun.", "Jalur yang tepat bergantung pada alasan penolakan sebelumnya."],
      ["Minta surat penolakan lama, catat alasannya.", "Jadwalkan konsultasi registered migration agent.", "Baru pilih jalur di bawah setelah ada analisa."], []);

  if (dest === "Australia" && vet && (stuck || mau !== "Harus VET"))
    add("vet_he", "Paket VET → Higher Education (Diploma lanjut Bachelor)", mau === "Harus VET" ? "Student ingin tetap mulai dari VET" : "Student terbuka ke universitas",
      ["Alur studi naik jenjang dan logis untuk karier: GS lebih mudah dijelaskan daripada VET berulang-ulang atau turun jenjang.", "Satu rencana studi panjang (paket CoE) dengan pengakuan kredit tertulis menunjukkan tujuan studi yang jelas.", "Prioritas MD 115 hanya memengaruhi kecepatan proses, bukan hasil; tapi pilih provider di Priority 1/2 agar tidak tertahan lama."],
      ["Cari Diploma di provider yang punya articulation agreement ke Bachelor bidang yang sama (tab Harga, kata kunci bidang + kota).", "Minta konfirmasi tertulis jumlah kredit/transfer ke Bachelor.", "Cek status prioritas MD 115 provider di laporan mingguan Home Affairs."],
      ["Credit transfer tertulis", "Status MD 115 provider (berubah mingguan)", "Biaya total 2 tahap + bukti dana tahun pertama"]);

  const pv = p.sekolah && typeof evLookup === "function" ? evLookup(p.sekolah) : null;
  if (dest === "Australia" && pv && (pv.level === 3 || (stuck && pv.level === 2)))
    add("provider", `Bandingkan dengan provider evidence level lebih rendah (sekarang ${pv.nama}: Level ${pv.level})`, "Kasus berisiko atau provider Level 3",
      ["Provider Level 1–2 punya syarat dokumen lebih ringan dan riwayat kepatuhan student yang lebih baik.", "Level (evidence) berbeda dengan prioritas proses MD 115: cek keduanya."],
      ["Cari program bidang & kota yang sama di tab Harga, lalu cek level-nya di Asesmen (isi kolom Sekolah).", "Bandingkan biaya, syarat English, dan intake.", "Jelaskan ke student alasan pindah sekolah secara jujur (bukan sekadar 'lebih mudah visa')."],
      ["Level provider terbaru (berubah tiap 6 bulan)", "Document Checklist Tool"]);
  if (dest === "Australia" && vet && mau === "Harus VET")
    add("tafe", "Kalau harus VET: pilih TAFE / universitas dual-sector", "Bidang vokasi (mis. cookery, hospitality, community services)",
      ["TAFE otomatis Priority 1 di MD 115 (proses lebih cepat); VET di Charles Darwin University juga Priority 1 (snapshot 16 Okt 2026).", "Provider negeri/dual-sector biasanya punya jalur lanjut ke Bachelor di institusi yang sama.", "Hindari provider yang sedang Priority 3 bila student butuh berangkat cepat."],
      ["Bandingkan biaya TAFE vs swasta di tab Harga (bisa lebih mahal, tapi prosesnya lebih cepat).", "Cek syarat bahasa TAFE (sering lebih tinggi) dan intake.", "Tetap siapkan GS, bukti dana, dan English lengkap."],
      ["Snapshot prioritas terbaru", "Syarat bahasa per TAFE", "Biaya"]);

  if (/patis|pastry|bak(er|ing)/.test(bid) && dest === "Australia")
    add("chef", "Bila targetnya kerja setelah lulus (485): Commercial Cookery, bukan Patisserie", "Student ingin 485",
      ["Chef 351311 ada di MLTSSL; Pastrycook tidak, jadi Patisserie tidak membuka 485 jalur Diploma."],
      ["Tawarkan paket Cert III Commercial Cookery + Cert IV Kitchen Management + Diploma (≥92 minggu CRICOS).", "Patisserie bisa diambil sebagai minat tambahan, bukan jalur utama 485."], ["Daftar okupasi resmi saat apply"]);

  const terbuka = p.split !== "Tidak";
  if (terbuka && (stuck || p.split === "Ya")) {
    if (dest === "Australia")
      add("split_au", "1+2: mulai di kampus cabang Asia, lanjut ke kampus induk di Australia", "Dana terbatas, English/akademik perlu dibangun, atau GS lemah",
        ["Tahun pertama di Malaysia/Singapura/Indonesia biasanya jauh lebih murah dan dekat rumah.", "Student membangun riwayat studi dan nilai nyata: alasan pindah ke kampus induk menjadi alur studi yang logis untuk GS.", "Waktu tambahan untuk menaikkan skor English dan menyiapkan bukti dana yang rapi."],
        ["Contoh kampus cabang yang punya transfer ke kampus induk: Swinburne Sarawak (Kuching) → Swinburne Melbourne; Curtin Malaysia (Miri) / Curtin Singapore → Curtin Perth; James Cook University Singapore → JCU Townsville/Cairns.", "Cari biaya di tab Harga atau web pricelist (Country: Malaysia / Singapore / Indonesia).", "Minta konfirmasi tertulis: jalur transfer, kredit yang diakui, syarat nilai minimum untuk pindah.", "Siapkan izin studi negara tahap 1 (Malaysia: EMGS; Singapura: Student's Pass ICA)."],
        ["Kampus & program transfer masih dibuka untuk intake yang dituju", "Visa Australia tahap 2 tetap dinilai baru (GS, dana, English)", "Biaya 2 negara"]);
    if (dest === "United States")
      add("split_us", "Jalur transfer ke Amerika: American Degree Program (Malaysia) atau 2+2 community college", "Tujuan akhir Amerika dengan dana terbatas",
        ["American Degree Transfer Program di Malaysia (mis. Taylor's, Sunway, HELP) memungkinkan 1–2 tahun kuliah di Asia lalu transfer kredit ke universitas di Amerika.", "Atau langsung F-1 ke community college 2 tahun lalu transfer ke universitas 4 tahun (biaya awal lebih rendah).", "Riwayat nilai yang baik memperkuat aplikasi F-1 di tahap transfer."],
        ["Cek daftar universitas tujuan yang menerima transfer dari program tersebut (tertulis).", "Siapkan TOEFL/IELTS/Duolingo sesuai kampus Amerika.", "Rencanakan bukti dana untuk I-20 tahap 2."],
        ["Kebijakan visa pelajar Amerika berubah cepat: cek berita resmi terbaru di tab Konten/Berita", "Credit transfer tertulis"]);
  }
  if (has("Bahasa Inggris"))
    add("english", "Perkuat English dulu: kelas persiapan + tes ulang, atau paket ELICOS resmi", "Skor di bawah syarat",
      ["Skor yang memenuhi syarat tanpa banyak ELICOS memperpendek studi dan biaya.", "Victory Scholars Academy (bagian Talented) menyediakan kelas & mock test gratis."],
      ["Tes diagnostik/mock test gratis.", "Target skor: Australia PTE 47 / 39 / 31 (lihat Jawab Cepat); negara lain mengikuti syarat kampus.", "Bila waktunya mepet: paket ELICOS ≥10 atau ≥20 minggu dengan CoE paket."], []);
  if (has("Dana"))
    add("dana", "Atur ulang rencana biaya secara sah", "Dana kurang dari kebutuhan",
      ["Bukti dana harus asli, stabil, dan asal-usulnya jelas. Dana pinjaman sementara tidak boleh dipakai."],
      ["Bandingkan kota/provider lebih hemat di tab Harga (urutkan 'Dana awal termurah').", "Pertimbangkan jalur 1+2 di Asia untuk menekan biaya tahun pertama.", "Tambah sponsor keluarga yang sah lengkap dengan dokumen hubungan & penghasilan."], []);
  return {stuck, opsi: O};
}

/* ---------- Bandingkan destinasi yang didukung Talented ---------- */
const KURS_AUD = 12330;
function destinations(p, r) {
  const age = Number(p.usia) || null, pend = p.pend || "", rp = AS_RANK_P[pend] || 0;
  const pte = p.tes === "PTE Academic" ? Number(p.skor) : p.tes === "IELTS" ? ({4.5: 24, 5: 31, 5.5: 39, 6: 47, 6.5: 55}[Number(p.skor)] ?? (Number(p.skor) >= 7 ? 66 : 20)) : null;
  const dana = Number(p.dana) || (Number(p.dana_rp) ? Number(p.dana_rp) * 1e6 / KURS_AUD : 0);
  const lang = p.bahasa || [];
  const refusal = /Pernah/.test(p.tolak || "") || p.overstay === "Ya";
  const fam = /Pasangan|Anak/.test(p.keluarga || "");
  const rows = [];
  const row = (dest, jalur, status, visa, biaya, kenapa, langkah) => rows.push({dest, jalur, status, visa, biaya, kenapa, langkah});
  const rpj = a => `± Rp ${Math.round(a * KURS_AUD / 1e6).toLocaleString("id-ID")} juta`;
  const needVET = 29710 + 10000 + 2000, needHE = 29710 + 34000 + 2000;

  // Australia VET
  { const k = [], note = []; let s = "Perlu persiapan", v = "Ketat (sektor VET sedang diperketat)";
    if (pte === null) k.push("belum ada skor English");
    if (pte !== null && pte < 31) k.push("English di bawah minimum (PTE 31 + ELICOS 20 mgg)");
    if (dana && dana < needVET * 0.85) k.push(`dana kurang (perlu ± AUD ${needVET.toLocaleString("id-ID")})`);
    else if (dana && dana < needVET) note.push(`dana hampir cukup (kurang ± AUD ${Math.round(needVET - dana).toLocaleString("id-ID")})`);
    if (rp >= 3) k.push("turun jenjang dari S1/S2 → GS harus kuat");
    if (refusal) { s = "Rujuk agen migrasi"; }
    else if (k.length >= 2) s = "Belum disarankan"; else if (!k.length && dana && pte !== null) s = "Bisa dipertimbangkan";
    row("Australia", "Student visa – VET (Cert/Diploma)", s, v, `dana bukti ± AUD ${needVET.toLocaleString("id-ID")} (${rpj(needVET)})`, (k.length || note.length) ? [...k, ...note].join("; ") : "Pilih TAFE / provider Level 1–2, Priority 1–2, jurusan nyambung karier", "Tab Harga + Asesmen (isi sekolah) untuk cek level & prioritas"); }
  // Australia HE
  { const k = [], note = []; let s = "Perlu persiapan";
    if (pte === null) k.push("belum ada skor English");
    if (pte !== null && pte < 50) k.push("English perlu naik (umumnya setara IELTS 6.0–6.5)");
    if (dana && dana < needHE * 0.85) k.push(`dana kurang (perlu ± AUD ${needHE.toLocaleString("id-ID")})`);
    else if (dana && dana < needHE) note.push(`dana hampir cukup (kurang ± AUD ${Math.round(needHE - dana).toLocaleString("id-ID")})`);
    if (refusal) s = "Rujuk agen migrasi"; else if (!k.length && dana && pte !== null) s = "Cocok"; else if (k.length >= 2) s = "Jangka menengah (6–12 bln)";
    row("Australia", "Student visa – Universitas (HE) / pathway", s, "Lebih kuat dari VET, terutama universitas Level 1", `dana bukti ± AUD ${needHE.toLocaleString("id-ID")} (${rpj(needHE)})`, (k.length || note.length) ? [...k, ...note].join("; ") : "Universitas Level 1 + Priority 1–2 paling kuat", "Cari universitas di tab Harga, cek level di Asesmen"); }
  // Australia WHV
  { const k = [];
    if (!age || age < 18 || age > 30) k.push("usia harus 18–30");
    if (rp < 2) k.push("pendidikan minimal D3 atau 2 tahun S1");
    if (pte !== null && pte < 24) k.push("English min. IELTS 4.5 / PTE 24");
    row("Australia", "Work & Holiday 462", k.length ? "Tidak memenuhi" : "Memenuhi syarat dasar", "Sistem ballot (undian) untuk visa pertama", "AUD 840 + dana ± AUD 5.000", k.length ? k.join("; ") : "Ikuti ballot; siapkan surat rekomendasi Imigrasi RI", "Jawab Cepat: kartu WHV"); }
  // 1+2 Asia -> Australia
  if (p.split !== "Tidak")
    row("Malaysia / Singapura → Australia", "1+2 kampus cabang (Swinburne Sarawak, Curtin Miri/Singapore, JCU Singapore)", "Opsi hemat", "Tahap 2 tetap dinilai baru; riwayat studi memperkuat GS", "Tahun 1 jauh lebih murah (cek pricelist Malaysia/Singapura)", "Membangun nilai, English, dan dana bertahap", "Pricelist: Country Malaysia / Singapore");
  // Japan SSW
  { const jp = lang.includes("Jepang");
    row("Jepang", "Kerja – Tokutei Ginou (SSW)", age && age < 18 ? "Tidak memenuhi" : jp ? "Cocok" : "Perlu belajar bahasa Jepang (6–12 bln)", "Kuat bila lulus tes & punya kontrak kerja (visa via perusahaan)", "Paling murah: kursus + biaya tes", "Tanpa syarat ijazah tinggi; JFT-Basic/JLPT N4 + tes keahlian (16 bidang)", "Kelas Jepang VSA; penempatan hanya lewat jalur resmi berizin"); }
  // Japan language school
  row("Jepang", "Sekolah bahasa (mis. OBKG Osaka)", rp >= 1 ? "Bisa dipertimbangkan" : "Cek syarat sekolah", "Sedang: dana & alasan studi harus jelas", "Awal JPY 1.050.000; total JPY 1,45–1,84 juta + hidup", "Kerja paruh waktu maks 28 jam/minggu (dengan izin); bisa lanjut ke SSW", "Pricelist: Country Japan");
  // China
  if (lang.includes("Mandarin") || /china|mandarin/i.test(p.bidang || ""))
    row("China", "Studi (bahasa / S1, mis. Zhejiang, UNNC, XJTLU)", "Cocok bila tujuannya studi", "Cek syarat visa X1/X2 resmi", "Program bahasa CNY 9.000/semester; S1 CNY 99.000–120.000/th", "Mandarin jadi keunggulan; bukan jalur kerja", "Pricelist: Country China");
  // NZ / UK – data belum diverifikasi di app
  row("Selandia Baru / Inggris", "Student visa", "Cek syarat resmi", "—", "Cek pricelist (NZD / GBP)", "Syarat dana & English berbeda; belum dihitung otomatis di app", "Pricelist: Country New Zealand / United Kingdom");
  if (fam) rows.forEach(x => { if (/Student visa/.test(x.jalur) && x.dest === "Australia") x.kenapa += "; bawa keluarga: tambah dana pasangan AUD 10.394 / anak AUD 4.449 (hanya di aplikasi pertama)"; });
  const order = {"Cocok": 0, "Memenuhi syarat dasar": 0, "Bisa dipertimbangkan": 1, "Opsi hemat": 1, "Cocok bila tujuannya studi": 1, "Perlu belajar bahasa Jepang (6–12 bln)": 1, "Perlu persiapan": 2, "Jangka menengah (6–12 bln)": 3, "Cek syarat resmi": 4, "Cek syarat sekolah": 4, "Belum disarankan": 5, "Rujuk agen migrasi": 5, "Tidak memenuhi": 6};
  return rows.sort((a, b) => (order[a.status] ?? 4) - (order[b.status] ?? 4));
}

const $ = (s, r = document) => r.querySelector(s);
const esc = s => String(s ?? "").replace(/[&<>"]/g, c => ({"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;"}[c]));
const bold = s => esc(s).replace(/\*([^*]+)\*/g, "<b>$1</b>");
const css = `
.ka-nav{display:flex;gap:6px;overflow-x:auto;padding:8px 0}
.ka-nav button{flex:none;border:1.5px solid #d6dbe3;background:#fff;color:#14213d;border-radius:999px;padding:6px 14px;font:inherit;font-weight:700;font-size:.9rem;cursor:pointer}
.ka-nav button[aria-pressed=true]{background:#14213d;color:#fff;border-color:#14213d}
.ka-panel{display:flex;flex-direction:column;gap:10px;margin:6px 0 18px}
.ka-panel[hidden]{display:none}
.ka-search{background:#fff;color:#14213d;width:100%;box-sizing:border-box;font:inherit;font-size:1rem;border:1.5px solid #d6dbe3;border-radius:10px;padding:9px 12px}
.ka-grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(min(100%,300px),1fr));gap:10px;align-items:start}
.ka-card{background:#fff;color:#14213d;border:1px solid #e3e7ee;border-radius:12px;padding:12px 14px;display:flex;flex-direction:column;gap:6px;min-width:0}
.ka-card h3{margin:0;font-size:1rem}
.ka-ans{white-space:pre-line;overflow-wrap:anywhere;margin:0;font-size:.92rem}
.ka-btn{align-self:flex-start;border:0;background:#18a058;color:#fff;border-radius:8px;padding:6px 12px;font:inherit;font-weight:700;font-size:.85rem;cursor:pointer}
.ka-muted{color:#6b7280;font-size:.8rem}
.ka-form{display:grid;grid-template-columns:repeat(auto-fill,minmax(min(100%,160px),1fr));gap:8px}
.ka-form label{display:flex;flex-direction:column;gap:3px;font-size:.8rem;color:#6b7280;min-width:0}
.ka-form input,.ka-form select{font:inherit;font-size:.95rem;border:1.5px solid #d6dbe3;border-radius:8px;padding:6px 8px;width:100%;box-sizing:border-box;min-width:0}
.ka-tag{display:inline-block;font-weight:700;font-size:.72rem;border-radius:999px;padding:1px 8px}
.ka-ok{background:#e1f4ea;color:#0f7049}.ka-warn{background:#fff1d6;color:#8f5600}.ka-bad{background:#fde7e7;color:#a42121}
.ka-table{overflow-x:auto} .ka-table table{border-collapse:collapse;min-width:620px;font-size:.84rem} .ka-table td,.ka-table th{border-bottom:1px solid #e3e7ee;padding:6px;text-align:left;vertical-align:top}
.ka-dot{display:inline-block;min-width:18px;margin-left:6px;padding:0 5px;border-radius:999px;background:#e5484d;color:#fff;font-size:.72rem;line-height:18px;text-align:center}
.ka-due{display:flex;align-items:center;gap:10px;flex-wrap:wrap;background:#fde7e7;border:1px solid #f5b5b5;color:#a42121;border-radius:12px;padding:10px 12px;font-weight:700;font-size:.9rem}
.ka-due[hidden],.ka-dot[hidden]{display:none}
.ka-due button{margin-left:auto;border:0;background:#e5484d;color:#fff;border-radius:8px;padding:7px 12px;font:inherit;font-weight:800;cursor:pointer}
.ka-chips{display:flex;gap:6px;flex-wrap:wrap}.ka-chips button{border:1.5px solid #d6dbe3;background:#f4f6f9;color:#14213d;border-radius:999px;padding:5px 12px;font:inherit;font-size:.85rem;font-weight:700;cursor:pointer}
.ka-h{margin:6px 0 0;font-size:1rem}
.ka-cta{display:inline-block;background:#14213d;color:#fff;border-radius:10px;padding:10px 16px;font-weight:700;text-decoration:none}
`;
function copy(text, btn) { const o = btn.textContent; (navigator.clipboard ? navigator.clipboard.writeText(text) : Promise.reject()).then(() => btn.textContent = "Tersalin", () => btn.textContent = "Salin gagal").finally(() => setTimeout(() => btn.textContent = o, 1500)); }
function mount(host) {
  const st = document.createElement("style"); st.textContent = css; document.head.append(st);
  host.innerHTML = `<nav class="ka-nav" role="group" aria-label="Asisten tim">
    <button type="button" data-v="konten" aria-pressed="true">📲 Konten<span class="ka-dot" id="ka-dot" hidden></span></button>
    <button type="button" data-v="ai" aria-pressed="false">💬 Tanya Jawab</button></nav>
    <div class="ka-due" id="ka-due" hidden role="status"><span id="ka-due-t"></span><button type="button" id="ka-due-go">📤 Posting sekarang</button></div>
    <section class="ka-panel" id="ka-ai" hidden><div class="ka-card"><h3>💬 Tanya Jawab</h3><textarea class="ka-search" id="ka-tq" rows="3" placeholder="Tempel / ketik pertanyaan student, mis. bawa suami bisa? dananya brp?" aria-label="Pertanyaan student"></textarea><div class="ka-chips" id="ka-chips">${["Dana","Biaya visa","PTE","Kerja","Bawa pasangan","485","Pindah sekolah","Harga sekolah","Visa pasti?"].map(x => `<button type="button">${x}</button>`).join("")}</div><span class="ka-muted">Jangan tempel nama lengkap, paspor, atau rekening. Dicek ${esc(KARTU.checked || "")} · 1 AUD ≈ Rp ${Number(KARTU.kurs || 12330).toLocaleString("id-ID")} · angka final mengikuti offer letter.</span></div><div id="ka-tres"></div><h3 class="ka-h" id="ka-allh">Semua jawaban</h3><div class="ka-grid" id="ka-list"></div></section>`;
  // Kit Tim: postingan dirender ulang ke <main id="list"> (innerHTML), jadi yang disembunyikan elemen halamannya, bukan anak <main>.
  const konten = ["#filters", "#howbox", "main", ".tabbar"].map(q => document.querySelector(q)).filter(n => n && !host.contains(n));
  const show = v => { host.querySelectorAll(".ka-nav button").forEach(b => b.setAttribute("aria-pressed", b.dataset.v === v)); $("#ka-ai", host).hidden = v !== "ai"; if (v === "ai") setTimeout(() => { try { $("#ka-tq", host).focus({preventScroll: true}); } catch {} }, 50); konten.forEach(n => n.style.display = v === "konten" ? "" : "none"); cur = v; due(); };
  // Pengingat posting: angka diambil dari chip "🔴 n belum dibagikan" milik Kit Tim (tidak mengubah logika posting).
  let cur = "konten";
  const unread = () => { const u = document.getElementById("unread"); return u && !u.hidden ? parseInt((u.textContent.match(/\d+/) || ["0"])[0], 10) : 0; };
  const due = () => { const n = unread(), dot = $("#ka-dot", host), bx = $("#ka-due", host);
    dot.hidden = !n; dot.textContent = n;
    bx.hidden = !n || cur === "konten";
    $("#ka-due-t", host).textContent = `🔴 ${n} postingan marketing belum kamu bagikan. Bagikan dulu, cuma ±2 menit.`; };
  $("#ka-due-go", host).addEventListener("click", () => { show("konten"); window.scrollTo({top: 0, behavior: "smooth"}); });
  { const u = document.getElementById("unread"); if (u) new MutationObserver(due).observe(u, {attributes: true, childList: true, characterData: true, subtree: true}); }
  host.querySelector(".ka-nav").addEventListener("click", e => { const b = e.target.closest("button[data-v]"); if (b) show(b.dataset.v); });
  // Semua kartu (tampil saat kotak pertanyaan kosong)
  const list = $("#ka-list", host);
  list.innerHTML = KARTU.items.map((c, i) => `<article class="ka-card"><h3>${esc(c.q)}</h3><p class="ka-ans">${bold(c.a)}</p><span class="ka-muted">${esc(c.src || "")}</span><button type="button" class="ka-btn" data-i="${i}">Salin</button></article>`).join("");
  list.addEventListener("click", e => { const b = e.target.closest(".ka-btn"); if (b) copy(KARTU.items[b.dataset.i].a, b); });
  // Tanya Sistem: pencocokan kata kunci (offline) ke kartu Jawab Cepat
  const SYN = {brp:"berapa",berapaan:"berapa",bayar:"biaya",harga:"biaya",ongkos:"biaya",duit:"dana",uang:"dana",tabungan:"dana",saldo:"dana",rekening:"dana",
    suami:"pasangan",istri:"pasangan",bini:"pasangan",pacar:"pasangan",anak:"anak",keluarga:"pasangan",kerja:"kerja",part:"kerja",parttime:"kerja",jam:"jam",
    ielts:"ielts",pte:"pte",toefl:"english",inggris:"english",english:"english",skor:"english",nilai:"english",
    asuransi:"oshc",insurance:"oshc",oshc:"oshc",ditolak:"tolak",reject:"tolak",refusal:"tolak",tolak:"tolak",refund:"refund",balik:"refund",kembali:"refund",
    jamin:"jamin",pasti:"jamin",dijamin:"jamin",garansi:"jamin",turis:"visitor",tourist:"visitor",liburan:"visitor",whv:"whv",holiday:"whv",
    pindah:"transfer",ganti:"transfer",diskon:"diskon",promo:"diskon",potongan:"diskon",murah:"diskon",gs:"gs",genuine:"gs",
    coe:"coe",offer:"coe",lama:"coe",kapan:"coe",pastry:"patisserie",patiseri:"patisserie",kue:"patisserie",bakery:"patisserie",chef:"cookery",masak:"cookery",
    hidup:"living",makan:"living",sewa:"living",kos:"living",level:"level",evidence:"level",streamlined:"level",dalam:"onshore",onshore:"onshore",australia:"australia"};
  const norm = t => String(t || "").toLowerCase().replace(/[^a-z0-9à-ÿ\s]/g, " ").split(/\s+/).filter(w => w.length > 1).map(w => SYN[w] || SYN[w.replace(/(nya|kah|lah|ku|mu)$/, "")] || w.replace(/(nya|kah|lah)$/, ""));
  const STOP = new Set("ya ga gak nggak ngga kak ka min aku saya kalau kalo kl yg yang dan atau di ke dari untuk utk buat itu ini ada bisa apa gimana bagaimana mau harus juga sih dong deh nya terus trus tp tapi sama dgn dengan aja saja boleh berapa".split(" "));
  const docs = KARTU.items.map(c => ({c, w: [...norm(c.q), ...norm(c.q), ...norm(c.k), ...norm(c.k), ...norm(c.k), ...norm(c.a)]}));
  const df = {}; docs.forEach(d => new Set(d.w).forEach(w => df[w] = (df[w] || 0) + 1));
  const idf = w => Math.log(1 + docs.length / (df[w] || docs.length));
  const score = (txt) => { const q = [...new Set(norm(txt).filter(w => !STOP.has(w)))];
    return docs.map(d => { let sc = 0; for (const w of q) { const n = d.w.filter(x => x === w || (w.length >= 4 && x.startsWith(w))).length; if (n) sc += idf(w) * (1 + Math.log(n)); } return {c: d.c, sc}; }).sort((a, b) => b.sc - a.sc); };
  const MIN = 1.2;
  const tq = $("#ka-tq", host), tres = $("#ka-tres", host);
  const answer = () => { const txt = tq.value.trim(); list.hidden = $("#ka-allh", host).hidden = !!txt; if (!txt) { tres.innerHTML = ""; return; }
    const parts = txt.split(/[?\n]+/).map(x => x.trim()).filter(x => x.length > 2);
    const pick = []; const add = c => { if (c && !pick.includes(c)) pick.push(c); };
    for (const part of parts) { const r = score(part); if (r[0].sc >= MIN) add(r[0].c); }
    const all = score(txt); if (!pick.length && all[0].sc >= MIN) add(all[0].c);
    const harga = /biaya|harga|tuition|fee|murah|mahal|sekolah|kampus|college|university|jurusan|kursus/.test(txt.toLowerCase());
    const hargaSaja = /harga|tuition|fee|kursus|jurusan|sekolah|kampus/.test(txt.toLowerCase()) && !/visa|dana|rekening|hidup|oshc|asuransi|485|kerja|pasangan|suami|istri/.test(txt.toLowerCase());
    if (hargaSaja) pick.length = 0;
    const alt = all.filter(x => x.sc >= MIN && !pick.includes(x.c)).slice(0, 3).map(x => x.c);
    const tip = hargaSaja ? KARTU.items.find(c => c.t === "Cek harga") : null;
    const wa = hargaSaja ? "Halo kak 😊\n\nRincian biaya per sekolah & jurusan (biaya awal, total studi, dan bukti dana) bisa dicek langsung di pricelist kami: " + PRICELIST + "\n\nAtau kabari kami jurusan, kota, dan rencana mulainya, nanti kami bantu kirimkan rinciannya. Angka final mengikuti offer letter resmi sekolah." : pick.length ? "Halo kak 😊\n\n" + pick.map(c => c.a).join("\n\n") + (harga ? "\n\nUntuk rincian biaya sekolah/jurusan, cek di sini ya: " + PRICELIST : "") + "\n\nAngka final mengikuti offer letter & situs resmi. Ada lagi yang mau ditanyakan, kak?" : "";
    tres.innerHTML = (tip ? `<div class="ka-card"><h3>💬 Balasan WA (pertanyaan harga)</h3><p class="ka-ans">${bold(wa)}</p><button type="button" class="ka-btn" id="ka-twa">Salin balasan</button></div><div class="ka-card"><h3>🧭 Untuk tim: ${esc(tip.q)}</h3><p class="ka-ans">${bold(tip.a)}</p><a class="ka-cta" href="${PRICELIST}" target="_blank" rel="noopener">Buka pricelist ↗</a></div>` : "") + (tip ? "" : pick.length ? `<div class="ka-card"><h3>💬 Balasan WA (cek dulu sebelum kirim)</h3><p class="ka-ans">${bold(wa)}</p><button type="button" class="ka-btn" id="ka-twa">Salin balasan</button><span class="ka-muted">Dari kartu: ${pick.map(c => esc(c.q)).join(" · ")}</span></div>`
        : `<div class="ka-card"><h3>Belum ada jawaban resmi yang cocok</h3><p class="ka-ans">Coba kata lain (mis. "dana", "PTE", "pasangan", "485"), cek harga di pricelist, atau teruskan ke konsultan senior. Jangan menebak angka.</p><a class="ka-cta" href="${PRICELIST}" target="_blank" rel="noopener">Buka pricelist ↗</a></div>`)
      + (alt.length ? `<h3>Mungkin juga relevan</h3><div class="ka-grid">${alt.map(c => `<article class="ka-card"><h3>${esc(c.q)}</h3><p class="ka-ans">${bold(c.a)}</p><button type="button" class="ka-btn" data-i="${KARTU.items.indexOf(c)}">Salin</button></article>`).join("")}</div>` : "");
    const b = $("#ka-twa", tres); if (b) b.onclick = () => copy(wa, b); };
  let tqT; tq.addEventListener("input", () => { clearTimeout(tqT); tqT = setTimeout(answer, 250); });
  $("#ka-chips", host).addEventListener("click", e => { const b = e.target.closest("button"); if (!b) return; const map = {"Harga sekolah": "harga sekolah", "Visa pasti?": "visa pasti keluar"}; tq.value = map[b.textContent] || b.textContent; answer(); });
  tres.addEventListener("click", e => { const b = e.target.closest(".ka-btn[data-i]"); if (b) copy(KARTU.items[b.dataset.i].a, b); });
  // Selalu buka di tab Konten, supaya tim melihat postingan yang belum dibagikan setiap membuka aplikasi.
  show("konten");
  try { localStorage.removeItem("ka-p"); localStorage.removeItem("ka-v"); } catch {} // data Cek Student lama dihapus dari HP
  document.addEventListener("visibilitychange", () => { if (document.visibilityState === "visible" && unread() && cur !== "konten") due(); });
}
const go = () => { const header = document.querySelector("header.appbar"); const host = document.createElement("div"); host.id = "teg-asisten";
  host.style.cssText = "max-width:1100px;margin:0 auto;padding:0 16px;box-sizing:border-box";
  // Di luar <main>: isi <main id="list"> ditimpa saat postingan dimuat.
  if (header) header.after(host); else { const main = document.querySelector("main"); if (main) main.before(host); else document.body.prepend(host); } mount(host); };
document.readyState === "loading" ? document.addEventListener("DOMContentLoaded", go) : go();
})();
