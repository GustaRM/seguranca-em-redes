# Atividade 02 - OAuth2 (Google) + RBAC

Junta **autenticação** (OAuth2 do Google) com **autorização** (RBAC da Atividade 01).

- **Autenticação**: o Google confirma quem é o usuário.
- **Autorização**: o e-mail recebido do Google define o **papel**, e o papel define o que ele pode acessar.

## Papéis e permissões
| Papel | Permissões |
|---|---|
| administrador | ver:avisos, ver:relatorios, gerenciar:usuarios |
| professor | ver:avisos, ver:notas, lancar:notas |
| aluno | ver:avisos, ver:notas |
| visitante | ver:avisos |

## Como o papel é escolhido (atributo: e-mail)
1. E-mail não verificado pelo Google -> `visitante`
2. E-mail em `ADMIN_EMAILS` / `PROFESSOR_EMAILS` / `ALUNO_EMAILS` (.env) -> papel da lista
3. Domínio com regra em `src/rbac.js` (ex.: `estudante.ufjf.br` -> aluno)
4. Caso contrário -> `visitante`

## Estrutura
```
02-oauth2-rbac/
├── public/index.html   página inicial com o link de login
├── src/index.js        servidor Express (OAuth2 + sessão + rotas protegidas)
├── src/rbac.js         papéis, permissões e regras de decisão
├── .env.example        modelo das variáveis (copie para .env)
└── package.json
```

## Configuração
1. No Google Cloud Console: **APIs e serviços > Credenciais > ID do cliente OAuth > Aplicativo da Web**.
   - Origem JavaScript autorizada: `http://localhost:3000`
   - URI de redirecionamento: `http://localhost:3000/callback`
2. Em **Tela de consentimento OAuth**, adicione seu e-mail (e o de quem for testar) como **usuário de teste**.
3. `cp .env.example .env` e preencha ID, segredo e os e-mails de cada papel.

## Como executar
```bash
bun install        # ou: npm install
bun src/index.js   # ou: node src/index.js
```
Abra `http://localhost:3000`, clique em login e entre com a conta Google.

## O que a página autenticada mostra
Nome, e-mail, **papel atribuído** e uma tabela PERMITIDO/NEGADO para cada recurso. Ao clicar num recurso sem permissão, aparece **403 - Acesso negado**.

## Mudanças em relação ao tutorial
- Nome e e-mail **não vão mais pela URL** (qualquer pessoa poderia forjar `?email=...`); ficam numa sessão no servidor.
- Uso do parâmetro `state` para proteger o login contra CSRF.
- Nome e e-mail são escapados antes de ir para o HTML.

## Capturas de tela para a entrega
Entre com contas de papéis diferentes e capture o painel de cada uma (use janela anônima ou saia pelo `/logout`), mais uma tela de 403.
