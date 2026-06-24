import { AbsoluteFill, staticFile } from "remotion";
import { Video } from "@remotion/media";
import { Captions, type PresetName } from "./Captions";

export type LegendaProps = {
  videoSrc: string; // arquivo em public/
  captionsSrc: string; // arquivo em public/
  preset: PresetName;
  // override opcional da distância do rodapé (px na altura REAL do vídeo). Quando
  // ausente, usa o bottomOffset do preset escalado pela altura. Serve pra afinar a
  // posição num still sem editar o preset (--props), e pro ajuste por formato.
  bottomOffsetPx?: number;
};

export const MyComposition: React.FC<LegendaProps> = ({
  videoSrc,
  captionsSrc,
  preset,
  bottomOffsetPx,
}) => {
  return (
    <AbsoluteFill style={{ backgroundColor: "black" }}>
      <Video src={staticFile(videoSrc)} />
      <Captions src={captionsSrc} preset={preset} bottomOffsetPx={bottomOffsetPx} />
    </AbsoluteFill>
  );
};
