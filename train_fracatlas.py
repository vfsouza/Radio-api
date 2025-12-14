"""
Script para treinar modelo YOLO11 com o dataset FracAtlas
FracAtlas: Dataset de detecção de fraturas ósseas em raios-X

Requisitos:
    pip install ultralytics roboflow
"""

import os
from pathlib import Path

from ultralytics import YOLO
import yaml
import torch


class FracAtlasTrainer:
    def __init__(self, project_dir="training"):
        """
        Inicializa o trainer do YOLO11 para FracAtlas

        Args:
            project_dir: Diretório onde os resultados serão salvos
        """
        self.project_dir = Path(project_dir)
        self.project_dir.mkdir(exist_ok=True)

        self.models_dir = self.project_dir / "models"
        self.models_dir.mkdir(exist_ok=True)

        self.dataset_dir = self.project_dir / "datasets"
        self.dataset_dir.mkdir(exist_ok=True)

    def create_dataset_yaml(self, dataset_path):
        """
        Cria arquivo de configuração YAML para o dataset
        """
        yaml_content = {
            'path': str(Path(dataset_path).absolute()),
            'train': 'images/train',
            'val': 'images/val',
            'test': 'images/test',
            'names': {
                0: 'fracture',  # Classe principal: fratura
            },
            'nc': 1  # Número de classes
        }

        yaml_path = self.dataset_dir / "fracatlas.yaml"
        with open(yaml_path, 'w') as f:
            yaml.dump(yaml_content, f, default_flow_style=False)

        print(f"✅ Arquivo de configuração criado: {yaml_path}")
        return str(yaml_path)

    def train_model(self, data_yaml, model_size='m', epochs=100, img_size=640, batch_size=32):
        """
        Treina o modelo YOLO11

        Args:
            data_yaml: Caminho para o arquivo YAML do dataset
            model_size: Tamanho do modelo ('n', 's', 'm', 'l', 'x')
            epochs: Número de épocas de treinamento
            img_size: Tamanho da imagem
            batch_size: Tamanho do batch
        """
        print(f"\n🚀 Iniciando treinamento YOLO11{model_size}...")
        print(f"   Épocas: {epochs}")
        print(f"   Tamanho da imagem: {img_size}")
        print(f"   Batch size: {batch_size}")

        # Carrega modelo pré-treinado
        model = YOLO(f'yolo11{model_size}.pt')

        # Treina o modelo
        results = model.train(
            data=data_yaml,
            epochs=epochs,
            imgsz=img_size,
            batch=batch_size,
            name=f'fracatlas_yolo11{model_size}',
            project=str(self.project_dir),
            patience=50,
            save=True,
            plots=True,
            device=0,
            lr0=0.01,
            lrf=0.01,
            momentum=0.937,
            weight_decay=0.0005,
            warmup_epochs=3.0,
            warmup_momentum=0.8,
            box=7.5,
            cls=0.5,
            augment=True,
        )

        return model, results

    def save_model(self, model, model_name="fracatlas_best.pt"):
        """
        Salva o modelo treinado
        """
        save_path = self.models_dir / model_name
        model.export(format='pt')  # Exporta para PyTorch

        # Copia o melhor modelo
        best_model_path = self.project_dir / f"fracatlas_yolo11m" / "weights" / "best.pt"
        if best_model_path.exists():
            import shutil
            shutil.copy(best_model_path, save_path)
            print(f"\n✅ Modelo salvo em: {save_path}")

        return str(save_path)

    def evaluate_model(self, model, data_yaml):
        """
        Avalia o modelo no conjunto de validação
        """
        print("\n📊 Avaliando modelo...")
        metrics = model.val(data=data_yaml)

        print(f"\n📈 Resultados:")
        print(f"   mAP50: {metrics.box.map50:.3f}")
        print(f"   mAP50-95: {metrics.box.map:.3f}")
        print(f"   Precisão: {metrics.box.mp:.3f}")
        print(f"   Recall: {metrics.box.mr:.3f}")

        return metrics

    def test_model(self, model_path, test_image):
        """
        Testa o modelo com uma imagem
        """
        print(f"\n🔍 Testando modelo com: {test_image}")
        model = YOLO(model_path)

        results = model(test_image)

        for result in results:
            boxes = result.boxes
            print(f"\n   Detecções encontradas: {len(boxes)}")
            for i, box in enumerate(boxes):
                print(f"   Detecção {i+1}:")
                print(f"      Confiança: {box.conf[0]:.3f}")
                print(f"      BBox: {box.xyxy[0].tolist()}")

        # Salva resultado
        result_path = self.project_dir / "test_result.jpg"
        results[0].save(str(result_path))
        print(f"\n   Resultado salvo em: {result_path}")

        return results


def main():
    """
    Função principal para executar o treinamento
    """
    print("="*60)
    print("🦴 YOLO11 - Treinamento FracAtlas (Detecção de Fraturas)")
    print("="*60)

    # Inicializa trainer
    trainer = FracAtlasTrainer(project_dir="fracatlas_training")

    # Configurações de treinamento
    config = {
        'model_size': 's',      # 'n' (nano), 's' (small), 'm' (medium), 'l' (large), 'x' (xlarge)
        'epochs': 100,          # Número de épocas
        'img_size': 640,        # Tamanho da imagem
        'batch_size': 32,       # Ajuste baseado na sua memória
    }

    try:
        data_yaml = r'C:\Users\vinif\PycharmProjects\DjangoProject\fracatlas_training\datasets\fracatlas\data.yaml'

        # Passo 1: Treinar modelo
        print("\n" + "="*60)
        print("PASSO 3: Treinamento do Modelo")
        print("="*60)
        model, results = trainer.train_model(
            data_yaml= data_yaml,
            model_size=config['model_size'],
            epochs=config['epochs'],
            img_size=config['img_size'],
            batch_size=config['batch_size']
        )

        # Passo 2: Avaliar modelo
        print("\n" + "="*60)
        print("PASSO 4: Avaliação do Modelo")
        print("="*60)
        metrics = trainer.evaluate_model(model, data_yaml)

        # Passo 3: Salvar modelo
        print("\n" + "="*60)
        print("PASSO 5: Salvando Modelo")
        print("="*60)
        model_path = trainer.save_model(model, "fracatlas_best.pt")

        print("\n" + "="*60)
        print("✅ TREINAMENTO CONCLUÍDO COM SUCESSO!")
        print("="*60)
        print(f"\n📁 Modelo salvo em: {model_path}")
        print(f"📊 Resultados em: {trainer.project_dir}")
        print("\n💡 Para usar o modelo na API, atualize em api/views.py:")
        print(f"   model = YOLO('{model_path}')")

    except Exception as e:
        print(f"\n❌ Erro durante o treinamento: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()