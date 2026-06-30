import "./index.css";
import { Composition, staticFile } from "remotion";
import { parseMedia } from "@remotion/media-parser";
import { MyComposition, type LegendaProps } from "./Composition";
import type { PresetName } from "./Captions";

const FPS = 30;

// Descobre duração e dimensão do próprio vídeo — a composição se adapta a
// qualquer combinação (cada uma tem duração diferente).
const calcMeta = async ({ props }: { props: LegendaProps }) => {
  const { slowDurationInSeconds, dimensions } = await parseMedia({
    src: staticFile(props.videoSrc),
    fields: { slowDurationInSeconds: true, dimensions: true },
    acknowledgeRemotionLicense: true,
  });
  return {
    durationInFrames: Math.round(slowDurationInSeconds * FPS),
    width: dimensions?.width ?? 1080,
    height: dimensions?.height ?? 1920,
    fps: FPS,
    props,
  };
};

// Uma composição por preset. O id é o nome do preset — aplicar.py renderiza
// `npx remotion render <preset>`.
const PRESETS: PresetName[] = [
  "reels",
  "hormozi",
  "minimal",
  "classic",
  "capsula",
  "capsula-palavra",
];

export const RemotionRoot: React.FC = () => {
  return (
    <>
      {PRESETS.map((preset) => (
        <Composition
          key={preset}
          id={preset}
          component={MyComposition}
          fps={FPS}
          durationInFrames={300}
          width={1080}
          height={1920}
          defaultProps={
            {
              videoSrc: "video.mp4",
              captionsSrc: "captions.json",
              preset,
            } satisfies LegendaProps
          }
          calculateMetadata={calcMeta}
        />
      ))}
    </>
  );
};
