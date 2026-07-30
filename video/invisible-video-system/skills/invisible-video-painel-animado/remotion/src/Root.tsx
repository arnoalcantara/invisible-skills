import React from "react";
import { Composition, staticFile, cancelRender } from "remotion";
import { FluxoDeNos } from "./templates/FluxoDeNos";
import { ErroCerto } from "./templates/ErroCerto";
import { ConceitoNomeado } from "./templates/ConceitoNomeado";
import { fluxoDeNosSchema, erroCertoSchema, conceitoNomeadoSchema } from "./schema";

const FPS = 30;

// Lê props de public/props.json (a skill escreve esse arquivo antes de renderizar).
// A duração (em segundos) também vem de lá, campo "duracaoSeg" (default 5).
const carregarProps = async (arquivo: string) => {
  try {
    const res = await fetch(staticFile(arquivo));
    if (!res.ok) return {};
    return await res.json();
  } catch (e) {
    cancelRender(e);
    return {};
  }
};

const metaFrom = (arquivo: string) => async () => {
  const data = await carregarProps(arquivo);
  const seg = typeof data.duracaoSeg === "number" ? data.duracaoSeg : 5;
  return {
    durationInFrames: Math.round(seg * FPS),
    props: data,
    width: 1080,
    height: 1920,
    fps: FPS,
  };
};

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="FluxoDeNos"
        component={FluxoDeNos as any}
        schema={fluxoDeNosSchema}
        defaultProps={{ titulo: "TÍTULO", nos: [{ label: "A", icone: "som" }, { label: "B", icone: "livro" }], selos: [] } as any}
        durationInFrames={150}
        fps={FPS}
        width={1080}
        height={1920}
        calculateMetadata={metaFrom("props.json")}
      />
      <Composition
        id="ErroCerto"
        component={ErroCerto as any}
        schema={erroCertoSchema}
        defaultProps={{ titulo: "O ERRO", esquerda: { rotulo: "X", icone: "letra" }, direita: { rotulo: "Y", icone: "cerebro" } } as any}
        durationInFrames={150}
        fps={FPS}
        width={1080}
        height={1920}
        calculateMetadata={metaFrom("props.json")}
      />
      <Composition
        id="ConceitoNomeado"
        component={ConceitoNomeado as any}
        schema={conceitoNomeadoSchema}
        defaultProps={{ titulo: "CONCEITO", explicacao: "explicação", icone: "mudo" } as any}
        durationInFrames={150}
        fps={FPS}
        width={1080}
        height={1920}
        calculateMetadata={metaFrom("props.json")}
      />
    </>
  );
};
