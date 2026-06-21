import { AbsoluteFill, staticFile } from "remotion";
import { Video } from "@remotion/media";
import { Captions, type PresetName } from "./Captions";
import { HookText } from "./HookText";

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

// Gancho escrito — animação de texto (overlay sobre o vídeo, que segue como áudio).
// O <Video> toca do começo ao fim (áudio original contínuo); o HookText cobre a
// imagem com fundo preto + tipografia até o boundary; do boundary em diante,
// aparece a imagem do desenvolvimento.
//
// Dois modos, mesmo código (interruptor `videoJaLegendado`):
//  - false (default): vídeo base = combinação CRUA; a legenda reels do
//    desenvolvimento é desenhada aqui (<Captions> a partir do captions.json).
//  - true: vídeo base = `_LEGENDADO.mp4` (desenvolvimento já tem a legenda
//    queimada e aprovada) — NÃO re-legenda; dispensa o captions.json.
export type GanchoEscritoProps = {
  videoSrc: string; // public/video.mp4
  captionsSrc: string; // public/captions.json (só usado se !videoJaLegendado)
  hookSrc: string; // public/hook.json (frases do gancho)
  videoJaLegendado?: boolean;
};

export const GanchoEscritoComposition: React.FC<GanchoEscritoProps> = ({
  videoSrc,
  captionsSrc,
  hookSrc,
  videoJaLegendado = false,
}) => {
  return (
    <AbsoluteFill style={{ backgroundColor: "black" }}>
      <Video src={staticFile(videoSrc)} />
      {!videoJaLegendado && <Captions src={captionsSrc} preset="reels" />}
      <HookText src={hookSrc} videoJaLegendado={videoJaLegendado} />
    </AbsoluteFill>
  );
};
