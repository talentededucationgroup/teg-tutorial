// TEG TTS Connector — remote MCP server (Cloudflare Worker, single file, no dependencies)
// Tools: list_voices, test_sample, generate_speech, generate_chapters
// Calls the official Azure AI Speech REST API; MP3 files are saved to a GitHub branch
// so Claude can fetch them for video editing. All credentials are Worker secrets.
//
// Secrets (Settings > Variables and Secrets > type "Secret"):
//   AZURE_SPEECH_KEY     Azure Speech resource key
//   AZURE_SPEECH_REGION  e.g. southeastasia
//   GITHUB_TOKEN         fine-grained token, only repo teg-tutorial, Contents: Read and write
//   MCP_PATH_TOKEN       long random string; the connector URL is https://<worker>/mcp/<MCP_PATH_TOKEN>
// Plain variables (optional): GITHUB_REPO (default talentededucationgroup/teg-tutorial),
//   GITHUB_BRANCH (default tts-audio), DEFAULT_VOICE (default id-ID-GadisNeural)

const VERSION = "1.0.0";
const MAX_CHARS = 5000;

const TOOLS = [
  {
    name: "list_voices",
    description: "List Azure Speech voices for a locale (default id-ID) and confirm whether id-ID-GadisNeural is available.",
    inputSchema: { type: "object", properties: { locale: { type: "string", default: "id-ID" } } },
  },
  {
    name: "test_sample",
    description: "Generate one short test MP3 (about 10 seconds) to check the voice before processing the whole script.",
    inputSchema: {
      type: "object",
      properties: {
        voice: { type: "string", description: "Azure voice short name, e.g. id-ID-GadisNeural" },
        rate: { type: "string", description: "Speaking rate, e.g. -5% or 0.95 or default" },
        text: { type: "string", description: "Optional sample text" },
      },
    },
  },
  {
    name: "generate_speech",
    description: "Turn text (or SSML) into an MP3 with Azure Speech and save it to GitHub. Returns the file URL and path.",
    inputSchema: {
      type: "object",
      required: ["text", "filename"],
      properties: {
        text: { type: "string", description: "Plain text, or full SSML when ssml=true (max 5000 chars)" },
        voice: { type: "string", description: "Azure voice short name (default id-ID-GadisNeural)" },
        rate: { type: "string", description: "e.g. -5%, +0%, 0.9, slow, medium" },
        pitch: { type: "string", description: "e.g. +2%, -1st, default" },
        filename: { type: "string", description: "File name, e.g. 07.mp3 (letters, digits, - _ . only)" },
        folder: { type: "string", description: "Folder in the audio branch, e.g. tutorial-v4" },
        ssml: { type: "boolean", default: false },
        sentence_pause_ms: { type: "integer", description: "Extra pause between sentences (0-1500)", default: 0 },
      },
    },
  },
  {
    name: "generate_chapters",
    description: "Generate one MP3 per chapter in a single call (max 20 chapters). Each item: {filename, text}.",
    inputSchema: {
      type: "object",
      required: ["chapters"],
      properties: {
        chapters: {
          type: "array", maxItems: 20,
          items: { type: "object", required: ["filename", "text"], properties: { filename: { type: "string" }, text: { type: "string" } } },
        },
        voice: { type: "string" }, rate: { type: "string" }, pitch: { type: "string" },
        folder: { type: "string" }, sentence_pause_ms: { type: "integer", default: 0 },
      },
    },
  },
];

const xmlEscape = (s) => s.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&apos;");
const safeName = (s, def) => {
  const v = String(s || def || "").trim();
  if (!/^[A-Za-z0-9._-]{1,80}$/.test(v) || v.includes("..")) throw new Error(`Invalid name: ${v}`);
  return v;
};
const safeProsody = (v, def) => {
  if (v === undefined || v === null || v === "") return def;
  const s = String(v).trim();
  if (/^(x-slow|slow|medium|fast|x-fast|default|x-low|low|high|x-high)$/.test(s)) return s;
  if (/^[+-]?\d+(\.\d+)?(%|st|Hz)?$/.test(s)) return s;
  throw new Error(`Invalid rate/pitch: ${s}`);
};

function buildSsml({ text, voice, rate, pitch, ssml, sentence_pause_ms }) {
  if (ssml) {
    if (!/^\s*<speak[\s>]/.test(text)) throw new Error("ssml=true needs a full <speak> document");
    return text;
  }
  const pause = Math.max(0, Math.min(1500, Number(sentence_pause_ms) || 0));
  let body = xmlEscape(text);
  if (pause) body = body.replace(/([.!?])\s+/g, `$1<break time="${pause}ms"/> `);
  return `<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="id-ID"><voice name="${xmlEscape(voice)}"><prosody rate="${rate}" pitch="${pitch}">${body}</prosody></voice></speak>`;
}

async function azureTts(env, ssml) {
  const r = await fetch(`https://${env.AZURE_SPEECH_REGION}.tts.speech.microsoft.com/cognitiveservices/v1`, {
    method: "POST",
    headers: {
      "Ocp-Apim-Subscription-Key": env.AZURE_SPEECH_KEY,
      "Content-Type": "application/ssml+xml",
      "X-Microsoft-OutputFormat": "audio-48khz-192kbitrate-mono-mp3",
      "User-Agent": "teg-tts-connector",
    },
    body: ssml,
  });
  if (!r.ok) throw new Error(`Azure Speech error ${r.status}: ${(await r.text()).slice(0, 300)}`);
  return new Uint8Array(await r.arrayBuffer());
}

function toBase64(bytes) {
  let bin = "";
  for (let i = 0; i < bytes.length; i += 0x8000) bin += String.fromCharCode.apply(null, bytes.subarray(i, i + 0x8000));
  return btoa(bin);
}

async function sha256Hex(bytes) {
  const h = await crypto.subtle.digest("SHA-256", bytes);
  return [...new Uint8Array(h)].map((b) => b.toString(16).padStart(2, "0")).join("");
}

async function gh(env, path, init = {}) {
  return fetch(`https://api.github.com${path}`, {
    ...init,
    headers: {
      Authorization: `Bearer ${env.GITHUB_TOKEN}`,
      Accept: "application/vnd.github+json",
      "X-GitHub-Api-Version": "2022-11-28",
      "User-Agent": "teg-tts-connector",
      ...(init.headers || {}),
    },
  });
}

async function ensureBranch(env, repo, branch) {
  const r = await gh(env, `/repos/${repo}/git/ref/heads/${branch}`);
  if (r.ok) return;
  const info = await (await gh(env, `/repos/${repo}`)).json();
  const base = await (await gh(env, `/repos/${repo}/git/ref/heads/${info.default_branch}`)).json();
  const c = await gh(env, `/repos/${repo}/git/refs`, { method: "POST", body: JSON.stringify({ ref: `refs/heads/${branch}`, sha: base.object.sha }) });
  if (!c.ok && c.status !== 422) throw new Error(`GitHub branch error ${c.status}`);
}

const branchReady = new Set();
async function saveToGithub(env, path, bytes, message) {
  const repo = env.GITHUB_REPO || "talentededucationgroup/teg-tutorial";
  const branch = env.GITHUB_BRANCH || "tts-audio";
  if (!branchReady.has(repo + branch)) { await ensureBranch(env, repo, branch); branchReady.add(repo + branch); }
  const content = toBase64(bytes);
  const put = (sha) => gh(env, `/repos/${repo}/contents/${path}`, {
    method: "PUT", body: JSON.stringify({ message, content, branch, ...(sha ? { sha } : {}) }),
  });
  let r = await put();
  if (r.status === 422 || r.status === 409) { // file already exists: overwrite with its sha
    const cur = await gh(env, `/repos/${repo}/contents/${path}?ref=${branch}`);
    r = await put(cur.ok ? (await cur.json()).sha : undefined);
  }
  if (!r.ok) throw new Error(`GitHub save error ${r.status}: ${(await r.text()).slice(0, 300)}`);
  const j = await r.json();
  return { repo, branch, path, commit: j.commit && j.commit.sha, raw_url: `https://raw.githubusercontent.com/${repo}/${branch}/${path}` };
}

async function generateOne(env, a) {
  const text = String(a.text || "");
  if (!text.trim()) throw new Error("text is empty");
  if (text.length > MAX_CHARS) throw new Error(`text longer than ${MAX_CHARS} characters; split it per chapter`);
  const voice = String(a.voice || env.DEFAULT_VOICE || "id-ID-GadisNeural");
  if (!/^[A-Za-z]{2,3}-[A-Za-z]{2,4}-[A-Za-z0-9:]+$/.test(voice)) throw new Error(`Invalid voice: ${voice}`);
  let filename = safeName(a.filename);
  if (!filename.toLowerCase().endsWith(".mp3")) filename += ".mp3";
  const folder = safeName(a.folder, "audio");
  const ssml = buildSsml({ text, voice, rate: safeProsody(a.rate, "default"), pitch: safeProsody(a.pitch, "default"), ssml: !!a.ssml, sentence_pause_ms: a.sentence_pause_ms });
  const mp3 = await azureTts(env, ssml);
  const saved = await saveToGithub(env, `${folder}/${filename}`, mp3, `TTS ${folder}/${filename} (${voice})`);
  return { ok: true, voice, filename, bytes: mp3.length, sha256: await sha256Hex(mp3), approx_seconds: Math.round((mp3.length * 8) / 192000 * 10) / 10, ...saved };
}

async function listVoices(env, locale = "id-ID") {
  const r = await fetch(`https://${env.AZURE_SPEECH_REGION}.tts.speech.microsoft.com/cognitiveservices/voices/list`, {
    headers: { "Ocp-Apim-Subscription-Key": env.AZURE_SPEECH_KEY },
  });
  if (!r.ok) throw new Error(`Azure voices/list error ${r.status}`);
  const all = await r.json();
  const voices = all.filter((v) => (v.Locale || "").toLowerCase() === locale.toLowerCase())
    .map((v) => ({ name: v.ShortName, display: v.DisplayName, gender: v.Gender, type: v.VoiceType, styles: v.StyleList || [] }));
  return { region: env.AZURE_SPEECH_REGION, locale, count: voices.length, gadis_available: voices.some((v) => v.name === "id-ID-GadisNeural"), voices };
}

async function callTool(env, name, a = {}) {
  switch (name) {
    case "list_voices": return listVoices(env, a.locale || "id-ID");
    case "test_sample":
      return generateOne(env, {
        text: a.text || "Hai, teman-teman! Ini contoh suara untuk video tutorial daftar harga biaya studi dari Talented Education Group. Semua angka dalam dolar Australia, ya.",
        voice: a.voice, rate: a.rate || "-5%", filename: `sample-${(a.voice || env.DEFAULT_VOICE || "id-ID-GadisNeural").replace(/[^A-Za-z0-9-]/g, "")}-${Date.now()}.mp3`,
        folder: "samples", sentence_pause_ms: 300,
      });
    case "generate_speech": return generateOne(env, a);
    case "generate_chapters": {
      const items = Array.isArray(a.chapters) ? a.chapters.slice(0, 20) : [];
      if (!items.length) throw new Error("chapters is empty");
      const results = [];
      for (const c of items) {
        try { results.push(await generateOne(env, { ...a, ...c, chapters: undefined })); }
        catch (e) { results.push({ ok: false, filename: c.filename, error: String(e.message || e) }); }
      }
      return { ok: results.every((r) => r.ok), count: results.length, results };
    }
    default: throw new Error(`Unknown tool: ${name}`);
  }
}

function rpc(id, result, error) {
  return error ? { jsonrpc: "2.0", id, error } : { jsonrpc: "2.0", id, result };
}

async function handleMessage(env, m) {
  const { id, method, params = {} } = m;
  if (id === undefined || id === null) return null; // notification
  if (method === "initialize") {
    return rpc(id, { protocolVersion: params.protocolVersion || "2025-06-18", capabilities: { tools: {} }, serverInfo: { name: "teg-tts", version: VERSION } });
  }
  if (method === "ping") return rpc(id, {});
  if (method === "tools/list") return rpc(id, { tools: TOOLS });
  if (method === "tools/call") {
    try {
      const out = await callTool(env, params.name, params.arguments || {});
      return rpc(id, { content: [{ type: "text", text: JSON.stringify(out, null, 2) }], structuredContent: out });
    } catch (e) {
      return rpc(id, { content: [{ type: "text", text: `Error: ${e.message || e}` }], isError: true });
    }
  }
  return rpc(id, undefined, { code: -32601, message: `Method not found: ${method}` });
}

function timingSafeEqual(a, b) {
  if (typeof a !== "string" || typeof b !== "string" || a.length !== b.length) return false;
  let d = 0;
  for (let i = 0; i < a.length; i++) d |= a.charCodeAt(i) ^ b.charCodeAt(i);
  return d === 0;
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const m = url.pathname.match(/^\/mcp\/([^/]+)\/?$/);
    if (!m || !env.MCP_PATH_TOKEN || env.MCP_PATH_TOKEN.length < 24 || !timingSafeEqual(m[1], env.MCP_PATH_TOKEN)) {
      return new Response("Not found", { status: 404 });
    }
    if (request.method === "GET") return new Response("Method not allowed", { status: 405, headers: { Allow: "POST" } });
    if (request.method === "DELETE") return new Response(null, { status: 204 });
    if (request.method !== "POST") return new Response("Method not allowed", { status: 405 });
    let body;
    try { body = await request.json(); } catch { return Response.json(rpc(null, undefined, { code: -32700, message: "Parse error" }), { status: 400 }); }
    const batch = Array.isArray(body);
    const out = (await Promise.all((batch ? body : [body]).map((x) => handleMessage(env, x)))).filter(Boolean);
    if (!out.length) return new Response(null, { status: 202 });
    return Response.json(batch ? out : out[0], { headers: { "Cache-Control": "no-store" } });
  },
};
