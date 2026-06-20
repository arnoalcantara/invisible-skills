import { AbsoluteFill, staticFile } from "remotion";
import { Video } from "@remotion/media";
import { Captions, type PresetName } from "./Captions";

export type LegendaProps = {
  videoSrc: string; // arquivo em public/
  captionsSrc: string; // arquivo em public/
  preset: PresetName;
};

export const MyComposition: React.FC<LegendaProps> = ({
  videoSrc,
  captionsSrc,
  preset,
}) => {
  return (
    <AbsoluteFill style={{ backgroundColor: "black" }}>
      <Video src={staticFile(videoSrc)} />
      <Captions src={captionsSrc} preset={preset} />
    </AbsoluteFill>
  );
};
