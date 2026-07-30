import React from "react";
import { AbsoluteFill, staticFile } from "remotion";
import { z } from "zod";
import { fluxoDeNosSchema } from "../schema";
import {
  PALETA,
  FONT,
  useEnter,
  Titulo,
  No,
  Seta,
  Selo,
  Icone,
  Personagem,
} from "../comum";
import { interpolate } from "remotion";

export const FluxoDeNos: React.FC<z.infer<typeof fluxoDeNosSchema>> = ({
  titulo,
  subtitulo,
  nos,
  selos,
  fecho,
  personagem,
}) => {
  const ink = PALETA.ink;
  const n = nos.length;

  // distribuição horizontal dos nós na faixa 70..1010
  const larguraNo = 260;
  const faixa = 1080 - 140; // margens 70 cada lado
  const gap = n > 1 ? (faixa - n * larguraNo) / (n - 1) : 0;
  const xDe = (i: number) => 70 + i * (larguraNo + gap);

  // timing: nós entram espaçados a partir do frame 36, de 21 em 21
  const startNo = (i: number) => 36 + i * 21;
  const startSeta = (i: number) => 50 + i * 21;
  const startSelo = (i: number) => 90 + i * 12;
  const mp = useEnter(120);

  return (
    <AbsoluteFill style={{ background: `linear-gradient(${PALETA.bgTop}, ${PALETA.bgBottom})`, fontFamily: FONT }}>
      <Titulo texto={titulo} sub={subtitulo} ink={ink} />

      {/* Fluxo de nós + setas */}
      <div style={{ position: "absolute", top: 560, left: 0, width: 1080, height: 340 }}>
        {nos.map((no, i) => (
          <React.Fragment key={i}>
            <No
              label={no.label}
              color={PALETA.slots[i % PALETA.slots.length]}
              start={startNo(i)}
              x={xDe(i)}
              ink={ink}
              icone={<Icone nome={no.icone} ink={ink} />}
            />
            {i < n - 1 ? (
              <Seta x={xDe(i) + larguraNo - 15} start={startSeta(i)} ink={ink} />
            ) : null}
          </React.Fragment>
        ))}
      </div>

      {/* Selos */}
      {selos.length > 0 ? (
        <div style={{ position: "absolute", top: 1080, left: 60, width: 960, display: "flex", gap: 20 }}>
          {selos.map((s, i) => (
            <Selo
              key={i}
              titulo={s.titulo}
              sub={s.sub}
              color={PALETA.slots[i % PALETA.slots.length]}
              start={startSelo(i)}
              ink={ink}
              icone={<Icone nome={s.icone} ink={ink} size={44} />}
            />
          ))}
        </div>
      ) : null}

      {/* Faixa-chão + personagem + fecho */}
      {personagem ? (
        <>
          <div
            style={{
              position: "absolute",
              bottom: 0,
              left: 0,
              width: 1080,
              height: 470,
              background: PALETA.slots[0],
              opacity: interpolate(mp, [0, 1], [0, 0.45]),
              borderTopLeftRadius: 120,
              borderTopRightRadius: 120,
            }}
          />
          <Personagem src={staticFile(personagem)} start={120} largura={560} left={30} />
        </>
      ) : null}

      {fecho ? (
        <div
          style={{
            position: "absolute",
            bottom: 150,
            right: 70,
            width: 470,
            textAlign: "right",
            opacity: useEnter(130),
          }}
        >
          <div style={{ fontFamily: FONT, fontWeight: 900, fontSize: 46, color: ink, lineHeight: 1.05, whiteSpace: "pre-line" }}>
            {fecho.forte}
          </div>
          <div style={{ fontFamily: FONT, fontWeight: 700, fontSize: 28, color: PALETA.coral, marginTop: 14, lineHeight: 1.2, whiteSpace: "pre-line" }}>
            {fecho.leve}
          </div>
        </div>
      ) : null}
    </AbsoluteFill>
  );
};
