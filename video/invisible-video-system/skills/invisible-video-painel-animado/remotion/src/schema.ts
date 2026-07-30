import { z } from "zod";

// Um painel do tipo "fluxo de nós": N nós encadeados por setas + selos.
export const fluxoDeNosSchema = z.object({
  titulo: z.string(),
  subtitulo: z.string().optional(),
  nos: z
    .array(z.object({ label: z.string(), icone: z.string() }))
    .min(2)
    .max(4),
  selos: z
    .array(z.object({ titulo: z.string(), sub: z.string(), icone: z.string() }))
    .max(4)
    .default([]),
  fecho: z.object({ forte: z.string(), leve: z.string() }).optional(),
  // caminho do PNG do personagem recortado (relativo ao public/), opcional
  personagem: z.string().optional(),
});

// "Erro vs certo": card dividido, um lado o erro (riscado), outro a consequência.
export const erroCertoSchema = z.object({
  titulo: z.string(),
  subtitulo: z.string().optional(),
  esquerda: z.object({ rotulo: z.string(), icone: z.string() }),
  direita: z.object({ rotulo: z.string(), icone: z.string() }),
  personagem: z.string().optional(),
});

// "Conceito nomeado": um diagnóstico com nome grande + explicação.
export const conceitoNomeadoSchema = z.object({
  titulo: z.string(),
  subtitulo: z.string().optional(),
  explicacao: z.string(),
  icone: z.string().default("mudo"),
  personagem: z.string().optional(),
});
