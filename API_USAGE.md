# Django REST API - Documentação

API REST configurada para receber imagens e processá-las com YOLO11 (detecção de objetos).

## Configuração Inicial

### 1. Instalar YOLO11 (Opcional)
```bash
pip install ultralytics
```

### 2. Iniciar o Servidor
```bash
python manage.py runserver
```

O servidor estará disponível em: `http://localhost:8000`

## Endpoints Disponíveis

### 1. Health Check
**GET** `/api/health/`

Verifica se a API está funcionando e se o YOLO está instalado.

**Exemplo:**
```bash
curl http://localhost:8000/api/health/
```

**Resposta:**
```json
{
    "status": "healthy",
    "message": "API is running",
    "yolo_available": false
}
```

---

### 2. Detecção com YOLO
**POST** `/api/detect/`

Envia uma imagem para processamento com YOLO11.

**Parâmetros:**
- `image` (file, obrigatório): Arquivo de imagem
- `data` (string, opcional): Dados adicionais em JSON

**Exemplo com curl:**
```bash
curl -X POST http://localhost:8000/api/detect/ \
  -F "image=@caminho/para/imagem.jpg" \
  -F "data={\"parametro\": \"valor\"}"
```

**Exemplo com Python:**
```python
import requests

url = "http://localhost:8000/api/detect/"
files = {"image": open("imagem.jpg", "rb")}
data = {"data": '{"parametro": "valor"}'}

response = requests.post(url, files=files, data=data)
print(response.json())
```

**Resposta (com YOLO instalado):**
```json
{
    "success": true,
    "detections": [
        {
            "class": 0,
            "class_name": "person",
            "confidence": 0.95,
            "bbox": [100, 150, 300, 400]
        }
    ],
    "image_name": "imagem.jpg",
    "image_size": 52431,
    "additional_data": {"parametro": "valor"}
}
```

**Resposta (sem YOLO instalado):**
```json
{
    "success": true,
    "detections": [
        {
            "message": "YOLO not installed",
            "note": "Install with: pip install ultralytics",
            "mock_detection": true,
            "class_name": "example",
            "confidence": 0.95,
            "bbox": [100, 100, 200, 200]
        }
    ],
    "image_name": "imagem.jpg",
    "image_size": 52431,
    "additional_data": {}
}
```

---

### 3. Upload de Imagem (Teste)
**POST** `/api/upload/`

Endpoint de teste para verificar se o upload de imagens está funcionando.

**Parâmetros:**
- `image` (file, obrigatório): Arquivo de imagem
- `description` (string, opcional): Descrição da imagem
- `tags` (string, opcional): Tags da imagem

**Exemplo:**
```bash
curl -X POST http://localhost:8000/api/upload/ \
  -F "image=@caminho/para/imagem.jpg" \
  -F "description=Teste de upload" \
  -F "tags=teste,exemplo"
```

**Resposta:**
```json
{
    "success": true,
    "message": "Image received successfully",
    "image_name": "imagem.jpg",
    "image_size": 52431,
    "content_type": "image/jpeg",
    "description": "Teste de upload",
    "tags": "teste,exemplo"
}
```

---

## Exemplo de Uso com JavaScript/React

```javascript
const handleImageUpload = async (file) => {
    const formData = new FormData();
    formData.append('image', file);
    formData.append('data', JSON.stringify({
        source: 'webapp',
        timestamp: Date.now()
    }));

    try {
        const response = await fetch('http://localhost:8000/api/detect/', {
            method: 'POST',
            body: formData,
        });

        const result = await response.json();
        console.log('Detections:', result.detections);
    } catch (error) {
        console.error('Error:', error);
    }
};
```

## Configurações

### CORS
O CORS está configurado para aceitar requisições de:
- `http://localhost:3000` (React)
- `http://localhost:5173` (Vite)
- Qualquer origem (desenvolvimento)

Para produção, edite em `Radio/settings.py:137`:
```python
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = [
    "https://seu-dominio.com",
]
```

### Modelo YOLO
Por padrão, a API usa o modelo `yolo11n.pt` (nano). Você pode alterar em `api/views.py:56`:
```python
model = YOLO('yolo11s.pt')  # small
model = YOLO('yolo11m.pt')  # medium
model = YOLO('yolo11l.pt')  # large
model = YOLO('yolo11x.pt')  # extra large
```

## Estrutura do Projeto

```
DjangoProject/
├── Radio/
│   ├── settings.py      # Configurações do Django
│   └── urls.py          # URLs principais
├── api/
│   ├── views.py         # Lógica dos endpoints
│   ├── urls.py          # URLs da API
│   ├── models.py        # Sem modelos (API sem DB)
│   └── admin.py
├── manage.py
└── API_USAGE.md         # Este arquivo
```

## Notas

1. A API **não usa banco de dados** - processa e retorna dados diretamente
2. YOLO11 é opcional - a API retorna dados mock se não estiver instalado
3. Arquivos de imagem não são salvos - apenas processados em memória
4. Para uso em produção, configure `DEBUG = False` e adicione um domínio em `ALLOWED_HOSTS`