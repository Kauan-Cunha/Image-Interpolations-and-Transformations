# Utilitário de Processamento de Imagens (CLI)

Este é um programa de linha de comando (CLI) para realizar operações de processamento de imagens, dividido em duas funcionalidades principais: **Transformações Geométricas** (rotação e escala) e **Criação de Panoramas** (registro de imagens).

## 📁 Estrutura de Diretórios Obrigatória

Para que o programa encontre e salve os arquivos corretamente, certifique-se de que a estrutura de pastas esteja assim:

    meu_projeto/
    ├── main.py
    ├── src.py
    ├── imgs/            <-- Coloque todas as suas imagens de ENTRADA aqui
    └── img_results/     <-- O programa salvará os RESULTADOS aqui

## ⚙️ Dependências

Certifique-se de ter o Python 3 instalado, junto com as seguintes bibliotecas:
    
    pip install numpy matplotlib opencv-python argparse

---

## 🚀 Como Usar

O programa possui dois subcomandos principais: `transform` e `panorama`. Você pode acessar o menu de ajuda geral a qualquer momento com:
    
    python main.py --help

### 1. Transformações Geométricas (`transform`)
Aplica operações de escala (zoom) ou rotação em uma única imagem. *Nota: não é possível aplicar escala e rotação no mesmo comando.*

**Sintaxe Básica:**
    
    python main.py transform -i <imagem.jpg> [OPÇÕES]

**Opções Disponíveis:**
* `-i`, `--input` (Obrigatório): Nome da imagem de entrada (deve estar na pasta `imgs/`).
* `-a`, `--angle`: Ângulo de rotação em radianos (ex: `0.5`).
* `-e`, `--scale`: Fator de escala (ex: `2.0` para dobrar o tamanho).
* `-m`, `--interpolation`: Algoritmo de interpolação. Opções: `cni`, `lagrange`, `bilinear`, `bicubic` (Padrão: `bilinear`).
* `-o`, `--output`: Nome personalizado para salvar o arquivo de saída.
* `-s`, `--show`: Abre uma janela para exibir o resultado na tela.

**Exemplos:**
Rotacionar uma imagem em 0.5 radianos usando interpolação bicúbica:
    
    python main.py transform -i foto.jpg -a 0.5 -m bicubic

Reduzir a imagem pela metade (escala 0.5) usando o vizinho mais próximo e mostrar na tela:
    
    python main.py transform -i foto.jpg -e 0.5 -m cni -s

---

### 2. Criação de Panorama (`panorama`)
Analisa duas imagens, encontra pontos em comum entre elas e as costura para formar uma imagem panorâmica.

**Sintaxe Básica:**
    
    python main.py panorama -i1 <imagem_esquerda.jpg> -i2 <imagem_direita.jpg> [OPÇÕES]

**Opções Disponíveis:**
* `-i1`, `--imagem1` (Obrigatório): Primeira imagem.
* `-i2`, `--imagem2` (Obrigatório): Segunda imagem.
* `-d`, `--detector`: Algoritmo detector de características. Opções: `sift` ou `orb` (Padrão: `sift`).
* `-t`, `--threshold`: Limiar do teste de Lowe (entre 0.0 e 1.0) para filtrar pontos errados. Valores menores são mais rigorosos (Padrão: `0.75`).
* `-o`, `--output`: Nome final do arquivo panorâmico (Padrão: `panorama_out.jpg`).
* `-s`, `--show-matches`: Abre uma janela mostrando as linhas que conectam os pontos em comum encontrados nas duas imagens.

**Exemplos:**
Criar um panorama simples (usando configurações padrão):
    
    python main.py panorama -i1 foto1.jpg -i2 foto2.jpg

Criar um panorama usando o detector ORB, filtro rigoroso (0.7), visualizando os matches na tela:
    
    python main.py panorama -i1 foto1.jpg -i2 foto2.jpg -d orb -t 0.7 -s
