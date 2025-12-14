"""
Script para organizar o dataset FracAtlas no formato YOLO
Divide automaticamente em train/val/test e organiza as pastas
"""

import os
import shutil
from pathlib import Path
import random
import yaml


def prepare_fracatlas_dataset(
    source_dir="FracAtlas/FracAtlas",
    output_dir="fracatlas_training/datasets/fracatlas",
    train_ratio=0.7,
    val_ratio=0.2,
    test_ratio=0.1
):
    """
    Organiza o dataset FracAtlas para treinamento YOLO

    Args:
        source_dir: Diretório do FracAtlas original
        output_dir: Diretório de saída organizado
        train_ratio: Proporção para treino (0.7 = 70%)
        val_ratio: Proporção para validação (0.2 = 20%)
        test_ratio: Proporção para teste (0.1 = 10%)
    """
    print("="*60)
    print("🦴 PREPARANDO DATASET FRACATLAS PARA YOLO11")
    print("="*60)

    source = Path(source_dir)
    output = Path(output_dir)

    # Verificar se o source existe
    if not source.exists():
        print(f"❌ Erro: Diretório {source} não encontrado!")
        print("   Certifique-se de que a pasta FracAtlas está na raiz do projeto")
        return

    # Criar estrutura de diretórios
    print("\n📁 Criando estrutura de diretórios...")
    for split in ['train', 'val', 'test']:
        (output / 'images' / split).mkdir(parents=True, exist_ok=True)
        (output / 'labels' / split).mkdir(parents=True, exist_ok=True)

    # Coletar todas as imagens
    print("\n📋 Coletando imagens...")
    fractured_imgs = list((source / 'images' / 'Fractured').glob('*.jpg'))
    non_fractured_imgs = list((source / 'images' / 'Non_fractured').glob('*.jpg'))

    all_images = fractured_imgs + non_fractured_imgs
    print(f"   Total de imagens: {len(all_images)}")
    print(f"   - Com fratura: {len(fractured_imgs)}")
    print(f"   - Sem fratura: {len(non_fractured_imgs)}")

    # Embaralhar
    random.seed(42)  # Para reprodutibilidade
    random.shuffle(all_images)

    # Calcular splits
    total = len(all_images)
    train_size = int(total * train_ratio)
    val_size = int(total * val_ratio)

    train_images = all_images[:train_size]
    val_images = all_images[train_size:train_size + val_size]
    test_images = all_images[train_size + val_size:]

    print(f"\n📊 Divisão do dataset:")
    print(f"   Treino: {len(train_images)} imagens ({train_ratio*100:.0f}%)")
    print(f"   Validação: {len(val_images)} imagens ({val_ratio*100:.0f}%)")
    print(f"   Teste: {len(test_images)} imagens ({test_ratio*100:.0f}%)")

    # Função para copiar imagens e labels
    def copy_files(image_list, split_name):
        """Copia imagens e seus labels correspondentes"""
        print(f"\n📦 Copiando arquivos para {split_name}...")
        copied = 0
        no_label = 0

        for img_path in image_list:
            # Copiar imagem
            img_dest = output / 'images' / split_name / img_path.name
            shutil.copy2(img_path, img_dest)

            # Copiar label
            label_name = img_path.stem + '.txt'
            label_src = source / 'Annotations' / 'YOLO' / label_name

            if label_src.exists():
                label_dest = output / 'labels' / split_name / label_name
                shutil.copy2(label_src, label_dest)
                copied += 1
            else:
                # Se não tem label, criar arquivo vazio (sem fraturas)
                label_dest = output / 'labels' / split_name / label_name
                label_dest.touch()
                no_label += 1

        print(f"   ✅ {copied} imagens com anotações")
        print(f"   📄 {no_label} imagens sem fraturas (labels vazios)")

    # Copiar arquivos para cada split
    copy_files(train_images, 'train')
    copy_files(val_images, 'val')
    copy_files(test_images, 'test')

    # Criar arquivo YAML de configuração
    print("\n📝 Criando arquivo de configuração...")
    yaml_content = {
        'path': str(output.absolute()),
        'train': 'images/train',
        'val': 'images/val',
        'test': 'images/test',
        'names': {
            0: 'fracture'
        },
        'nc': 1
    }

    yaml_path = output / 'data.yaml'
    with open(yaml_path, 'w') as f:
        yaml.dump(yaml_content, f, default_flow_style=False, sort_keys=False)

    print(f"   ✅ Configuração salva em: {yaml_path}")

    # Mostrar estatísticas finais
    print("\n" + "="*60)
    print("✅ DATASET PREPARADO COM SUCESSO!")
    print("="*60)
    print(f"\n📁 Estrutura criada em: {output}")
    print(f"\n📊 Estatísticas:")
    print(f"   Total: {total} imagens")
    print(f"   Train: {len(train_images)} imagens")
    print(f"   Val: {len(val_images)} imagens")
    print(f"   Test: {len(test_images)} imagens")

    print(f"\n🚀 Próximo passo:")
    print(f"   python train_fracatlas.py")
    print(f"\n   Ou use o caminho do YAML:")
    print(f"   {yaml_path}")

    return str(yaml_path)


def verify_dataset(dataset_dir="fracatlas_training/datasets/fracatlas"):
    """
    Verifica a integridade do dataset preparado
    """
    print("\n🔍 Verificando dataset...")
    dataset = Path(dataset_dir)

    for split in ['train', 'val', 'test']:
        img_dir = dataset / 'images' / split
        lbl_dir = dataset / 'labels' / split

        imgs = list(img_dir.glob('*.jpg'))
        lbls = list(lbl_dir.glob('*.txt'))

        print(f"\n   {split.upper()}:")
        print(f"      Imagens: {len(imgs)}")
        print(f"      Labels: {len(lbls)}")

        if len(imgs) != len(lbls):
            print(f"      ⚠️ Aviso: Número de imagens e labels não coincidem!")

    # Verificar arquivo YAML
    yaml_path = dataset / 'data.yaml'
    if yaml_path.exists():
        print(f"\n   ✅ Arquivo YAML encontrado: {yaml_path}")
    else:
        print(f"\n   ❌ Arquivo YAML não encontrado!")


if __name__ == "__main__":
    # Preparar dataset
    yaml_path = prepare_fracatlas_dataset()

    # Verificar
    verify_dataset()

    print("\n" + "="*60)
    print("🎯 TUDO PRONTO PARA O TREINAMENTO!")
    print("="*60)