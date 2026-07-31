import React from "react";
import { Composition, staticFile } from "remotion";
import { Titulo, TituloProps } from "./Titulo";

// props vêm de public/props.json (paramétrico: texto por gancho + timing)
const calcMeta = async ({ props }: { props: TituloProps }) => {
  const data = (await fetch(staticFile("props.json")).then((r) =>
    r.json(),
  )) as Partial<TituloProps>;
  const merged: TituloProps = {
    texto: data.texto ?? "TÍTULO",
    emoji: data.emoji ?? "✨",
    duracaoSeg: data.duracaoSeg ?? 3,
    topOffset: data.topOffset ?? 150,
    fontSize: data.fontSize ?? 64,
  };
  return {
    durationInFrames: Math.ceil(merged.duracaoSeg * 30),
    props: merged,
    width: 1080,
    height: 1920,
  };
};

export const RemotionRoot: React.FC = () => {
  return (
    <Composition
      id="Titulo"
      component={Titulo}
      durationInFrames={90}
      fps={30}
      width={1080}
      height={1920}
      defaultProps={{
        texto: "TÍTULO",
        emoji: "✨",
        duracaoSeg: 3,
        topOffset: 150,
        fontSize: 64,
      }}
      calculateMetadata={calcMeta}
    />
  );
};
