# Prompt: painel de obtenção de textos completos

Prompt reutilizável para gerar, a partir de qualquer conjunto de referências bibliográficas, um painel HTML de arquivo único que organize e acompanhe o download dos textos completos.

Foi extraído de uma aplicação real em revisão sistemática de literatura e incorpora as armadilhas encontradas naquele caso. Serve para qualquer corpus, de dez a alguns milhares de registros.

---

## Como usar

Copie a seção **PROMPT** inteira, substitua os campos entre `<colchetes angulares>` e envie junto com o arquivo de referências. As seções seguintes existem para você entender e ajustar o que está sendo pedido; não precisam ser enviadas.

Se quiser apenas o essencial, use a **versão curta** no final.

---

## PROMPT

> Preciso de um painel HTML para acompanhar a obtenção dos textos completos de um conjunto de referências bibliográficas.
>
> **Fonte dos dados:** `<caminho ou anexo do arquivo>`
> **Formato:** `<CSV da Scopus | exportação da Web of Science | RIS | BibTeX | CSV genérico | JSON>`
> **Volume aproximado:** `<N>` referências
> **Contexto do projeto:** `<uma frase: tema, finalidade, etapa>`
>
> ### 1. Preparo dos dados, antes de gerar o painel
>
> Extraia de cada referência: identificador estável, título, autores, ano, periódico, DOI, contagem de citações e resumo. Quando um campo não existir na fonte, deixe vazio; não invente e não infira.
>
> Atribua a cada registro um identificador curto e estável, no formato `REC0001`, mesmo que a fonte já traga um. É esse identificador que aparece na interface e permite conversar sobre um registro específico.
>
> **Deduplique em duas passagens.** Primeiro por DOI normalizado, removendo o prefixo `https://doi.org/` e convertendo para minúsculas. Depois por título normalizado, isto é, transliterado para ASCII, em minúsculas, sem artigo inicial e sem caracteres não alfanuméricos. Em seguida faça uma **varredura de similaridade textual** entre todos os pares de títulos restantes, com limiar de 0,90, e me apresente os pares suspeitos antes de fundi-los. Deduplicação por DOI sozinha deixa passar duplicatas; isso é regra, não exceção.
>
> **Detecte o acesso aberto** a partir dos campos da própria fonte quando existirem, classificando na taxonomia usual: gold, green, bronze, híbrido. Se a fonte não trouxer essa informação, deixe o campo vazio e diga isso claramente; não presuma que um artigo é fechado só porque o campo está ausente.
>
> Ao final desta etapa, informe: quantos registros brutos, quantas duplicatas removidas, quantos únicos, quantos com DOI, quantos com resumo e a distribuição de acesso aberto.
>
> ### 2. Campos opcionais, incluir apenas se eu fornecer
>
> - **Classificação por triagem:** `<descreva as categorias, por exemplo A incluir, B dúvida, C excluir>`. Se houver, o painel deve filtrar por ela e exibir cada categoria com cor e rótulo próprios.
> - **Situação em gerenciador de referências:** se eu indicar uma biblioteca Zotero, Mendeley ou similar, verifique quais registros já possuem o PDF anexado e **confirme que o arquivo existe no disco**, não apenas que há registro de anexo. Marque cada registro como `pdf`, `apenas referência` ou `ausente`.
> - **Campos temáticos livres:** `<liste os campos, por exemplo país, método, construto>`. Aparecem como etiquetas no cartão e como filtro quando tiverem poucos valores distintos.
>
> ### 3. O que o painel precisa fazer
>
> Arquivo HTML único, sem dependências além de fontes do Google Fonts, que eu abro no navegador com dois cliques.
>
> **Cabeçalho fixo** com o nome do projeto, um medidor de progresso e indicadores numéricos: total obtido, total pendente, e quantos dos pendentes estão em acesso aberto. Esse último número é o mais acionável de todos, porque separa o que resolve em um clique do que vai exigir acesso institucional.
>
> **Barra de filtros combináveis:** busca livre sobre título, autores, periódico, DOI e campos temáticos; filtro por classificação de triagem, se houver; filtro por via de acesso aberto; filtro por situação no gerenciador de referências, se houver; filtro por situação de obtenção. O filtro de situação deve **abrir por padrão em pendentes**, porque o painel existe para mostrar o que falta, não o que já foi feito.
>
> **Lista de cartões**, um por referência, contendo identificador, ano, título, autores abreviados com "et al." a partir do quarto, periódico em itálico, contagem de citações, etiquetas de acesso aberto e demais campos, e o DOI em fonte monoespaçada.
>
> **Ações por cartão:** botão primário que abre o artigo pelo DOI em nova aba; botão secundário de busca no Google Scholar pelo título, como alternativa quando o DOI não resolve; e um controle de marcação de obtido.
>
> **Persistência de estado.** As marcações manuais ficam no `localStorage` do navegador e sobrevivem ao fechamento da página. Envolva toda leitura e escrita em `try/catch` e faça a página renderizar corretamente quando o armazenamento estiver vazio ou indisponível; em janela anônima ele falha silenciosamente.
>
> **Distinção entre estado verificado e estado declarado.** Se houver verificação em gerenciador de referências, os registros com PDF confirmado contam como obtidos automaticamente, aparecem esmaecidos e com rótulo fixo em vez de caixa de marcação, e não podem ser desmarcados. Só o que eu marco à mão é reversível. O medidor deve distinguir visualmente as duas origens.
>
> **Exportação do pendente:** um botão que copia para a área de transferência a lista do que falta, em formato separado por tabulações, pronto para colar em planilha, contendo identificador, classificação, ano, título, DOI e via de acesso.
>
> **Reinício:** um botão que apaga apenas as marcações manuais, com confirmação, preservando o que foi verificado automaticamente.
>
> ### 4. Design
>
> Trate como ferramenta de trabalho, não como peça editorial: a página é operada e escaneada, não lida de cima a baixo. Investimento em hierarquia tipográfica, espaçamento e legibilidade; nada de herói decorativo.
>
> Defina uma paleta de quatro a seis valores nomeados e derive tudo dela. **Não use a paleta creme com serifa e acento terracota**, nem gradiente roxo-azul, nem Inter como tipografia padrão: são os defaults reconhecíveis de página gerada por IA. Prefira uma escolha ancorada no assunto.
>
> Para as etiquetas de acesso aberto, use as cores da própria convenção da área: dourado para gold, verde para green, bronze para bronze, e um tom distinto para híbrido. É semanticamente correto e evita paleta arbitrária.
>
> **Os três estados de tema precisam funcionar.** Defina a paleta clara completa em `:root`; redefina apenas os tokens em `@media (prefers-color-scheme: dark)` protegido por `:root:not([data-theme="light"])`; redefina de novo em `:root[data-theme="dark"]`. Nenhuma cor pode ter sua única definição dentro de um bloco de media ou de `[data-theme]`. O `body` precisa de `background` explícito vindo de token.
>
> Tipografia em pelo menos dois papéis, com uma família para títulos e outra para interface, mais monoespaçada para DOI e números. Use `font-variant-numeric: tabular-nums` onde houver dígitos alinhados. Layout responsivo, com os cartões reorganizando abaixo de 720 pixels de largura.
>
> ### 5. Antes de me entregar, verifique
>
> Abra o arquivo em navegador headless e confirme, reportando os números:
>
> - a quantidade de cartões renderizados bate com a quantidade de registros únicos;
> - nenhum erro de JavaScript no console;
> - cada filtro isoladamente devolve a contagem esperada;
> - marcar um item incrementa o medidor e remove o cartão da vista quando o filtro está em pendentes;
> - a página não rola horizontalmente em 1280 e em 375 pixels de largura.
>
> Se qualquer verificação falhar, corrija antes de entregar. Não me entregue um painel que você não abriu.
>
> ### 6. Entregue também
>
> - o painel HTML;
> - um arquivo RIS com os registros pendentes, para importação em gerenciador de referências;
> - o relatório dos números do preparo, incluindo os pares de duplicatas encontrados e o que foi feito com cada um.

---

## O que este prompt assume sobre a fonte

**Campos indispensáveis:** título e, na prática, DOI. Sem DOI o painel funciona, mas o botão primário perde a função e sobra apenas a busca no Scholar.

**Campos que mudam a utilidade:** resumo, se o painel também servir para decidir; contagem de citações, para ordenar por relevância; marcação de acesso aberto, que é o que torna o painel acionável em vez de apenas informativo.

**Formatos que funcionam bem.** A exportação CSV da Scopus com o conjunto *All fields* traz tudo. A exportação da Web of Science em texto com registros etiquetados, no modo *Full Record and Cited References*, também. RIS e BibTeX funcionam, mas costumam não trazer a marcação de acesso aberto. Uma planilha genérica funciona desde que tenha ao menos título e DOI.

---

## Armadilhas conhecidas

**Título truncado na origem.** Bases indexadoras eventualmente exportam títulos incompletos. Num corpus real, dois registros em 141 exclusivos de uma base vieram com a primeira metade do título faltando, e o defeito estava no arquivo bruto exportado, não no processamento. Quando o corpus for insumo de trabalho sério, vale conferir os títulos contra uma terceira fonte, como o OpenAlex, comparando comprimento e soma de verificação sobre o título normalizado. Cuidado com o inverso: o OpenAlex descarta o subtítulo depois dos dois pontos em parte de suas fontes, de modo que a maioria das divergências será defeito dele, não seu. Na dúvida, o título mais longo costuma ser o correto.

**Deduplicação por DOI é insuficiente.** Quatro causas observadas: o mesmo artigo com DOI de *online first* e DOI da versão final; o mesmo artigo indexado com DOIs de editoras diferentes; DOI ausente em um dos lados do par; e título concatenado com a tradução para outro idioma, o que altera a chave de título normalizado. A varredura de similaridade complementar é barata e pega os quatro casos.

**Títulos bilíngues.** Algumas bases concatenam a versão em inglês com a tradução entre colchetes, o que polui a exibição e quebra a comparação. Normalize para a parte em inglês, guardando o original.

**Verificação de anexo em gerenciador de referências.** Conferir se existe registro de anexo não basta: o arquivo pode ter sido movido ou nunca baixado. Confirme a existência no disco.

**Downloads dentro de ambiente restrito.** Se o painel for publicado em ambiente que isola a página, links que disparam download podem ficar inertes. Links que apenas navegam para o site do editor funcionam. Para uso pessoal, um arquivo HTML local aberto no próprio navegador é a entrega mais confiável.

---

## Variações que valem pedir

**Para triagem, não só obtenção.** Acrescente o resumo recolhível no cartão e controles de decisão por registro, com exportação das decisões em CSV. O painel deixa de ser lista de download e vira ferramenta de triagem.

**Para trabalho em dupla.** Peça um campo de identificação do avaliador e exportação que permita comparar duas codificações, calculando concordância.

**Para acompanhamento de leitura.** Troque a marcação binária por estados sucessivos, do tipo obtido, lido, fichado, e ordene por prioridade.

**Para corpus grande.** Acima de mil registros, peça renderização por partes ou virtualização da lista, senão a página trava ao filtrar.

---

## Versão curta

> Gere um painel HTML de arquivo único para acompanhar a obtenção de textos completos a partir de `<arquivo>`.
>
> Extraia identificador, título, autores, ano, periódico, DOI, citações e acesso aberto. Deduplique por DOI, depois por título normalizado, e faça uma varredura de similaridade com limiar de 0,90 apresentando os pares suspeitos antes de fundir.
>
> O painel precisa ter: cabeçalho fixo com medidor de progresso e contagem de pendentes em acesso aberto; busca livre; filtros combináveis por acesso aberto e por situação de obtenção, abrindo em pendentes; um cartão por referência com título, autores, periódico, citações, etiquetas e DOI; botão que abre o artigo pelo DOI e alternativa via Google Scholar; marcação de obtido persistida em `localStorage` com `try/catch`; e botão que copia a lista de pendentes em formato de planilha.
>
> Design de ferramenta, não de peça editorial. Paleta própria de quatro a seis cores, evitando os defaults reconhecíveis de página gerada por IA. Cores das etiquetas de acesso aberto seguindo a convenção da área. Os três estados de tema precisam funcionar, com todos os tokens definidos em `:root` e apenas redefinidos nos blocos de tema.
>
> Antes de entregar, abra o arquivo em navegador headless e confirme a contagem de cartões, a ausência de erros no console e o funcionamento de cada filtro. Reporte os números. Entregue também um RIS com os pendentes.

---

**Versão:** 1.0
