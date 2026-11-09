# TEG TTS Connector (Azure Speech → MP3 → GitHub)

Remote MCP server untuk Claude. Alat: `list_voices`, `test_sample`, `generate_speech`, `generate_chapters`.
Memanggil API resmi Azure AI Speech (REST `cognitiveservices/v1`), menyimpan MP3 di branch `tts-audio`
repo ini, dan mengembalikan `raw_url` + `path` + `sha256`. Semua kredensial disimpan sebagai **Secret** di Cloudflare,
tidak pernah di kode, chat, atau artifact.

## Secret yang dibutuhkan
| Nama | Isi |
|---|---|
| AZURE_SPEECH_KEY | Key 1 dari resource Azure Speech |
| AZURE_SPEECH_REGION | Region resource, mis. `southeastasia` |
| GITHUB_TOKEN | Fine-grained token: hanya repo `teg-tutorial`, izin **Contents: Read and write** |
| MCP_PATH_TOKEN | Teks acak minimal 24 karakter (huruf/angka). Menjadi bagian rahasia URL connector |

URL connector: `https://teg-tts.<subdomain>.workers.dev/mcp/<MCP_PATH_TOKEN>` (simpan seperti password).

## Batas
- Maks 5.000 karakter per file, 20 bab per panggilan `generate_chapters`.
- Cloudflare Workers paket gratis membatasi waktu CPU; bila `generate_chapters` gagal, buat per bab dengan `generate_speech` atau pakai paket Workers Paid.
