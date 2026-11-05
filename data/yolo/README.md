# Dataset YOLO (local)

O dataset padrão pode ser baixado e preparado automaticamente:

```bash
python src/setup_yolo.py
```

Para preparar e iniciar o treinamento:

```bash
python src/setup_yolo.py --train
```

O utilitário instala as dependências, baixa o dataset CC0 `rikkarth/welding-defect-object-detection`, mapeia os splits `train/valid/test` para `train/val/test` e gera `data.yaml`.

Estrutura gerada:

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

Imagens, anotações, cache e pesos não são versionados no Git. Use `--force` para substituir o dataset local. Consulte [../../docs/dataset_yolo.md](../../docs/dataset_yolo.md) para limitações e critérios de avaliação.
