# Atividade 01 - RBAC

Implementação simples de **Role-Based Access Control** em Python (sem bibliotecas externas).

## Cenário
Sistema acadêmico de uma universidade, com 4 papéis:

| Papel | Permissões |
|---|---|
| aluno | ver:notas, ver:material, fazer:matricula |
| professor | ver:notas, ver:material, lancar:notas, postar:material |
| coordenador | ver:notas, ver:material, alterar:notas, aprovar:matricula, ver:relatorios |
| administrador | criar:usuario, remover:usuario, ver:logs |

## Como executar
```bash
python3 rbac.py
```

## O que a demonstração mostra
1. Cada papel só consegue fazer o que foi definido para ele.
2. Um usuário pode ter mais de um papel (as permissões se somam).
3. Ao remover um papel, as permissões somem automaticamente, sem reconfigurar nada.
4. Usuário desconhecido não tem acesso a nada.

## Limitação
O RBAC puro não diz *qual* nota o aluno pode ver (só as dele). Esse tipo de regra
depende de atributos e é o que o ABAC resolve.
