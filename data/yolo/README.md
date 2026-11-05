# Dataset YOLO (local)

Este diretório recebe os dados de treinamento. As imagens, anotações e pesos não são versionados no Git.

Estrutura esperada:

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

Cada imagem anotada deve ter um arquivo `.txt` homônimo. Imagens negativas, sem objetos, podem ficar sem arquivo de rótulo. Consulte [../../docs/dataset_yolo.md](../../docs/dataset_yolo.md) para fontes, classes, licenças e regras de divisão.

Não coloque imagens sintéticas na validação ou no teste final. O teste principal deve conter imagens reais de origem independente.
