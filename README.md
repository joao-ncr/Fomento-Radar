# FomentoRadar

> Descubra em minutos se vale a pena submeter a um edital de fomento e o que falta para ser elegível.

**Status:** 🚧 Fase inicial de construção do MVP e validação com fundadores.

---

## O problema

Startups de base tecnológica e pequenas empresas inovadoras têm acesso a um volume crescente de recursos de fomento (Fapemig, Finep, Sebrae e outros). Na prática, porém, esse acesso esbarra em dificuldades recorrentes:

- **Editais longos e densos**, com requisitos espalhados entre o texto principal, anexos, notas de rodapé e retificações.
- **Descoberta tardia:** a oportunidade é percebida quando o prazo já está curto, ou nem chega a ser percebida.
- **Esforço desperdiçado:** equipes gastam dias preparando uma proposta para só então descobrir uma inelegibilidade (porte, tempo de constituição, localização, enquadramento, documentação).
- **Dependência de consultores** para uma triagem que deveria ser rápida e barata.
- **Mudanças silenciosas:** prorrogações, suspensões e retificações alteram regras e prazos e nem sempre chegam a quem precisa.

## A proposta

O **FomentoRadar** é um **radar de oportunidades com verificador de elegibilidade**. Ele monitora chamadas de fomento, compara o perfil da empresa com os requisitos de cada edital e entrega, **antes da submissão**, um diagnóstico claro:

| Entrega | O que o usuário recebe |
|---|---|
| **Chamadas compatíveis** | Oportunidades relevantes para o perfil da empresa, com prazos |
| **Mapa de requisitos** | Cada requisito classificado como *atendido*, *não atendido* ou *desconhecido* |
| **Evidência do edital** | Citação do trecho e da página de onde cada requisito foi extraído |
| **Lacunas e riscos** | O que falta para ser elegível e o que merece atenção |
| **Checklist de submissão** | Documentos e etapas, com prazos |
| **Alertas** | Avisos de abertura, prorrogação, suspensão ou retificação |

### O que o FomentoRadar **não** é

Ser transparente sobre os limites é parte da proposta de valor:

- Não promete nem estima aprovação.
- Não escreve a proposta completa.
- Não substitui consultor, assessoria jurídica ou parecer humano.
- Não infere elegibilidade legal: o resultado é um apoio à decisão, sempre com recomendação de conferência no edital oficial.

## Princípio de confiança

> **Nenhum requisito é tratado como confirmado sem citação verificável do edital oficial.**

Quando não há evidência suficiente, o resultado é **"desconhecido"**, e nunca um "sim" ou "não" presumido. Para uma ferramenta que orienta decisões de investimento de tempo e dinheiro, errar dizendo que a empresa é elegível é o erro mais grave. Por isso toda conclusão do sistema é rastreável até o documento de origem, e as primeiras chamadas passam por revisão humana.

## Para quem

**Usuários:** fundadores, CEOs e responsáveis por P&D de startups de base tecnológica e pequenas empresas inovadoras.

**Segmento inicial:** hardware e deeptech do polo de Itajubá (MG), em articulação com o ecossistema local (CEU/UNIFEI, INCIT, Inatel).

**Parceiros naturais:** incubadoras, aceleradoras, parques tecnológicos e núcleos de inovação que apoiam empresas na captação de recursos.

## Fase atual: construção do MVP

O objetivo desta fase é **provar valor com o menor escopo possível**, antes de ampliar cobertura.

### Escopo do MVP

- **2 chamadas de referência:** uma da Fapemig (candidata: Centelha MG, edital 010/2026) e uma da Finep ou do Sebrae.
- **15 a 20 requisitos por chamada**, estruturados e revisados manualmente.
- **Entrada:** perfil da empresa (porte, data de constituição, CNAE, cidade/UF, equipe, área tecnológica, estágio, orçamento aproximado e um parágrafo descrevendo o projeto).
- **Saída:** diagnóstico de elegibilidade com mapa de requisitos, lacunas, checklist de submissão e alertas de prazo.

### Fora do escopo do MVP

- Cobertura de todas as agências e fontes de fomento.
- Estimativa de taxa de êxito.
- Geração completa de propostas.

### Validação antes de escala

O produto só avança se resolver uma dor real. Estamos conduzindo **conversas de diagnóstico com fundadores** para confirmar que o problema é frequente e relevante.

**Critério de parada:** se menos de 3 das 5 primeiras conversas confirmarem dor real e recorrente, o desenvolvimento é interrompido para reavaliação. Não criaremos funcionalidades para compensar falta de validação.

## Objetivos de negócio

1. **Reduzir o custo de triagem de editais** para empresas pequenas, de dias para minutos.
2. **Evitar propostas inelegíveis**, direcionando o esforço para chamadas em que a empresa tem chance real de participar.
3. **Aumentar a visibilidade de oportunidades** e prazos, reduzindo a perda por descoberta tardia.
4. **Construir uma base confiável e auditável de requisitos de editais**, ativo central do produto, com evidência, página e versão do documento.
5. **Estabelecer confiança com o ecossistema** (empresas, incubadoras, instituições de apoio) por meio de transparência sobre limites e rastreabilidade.

### Perguntas que o MVP precisa responder

- A dor de triar editais é recorrente e forte o bastante para justificar um produto?
- O diagnóstico gerado é correto e útil, comparado à leitura manual de um especialista?
- Os fundadores confiam o suficiente para agir com base no resultado?
- O esforço para estruturar e manter requisitos por chamada é sustentável?
- Existe disposição de pagar, e por quem (empresa, incubadora, aceleradora)?

*Modelo de monetização e preços ainda não estão definidos; serão decididos com base nos aprendizados do piloto.*

## Visão de longo prazo

O FomentoRadar faz parte de uma trilha de produtos que reaproveitam o mesmo núcleo de requisitos estruturados:

**Radar Acadêmico → FomentoRadar → GrantGraph**

O crescimento previsto acontece em três direções, sempre condicionado a evidências de demanda:

- **Mais chamadas e agências** monitoradas.
- **Mais empresas** atendidas, inclusive via incubadoras e aceleradoras.
- **Mais produtos** construídos sobre a mesma base de conhecimento de editais.

## Princípios de condução

- **Rastreabilidade acima de tudo:** toda avaliação aponta para requisito, evidência, página, documento e versão.
- **Honestidade sobre incerteza:** na dúvida, o sistema diz "desconhecido".
- **Histórico preservado:** versões de editais e avaliações antigas nunca são sobrescritas.
- **Privacidade por padrão:** coleta do mínimo de dados necessário e isolamento entre empresas (LGPD em mente).
- **Proporcionalidade:** começar simples, crescer quando houver demanda comprovada.

## Abordagem técnica (visão geral)

Detalhes técnicos ficam na documentação de engenharia (a ser publicada). Para contextualização:

- Um **monólito modular** em Python com interface em Streamlit, pensado para rodar localmente no início.
- Inteligência artificial usada para **extrair requisitos** dos editais em formato estruturado. **Quem julga a elegibilidade são regras explícitas e testáveis**, não o modelo de linguagem.
- Todo conteúdo externo é tratado como dado não confiável, e toda saída de IA é validada antes de uso.

## Como colaborar

Estamos especialmente interessados em conversar com:

- **Fundadores e gestores de P&D** dispostos a participar de um diagnóstico e compartilhar a experiência com editais.
- **Incubadoras, aceleradoras e núcleos de inovação** que queiram apoiar a validação com suas empresas.
- **Especialistas em fomento e captação** para revisar requisitos e a qualidade do diagnóstico.
- **Parceiros institucionais** interessados em fontes, dados abertos e integrações futuras.

**Contato:** _[a preencher: nome, e-mail e/ou canal de contato]_

## Aviso importante

O FomentoRadar é uma ferramenta de apoio à decisão. Seus resultados **não constituem parecer jurídico, garantia de elegibilidade ou de aprovação**. Confira sempre o edital oficial vigente antes de submeter qualquer proposta.

---

*Este README é uma versão de contextualização para colaboração e apresentação a parceiros. Uma documentação técnica completa será publicada em momento oportuno.*
