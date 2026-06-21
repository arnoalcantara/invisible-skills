import { useCallback, useEffect, useState } from "react";
import {
  AbsoluteFill,
  Easing,
  Sequence,
  interpolate,
  staticFile,
  useCurrentFrame,
  useDelayRender,
  useVideoConfig,
} from "remotion";

// ----------------------------------------------------------------------------
// HOOK ESCRITO — animação de tipografia do gancho sobre fundo preto.
// As palavras surgem sincronizadas com a fala (timestamps WhisperX) e se
// organizam por frase: cada frase aparece, segura, e dá lugar à próxima.
// No boundary (fim do gancho) o overlay some e revela o vídeo do desenvolvimento.
// ----------------------------------------------------------------------------

type HookWord = { text: string; startMs: number; endMs: number; emphasis: boolean };
type Sentence = { startMs: number; endMs: number; words: HookWord[] };
type HookData = { boundaryMs: number; sentences: Sentence[] };

// tipografia (fonte serifada nativa do macOS — sem download)
const FONT_FAMILY = '"Hoefler Text", "Didot", Georgia, "Times New Roman", serif';
const SIZE_BASE = 96;
const SIZE_EMPH = 132;
const COLOR = "#F7F3EC"; // branco levemente quente, editorial
const WORD_ENTER_FRAMES = 7; // duração da entrada de cada palavra
const FADE_OUT_FRAMES = 8; // fade do overlay ao virar pro desenvolvimento

export const HookText: React.FC<{ src: string; videoJaLegendado?: boolean }> = ({
  src,
  videoJaLegendado = false,
}) => {
  const [hook, setHook] = useState<HookData | null>(null);
  const { delayRender, continueRender, cancelRender } = useDelayRender();
  const [handle] = useState(() => delayRender());
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const fetchHook = useCallback(async () => {
    try {
      const r = await fetch(staticFile(src));
      setHook((await r.json()) as HookData);
      continueRender(handle);
    } catch (e) {
      cancelRender(e);
    }
  }, [src, continueRender, cancelRender, handle]);

  useEffect(() => {
    fetchHook();
  }, [fetchHook]);

  if (!hook) return null;

  const boundaryFrame = (hook.boundaryMs / 1000) * fps;
  if (frame >= boundaryFrame) return null; // some no boundary -> revela o vídeo

  // fade-out curto do overlay nos últimos frames do gancho (corte suave).
  // No modo "vídeo já legendado", o fade revelaria a legenda do gancho
  // queimada por baixo (flash) — então corta seco (sem fade).
  const fadeFrames = videoJaLegendado ? 0 : FADE_OUT_FRAMES;
  const overlayOpacity = fadeFrames
    ? interpolate(frame, [boundaryFrame - fadeFrames, boundaryFrame], [1, 0], {
        extrapolateLeft: "clamp",
        extrapolateRight: "clamp",
      })
    : 1;

  return (
    <AbsoluteFill style={{ backgroundColor: "#000", opacity: overlayOpacity }}>
      {hook.sentences.map((s, i) => {
        const startFrame = (s.words[0].startMs / 1000) * fps;
        const next = hook.sentences[i + 1] ?? null;
        const endFrame = next ? (next.words[0].startMs / 1000) * fps : boundaryFrame;
        const dur = endFrame - startFrame;
        if (dur <= 0) return null;
        return (
          <Sequence
            key={i}
            from={Math.round(startFrame)}
            durationInFrames={Math.round(dur)}
          >
            <SentenceView sentence={s} />
          </Sequence>
        );
      })}
    </AbsoluteFill>
  );
};

const SentenceView: React.FC<{ sentence: Sentence }> = ({ sentence }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const baseMs = sentence.words[0].startMs;

  return (
    <AbsoluteFill
      style={{
        justifyContent: "center",
        alignItems: "center",
        padding: "0 110px",
      }}
    >
      <div
        style={{
          fontFamily: FONT_FAMILY,
          fontSize: SIZE_BASE, // base para os gaps em "em" (spans sobrescrevem o seu)
          textAlign: "center",
          lineHeight: 1.18,
          color: COLOR,
          display: "flex",
          flexWrap: "wrap",
          justifyContent: "center",
          alignItems: "baseline",
          columnGap: "0.30em",
          rowGap: "0.05em",
          maxWidth: "100%",
        }}
      >
        {sentence.words.map((w, i) => {
          const appearFrame = ((w.startMs - baseMs) / 1000) * fps;
          const local = frame - appearFrame;
          const opacity = interpolate(local, [0, WORD_ENTER_FRAMES], [0, 1], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
          });
          const translateY = interpolate(local, [0, WORD_ENTER_FRAMES], [16, 0], {
            extrapolateLeft: "clamp",
            extrapolateRight: "clamp",
            easing: Easing.out(Easing.cubic),
          });
          return (
            <span
              key={i}
              style={{
                display: "inline-block",
                fontSize: w.emphasis ? SIZE_EMPH : SIZE_BASE,
                fontWeight: w.emphasis ? 700 : 500,
                fontStyle: w.emphasis ? "italic" : "normal",
                opacity,
                transform: `translateY(${translateY}px)`,
              }}
            >
              {w.text.trim()}
            </span>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};
