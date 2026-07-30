import React from "react";
import { AbsoluteFill, staticFile, interpolate } from "remotion";
import { z } from "zod";
import { conceitoNomeadoSchema } from "../schema";
import { PALETA, FONT, useEnter, Titulo, Icone, Personagem } from "../comum";

export const ConceitoNomeado: React.FC<z.infer<typeof conceitoNomeadoSchema>> = ({
  titulo,
  subtitulo,
  explicacao,
  icone,
  personagem,
}) => {
  const ink = PALETA.ink;
  const ip = useEnter(45);
  const ep = useEnter(75);

  return (
    <AbsoluteFill style={{ background: `linear-gradient(${PALETA.bgTop}, ${PALETA.bgBottom})`, fontFamily: FONT }}>
      <Titulo texto={titulo} sub={subtitulo} ink={ink} />

      {/* Ícone-conceito grande no centro */}
      <div
        style={{
          position: "absolute",
          top: 620,
          width: "100%",
          display: "flex",
          justifyContent: "center",
          opacity: ip,
          transform: `scale(${interpolate(ip, [0, 1], [0.7, 1])})`,
        }}
      >
        <div
          style={{
            width: 300,
            height: 300,
            borderRadius: "50%",
            background: PALETA.slots[2],
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
          }}
        >
          <Icone nome={icone} ink={ink} size={150} />
        </div>
      </div>

      {/* Explicação num cartão */}
      <div
        style={{
          position: "absolute",
          top: 1000,
          left: 90,
          width: 900,
          opacity: ep,
          transform: `translateY(${interpolate(ep, [0, 1], [30, 0])}px)`,
          background: "#FBF3E7",
          borderRadius: 32,
          padding: "40px 50px",
          textAlign: "center",
        }}
      >
        <span style={{ fontFamily: FONT, fontWeight: 700, fontSize: 40, color: ink, lineHeight: 1.3, whiteSpace: "pre-line" }}>
          {explicacao}
        </span>
      </div>

      {personagem ? <Personagem src={staticFile(personagem)} start={100} largura={460} left={40} /> : null}
    </AbsoluteFill>
  );
};
