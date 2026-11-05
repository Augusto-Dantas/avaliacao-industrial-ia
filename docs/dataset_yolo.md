# Dataset híbrido para YOLO

## Objetivo e limites

Este projeto possui um pipeline opcional de detecção de objetos com Ultralytics YOLO. O CSV industrial original é tabular e **não contém imagens**; portanto, ele não treina o detector visual. A detecção visual deve ser avaliada separadamente da classificação tabular.

Uma fotografia convencional pode mostrar porosidade aberta, depósitos, respingos e descontinuidades superficiais. Ela não confirma, por si só, sobrecarga elétrica, vibração do equipamento ou desvio térmico interno. Essas condições exigem sensores, termografia ou dados sincronizados.

## Fontes reais iniciais

1. **Welding Defect Object Detection (Hugging Face)** — dataset publicado com imagens anotadas e classes originais `Bad Weld`, `Good Weld` e `Defect`. Consulte o cartão do dataset para confirmar contagem, formato, licença e versão atuais.
   - Dataset: https://huggingface.co/datasets/rikkarth/welding-defect-object-detection
   - Download: use as instruções atuais do cartão do dataset e inspecione a estrutura baixada antes de adaptar os caminhos.
   - Não presuma que a classe genérica `Defect` equivale a porosidade ou a uma causa específica.

2. **LoHi-WELD** — conjunto de imagens de cordões de solda com anotações manuais.
   - Artigo: https://doi.org/10.1109/ACCESS.2024.3407019
   - Repositório e instruções de download: https://github.com/SylvioBlock/LoHi-Weld
   - Consulte os termos do pacote efetivamente baixado e cite o artigo ao reutilizar os dados.

**Não una automaticamente as fontes.** Primeiro verifique rótulos, resolução, modalidade, duplicatas e licença. Não converta a classe genérica `Defect` em `porosity` sem inspeção e nova anotação.

## Imagens sintéticas

As imagens sintéticas entram apenas como complemento de treinamento. Gere variações plausíveis de iluminação, ângulo, distância, material, acabamento e intensidade do defeito. Cada imagem sintética precisa de anotação revisada por pessoa; não use a descrição do prompt como rótulo automático.

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

Veja [data/yolo/README.md](../data/yolo/README.md). A estrutura esperada é:

```text
data/yolo/
├── data.yaml
├── images/
│   ├── train/
│   ├── val/
│   └── test/
└── labels/
    ├── train/
    ├── val/
    └── test/
```

O `data/yolo/data.yaml` incluído é um modelo inicial de três classes. Ajuste `path`, `train`, `val`, `test`, `names` e os IDs para corresponder exatamente ao dataset anotado. O diretório `images/train` e `images/val` devem existir e conter imagens.

## Instalação, treinamento e inferência

As dependências YOLO são opcionais e estão separadas para que a instalação da API não baixe PyTorch/CUDA desnecessariamente.

Em máquina sem GPU NVIDIA, instale PyTorch CPU e depois Ultralytics:

```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
pip install -r requirements-vision.txt
```

Em máquina com CUDA, instale uma versão de PyTorch compatível com o driver/GPU seguindo https://pytorch.org/get-started/locally/ e depois instale `requirements-vision.txt`.

Execute na raiz do repositório:

```bash
python src/train_yolo.py --data data/yolo/data.yaml --weights yolo26n.pt --epochs 100 --imgsz 640
python src/predict_yolo.py --weights runs/detect/welding-yolo/weights/best.pt --source caminho/para/imagem.jpg
```

O treinamento verifica previamente a existência das pastas de treino e validação e se elas contêm imagens. Se não estiverem preparadas, encerra com instruções em vez de baixar pesos e falhar dentro do Ultralytics. O arquivo `best.pt` só existe após treinamento concluído com sucesso.

O script salva pesos e resultados em `runs/`, que são artefatos locais e não devem ser commitados sem necessidade.

## Critérios de avaliação

Relate mAP50, mAP50-95, precisão, recall e matriz de confusão por classe. Examine falsos negativos, principalmente em defeitos pequenos. Compare:
1. treino só com imagens reais;
2. treino com reais + sintéticas;
3. avaliação final exclusivamente em imagens reais independentes.

Não declare ganho por adicionar imagens sintéticas sem essa comparação. Um detector experimental não deve acionar ou parar máquinas; toda decisão operacional requer validação e supervisão humana.
