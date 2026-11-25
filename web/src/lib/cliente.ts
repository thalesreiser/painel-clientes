import { z } from 'astro/zod';
import { CLIENTE } from 'astro:env/server';
import { clienteSchema, type Cliente } from './schema.ts';

const arquivos = import.meta.glob<unknown>('../../../clientes/*.json', {
  eager: true,
  import: 'default',
});

let carregado: Cliente | undefined;

/** Loads and validates clientes/<CLIENTE>.json; fails the build with a readable message. */
export function carregarCliente(): Cliente {
  if (carregado) return carregado;
  const dados = arquivos[`../../../clientes/${CLIENTE}.json`];
  if (dados === undefined) {
    throw new Error(`Cliente "${CLIENTE}" não encontrado em clientes/.`);
  }
  const resultado = clienteSchema.safeParse(dados);
  if (!resultado.success) {
    throw new Error(`clientes/${CLIENTE}.json inválido:\n${z.prettifyError(resultado.error)}`);
  }
  carregado = resultado.data;
  return carregado;
}
