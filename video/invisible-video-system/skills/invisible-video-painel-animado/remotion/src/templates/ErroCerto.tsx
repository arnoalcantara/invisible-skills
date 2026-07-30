import React from "react";
import { AbsoluteFill, staticFile, interpolate } from "remotion";
import { z } from "zod";
import { erroCertoSchema } from "../schema";
import { PALETA, FONT, useEnter, Titulo, Icone, Personagem } from "../comum";

export const ErroCerto: React.FC<z.infer<typeof erroCertoSchema>> = ({
  titulo,
  subtitulo,
  esquerda,
  direita,
  personagem,
}) => {
  const ink = PALETA.ink;
  const le = useEnter(30);
  const ri = useEnter(48);
  const xMark = interpolate(useEnter(40), [0, 1], [0, 1]);

  const Metade: React.FC<{
    lado: "esq" | "dir";
    rotulo: string;
    icone: string;
    p: number;
    riscado: boolean;
  }> = ({ lado, rotulo, icone, p, riscado }) => (
    <div
      style={{
        position: "absolute",
        top: 560,
        left: lado === "esq" ? 70 : 570,
        width: 440,
        height: 620,
        background: "#FBF3E7",
        borderRadius: 40,
        opacity: p,
        transform: `translateY(${interpolate(p, [0, 1], [40, 0])}px)`,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        gap: 40,
      }}
    >
      <div style={{ position: "relative", width: 220, height: 220, display: "flex", alignItems: "center", justifyContent: "center" }}>
        <Icone nome={icone} ink={ink} size={150} />
        {riscado ? (
          <svg width="240" height="240" viewBox="0 0 240 240" style={{ position: "absolute", top: -10, left: -10, clipPath: `inset(0 ${(1 - xMark) * 100}% 0 0)` }}>
            <path d="M30 30 L210 210 M210 30 L30 210" stroke={PALETA.coral} strokeWidth="16" strokeLinecap="round" />
          </svg>
        ) : null}
      </div>
      <span style={{ fontFamily: FONT, fontWeight: 800, fontSize: 44, color: ink }}>{rotulo}</span>
    </div>
  );

  return (
    <AbsoluteFill style={{ background: `linear-gradient(${PALETA.bgTop}, ${PALETA.bgBottom})`, fontFamily: FONT }}>
      <Titulo texto={titulo} sub={subtitulo} ink={ink} />
      <Metade lado="esq" rotulo={esquerda.rotulo} icone={esquerda.icone} p={le} riscado />
      <Metade lado="dir" rotulo={direita.rotulo} icone={direita.icone} p={ri} riscado={false} />
      {personagem ? <Personagem src={staticFile(personagem)} start={90} largura={440} left={320} /> : null}
    </AbsoluteFill>
  );
};
