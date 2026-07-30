import React from "react";
import {
  useCurrentFrame,
  useVideoConfig,
  interpolate,
  spring,
  Easing,
} from "remotion";

// ---- Paleta base (didático materno/infantil; sobrescrevível por props) ----
export const PALETA = {
  bgTop: "#FCE9D4",
  bgBottom: "#F6DCC0",
  ink: "#1E3A5F",
  coral: "#F08A6E",
  // cores rotativas dos nós/selos
  slots: ["#A8D5C8", "#F4D06F", "#B9A7E0", "#F3B0A3", "#9FC3E8"],
};

// entrada com spring suave — damping alto + stiffness baixa = entra sem pressa
export const useEnter = (startFrame: number, damping = 22) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  return spring({
    frame: frame - startFrame,
    fps,
    config: { damping, mass: 1, stiffness: 70 },
  });
};

export const FONT =
  "Arial, 'Helvetica Neue', Helvetica, sans-serif";

// Título grande no topo, descendo e assentando
export const Titulo: React.FC<{ texto: string; sub?: string; ink: string }> = ({
  texto,
  sub,
  ink,
}) => {
  const tp = useEnter(0);
  const sp = useEnter(15);
  return (
    <>
      <div
        style={{
          position: "absolute",
          top: 90,
          width: "100%",
          textAlign: "center",
          opacity: tp,
          transform: `translateY(${interpolate(tp, [0, 1], [-60, 0])}px)`,
        }}
      >
        <div
          style={{
            fontFamily: FONT,
            fontWeight: 900,
            fontSize: texto.length > 12 ? 104 : 130,
            color: ink,
            letterSpacing: -2,
            lineHeight: 0.95,
          }}
        >
          {texto}
        </div>
      </div>
      {sub ? (
        <div
          style={{
            position: "absolute",
            top: texto.length > 12 ? 300 : 250,
            width: "100%",
            textAlign: "center",
            opacity: sp,
          }}
        >
          <div
            style={{
              fontFamily: FONT,
              fontWeight: 700,
              fontSize: 38,
              color: ink,
              lineHeight: 1.25,
              whiteSpace: "pre-line",
            }}
          >
            {sub}
          </div>
        </div>
      ) : null}
    </>
  );
};

// Nó (pedra arredondada com ícone flutuante e rótulo)
export const No: React.FC<{
  label: string;
  color: string;
  start: number;
  x: number;
  ink: string;
  icone: React.ReactNode;
}> = ({ label, color, start, x, ink, icone }) => {
  const p = useEnter(start);
  return (
    <div
      style={{
        position: "absolute",
        left: x,
        bottom: 0,
        width: 260,
        opacity: p,
        transform: `translateY(${interpolate(p, [0, 1], [60, 0])}px) scale(${interpolate(p, [0, 1], [0.6, 1])})`,
        transformOrigin: "bottom center",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
      }}
    >
      <div
        style={{
          width: 96,
          height: 96,
          borderRadius: "50%",
          background: "#fff",
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          boxShadow: "0 6px 18px rgba(30,58,95,0.15)",
          marginBottom: -34,
          zIndex: 2,
        }}
      >
        {icone}
      </div>
      <div
        style={{
          width: 260,
          height: 190,
          borderRadius: "48% 48% 46% 46% / 60% 60% 40% 40%",
          background: color,
          display: "flex",
          alignItems: "flex-end",
          justifyContent: "center",
          paddingBottom: 30,
          boxShadow: "inset 0 -10px 20px rgba(0,0,0,0.06)",
        }}
      >
        <span
          style={{
            fontFamily: FONT,
            fontWeight: 800,
            fontSize: label.length > 6 ? 40 : 46,
            color: ink,
            letterSpacing: -0.5,
          }}
        >
          {label}
        </span>
      </div>
    </div>
  );
};

// Seta que se desenha (clip-path avançando)
export const Seta: React.FC<{ x: number; start: number; ink: string }> = ({
  x,
  start,
  ink,
}) => {
  const frame = useCurrentFrame();
  const draw = interpolate(frame, [start, start + 18], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });
  return (
    <div
      style={{
        position: "absolute",
        left: x,
        bottom: 210,
        width: 90,
        height: 40,
        clipPath: `inset(0 ${(1 - draw) * 100}% 0 0)`,
      }}
    >
      <svg width="90" height="40" viewBox="0 0 90 40" fill="none">
        <path d="M4 20 H74" stroke={ink} strokeWidth="7" strokeLinecap="round" />
        <path
          d="M62 8 L80 20 L62 32"
          stroke={ink}
          strokeWidth="7"
          strokeLinecap="round"
          strokeLinejoin="round"
          fill="none"
        />
      </svg>
    </div>
  );
};

// Selo de benefício (círculo com ícone + título + subtítulo)
export const Selo: React.FC<{
  titulo: string;
  sub: string;
  color: string;
  start: number;
  ink: string;
  icone: React.ReactNode;
}> = ({ titulo, sub, color, start, ink, icone }) => {
  const p = useEnter(start);
  return (
    <div
      style={{
        flex: 1,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        opacity: p,
        transform: `translateY(${interpolate(p, [0, 1], [24, 0])}px)`,
      }}
    >
      <div
        style={{
          width: 92,
          height: 92,
          borderRadius: "50%",
          background: color,
          display: "flex",
          alignItems: "center",
          justifyContent: "center",
          marginBottom: 16,
        }}
      >
        {icone}
      </div>
      <span style={{ fontFamily: FONT, fontWeight: 800, fontSize: 30, color: ink }}>
        {titulo}
      </span>
      <span
        style={{
          fontFamily: FONT,
          fontWeight: 600,
          fontSize: 22,
          color: ink,
          opacity: 0.8,
          textAlign: "center",
          marginTop: 4,
          lineHeight: 1.2,
          maxWidth: 260,
        }}
      >
        {sub}
      </span>
    </div>
  );
};

// Ícones nomeados (o JSON passa uma string; aqui vira SVG)
export const Icone: React.FC<{ nome: string; ink: string; size?: number }> = ({
  nome,
  ink,
  size = 46,
}) => {
  const s = size;
  switch (nome) {
    case "som":
      return (
        <svg width={s} height={s} viewBox="0 0 24 24" fill="none">
          <path d="M4 9v6h4l5 4V5L8 9H4z" fill={ink} />
          <path d="M16 8c1.5 1.2 1.5 6.8 0 8" stroke={ink} strokeWidth="2" strokeLinecap="round" fill="none" />
        </svg>
      );
    case "letra":
      return <span style={{ fontFamily: FONT, fontWeight: 900, fontSize: s + 6, color: ink }}>A</span>;
    case "livro":
      return (
        <svg width={s} height={s} viewBox="0 0 24 24" fill="none">
          <path d="M3 5c3-1 6-1 9 1 3-2 6-2 9-1v13c-3-1-6-1-9 1-3-2-6-2-9-1V5z" stroke={ink} strokeWidth="2" fill="#fff" strokeLinejoin="round" />
          <path d="M12 7v11" stroke={ink} strokeWidth="2" />
        </svg>
      );
    case "cerebro":
      return (
        <svg width={s} height={s} viewBox="0 0 24 24" fill="none">
          <path d="M12 4c-1.6 0-3 1-3.5 2.4C7 6.6 6 7.9 6 9.4c0 .7.2 1.3.5 1.9C6 11.8 5.7 12.6 5.7 13.4c0 1.6 1.2 2.9 2.8 3 .5 1 1.5 1.7 2.7 1.7.5 0 .8-.4.8-.9V5c0-.6-.4-1-1-1z" fill="#fff" stroke={ink} strokeWidth="1.6" strokeLinejoin="round" />
          <path d="M13 4c1.6 0 3 1 3.5 2.4C18 6.6 19 7.9 19 9.4c0 .7-.2 1.3-.5 1.9.3.5.6 1.3.6 2.1 0 1.6-1.2 2.9-2.8 3-.5 1-1.5 1.7-2.7 1.7-.5 0-.8-.4-.8-.9V5c0-.6.4-1 1-1z" fill="#fff" stroke={ink} strokeWidth="1.6" strokeLinejoin="round" />
        </svg>
      );
    case "lapis":
      return (
        <svg width={s} height={s} viewBox="0 0 24 24" fill="none">
          <path d="M4 20l2-6L16 4l4 4L10 18l-6 2z" stroke={ink} strokeWidth="1.8" fill="#fff" strokeLinejoin="round" />
        </svg>
      );
    case "check":
      return (
        <svg width={s} height={s} viewBox="0 0 24 24" fill="none">
          <path d="M4 12l5 5L20 6" stroke={ink} strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" fill="none" />
        </svg>
      );
    case "x":
      return (
        <svg width={s} height={s} viewBox="0 0 24 24" fill="none">
          <path d="M6 6l12 12M18 6L6 18" stroke={ink} strokeWidth="3" strokeLinecap="round" />
        </svg>
      );
    case "mudo":
      return (
        <svg width={s} height={s} viewBox="0 0 24 24" fill="none">
          <path d="M4 9v6h4l5 4V5L8 9H4z" fill={ink} />
          <path d="M16 8l6 8M22 8l-6 8" stroke={ink} strokeWidth="2" strokeLinecap="round" />
        </svg>
      );
    default:
      return <span style={{ fontFamily: FONT, fontWeight: 900, fontSize: s, color: ink }}>?</span>;
  }
};

// Personagem recortado (PNG com alpha) subindo no rodapé
export const Personagem: React.FC<{ src: string; start: number; largura: number; left: number }> = ({
  src,
  start,
  largura,
  left,
}) => {
  const p = useEnter(start);
  return (
    <div
      style={{
        position: "absolute",
        bottom: -30,
        left,
        width: largura,
        opacity: p,
        transform: `translateY(${interpolate(p, [0, 1], [90, 0])}px)`,
      }}
    >
      <img src={src} style={{ width: "100%" }} alt="" />
    </div>
  );
};
