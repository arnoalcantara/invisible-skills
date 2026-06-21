// Converte o JSON do WhisperX (segments→words) — a saída da skill
// invisible-legenda-arquivos — para Caption[] do @remotion/captions.
// Uma Caption por palavra (token), base da legenda karaokê com word-highlight.
//
// Uso: node convert_captions.mjs <whisperx.json> <saida-captions.json>
//
// Trata palavras sem timestamp (score 0 / sem start-end): interpola entre a
// borda da palavra anterior e o início da próxima, para nenhuma palavra "sumir".

import { readFileSync, writeFileSync } from "node:fs";

const [, , inPath, outPath] = process.argv;
if (!inPath || !outPath) {
  console.error("uso: node convert_captions.mjs <whisperx.json> <captions.json>");
  process.exit(1);
}

const wx = JSON.parse(readFileSync(inPath, "utf8"));

// 1) achata todas as palavras na ordem, guardando o que tem timestamp
const flat = [];
for (const seg of wx.segments ?? []) {
  for (const w of seg.words ?? []) {
    flat.push({
      word: w.word,
      start: typeof w.start === "number" ? w.start : null,
      end: typeof w.end === "number" ? w.end : null,
      score: typeof w.score === "number" ? w.score : null,
    });
  }
}

if (flat.length === 0) {
  console.error(`erro: nenhuma palavra encontrada em ${inPath}`);
  process.exit(2);
}

// 2) preenche buracos: palavra sem start/end herda da vizinhança
for (let i = 0; i < flat.length; i++) {
  const w = flat[i];
  if (w.start === null) {
    const prev = flat[i - 1];
    w.start = prev && prev.end !== null ? prev.end : (w.end ?? 0);
  }
  if (w.end === null) {
    const next = flat[i + 1];
    w.end = next && next.start !== null ? next.start : w.start + 0.12;
  }
  if (w.end < w.start) w.end = w.start + 0.08; // segurança
}

// 3) vira Caption[] — text com espaço inicial (whitespace preservation)
const captions = flat.map((w) => ({
  text: " " + w.word.trim(),
  startMs: Math.round(w.start * 1000),
  endMs: Math.round(w.end * 1000),
  timestampMs: Math.round(((w.start + w.end) / 2) * 1000),
  confidence: w.score,
}));

writeFileSync(outPath, JSON.stringify(captions, null, 2));
console.log(`ok: ${captions.length} palavras -> ${outPath}`);
