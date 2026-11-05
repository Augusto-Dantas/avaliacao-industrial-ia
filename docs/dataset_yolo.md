# Dataset híbrido para YOLO

## Objetivo e limites

Este projeto passa a ter um pipeline de detecção de objetos com Ultralytics YOLO. O CSV industrial original é tabular e **não contém imagens**; portanto, ele não treina o detector visual. A detecção visual deve ser avaliada separadamente da classificação tabular.

Uma fotografia convencional pode mostrar porosidade aberta, depósitos, respingos e descontinuidades superficiais. Ela não confirma, por si só, sobrecarga elétrica, vibração do equipamento ou desvio térmico interno. Essas condições exigem sensores, termografia ou dados sincronizados.

## Fontes reais iniciais

1. **Welding Defect Object Detection (Hugging Face)** — 2.028 imagens anotadas, já distribuídas em treino/validação/teste e nos formatos YOLO e COCO. O cartão informa as classes originais `Bad Weld`, `Good Weld` e `Defect`, e licença CC0. É um baseline útil, mas a classe genérica `Defect` não equivale a porosidade ou a qualquer causa específica.
   - Dataset: https://huggingface.co/datasets/rikkarth/welding-defect-object-detection
   - Download local: `hf download rikkarth/welding-defect-object-detection --repo-type dataset --local-dir data/raw/welding-defect-object-detection`
   - Inspecione a estrutura e o `data.yaml` fornecidos antes de treinar; adapte os caminhos sem renomear classes de forma enganosa.

2. **LoHi-WELD** — 3.022 imagens reais de cordões de solda, anotadas manualmente, com poros, depósitos, descontinuidades e manchas. O repositório do estudo disponibiliza o dataset e anotações; consulte os termos e cite o artigo ao reutilizar os dados.
   - Artigo: https://doi.org/10.1109/ACCESS.2024.3407019
   - Repositório e instruções de download: https://github.com/SylvioBlock/LoHi-Weld
   - O artigo informa possibilidade de uso comercial e não comercial com citação adequada; confirme os termos do pacote baixado.

**Não una automaticamente as duas fontes.** Primeiro verifique rótulos, resolução, modalidade, duplicatas e licença. A classe genérica `Defect` da primeira fonte não deve ser convertida em `porosity` sem inspeção e nova anotação.

## Imagens sintéticas

As imagens sintéticas entram apenas como complemento de treinamento. Gere variações plausíveis de iluminação, ângulo, distância, material, acabamento e intensidade do defeito. Cada imagem sintética precisa ter anotação revisada por pessoa; não use a descrição do prompt como rótulo automático.

Registre a origem em um manifesto CSV com, no mínimo: `image_path`, `source_type` (real/synthetic), `source_dataset`, `license`, `class_names`, `annotator` e `review_status`.

Regras:
- Não apresentar imagem gerada como fotografia industrial real.
- Não duplicar uma imagem real e sua variante aumentada entre splits diferentes.
- Não colocar sintéticas na validação ou no teste de desempenho principal.
- Manter um teste final composto exclusivamente por imagens reais, de lotes/equipamentos/fontes que não aparecem no treino.
- Relatar métricas separadas para teste real e para qualquer avaliação sintética.

## Formato de anotação

Ultralytics YOLO Detection usa um arquivo `.txt` por imagem. Cada linha representa um objeto:

```text
<class_id> <x_center> <y_center> <width> <height>
```

As coordenadas são normalizadas entre 0 e 1 em relação à largura/altura da imagem; IDs de classe começam em zero. Imagens sem defeitos podem não ter arquivo de rótulo. Consulte https://docs.ultralytics.com/datasets/detect/.

## Estrutura local

Veja [data/yolo/README.md](../data/yolo/README.md). Exemplo de `data/yolo/data.yaml` (ajuste nomes e IDs para corresponder exatamente aos rótulos):

```yaml
path: data/yolo
train: images/train
val: images/val
test: images/test
names:
  0: bad_weld
  1: good_weld
  2: defect
```

O exemplo acima corresponde apenas ao dataset de três classes do Hugging Face; não é uma taxonomia universal de defeitos.

## Treinamento e inferência

Instale as dependências e execute na raiz do repositório:

```bash
pip install -r requirements.txt
python src/train_yolo.py --data data/yolo/data.yaml --weights yolo26n.pt --epochs 100 --imgsz 640
python src/predict_yolo.py --weights runs/detect/welding-yolo/weights/best.pt --source caminho/para/imagem.jpg
```

O script salva pesos e resultados em `runs/`, que são artefatos locais e não devem ser commitados sem necessidade.

## Critérios de avaliação

Relate mAP50, mAP50-95, precisão, recall e matriz de confusão por classe. Examine falsos negativos, principalmente em defeitos pequenos. Compare:
1. treino só com imagens reais;
2. treino com reais + sintéticas;
3. avaliação final exclusivamente em imagens reais independentes.

Não declare ganho por adicionar imagens sintéticas sem essa comparação. Um detector experimental não deve acionar ou parar máquinas; toda decisão operacional requer validação e supervisão humana.
