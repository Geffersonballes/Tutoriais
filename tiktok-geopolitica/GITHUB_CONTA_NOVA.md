# GitHub na conta nova — passo a passo

O sistema já está pronto no repositório **Geffersonballes/Tutoriais**, branch **claude/nifty-noether-jtt32a**.
Esse repositório é **privado**, e a conta nova do GitHub não tem acesso a ele. Escolha UM dos caminhos da Parte A.

---

## PARTE A — o que VOCÊ faz (5 a 10 minutos)

### 1. Criar o repositório na conta nova
1. Entre no GitHub com a conta nova → botão **New repository**.
2. Nome sugerido: `videos-automaticos` (ou o nome da série). Pode ser **Private**.
3. Marque **Add a README file** (o repositório não pode nascer vazio) → **Create repository**.

### 2. Dar acesso ao código pronto — escolha A1 ou A2
- **A1 (mais simples): convidar a conta nova para o repositório atual.**
  Na conta atual (Geffersonballes): `Tutoriais` → **Settings** → **Collaborators** → **Add people** → digite
  o usuário da conta nova → permissão de leitura basta. Na conta nova, aceite o convite (chega por e-mail ou em
  github.com/notifications).
- **A2 (sem convite): subir o pacote.** Baixe o arquivo **`pacote_peca_por_peca.zip`** que te mandei
  (≈ 12 MB: agentes, skill, motor, fontes, céus e documentação). No repositório novo: **Add file** →
  **Upload files** → arraste o .zip → **Commit changes**. A outra conversa descompacta.

### 3. Ligar o GitHub novo ao Claude
1. Na **conta do Claude que vai usar o GitHub novo**, conecte o GitHub: claude.ai → **Configurações** →
   **Conectores** → **GitHub** → entre com a conta nova do GitHub.
2. Instale o app do Claude no repositório novo: **github.com/apps/claude** → **Configure/Install** →
   escolha a conta nova → **Only select repositories** → marque o repositório novo (e, no caminho A1,
   também `Geffersonballes/Tutoriais`, se aparecer) → **Save**.
3. Abra uma sessão nova do Claude Code na nuvem **com o repositório novo selecionado** e cole o
   `PROMPT_OUTRA_CONTA.md` (com a ficha preenchida) junto com a PARTE B abaixo.

---

## PARTE B — cole isto na outra conversa, logo depois do prompt principal

```
INSTRUÇÕES DE GITHUB (conta nova)
- O repositório desta sessão é o meu repositório NOVO. Tudo o que você criar fica nele.
- Para trazer o sistema pronto, tente nesta ordem:
  1) add_repo owner "Geffersonballes", repo "Tutoriais" (fui convidado como colaborador). Se der certo,
     copie da branch "claude/nifty-noether-jtt32a" as pastas ".claude/agents/", ".claude/skills/" e
     "tiktok-geopolitica/" para o MEU repositório (sem a pasta "producao/*/frames" e sem arquivos .mp4).
  2) Se não tiver acesso, procure "pacote_peca_por_peca.zip" na raiz do meu repositório e descompacte
     (unzip -o pacote_peca_por_peca.zip), depois apague o .zip do repositório.
  3) Se nenhum dos dois existir, reconstrua tudo pela PARTE 3 do prompt principal.
- Confira que existem: .claude/skills/tiktok-peca-por-peca/SKILL.md, .claude/agents/*.md (18),
  tiktok-geopolitica/motor/{lowpoly.py,cena_defesa.py,compor.py,alinhar.py,palavras.py,ilustrado.py,instalar.sh},
  tiktok-geopolitica/assets/{fonts,hdri}.
- Ajuste para o meu projeto: troque em config.md, SKILL.md e nos agentes tudo o que for da FICHA
  (nicho, redes, perfis, horários, voz, CTA). Remova referências a contas, e-mails ou IDs do projeto antigo
  (blogId 8049742, perfis e canais antigos) e use só os que o Metricool desta conta mostrar.
- .gitignore obrigatório na pasta do projeto:
    producao/*/frames/
    producao/*/preview*/
    producao/*/*.mp4
    producao/*/*.wav
    producao/*/render_*.log
    __pycache__/
  (vídeos e quadros NÃO vão para o git: o GitHub recusa arquivos acima de 100 MB.)
- Trabalhe numa branch própria, faça commit e push ao fim de cada etapa. Quando a primeira versão estiver
  pronta e aprovada por mim, abra um Pull Request para a branch principal e me peça para juntar:
  as tarefas agendadas e as sessões novas partem da branch principal, então a skill precisa estar lá.
- Script de configuração do ambiente: depois de rodar instalar.sh com sucesso, proponha salvar no ambiente
  a linha  if [ -f <nome-do-repo>/tiktok-geopolitica/motor/instalar.sh ]; then bash <nome-do-repo>/tiktok-geopolitica/motor/instalar.sh || true; fi
  (troque <nome-do-repo> pelo nome da pasta do meu repositório) para toda sessão já começar com o Blender.
- Nunca faça force-push nem apague branches sem me perguntar.
```

---

## Conferência rápida (depois que a outra conversa terminar)
- [ ] O repositório novo tem `.claude/skills/tiktok-peca-por-peca/SKILL.md` e `.claude/agents/`.
- [ ] Existe um Pull Request para a branch principal, e você juntou (Merge).
- [ ] O `config.md` mostra as SUAS redes, perfis e horários, não os do projeto antigo.
- [ ] O primeiro vídeo chegou para você aprovar antes de qualquer agendamento.
