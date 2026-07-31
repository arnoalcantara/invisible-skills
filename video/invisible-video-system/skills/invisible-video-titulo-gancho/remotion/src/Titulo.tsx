import React from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig, interpolate, Easing } from "remotion";

// ---- Estilo: fundo branco único, texto preto Helvetica bold, cantos arredondados.
const CAP_BG = "#FFFFFF";
const CAP_INK = "#000000";
const FONT = "Helvetica, Arial, sans-serif";

export type TituloProps = {
  texto: string; // frase do título; " / " força quebra de linha
  emoji: string; // um emoji, exibido acima do texto
  duracaoSeg: number; // quanto tempo o título fica na tela
  topOffset: number; // distância do topo em px
  fontSize: number;
};

export const Titulo: React.FC<TituloProps> = ({
  texto,
  emoji,
  duracaoSeg,
  topOffset,
  fontSize,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // sem "entrada": já está na tela desde o frame 0. Só sai com fade no fim.
  const fimF = duracaoSeg * fps;
  const opacity = interpolate(frame, [fimF - 8, fimF], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.in(Easing.cubic),
  });

  // quebra manual por " / "; senão o texto flui e o balão único abraça tudo.
  const linhas = texto.includes(" / ")
    ? texto.split(" / ").map((s) => s.trim())
    : [texto.trim()];

  return (
    <AbsoluteFill>
      <div
        style={{
          position: "absolute",
          top: topOffset,
          width: "100%",
          display: "flex",
          justifyContent: "center",
          opacity,
        }}
      >
        <div
          style={{
            background: CAP_BG,
            color: CAP_INK,
            fontFamily: FONT,
            borderRadius: 28,
            boxShadow: "0 8px 24px rgba(0,0,0,0.18)",
            padding: "28px 40px",
            maxWidth: 860,
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            gap: 8,
          }}
        >
          <div style={{ fontSize: fontSize * 1.35, lineHeight: 1 }}>{emoji}</div>
          <div
            style={{
              fontWeight: 800,
              fontSize,
              lineHeight: 1.12,
              letterSpacing: -0.5,
              textAlign: "center",
              whiteSpace: "pre-line",
            }}
          >
            {linhas.join("\n")}
          </div>
        </div>
      </div>
    </AbsoluteFill>
  );
};
