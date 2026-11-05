# Relatório técnico

## Dataset e preparação

15.000 linhas, 21 colunas, nenhum valor ausente; período observado de 01/10/2026 a 11/10/2026. Converter timestamp, ordenar por tempo e preservar lote_id. Validar soma de peças boas/defeituosas, percentuais entre 0 e 100 e tempos não negativos. Não remover zeros sem análise: podem indicar parada.

## OEE

OEE = Disponibilidade × Desempenho × Qualidade. Disponibilidade = (tempo planejado − parada) / planejado; desempenho = produção real / teórica no tempo operacional; qualidade = boas / produzidas. Médias observadas: disponibilidade 98,63%, desempenho 98,59%, qualidade 96,11%, OEE 94,24%. Para OEE agregado, usar numeradores/denominadores do período, não a média simples dos percentuais.

## Classes e desbalanceamento

| Classe | Registros | % |
|---|---:|---:|
| Sem Falha | 13.214 | 88,09 |
| Porosidade na Solda | 1.263 | 8,42 |
| Desvio Termico HAZ | 388 | 2,59 |
| Sobrecarga de Corrente | 76 | 0,51 |
| Vibracao Excessiva | 59 | 0,39 |

A classe majoritária é cerca de 224 vezes a menor. Acurácia isolada é enganosa; usar macro-F1, balanced accuracy, recall por classe e matriz de confusão.

## Correlação de Pearson com OEE

Peças boas +0,926; desempenho +0,769; disponibilidade +0,765; qualidade +0,594; tempo parada −0,765; peças defeituosas −0,581; anomalia −0,459; área porosidade −0,422; temperatura máxima HAZ −0,279; pressão gás +0,237; temperatura solda −0,109. Corrente, tensão, velocidade e vibração têm correlação linear próxima de zero no agregado. Correlações com componentes/contagens são em parte matemáticas; não implicam causalidade. Fazer análises por lote/classe, Spearman, dispersões e defasagens.

## Pipeline e features

Ingestão CSV/Parquet e validação de schema; tratamento rastreável de ausências/outliers; janelas móveis (média, desvio, amplitude, mínimo/máximo), tendências e derivadas de sinais; atributos de solda calibrados px/mm² e métricas térmicas; hora/turno sem identificar trabalhadores. Separar treino/teste por tempo e lote e monitorar drift.

## Modelagem

Random Forest multiclasse com pesos `balanced_subsample`, imputação mediana e holdout estratificado 75/25. Excluir OEE, componentes, quantidades finais e rótulos auxiliares como features para evitar vazamento. Isolation Forest treinado em Sem Falha como triagem. Métricas são gravadas em `models/metrics.json`. Oversampling/SMOTE pode ser comparado somente dentro dos folds de treino. Validação por lote/tempo ainda necessária.

## Operação e limitações

API demonstra POST /v1/infer (202 + job_id) e GET /v1/jobs/{id}. A fila é simulada em memória; produção requer broker, persistência, autenticação, TLS, idempotência, logs, versionamento e fallback. Dataset não tem imagens, metadados de câmera, limites normativos nem especificação oficial de API; não é possível treinar detector visual com os anexos. Resultados não provam desempenho em indústria real.
