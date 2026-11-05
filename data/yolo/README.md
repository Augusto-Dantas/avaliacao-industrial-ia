# Dataset YOLO e fontes auxiliares

Na raiz do repositório, com a virtualenv ativada:

```bash
python src/setup_yolo.py
```

O comando instala as dependências necessárias, consulta o tamanho publicado dos datasets antes de baixar, aplica um teto combinado de **25 GB** e baixa as fontes públicas catalogadas. Downloads interrompidos podem ser retomados pelo cache do Hugging Face. Para treinar ao final:

```bash
python src/setup_yolo.py --train
```

## Catálogo padrão

| Dataset | Conteúdo | Licença indicada pela fonte | Uso no projeto |
|---|---|---|---|
| [rikkarth/welding-defect-object-detection](https://huggingface.co/datasets/rikkarth/welding-defect-object-detection) | 2.028 imagens, caixas YOLO, 3 classes | CC0-1.0 | Preparado automaticamente para o detector atual |
| [AI4Manufacturing/217](https://huggingface.co/datasets/AI4Manufacturing/217) | 448 imagens SMAW, caixas em pixels no schema parquet | CC BY 4.0 (fonte Mendeley) | Download auxiliar; conversor ainda necessário |
| [AI4Manufacturing/218](https://huggingface.co/datasets/AI4Manufacturing/218) | 61.670 tiras de solda laser, rótulo de imagem ok/defective | CC BY 4.0 (fonte Zenodo) | Download auxiliar para classificação, não detecção |

As fontes são baixadas em `.download/` (cache) e `sources/` (cópias locais) e registradas em `datasets-manifest.json`. Apenas o dataset nativo YOLO é convertido para `images/{train,val,test}` e `labels/{train,val,test}`. Os demais ficam separados: classificação de imagem não fornece caixas delimitadoras; não misture suas imagens/labels com o detector YOLO sem conversão e revisão.

## Opções

```bash
# Limite menor ou maior
python src/setup_yolo.py --max-gb 10

# Selecionar somente uma ou duas fontes
python src/setup_yolo.py --datasets rikkarth/welding-defect-object-detection AI4Manufacturing/217

# Preparar e treinar
python src/setup_yolo.py --train --epochs 100 --imgsz 640 --batch 8 --device cpu

# Usar GPU NVIDIA com PyTorch CUDA já instalado e compatível
python src/setup_yolo.py --train --device 0

# Atualizar downloads e reconstruir a estrutura YOLO
python src/setup_yolo.py --force
```

O limite é calculado com os tamanhos informados pelo Hugging Face antes do download; o tamanho em disco pode variar ligeiramente por cache/metadados. O programa não baixa fontes sem tamanho verificável. Verifique espaço livre em disco antes de iniciar.

## Fontes que não entram no download automático

- [LoHi-WELD](https://github.com/SylvioBlock/LoHi-Weld): 3.022 imagens reais e anotações em pacote do Google Drive. O repositório instrui download manual, mas não apresenta uma licença de dados clara; por isso não é baixado automaticamente nem incluído no limite.
- [Intel Robotic Welding Multimodal Dataset](https://huggingface.co/datasets/IntelLabs/Intel_Robotic_Welding_Multimodal_Dataset): exige aprovação/aceitação explícita da licença Intel Research Use, não comercial. O instalador não aceita termos em nome do usuário e não tenta contornar o gate.

As licenças, proveniência e condições devem ser revistas antes de redistribuir, publicar ou usar comercialmente os dados. Consulte `docs/dataset_yolo.md`.
