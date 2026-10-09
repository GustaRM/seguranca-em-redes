// ======================================================================
// index.js - Atividade 02: OAuth2 (Google) + RBAC
//
// Fluxo completo:
//   AUTENTICAÇÃO (quem é você?)  -> OAuth2 / OpenID com o Google
//   AUTORIZAÇÃO  (o que pode?)   -> RBAC, usando o e-mail recebido
//
// Passo a passo:
//   1. Usuário clica em "Login com Google"            (/login)
//   2. Redirecionamos para o Google, que autentica
//   3. Google volta com um "code"                     (/callback)
//   4. Trocamos o code por tokens e validamos o ID token
//   5. Pegamos o e-mail do token e descobrimos o PAPEL (RBAC)
//   6. Cada página consulta o papel antes de liberar o acesso
// ======================================================================

import express from 'express';
import crypto from 'node:crypto';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { OAuth2Client } from 'google-auth-library';
import dotenv from 'dotenv';
import { PAPEIS, RECURSOS, descobrirPapel, temPermissao } from './rbac.js';

dotenv.config(); // carrega as variáveis do arquivo .env

// Sem as credenciais não adianta subir o servidor.
for (const nome of ['GOOGLE_CLIENT_ID', 'GOOGLE_CLIENT_SECRET', 'GOOGLE_REDIRECT_URI']) {
  if (!process.env[nome]) {
    console.error(`Faltou configurar ${nome} no arquivo .env`);
    process.exit(1);
  }
}

const app = express();
const PORT = 3000;
const PASTA_PUBLIC = path.join(path.dirname(fileURLToPath(import.meta.url)), '..', 'public');

// Cliente OAuth2 do Google (mesmo do tutorial).
const client = new OAuth2Client(
  process.env.GOOGLE_CLIENT_ID,
  process.env.GOOGLE_CLIENT_SECRET,
  process.env.GOOGLE_REDIRECT_URI
);

// ----------------------------------------------------------------------
// Sessões em memória.
// O tutorial passava nome e e-mail pela URL (?name=...&email=...), mas
// isso é inseguro: qualquer um poderia digitar a URL com um e-mail de
// administrador e se passar por ele. Aqui o papel fica guardado NO
// SERVIDOR e o navegador só recebe um id aleatório num cookie.
// (Ao reiniciar o servidor as sessões se perdem, ok para a prática.)
// ----------------------------------------------------------------------
const sessoes = new Map(); // idSessao -> { nome, email, foto, papel }
const statesPendentes = new Set(); // proteção contra CSRF no login

// Lê o cookie "sid" do cabeçalho (evita instalar cookie-parser).
function lerSid(req) {
  const cookies = (req.headers.cookie || '').split(';');
  for (const c of cookies) {
    const [chave, ...resto] = c.trim().split('=');
    if (chave === 'sid') return resto.join('=');
  }
  return null;
}

// Escapa HTML para o nome/e-mail não conseguirem injetar código na página.
function esc(texto) {
  return String(texto ?? '').replace(/[&<>"']/g, (c) => ({
    '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;',
  }[c]));
}

// Moldura HTML simples compartilhada por todas as páginas.
function pagina(titulo, corpo) {
  return `<!DOCTYPE html>
<html lang="pt-BR"><head><meta charset="UTF-8" /><title>${esc(titulo)}</title>
<style>
  body{font-family:Arial,sans-serif;max-width:720px;margin:40px auto;padding:0 16px}
  table{border-collapse:collapse;width:100%} th,td{border:1px solid #ccc;padding:8px;text-align:left}
  .ok{color:#0a7d2c;font-weight:bold} .no{color:#b00020;font-weight:bold}
  .papel{background:#e8eaf6;padding:2px 10px;border-radius:10px}
  img{border-radius:50%;width:64px;height:64px}
</style></head><body>${corpo}</body></html>`;
}

// ----------------------------------------------------------------------
// Middlewares (funções que rodam ANTES da rota)
// ----------------------------------------------------------------------

// Exige que o usuário esteja autenticado (tenha sessão válida).
function exigirLogin(req, res, next) {
  const usuario = sessoes.get(lerSid(req));
  if (!usuario) return res.redirect('/'); // não logado: volta pro início
  req.usuario = usuario;
  next();
}

// Exige uma PERMISSÃO específica. É aqui que o RBAC age de verdade:
// olha o papel do usuário e decide se libera (next) ou nega (403).
function exigirPermissao(permissao) {
  return [
    exigirLogin, // primeiro autentica, depois autoriza
    (req, res, next) => {
      if (temPermissao(req.usuario.papel, permissao)) return next();
      console.log(`[NEGADO]    ${req.usuario.email} (${req.usuario.papel}) -> ${permissao}`);
      res.status(403).send(pagina('Acesso negado', `
        <h1 class="no">403 - Acesso negado</h1>
        <p>O papel <span class="papel">${esc(req.usuario.papel)}</span>
           não tem a permissão <code>${esc(permissao)}</code>.</p>
        <p><a href="/painel">Voltar ao painel</a></p>`));
    },
  ];
}

// ----------------------------------------------------------------------
// ETAPA 1 - AUTENTICAÇÃO com o Google
// ----------------------------------------------------------------------

// Serve o public/index.html na raiz ("/").
app.use(express.static(PASTA_PUBLIC));

// Gera a URL de login do Google e redireciona o usuário para lá.
app.get('/login', (req, res) => {
  const state = crypto.randomBytes(16).toString('hex'); // valor aleatório
  statesPendentes.add(state);

  const url = client.generateAuthUrl({
    access_type: 'offline',
    scope: ['email', 'profile', 'openid'],
    state, // o Google devolve igualzinho no callback
  });
  res.redirect(url);
});

// O Google redireciona para cá depois que o usuário autenticou.
app.get('/callback', async (req, res) => {
  try {
    const { code, state } = req.query;

    // O state tem que ser um dos que nós geramos; senão o pedido é suspeito.
    if (!state || !statesPendentes.delete(state)) {
      return res.status(400).send('State inválido.');
    }

    // Troca o "code" pelos tokens (access token, id token...).
    const { tokens } = await client.getToken(code);
    client.setCredentials(tokens);

    // Valida a assinatura do ID token e confere que ele é para o NOSSO app.
    const ticket = await client.verifyIdToken({
      idToken: tokens.id_token,
      audience: process.env.GOOGLE_CLIENT_ID,
    });
    const payload = ticket.getPayload(); // dados do usuário (email, name...)

    // ------------------------------------------------------------------
    // ETAPA 2 - AUTORIZAÇÃO (RBAC)
    // Usamos o ATRIBUTO "email" do payload para decidir o papel.
    // ------------------------------------------------------------------
    const papel = descobrirPapel(payload);
    console.log(`[LOGIN]     ${payload.email} -> papel "${papel}"`);

    // Cria a sessão e entrega só o id aleatório ao navegador.
    const sid = crypto.randomBytes(32).toString('hex');
    sessoes.set(sid, {
      nome: payload.name,
      email: payload.email,
      foto: payload.picture,
      papel,
    });
    res.setHeader('Set-Cookie', `sid=${sid}; HttpOnly; SameSite=Lax; Path=/`);
    res.redirect('/painel');
  } catch (error) {
    console.error('Erro na autenticação:', error);
    res.status(500).send('Erro ao autenticar com o Google.');
  }
});

// ----------------------------------------------------------------------
// Página autenticada: mostra o resultado do controle de acesso
// ----------------------------------------------------------------------
app.get('/painel', exigirLogin, (req, res) => {
  const u = req.usuario;

  // Uma linha da tabela para cada recurso: permitido ou negado.
  const linhas = RECURSOS.map((r) => {
    const permitido = temPermissao(u.papel, r.permissao);
    return `<tr>
      <td><a href="${r.rota}">${esc(r.titulo)}</a></td>
      <td><code>${esc(r.permissao)}</code></td>
      <td class="${permitido ? 'ok' : 'no'}">${permitido ? 'PERMITIDO' : 'NEGADO'}</td>
    </tr>`;
  }).join('');

  res.send(pagina('Painel', `
    ${u.foto ? `<img src="${esc(u.foto)}" referrerpolicy="no-referrer" alt="foto" />` : ''}
    <h1>Bem-vindo, ${esc(u.nome)}!</h1>
    <p>E-mail: ${esc(u.email)}</p>
    <p>Papel atribuído (RBAC): <span class="papel">${esc(u.papel)}</span></p>
    <h2>Resultado do controle de acesso</h2>
    <table>
      <tr><th>Recurso</th><th>Permissão exigida</th><th>Resultado</th></tr>
      ${linhas}
    </table>
    <p>Clique nos recursos para testar o acesso de verdade.</p>
    <p><a href="/logout">Sair</a></p>`));
});

// ----------------------------------------------------------------------
// Recursos protegidos: cada rota exige UMA permissão.
// ----------------------------------------------------------------------
function rotaProtegida(rota, permissao, titulo, mensagem) {
  app.get(rota, exigirPermissao(permissao), (req, res) => {
    console.log(`[PERMITIDO] ${req.usuario.email} (${req.usuario.papel}) -> ${permissao}`);
    res.send(pagina(titulo, `
      <h1 class="ok">${esc(titulo)}</h1>
      <p>${esc(mensagem)}</p>
      <p>Acesso liberado para o papel <span class="papel">${esc(req.usuario.papel)}</span>.</p>
      <p><a href="/painel">Voltar ao painel</a></p>`));
  });
}

rotaProtegida('/avisos', 'ver:avisos', 'Mural de avisos', 'Aviso: matrículas abertas até sexta.');
rotaProtegida('/notas', 'ver:notas', 'Consultar notas', 'Aqui apareceriam as notas da turma.');
rotaProtegida('/lancar-notas', 'lancar:notas', 'Lançar notas', 'Formulário de lançamento de notas.');
rotaProtegida('/relatorios', 'ver:relatorios', 'Relatórios', 'Relatórios gerenciais da instituição.');
rotaProtegida('/usuarios', 'gerenciar:usuarios', 'Gerenciar usuários', 'Criação e remoção de contas.');

// Encerra a sessão: apaga do servidor e expira o cookie.
app.get('/logout', (req, res) => {
  sessoes.delete(lerSid(req));
  res.setHeader('Set-Cookie', 'sid=; Max-Age=0; Path=/');
  res.redirect('/');
});

app.listen(PORT, () => {
  console.log(`Servidor rodando em http://localhost:${PORT}`);
  console.log('Papéis disponíveis:', Object.keys(PAPEIS).join(', '));
});
