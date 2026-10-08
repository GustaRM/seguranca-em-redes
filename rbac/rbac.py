"""
Atividade 01 - RBAC (Role-Based Access Control)
Disciplina: DCC075 - Segurança em Sistemas de Computação

Cenário: sistema acadêmico de uma universidade.
Papéis: aluno, professor, coordenador e administrador.

Ideia principal do RBAC:
    usuário --(tem)--> papel --(concede)--> permissões
O usuário NUNCA recebe permissão direto. Ele recebe um papel, e o
papel é quem carrega as permissões. Assim, se o João deixa de ser
coordenador, basta tirar o papel dele; não precisa mexer em permissão
nenhuma (esse é o exemplo do João/gerente que aparece nos slides).
"""


class RBAC:
    def __init__(self):
        # dicionário: nome do papel -> conjunto de permissões desse papel
        self.papeis = {}
        # dicionário: nome do usuário -> conjunto de papéis que ele tem
        self.usuarios = {}

    # ---------- administração (quem configura o sistema) ----------

    def criar_papel(self, papel, permissoes):
        """Cria um papel já com a lista de permissões dele."""
        self.papeis[papel] = set(permissoes)

    def criar_usuario(self, nome):
        """Cadastra um usuário sem nenhum papel ainda."""
        self.usuarios[nome] = set()

    def atribuir_papel(self, nome, papel):
        """Dá um papel para um usuário (só se os dois existirem)."""
        if nome not in self.usuarios:
            raise ValueError(f"Usuário '{nome}' não existe")
        if papel not in self.papeis:
            raise ValueError(f"Papel '{papel}' não existe")
        self.usuarios[nome].add(papel)

    def remover_papel(self, nome, papel):
        """Tira um papel do usuário. As permissões dele mudam sozinhas."""
        self.usuarios[nome].discard(papel)

    # ---------- verificação (a parte que decide o acesso) ----------

    def permissoes_do_usuario(self, nome):
        """Junta as permissões de TODOS os papéis que o usuário tem."""
        todas = set()
        for papel in self.usuarios.get(nome, set()):
            todas |= self.papeis[papel]  # união dos conjuntos
        return todas

    def pode(self, nome, permissao):
        """Retorna True se o usuário tem a permissão por algum papel."""
        return permissao in self.permissoes_do_usuario(nome)

    def tentar(self, nome, permissao):
        """Simula o usuário tentando fazer uma ação e mostra o resultado."""
        if self.pode(nome, permissao):
            print(f"  [PERMITIDO] {nome} -> {permissao}")
            return True
        print(f"  [NEGADO]    {nome} -> {permissao}")
        return False


# ======================================================================
# Demonstração
# ======================================================================
if __name__ == "__main__":
    sistema = RBAC()

    # 1) Definindo os papéis e o que cada um pode fazer.
    #    As permissões são no formato "acao:recurso".
    sistema.criar_papel("aluno", [
        "ver:notas",
        "ver:material",
        "fazer:matricula",
    ])
    sistema.criar_papel("professor", [
        "ver:notas",
        "ver:material",
        "lancar:notas",
        "postar:material",
    ])
    sistema.criar_papel("coordenador", [
        "ver:notas",
        "ver:material",
        "alterar:notas",      # corrigir nota já lançada
        "aprovar:matricula",
        "ver:relatorios",
    ])
    sistema.criar_papel("administrador", [
        "criar:usuario",
        "remover:usuario",
        "ver:logs",
    ])

    # 2) Cadastrando usuários e dando papéis a eles.
    for nome in ["Ana", "Bruno", "Carla", "Diego"]:
        sistema.criar_usuario(nome)

    sistema.atribuir_papel("Ana", "aluno")
    sistema.atribuir_papel("Bruno", "professor")
    sistema.atribuir_papel("Carla", "coordenador")
    sistema.atribuir_papel("Diego", "administrador")

    # 3) Testando acessos. O resultado depende só do papel.
    print("=== Teste 1: acessos básicos ===")
    sistema.tentar("Ana", "ver:notas")           # aluno pode
    sistema.tentar("Ana", "lancar:notas")        # aluno NÃO pode
    sistema.tentar("Bruno", "lancar:notas")      # professor pode
    sistema.tentar("Bruno", "alterar:notas")     # professor NÃO pode
    sistema.tentar("Carla", "alterar:notas")     # coordenador pode
    sistema.tentar("Carla", "criar:usuario")     # coordenador NÃO pode
    sistema.tentar("Diego", "criar:usuario")     # admin pode
    sistema.tentar("Diego", "ver:notas")         # admin NÃO pode (princípio do menor privilégio)

    # 4) Um usuário com mais de um papel (ex.: professor que também coordena).
    print("\n=== Teste 2: usuário com dois papéis ===")
    sistema.atribuir_papel("Bruno", "coordenador")
    sistema.tentar("Bruno", "lancar:notas")      # vem do papel professor
    sistema.tentar("Bruno", "aprovar:matricula") # vem do papel coordenador

    # 5) Mudança de papel: o ponto forte do RBAC.
    #    Só removemos o papel; não alteramos nenhuma permissão.
    print("\n=== Teste 3: Bruno deixa de ser coordenador ===")
    sistema.remover_papel("Bruno", "coordenador")
    sistema.tentar("Bruno", "aprovar:matricula") # agora negado
    sistema.tentar("Bruno", "lancar:notas")      # continua professor

    # 6) Usuário inexistente não tem nenhuma permissão.
    print("\n=== Teste 4: usuário desconhecido ===")
    sistema.tentar("Intruso", "ver:notas")

    # 7) Resumo final de cada usuário.
    print("\n=== Resumo ===")
    for nome, papeis in sistema.usuarios.items():
        print(f"  {nome}: papéis={sorted(papeis)}")
        print(f"     permissões={sorted(sistema.permissoes_do_usuario(nome))}")
