# Dataset YOLO híbrido para soldagem

## Preparação automatizada

Na raiz do repositório, com a virtualenv ativada, execute:

```bash
python src/setup_yolo.py --train
```

O utilitário instala as dependências de visão, baixa o dataset público `rikkarth/welding-defect-object-detection` do Hugging Face, organiza as imagens/anotações e escreve `data/yolo/data.yaml`. O download inicial tem aproximadamente 104 MB. Por padrão, o treinamento usa CPU para evitar dependência de CUDA.

Para preparar sem treinar, omita `--train`. Para GPU NVIDIA, use `--device 0` somente se o PyTorch CUDA compatível já estiver instalado. Use `--force` para substituir os dados locais preparados.

Fonte do dataset: https://huggingface.co/datasets/rikkarth/welding-defect-object-detection. O cartão informa 2.028 imagens, splits train/valid/test, três classes e licença CC0. Verifique o cartão antes de redistribuir ou publicar derivados.

## Objetivo e limites

O CSV industrial original é tabular e **não contém imagens**; portanto, ele não treina o detector visual. A detecção visual deve ser avaliada separadamente da classificação tabular.

Uma fotografia convencional pode mostrar porosidade aberta, depósitos, respingos e descontinuidades superficiais. Ela não confirma, por si só, sobrecarga elétrica, vibração do equipamento ou desvio térmico interno. Essas condições exigem sensores, termografia ou dados sincronizados.

## Classes e anotação

O dataset automatizado usa exatamente as classes originais:
- `0: bad_weld`
- `1: good_weld`
- `2: defect`

Não renomeie a classe genérica `defect` como porosidade ou causa específica sem inspeção e nova anotação.

Ultralytics YOLO Detection usa um arquivo `.txt` por imagem. Cada linha representa:

```text
<class_id> <x_center> <y_center> <width> <height>
```

As coordenadas são normalizadas entre 0 e 1. Imagens sem defeitos podem não ter arquivo de rótulo.

## Estrutura local gerada

```text
data/yolo/
├── data.yaml
├── .download/
├── images/
│   ├── train/
│   ├── val/
│   └── test/
└── labels/
    ├── train/
    ├── val/
    └── test/
```

Imagens, anotações e pesos não são versionados no Git. O utilitário mantém uma cópia de download em `.download/` para evitar baixar novamente os arquivos.

## Imagens sintéticas e avaliação

Imagens sintéticas podem complementar apenas o treinamento. Cada imagem sintética precisa de anotação revisada por pessoa; não use a descrição do prompt como rótulo automático.

- Não apresentar imagem gerada como fotografia industrial real.
- Não duplicar uma imagem real e sua variante aumentada entre splits diferentes.
- Não colocar sintéticas na validação ou no teste final de desempenho.
- Manter um teste final composto exclusivamente por imagens reais independentes.
- Relatar mAP50, mAP50-95, precisão, recall e matriz de confusão por classe.

Um detector experimental não deve acionar ou parar máquinas; toda decisão operacional requer validação e supervisão humana.

## Fonte adicional

LoHi-WELD contém imagens reais de cordões de solda com anotações manuais. Seu download e seus termos são separados; não é baixado pelo utilitário automático:
https://github.com/SylvioBlock/LoHi-Weld
