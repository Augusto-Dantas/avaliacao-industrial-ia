# Datasets de soldagem: instalação, proveniência e limites

## Instalação automatizada

Na raiz do projeto:

```bash
python src/setup_yolo.py --train
```

Por padrão, o instalador:
1. Mantém PyTorch existente se estiver funcional; caso contrário instala a build CPU para evitar CUDA desnecessário.
2. Instala Ultralytics e Hugging Face Hub.
3. Consulta o tamanho total dos arquivos dos repositórios selecionados antes do download.
4. Baixa os datasets públicos catalogados até o limite padrão de 25 GB.
5. Registra origem, licença declarada, tamanho e diretório em `data/yolo/datasets-manifest.json`.
6. Prepara para YOLO somente a fonte CC0 com anotações nativas YOLO.
7. Opcionalmente inicia o treinamento.

O download usa cache do Hugging Face e pode ser retomado. O teto pode ser alterado com `--max-gb`; selecione fontes com `--datasets`. O cálculo usa o tamanho informado pelo Hub e pode diferir ligeiramente do espaço efetivamente ocupado.

## Catálogo baixado automaticamente

### 1. Welding Defect Object Detection

- Repositório: https://huggingface.co/datasets/rikkarth/welding-defect-object-detection
- Licença declarada: CC0-1.0.
- 2.028 imagens e 5.686 caixas, formato YOLO e COCO.
- Classes originais: `bad_weld`, `good_weld`, `defect`.
- Única fonte do catálogo que o instalador atual integra automaticamente ao treinamento YOLO.

### 2. AI4Manufacturing/217 — SMAW surface defects

- Repositório: https://huggingface.co/datasets/AI4Manufacturing/217
- 448 imagens, 3 classes: `spatter`, `undercut`, `slag inclusion`.
- Caixas em coordenadas de pixels no formato COCO xywh, dentro do schema parquet.
- Licença upstream declarada: CC BY 4.0 (Mendeley Data).
- É baixado e mantido isolado. Ainda requer extração/conversão validada de parquet e normalização de caixas antes de treinar.

### 3. AI4Manufacturing/218 — laser weld seams

- Repositório: https://huggingface.co/datasets/AI4Manufacturing/218
- 61.670 tiras de solda laser, rótulos de imagem `ok` / `defective`.
- Licença upstream declarada: CC BY 4.0 (Zenodo).
- É classificação em nível de imagem, não detecção de objetos. Fica isolado e não é misturado ao treino YOLO.

Os três datasets têm tarefas, domínios e esquemas diferentes. O instalador deliberadamente não concatena labels de classes diferentes nem transforma rótulos de imagem em bounding boxes.

## Fontes não baixadas automaticamente

- LoHi-WELD: https://github.com/SylvioBlock/LoHi-Weld — 3.022 imagens reais de cordões de solda, com anotações. O pacote está em Google Drive e o repositório consultado não apresenta licença clara para os dados. Requer avaliação manual dos termos e download manual.
- Intel Robotic Welding Multimodal Dataset: https://huggingface.co/datasets/IntelLabs/Intel_Robotic_Welding_Multimodal_Dataset — contém vídeo, áudio, séries temporais e imagens. A licença Intel Research Use exige aprovação/aceitação e limita o uso à pesquisa; não é baixado automaticamente nem pode ser usado comercialmente.

## Comandos

```bash
python src/setup_yolo.py
python src/setup_yolo.py --max-gb 10
python src/setup_yolo.py --datasets rikkarth/welding-defect-object-detection AI4Manufacturing/217
python src/setup_yolo.py --train --epochs 100 --imgsz 640 --batch 8 --device cpu
python src/setup_yolo.py --train --device 0
python src/setup_yolo.py --force
```

## Estrutura

```text
data/yolo/
├── data.yaml
├── datasets-manifest.json
├── .download/                  # cache do Hub
├── sources/
│   ├── welding-defect-object-detection/
│   ├── ai4manufacturing-217-smaw/
│   └── ai4manufacturing-218-laser-weld/
├── images/{train,val,test}/    # dataset YOLO principal convertido
└── labels/{train,val,test}/
```

Imagens, rótulos, cache e pesos não são versionados no Git.

## Avaliação e segurança

A validação e o teste final devem permanecer independentes e, idealmente, compostos por imagens reais não vistas. Não use versões aumentadas da mesma imagem em splits distintos. Relate mAP50, mAP50-95, precisão, recall e matriz de confusão por classe. A classe genérica `defect` não deve ser renomeada como porosidade ou outra causa sem nova anotação.

Fotografias convencionais não comprovam sobrecarga elétrica, vibração ou desvio térmico interno. Essas condições requerem sensores, termografia ou dados sincronizados. O modelo é experimental e não deve comandar máquinas; decisões operacionais exigem supervisão e validação humanas.

## Referências

- https://huggingface.co/datasets/rikkarth/welding-defect-object-detection
- https://huggingface.co/datasets/AI4Manufacturing/217
- https://huggingface.co/datasets/AI4Manufacturing/218
- https://github.com/SylvioBlock/LoHi-Weld
- https://huggingface.co/datasets/IntelLabs/Intel_Robotic_Welding_Multimodal_Dataset


### Fontes adicionais de grande volume (acesso restrito)

O catálogo também tenta baixar, respeitando o teto total, duas fontes maiores. Elas exigem login e aprovação/aceitação manual no Hugging Face; o instalador não tenta contornar o gate e continua com as fontes públicas se o acesso ainda não estiver liberado:

- [AI4Manufacturing/105 — TIG Stainless Steel 304](https://huggingface.co/datasets/AI4Manufacturing/105): cerca de 9,93 GB, 45.058 quadros de 58 execuções TIG e seis rótulos em nível de execução. Licença upstream CC BY-SA 4.0; splits devem permanecer por execução, nunca por quadro.
- [AI4Manufacturing/219 — BAM hot-cracking metallography](https://huggingface.co/datasets/AI4Manufacturing/219): cerca de 11,6 GB, 609 imagens microscópicas de seções de solda. Licença upstream CC BY 4.0; separar por corpo de prova.

Para habilitar: abra cada página, entre na conta Hugging Face, solicite/aceite as condições e aguarde aprovação. Depois execute novamente `python src/setup_yolo.py`. Se não houver acesso, o instalador registra o item como ignorado e continua. O manifesto indica status e tamanho. Esses conjuntos são auxiliares e não são convertidos para YOLO automaticamente.

O catálogo conhecido soma aproximadamente 22,8 GB se todos os cinco conjuntos forem acessíveis, abaixo do limite padrão de 25 GB. O limite real é recalculado a cada execução usando os tamanhos informados pelo Hub. Não incluí o MIAD (32,3 GB), pois sozinho excede o teto; nem conjuntos com licença/condições incompatíveis ou duplicatas.
