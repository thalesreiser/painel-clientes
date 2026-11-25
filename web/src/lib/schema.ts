import { z } from 'astro/zod';
import schemaJson from '../../../schemas/cliente.schema.json';

// Zod mirror of schemas/cliente.schema.json (RF-01). KPI and column lists come from the JSON
// Schema itself, so it stays the single source of truth; pipeline/config.py does the same.

export const TEMPLATES = ['financeiro', 'entregas'] as const;
export type Template = (typeof TEMPLATES)[number];

const defs = schemaJson.$defs;

export const KPIS: Record<Template, readonly string[]> = {
  financeiro: defs.kpis_financeiro.enum,
  entregas: defs.kpis_entregas.enum,
};

export const COLUNAS: Record<Template, readonly string[]> = {
  financeiro: defs.colunas_financeiro.propertyNames.enum,
  entregas: defs.colunas_entregas.propertyNames.enum,
};

export const COLUNAS_OBRIGATORIAS: Record<Template, readonly string[]> = {
  financeiro: defs.colunas_financeiro.required,
  entregas: defs.colunas_entregas.required,
};

const texto = z.string().min(1);

const fonte = z
  .object({
    tipo: z.enum(['csv', 'xlsx']),
    arquivos: z.array(texto).min(1),
    mapeamento_colunas: z.record(z.string(), texto),
    separador: z.string().length(1).optional(),
    aba: texto.optional(),
    encoding: texto.optional(),
  })
  .strict();

const marca = z
  .object({
    nome: texto,
    logo: texto.optional(),
    cor_primaria: z.string().regex(/^#[0-9a-fA-F]{6}$/, 'use uma cor hexadecimal, ex.: #1F6FEB'),
    preparado_por: texto.optional(),
  })
  .strict();

export const clienteSchema = z
  .object({
    $schema: z.string().optional(),
    id: z.string().regex(/^[a-z0-9]+(-[a-z0-9]+)*$/, 'use um slug, ex.: demo-bpo'),
    nome: texto,
    template: z.enum(TEMPLATES),
    fonte,
    kpis_ativos: z.array(z.string()).min(1),
    marca,
    fuso: texto.default('America/Sao_Paulo'),
  })
  .strict()
  .superRefine((c, ctx) => {
    const kpis = KPIS[c.template];
    c.kpis_ativos.forEach((k, i) => {
      if (!kpis.includes(k)) {
        ctx.addIssue({
          code: 'custom',
          path: ['kpis_ativos', i],
          message: `KPI "${k}" não existe no template ${c.template}`,
        });
      }
    });
    if (new Set(c.kpis_ativos).size !== c.kpis_ativos.length) {
      ctx.addIssue({ code: 'custom', path: ['kpis_ativos'], message: 'há KPIs repetidos' });
    }
    const mapa = Object.keys(c.fonte.mapeamento_colunas);
    for (const col of mapa.filter((m) => !COLUNAS[c.template].includes(m))) {
      ctx.addIssue({
        code: 'custom',
        path: ['fonte', 'mapeamento_colunas', col],
        message: `coluna "${col}" não existe no template ${c.template}`,
      });
    }
    for (const col of COLUNAS_OBRIGATORIAS[c.template].filter((m) => !mapa.includes(m))) {
      ctx.addIssue({
        code: 'custom',
        path: ['fonte', 'mapeamento_colunas', col],
        message: `coluna obrigatória "${col}" não mapeada`,
      });
    }
  });

export type Cliente = z.infer<typeof clienteSchema>;
