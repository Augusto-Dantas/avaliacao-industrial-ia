# Prompts para geração de imagens no Gemini

Este catálogo reúne prompts para gerar a identidade visual, diagramas e imagens de apoio do projeto **Avaliação Industrial com IA**.

## Direção visual comum

Manter em toda a série: fotografia industrial editorial ou infográfico técnico limpo; fábrica moderna de manufatura metálica e célula robotizada de soldagem; paleta grafite, azul-petróleo, aço e branco, com laranja apenas para alertas; iluminação realista; composição profissional; sem marcas, logotipos ou marcas d'água. Preferir 16:9, exceto o avatar (1:1). Não representar IA como robô humanoide. Não inventar métricas, certificações, sensores ou funcionalidades. Textos renderizados devem ser curtos e em português brasileiro; para diagramas, é melhor gerar sem texto e inserir os rótulos depois.

**Instrução de consistência para cada prompt:** “Use a imagem de capa anexada como referência estética. Preserve a mesma paleta, materiais, iluminação e linguagem visual desta série.”

## 1. Capa do projeto

**Arquivo sugerido:** `docs/images/capa-projeto.png`

> Crie uma imagem horizontal 16:9 para o projeto técnico “Avaliação Industrial com IA”. Mostre uma célula industrial moderna de soldagem de componentes metálicos, com braço robótico de solda, peça metálica em primeiro plano e sensores industriais discretos. Sobreponha elementos gráficos translúcidos que sugiram análise de dados, séries temporais e inspeção de qualidade, sem números ou textos legíveis. Comunicar manufatura, monitoramento de processo, detecção de falhas e apoio à decisão. Fotografia industrial editorial fotorrealista, composição cinematográfica sóbria, paleta grafite e azul-petróleo com pequenos detalhes laranja, iluminação realista, sem pessoas identificáveis, logotipos ou marcas d'água.

## 2. Arquitetura da solução

**Arquivo:** `docs/images/arquitetura-solucao.png`

> Infográfico técnico horizontal 16:9, da esquerda para a direita: sensores e dados de produção; ingestão e validação; preparação e engenharia de atributos; dois caminhos paralelos (classificação de falhas e detecção de anomalias); saída com classe prevista, indicador de anomalia e recomendação para avaliação humana. Ícones simples de sensor, banco de dados, engrenagem, gráfico e painel, conectados por setas claras. Paleta grafite, azul-petróleo, branco e laranja discreto. Não incluir métricas de desempenho nem sugerir automação física.

## 3. Célula de soldagem industrial

**Arquivo:** `docs/images/celula-soldagem.png`

> Fotografia técnica fotorrealista de uma célula de soldagem industrial em fábrica organizada. Robô de soldagem trabalhando sobre peça metálica, cabos, dispositivos de fixação e sensores instalados de forma plausível. Enquadramento amplo, sem trabalhadores identificáveis, sem faíscas exageradas e sem estética sci-fi. Iluminação industrial realista, aço e grafite, detalhes azul-petróleo, 16:9, sem texto, logotipo ou marca d'água.

## 4. Sensores e variáveis do processo

**Arquivo:** `docs/images/sensores-processo.png`

> Visualização técnica 3D realista de uma estação de soldagem industrial, com chamadas visuais apontando para sensores de corrente elétrica, tensão, temperatura, pressão de gás, vibração e velocidade da linha. Cada sensor deve estar fisicamente posicionado de forma plausível. Linhas finas e ícones pequenos, sem valores numéricos ou parágrafos. Paleta grafite, aço, azul-petróleo e pequenos destaques laranja, fundo limpo, 16:9.

## 5. Dashboard de OEE

**Arquivo:** `docs/images/dashboard-oee.png`

> Mockup de dashboard industrial profissional em tela widescreen 16:9. Cartões para Disponibilidade, Desempenho, Qualidade e OEE; abaixo, gráficos simples de tendência temporal e barras comparativas. Usar dados fictícios sem valores legíveis ou rotular claramente “exemplo ilustrativo”. Não sugerir que os números são resultados reais do estudo. Design limpo, fundo grafite, painéis claros, acentos azul-petróleo e laranja, sem logotipos.

## 6. Desbalanceamento das classes

**Arquivo:** `docs/images/desbalanceamento-classes.png`

> Infográfico estatístico 16:9 com gráfico de barras de cinco classes de falha industrial fortemente desbalanceadas: uma barra dominante “Sem Falha” e quatro barras menores “Porosidade na Solda”, “Desvio Térmico HAZ”, “Sobrecarga de Corrente” e “Vibração Excessiva”. Não inserir percentuais nem quantidades; os números serão adicionados depois com base no relatório. Não distorcer proporções. Estilo vetorial corporativo, fundo claro, grafite, azul-petróleo e laranja.

## 7. Classificação supervisionada

**Arquivo:** `docs/images/classificacao-falhas.png`

> Infográfico técnico 16:9 de um pipeline de classificação supervisionada para dados industriais tabulares. À esquerda, tabela abstrata de variáveis de sensores; no centro, conjunto de árvores de decisão formando Random Forest; à direita, cinco classes de saída: Sem Falha, Porosidade na Solda, Desvio Térmico HAZ, Sobrecarga de Corrente e Vibração Excessiva. Setas e hierarquia visual clara. Não inventar acurácia, confiança ou validação. Estilo vetorial limpo, fundo claro, grafite e azul-petróleo com laranja para alertas.

## 8. Detecção de anomalias

**Arquivo:** `docs/images/deteccao-anomalias.png`

> Infográfico 16:9 sobre detecção não supervisionada de anomalias. Gráfico de dispersão conceitual com nuvem principal representando comportamento comum e poucos pontos afastados destacados como possíveis anomalias. Ao lado, equipamento industrial e bloco analítico “Isolation Forest”. Incluir a nota “Anomalia não é diagnóstico de falha”. Não usar dados reais nem valores numéricos. Design técnico legível, fundo claro, grafite, azul-petróleo e laranja.

## 9. Fluxo de inferência e apoio à decisão

**Arquivo:** `docs/images/fluxo-inferencia.png`

> Infográfico horizontal 16:9: entrada de leituras industriais; validação dos campos; modelo de classificação; detector de anomalias; resposta com classe prevista, confiança estimada e indicador de anomalia; recomendação de inspeção humana. Representar explicitamente que a saída é apoio à decisão e que ações físicas não são executadas automaticamente. Ícones simples, setas, textos curtos em português, grafite, azul-petróleo, branco e laranja.

## 10. API de inferência

**Arquivo:** `docs/images/api-inferencia.png`

> Ilustração técnica 16:9 para documentação de uma API de inferência industrial. Mostrar um cliente enviando JSON simplificado para serviço de API, que consulta modelos de classificação e detecção de anomalias e devolve JSON com identificador de tarefa, classe prevista e indicador de anomalia. Blocos e setas, sem código extenso nem endpoints inventados. Identificar o serviço “API de Inferência”. Estilo isométrico vetorial, fundo claro, grafite e azul-petróleo, detalhes laranja.

## 11. Visão computacional — proposta conceitual

**Arquivo:** `docs/images/visao-computacional-conceito.png`

> Prancha conceitual 16:9 de uma possível estação de inspeção visual de soldas. Câmera industrial RGB e câmera termográfica observando junta soldada; ao lado, imagem ampliada da região com máscara hipotética de segmentação indicando porosidade e região térmica HAZ. Identificar de forma explícita “Proposta conceitual — não treinada neste estudo”. Não afirmar que imagens foram coletadas ou que modelo visual foi validado. Visualização técnica realista com sobreposições discretas, grafite, azul-petróleo e laranja.

## 12. Supervisão humana e segurança

**Arquivo:** `docs/images/supervisao-humana.png`

> Fotografia editorial fotorrealista de profissional de qualidade industrial usando EPI adequado e analisando em monitor alertas de um sistema de apoio à decisão em célula de soldagem. Pessoa em posição segura, sem rosto identificável, empresa ou marca. Comunicar supervisão humana, responsabilidade, segurança e colaboração entre pessoas e tecnologia. Não mostrar IA tomando decisões autônomas nem robôs humanoides. Paleta industrial sóbria, iluminação naturalista, 16:9, sem texto ou marca d'água.

## 13. Ciclo de melhoria contínua

**Arquivo:** `docs/images/melhoria-continua.png`

> Ilustração técnica 16:9 de um ciclo de melhoria contínua industrial: monitorar processo, analisar dados, investigar alertas, validar com especialistas e melhorar parâmetros de produção. Linha industrial ao fundo e cinco etapas conectadas em ciclo com ícones simples. Não sugerir alteração automática de parâmetros. Textos curtos em português, estilo vetorial corporativo, grafite, azul-petróleo, branco e laranja discreto.

## 14. Avatar do GitHub

**Arquivo:** `docs/images/avatar-github.png`

> Símbolo quadrado 1:1, simples e reconhecível em tamanho pequeno, para “Avaliação Industrial com IA”. Combinar minimalisticamente engrenagem industrial, gráfico de dados e sinal de inspeção/qualidade. Sem letras, palavras ou logotipos de terceiros. Fundo grafite, símbolo branco e azul-petróleo, pequeno acento laranja. Design vetorial flat, alto contraste, centralizado, sem linhas finas ou marca d'água.

## 15. Banner de apresentação

**Arquivo:** `docs/images/banner-apresentacao.png`

> Banner horizontal 16:9 para apresentação técnica sobre IA aplicada à avaliação de processos industriais. Fábrica moderna de soldagem no lado direito e espaço negativo amplo e escuro no lado esquerdo para inserir título e subtítulo posteriormente. Linhas discretas de dados e sinais de monitoramento integrados ao ambiente, sem texto gerado. Fotografia industrial editorial fotorrealista, grafite e azul-petróleo com acentos laranja, visual sóbrio, alta resolução, sem logotipos ou marca d'água.

## Prompt negativo geral

Acrescente ao final quando o Gemini aceitar instruções negativas:

> Evitar texto ilegível, palavras inventadas, números falsos, gráficos com escalas enganosas, marcas comerciais, logotipos, marcas d'água, mãos deformadas, equipamentos impossíveis, sensores flutuantes, cabos desconectados, faíscas exageradas, estética cyberpunk, robôs humanoides, interfaces holográficas excessivas e qualquer indicação de que o sistema toma decisões físicas autônomas.

## Recomendações de uso

1. Gere primeiro a capa e o avatar para estabelecer a direção visual.
2. Anexe a capa como referência ao gerar as demais imagens e solicite consistência estética.
3. Para diagramas com texto, prefira gerar sem texto e adicionar rótulos num editor. Revise a ortografia e as proporções dos gráficos.
4. Mockups de dashboard, gráficos e segmentações devem ser identificados como ilustrativos, não como resultados experimentais.
5. O dataset disponibilizado é tabular e não contém imagens. A seção de visão computacional é uma proposta técnica, não um detector visual treinado.
6. Salve as imagens em `docs/images/` com os nomes sugeridos acima.
