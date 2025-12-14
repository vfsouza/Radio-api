# Guia de Deploy com Docker

Este projeto agora usa Docker para deployment, garantindo compatibilidade total com todas as dependências, incluindo OpenCV e YOLO/Ultralytics.

## Arquivos Docker

- `Dockerfile` - Imagem de produção com todas as dependências do sistema
- `docker-compose.yml` - Configuração para desenvolvimento local
- `.dockerignore` - Arquivos excluídos do build Docker

## Desenvolvimento Local

### Pré-requisitos

- Docker Desktop instalado
- Docker Compose (incluído no Docker Desktop)

### Iniciar o projeto

```bash
# Construir e iniciar o container
docker-compose up --build

# Ou em background
docker-compose up -d --build
```

O servidor estará disponível em `http://localhost:8000`

### Comandos úteis

```bash
# Ver logs
docker-compose logs -f web

# Executar comandos Django
docker-compose exec web python manage.py shell

# Parar o container
docker-compose down
```

## Deploy no Railway com Docker

### 1. Preparar o repositório

Certifique-se de que os arquivos Docker estão commitados:

```bash
git add Dockerfile docker-compose.yml .dockerignore
git commit -m "Add Docker configuration"
git push
```

### 2. Configurar o Railway

1. No Railway, vá em **Settings → Deploy**
2. Em **Build Settings**, configure:
   - **Builder**: Docker
   - **Dockerfile Path**: `Dockerfile`

### 3. Configurar variáveis de ambiente

No Railway, em **Variables**, adicione:

```env
SECRET_KEY=<gere-uma-chave-secreta-forte>
DEBUG=False
ALLOWED_HOSTS=*
CORS_ALLOW_ALL_ORIGINS=True
```

**Nota**: A configuração acima permite todas as origins no CORS (útil para desenvolvimento e APIs públicas). Para produção com restrições, você pode configurar:
```env
CORS_ALLOW_ALL_ORIGINS=False
CORS_ALLOWED_ORIGINS=https://seu-frontend.com,https://outro-dominio.com
CSRF_TRUSTED_ORIGINS=https://seu-app.railway.app
```

Gerar SECRET_KEY:
```bash
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

### 4. Deploy

O Railway fará deploy automaticamente após o push. O Dockerfile já está configurado para:
- ✓ Instalar todas as dependências do sistema (OpenCV, etc.)
- ✓ Executar migrations automaticamente
- ✓ Coletar arquivos estáticos
- ✓ Iniciar o servidor Gunicorn

## Deploy em Outras Plataformas

### Google Cloud Run

```bash
# Build e push da imagem
gcloud builds submit --tag gcr.io/PROJECT-ID/radio-api

# Deploy
gcloud run deploy radio-api \
  --image gcr.io/PROJECT-ID/radio-api \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### AWS ECS / Fargate

1. Crie um repositório ECR:
```bash
aws ecr create-repository --repository-name radio-api
```

2. Build e push:
```bash
# Login no ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

# Build
docker build -t radio-api .

# Tag e push
docker tag radio-api:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/radio-api:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/radio-api:latest
```

3. Configure ECS/Fargate pela console AWS

### Heroku

```bash
# Login no Heroku Container Registry
heroku container:login

# Build e push
heroku container:push web -a seu-app

# Release
heroku container:release web -a seu-app
```

## Dependências do Sistema

O Dockerfile instala automaticamente:

- **OpenCV**: `libgl1`, `libglib2.0-0`, `libgomp1`, `libsm6`, `libxext6`, `libxrender1`
- **Build tools**: `gcc`, `g++`

Isso resolve o erro `libGL.so.1: cannot open shared object file`.

## Otimizações de Produção

### Multi-stage build (opcional)

Para reduzir o tamanho da imagem, você pode usar multi-stage build:

```dockerfile
# Build stage
FROM python:3.12-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Runtime stage
FROM python:3.12-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
# ... resto da configuração
```

### Configuração do Gunicorn

Ajuste workers no Dockerfile baseado na CPU:
```dockerfile
CMD gunicorn Radio.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 4 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -
```

## Troubleshooting

### Erro: "libGL.so.1: cannot open shared object file"
✓ Resolvido pelo Dockerfile com instalação de `libgl1` e dependências

### Container não inicia
```bash
# Ver logs detalhados
docker logs <container-id>

# Entrar no container
docker exec -it <container-id> /bin/bash
```

### Migrations não executam
```bash
# Executar manualmente
docker-compose exec web python manage.py migrate

# Ou no Railway
railway run python manage.py migrate
```

## Monitoramento

### Health Check

Adicione um endpoint de health check no Django:

```python
# api/views.py
from django.http import JsonResponse

def health_check(request):
    return JsonResponse({"status": "healthy"}, status=200)
```

### Logs

```bash
# Docker Compose
docker-compose logs -f

# Railway
railway logs

# Cloud Run
gcloud logging read "resource.type=cloud_run_revision"
```

## Segurança

1. **Nunca commite** `.env` ou secrets
2. Use **variables de ambiente** para configuração
3. Mantenha `DEBUG=False` em produção
4. Configure **ALLOWED_HOSTS** e **CSRF_TRUSTED_ORIGINS**
5. Use **HTTPS** (Railway fornece automaticamente)

## Recursos

- Docker: https://docs.docker.com
- Docker Compose: https://docs.docker.com/compose
- Railway Docker Deploy: https://docs.railway.app/deploy/dockerfiles
- Django Deployment: https://docs.djangoproject.com/en/stable/howto/deployment

---

Seu projeto agora está configurado para deploy com Docker em qualquer plataforma!