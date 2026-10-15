// ======================================================================
// rbac.js - parte de AUTORIZAÇÃO (RBAC) da atividade 02
//
// Aqui fica só a lógica de papéis e permissões, separada do servidor.
// Assim dá para testar sem precisar do Google e reaproveitar a ideia
// da Atividade 01: usuário -> papel -> permissões.
// ======================================================================

// Cada papel guarda a lista de permissões dele ("acao:recurso").
// O usuário nunca recebe permissão direto, só um papel.
export const PAPEIS = {
  administrador: ['ver:avisos', 'ver:relatorios', 'gerenciar:usuarios'],
  professor: ['ver:avisos', 'ver:notas', 'lancar:notas'],
  aluno: ['ver:avisos', 'ver:notas'],
  visitante: ['ver:avisos'], // papel padrão de quem não se encaixa em nada
};

// Catálogo dos recursos do sistema. Serve para a página mostrar o que
// foi permitido e o que foi negado para o papel do usuário.
export const RECURSOS = [
  { permissao: 'ver:avisos', rota: '/avisos', titulo: 'Mural de avisos' },
  { permissao: 'ver:notas', rota: '/notas', titulo: 'Consultar notas' },
  { permissao: 'lancar:notas', rota: '/lancar-notas', titulo: 'Lançar notas' },
  { permissao: 'ver:relatorios', rota: '/relatorios', titulo: 'Relatórios' },
  { permissao: 'gerenciar:usuarios', rota: '/usuarios', titulo: 'Gerenciar usuários' },
];

// Transforma "a@x.com, b@y.com" em ['a@x.com', 'b@y.com'] (minúsculo).
// Usado para ler as listas de e-mails que ficam no arquivo .env.
function lerLista(texto) {
  return (texto || '')
    .split(',')
    .map((e) => e.trim().toLowerCase())
    .filter((e) => e.length > 0);
}

// Regras por domínio do e-mail. Ajuste conforme o seu cenário.
// (Exemplo: e-mail institucional de servidor = professor.)
const PAPEL_POR_DOMINIO = {
  'estudante.ufjf.br': 'aluno',
  'ufjf.br': 'professor',
  'ice.ufjf.br': 'professor',
};

// ----------------------------------------------------------------------
// Descobre o papel do usuário a partir do ATRIBUTO recebido na
// autenticação do Google (o e-mail que vem no ID token).
//
// Ordem de decisão:
//   1) e-mail não verificado pelo Google -> visitante (não confiamos)
//   2) e-mail está numa lista explícita do .env -> papel da lista
//   3) domínio do e-mail tem regra -> papel do domínio
//   4) nenhum dos casos -> visitante
//
// "env" é passado como parâmetro para facilitar os testes.
// ----------------------------------------------------------------------
export function descobrirPapel(payload, env = process.env) {
  // Só confiamos no e-mail se o Google garantiu que ele foi verificado.
  if (!payload.email || payload.email_verified !== true) {
    return 'visitante';
  }

  const email = payload.email.toLowerCase();

  // 2) listas explícitas (têm prioridade sobre o domínio)
  if (lerLista(env.ADMIN_EMAILS).includes(email)) return 'administrador';
  if (lerLista(env.PROFESSOR_EMAILS).includes(email)) return 'professor';
  if (lerLista(env.ALUNO_EMAILS).includes(email)) return 'aluno';

  // 3) regra por domínio: pega o que vem depois do último "@"
  const dominio = email.slice(email.lastIndexOf('@') + 1);
  if (PAPEL_POR_DOMINIO[dominio]) return PAPEL_POR_DOMINIO[dominio];

  // 4) padrão
  return 'visitante';
}

// Pergunta central do RBAC: este papel tem esta permissão?
export function temPermissao(papel, permissao) {
  const permissoes = PAPEIS[papel] || []; // papel desconhecido = sem nada
  return permissoes.includes(permissao);
}
