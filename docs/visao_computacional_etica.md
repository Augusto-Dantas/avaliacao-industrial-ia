# Visão computacional: porosidade e HAZ

## Arquitetura proposta

Câmera RGB/macro com iluminação controlada para cordão e câmera termográfica radiométrica calibrada para ZTA/HAZ. Registrar lote, peça, timestamp, câmera, lente, distância, emissividade e parâmetros de solda. Pré-processar foco/exposição, correção geométrica, calibração px/mm e ROI. Segmentar poros (YOLO-seg ou U-Net), retornando máscara, contagem, área px/mm², posição e confiança. Na HAZ extrair temperatura máxima/média, gradiente e largura; validar com referência rastreável/termopares. Fazer fusão multimodal com sinais do processo. Inferência edge versionada e assinada; falha de câmera/calibração deve gerar `indeterminado`, nunca aceite automático.

## Contrato sugerido

```json
{
  "job_id": "uuid",
  "peca_id": "string",
  "status": "completed|indeterminate|failed",
  "porosidade": {"count": 0, "area_mm2": 0.0, "confidence": 0.0},
  "haz": {"max_temp_c": 0.0, "mean_temp_c": 0.0, "width_mm": 0.0},
  "model_version": "string",
  "calibration_id": "string"
}
```

## Validação

Criar dataset representativo por lote, material, geometria, acabamento, iluminação e condição de câmera. Anotar por especialistas com protocolo e dupla revisão; separar treino/validação/teste por lote e período. Avaliar precisão/recall por classe, IoU/Dice, erro dimensional em mm²/mm, calibração de confiança e taxa de indeterminação. Testar deriva, contaminação, reflexos, oclusão e falhas de sensor. Definir limites de aceitação com engenharia e normas aplicáveis, nunca inventá-los.

## Ética, segurança e impacto social

- Supervisão humana para alertas, liberação de peças e decisões de manutenção.
- Não usar o sistema para vigilância ou avaliação individual de trabalhadores.
- Minimizar dados pessoais, controlar acesso, registrar auditoria e definir retenção.
- Documentar falsos positivos/negativos, incerteza, limites e versões.
- Treinar operadores para interpretar alertas e contestar resultados.
- Aplicar fail-safe: dados ausentes, câmera fora de calibração ou modelo indisponível resultam em estado indeterminado e inspeção alternativa.
- Não conectar diretamente a saída experimental a CLP/atuadores sem análise de risco, validação independente e mecanismos de segurança certificados.

**Limitação central:** o dataset entregue é tabular e não contém imagens. Esta seção é uma proposta técnica, não evidência de modelo visual treinado ou validado.
