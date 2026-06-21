import { Fragment, useCallback, useEffect, useMemo, useState } from "react";
import {
  AbsoluteFill,
  Easing,
  Sequence,
  interpolate,
  interpolateColors,
  spring,
  staticFile,
  useCurrentFrame,
  useDelayRender,
  useVideoConfig,
} from "remotion";
import {
  createTikTokStyleCaptions,
  type Caption,
  type TikTokPage,
} from "@remotion/captions";
import type { CSSProperties } from "react";

// ----------------------------------------------------------------------------
// PRESETS DE ESTILO
// Cada preset descreve ritmo (combineMs), tipografia, posição e como destaca a
// palavra falada. Trocar de visual = trocar de preset.
// Fontes dedicadas (Google/local) reforçam ainda mais cada "cara" — aqui ficam
// fontes de sistema para o template rodar sem download extra.
//
// CAMADA DE ANIMAÇÃO (campos opcionais — quando ausentes, o destaque é "seco",
// o comportamento original de liga/desliga):
//   - pop:            spring no scale da palavra ativa (overshoot estilo TikTok)
//   - colorFadeFrames: nº de frames pra suavizar a troca de cor (0 = seco)
//   - enter:          entrada da página (fade-in + slide de baixo)
// ----------------------------------------------------------------------------

type HighlightMode = "color" | "box" | "opacity" | "none";

export type PresetName = "reels" | "hormozi" | "minimal" | "classic";

// spring de entrada da palavra ativa (pop com overshoot)
type PopAnim = {
  damping: number; // menor = mais "molinha"/overshoot
  stiffness?: number; // maior = mais rápido/seco
  mass?: number; // maior = mais lento/pesado
  outFrames?: number; // frames pra voltar ao normal quando a palavra passa
};

// entrada da página inteira
type EnterAnim = {
  fadeFrames?: number; // frames de fade-in (0 = sem fade)
  slideY?: number; // px de slide de baixo pra cima na entrada
};

type Preset = {
  combineMs: number; // quanto tempo de palavras cabe por página
  fontFamily: string;
  fontSize: number;
  fontWeight: number;
  uppercase: boolean;
  letterSpacing: number;
  lineHeight: number;
  bottomOffset: number; // distância do rodapé (px) em 1920 de altura
  paddingX: number;
  baseColor: string;
  activeColor: string;
  stroke: string | null;
  textShadow: string | null;
  highlightMode: HighlightMode;
  boxColor?: string;
  boxTextColor?: string;
  inactiveOpacity?: number;
  scaleActive: number;
  // --- camada de animação (opcional) ---
  pop?: PopAnim;
  colorFadeFrames?: number;
  enter?: EnterAnim;
};

export const PRESETS: Record<PresetName, Preset> = {
  // 1. Reels amarelo — palavra falada acende em amarelo
  reels: {
    combineMs: 1200,
    fontFamily: "Helvetica, Arial, sans-serif",
    fontSize: 92,
    fontWeight: 800,
    uppercase: true,
    letterSpacing: 0,
    lineHeight: 1.15,
    bottomOffset: 430,
    paddingX: 80,
    baseColor: "#FFFFFF",
    activeColor: "#FFD400",
    stroke: "3px #000",
    textShadow: "0 4px 14px rgba(0,0,0,0.55), 0 0 2px rgba(0,0,0,0.9)",
    highlightMode: "color",
    scaleActive: 1.12,
    // animação aprovada (validada ao vivo no studio)
    pop: { damping: 9, stiffness: 130, mass: 0.7, outFrames: 5 },
    colorFadeFrames: 3,
    enter: { fadeFrames: 5, slideY: 24 },
  },
  // 2. Hormozi caixa — palavra falada ganha um retângulo amarelo, texto preto
  //    (EXPERIMENTAL — ainda em ajuste; não ofereça como pronto)
  hormozi: {
    combineMs: 900,
    fontFamily: "Helvetica, Arial, sans-serif",
    fontSize: 96,
    fontWeight: 800,
    uppercase: true,
    letterSpacing: 1,
    lineHeight: 1.1,
    bottomOffset: 470,
    paddingX: 90,
    baseColor: "#FFFFFF",
    activeColor: "#000000",
    stroke: "4px #000",
    textShadow: "0 4px 16px rgba(0,0,0,0.6)",
    highlightMode: "box",
    boxColor: "#FFE000",
    boxTextColor: "#000000",
    scaleActive: 1.06,
  },
  // 3. Minimalista branco — tudo branco; o que ainda não foi falado fica esmaecido
  minimal: {
    combineMs: 1400,
    fontFamily: '"Helvetica Neue", Helvetica, Arial, sans-serif',
    fontSize: 76,
    fontWeight: 600,
    uppercase: false,
    letterSpacing: 0,
    lineHeight: 1.25,
    bottomOffset: 360,
    paddingX: 110,
    baseColor: "#FFFFFF",
    activeColor: "#FFFFFF",
    stroke: null,
    textShadow: "0 2px 10px rgba(0,0,0,0.6)",
    highlightMode: "opacity",
    inactiveOpacity: 0.45,
    scaleActive: 1.0,
  },
  // 4. Clássico legenda — bloco de frase, branco com sombra, sem karaokê.
  //    bottomOffset 380: terço inferior, longe da zona de UI do Instagram.
  classic: {
    combineMs: 2200,
    fontFamily: "Helvetica, Arial, sans-serif",
    fontSize: 54,
    fontWeight: 500,
    uppercase: false,
    letterSpacing: 0,
    lineHeight: 1.3,
    bottomOffset: 380,
    paddingX: 120,
    baseColor: "#FFFFFF",
    activeColor: "#FFFFFF",
    stroke: null,
    textShadow: "0 2px 4px rgba(0,0,0,0.95), 0 0 6px rgba(0,0,0,0.7)",
    highlightMode: "none",
    scaleActive: 1.0,
  },
};

// "activeness" animado de um token: sobe ao acender (pop), assenta enquanto
// ativo e volta a 0 quando a palavra passa. Retorna o progresso pro scale (com
// overshoot do spring) e pro fade de cor (clampado 0..1).
function computeTokenAnim(
  preset: Preset,
  token: { fromMs: number; toMs: number },
  pageStartMs: number,
  frame: number,
  fps: number,
): { scaleProg: number; colorProg: number } {
  const startF = ((token.fromMs - pageStartMs) / 1000) * fps;
  const endF = ((token.toMs - pageStartMs) / 1000) * fps;

  // sem animação de pop: degrau (comportamento original)
  if (!preset.pop) {
    const isActive = frame >= startF && frame < endF;
    return { scaleProg: isActive ? 1 : 0, colorProg: isActive ? 1 : 0 };
  }

  const outFrames = preset.pop.outFrames ?? 5;
  // subida: spring (com overshoot) a partir do acender da palavra
  const rise = spring({
    frame: frame - startF,
    fps,
    config: {
      damping: preset.pop.damping,
      stiffness: preset.pop.stiffness ?? 100,
      mass: preset.pop.mass ?? 1,
    },
  });
  // descida: depois que a palavra passa, volta a 0
  const release = interpolate(frame, [endF, endF + outFrames], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const scaleProg = frame < startF ? 0 : frame < endF ? rise : rise * release;

  // cor: fade clampado (sem overshoot, pra não "estourar" a cor)
  const fadeFrames = preset.colorFadeFrames ?? 0;
  const colorRise = fadeFrames
    ? interpolate(frame, [startF, startF + fadeFrames], [0, 1], {
        extrapolateLeft: "clamp",
        extrapolateRight: "clamp",
      })
    : frame >= startF
      ? 1
      : 0;
  const colorProg =
    frame < startF ? 0 : frame < endF ? colorRise : colorRise * release;

  return { scaleProg, colorProg };
}

function tokenStyle(
  preset: Preset,
  scaleProg: number,
  colorProg: number,
): CSSProperties {
  const base: CSSProperties = { display: "inline-block" };
  const scale = 1 + (preset.scaleActive - 1) * scaleProg;

  switch (preset.highlightMode) {
    case "box": {
      const on = colorProg > 0.5;
      if (on) {
        return {
          ...base,
          color: preset.boxTextColor,
          backgroundColor: preset.boxColor,
          padding: "0 0.14em",
          borderRadius: 14,
          WebkitTextStroke: "0",
          transform: `scale(${scale})`,
        };
      }
      return { ...base, color: preset.baseColor };
    }
    case "opacity":
      return {
        ...base,
        color: preset.baseColor,
        opacity: interpolate(
          colorProg,
          [0, 1],
          [preset.inactiveOpacity ?? 0.5, 1],
        ),
        transform: `scale(${scale})`,
      };
    case "none":
      return { ...base, color: preset.baseColor };
    case "color":
    default:
      return {
        ...base,
        color: interpolateColors(
          colorProg,
          [0, 1],
          [preset.baseColor, preset.activeColor],
        ),
        transform: `scale(${scale})`,
      };
  }
}

export const Captions: React.FC<{ src: string; preset: PresetName }> = ({
  src,
  preset: presetName,
}) => {
  const preset = PRESETS[presetName];
  const [captions, setCaptions] = useState<Caption[] | null>(null);
  const { delayRender, continueRender, cancelRender } = useDelayRender();
  const [handle] = useState(() => delayRender());

  const fetchCaptions = useCallback(async () => {
    try {
      const response = await fetch(staticFile(src));
      const data = (await response.json()) as Caption[];
      setCaptions(data);
      continueRender(handle);
    } catch (e) {
      cancelRender(e);
    }
  }, [src, continueRender, cancelRender, handle]);

  useEffect(() => {
    fetchCaptions();
  }, [fetchCaptions]);

  const { pages } = useMemo(() => {
    if (!captions) return { pages: [] as TikTokPage[] };
    return createTikTokStyleCaptions({
      captions,
      combineTokensWithinMilliseconds: preset.combineMs,
    });
  }, [captions, preset.combineMs]);

  const { fps } = useVideoConfig();

  if (!captions) {
    return null;
  }

  return (
    <AbsoluteFill>
      {pages.map((page, index) => {
        const nextPage = pages[index + 1] ?? null;
        const startFrame = (page.startMs / 1000) * fps;
        const endFrame = Math.min(
          nextPage ? (nextPage.startMs / 1000) * fps : Infinity,
          startFrame + (preset.combineMs / 1000) * fps,
        );
        const durationInFrames = endFrame - startFrame;
        if (durationInFrames <= 0) return null;

        return (
          <Sequence
            key={index}
            from={Math.round(startFrame)}
            durationInFrames={Math.round(durationInFrames)}
          >
            <CaptionPage page={page} preset={preset} />
          </Sequence>
        );
      })}
    </AbsoluteFill>
  );
};

const CaptionPage: React.FC<{ page: TikTokPage; preset: Preset }> = ({
  page,
  preset,
}) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  // entrada da página: fade-in + slide de baixo pra cima
  const enterFade = preset.enter?.fadeFrames ?? 0;
  const enterSlide = preset.enter?.slideY ?? 0;
  const enterOpacity = enterFade
    ? interpolate(frame, [0, enterFade], [0, 1], {
        extrapolateLeft: "clamp",
        extrapolateRight: "clamp",
      })
    : 1;
  const enterTranslateY = enterSlide
    ? interpolate(frame, [0, enterFade || 8], [enterSlide, 0], {
        extrapolateLeft: "clamp",
        extrapolateRight: "clamp",
        easing: Easing.out(Easing.cubic),
      })
    : 0;

  return (
    <AbsoluteFill
      style={{
        justifyContent: "flex-end",
        alignItems: "center",
        paddingBottom: preset.bottomOffset,
        paddingLeft: preset.paddingX,
        paddingRight: preset.paddingX,
      }}
    >
      <div
        style={{
          fontFamily: preset.fontFamily,
          fontSize: preset.fontSize,
          fontWeight: preset.fontWeight,
          textAlign: "center",
          lineHeight: preset.lineHeight,
          letterSpacing: preset.letterSpacing,
          // largura limitada + quebra normal: impede o texto de vazar a margem
          // (o espaço entre palavras fica FORA do inline-block, virando ponto de
          // quebra; a palavra fica dentro para o scale do destaque funcionar).
          width: "100%",
          textTransform: preset.uppercase ? "uppercase" : "none",
          WebkitTextStroke: preset.stroke ?? undefined,
          paintOrder: "stroke fill",
          textShadow: preset.textShadow ?? undefined,
          opacity: enterOpacity,
          transform: `translateY(${enterTranslateY}px)`,
        }}
      >
        {page.tokens.map((token, i) => {
          const { scaleProg, colorProg } = computeTokenAnim(
            preset,
            token,
            page.startMs,
            frame,
            fps,
          );
          return (
            <Fragment key={token.fromMs}>
              {i > 0 ? " " : ""}
              <span style={tokenStyle(preset, scaleProg, colorProg)}>
                {token.text.trim()}
              </span>
            </Fragment>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};
