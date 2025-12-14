# Guia de Deploy no Railway

## Preparação Concluída ✓

Seu projeto Django já está preparado para deploy no Railway com os seguintes arquivos:

- `requirements.txt` - Dependências do projeto
- `Procfile` - Comando para iniciar o servidor
- `railway.json` - Configurações do Railway
- `runtime.txt` - Versão do Python
- `.env.example` - Exemplo de variáveis de ambiente
- `.gitignore` - Arquivos a serem ignorados no Git
- `Radio/settings.py` - Atualizado com configurações de produção

## Passos para Deploy

### 1. Criar conta no Railway
- Acesse https://railway.app
- Faça login com GitHub, GitLab ou email

### 2. Criar repositório Git (se ainda não tiver)
```bash
git init
git add .
git commit -m "Configuração inicial para deploy no Railway"
```

### 3. Fazer push para GitHub/GitLab
```bash
# Criar repositório no GitHub e depois:
git remote add origin https://github.com/seu-usuario/seu-repo.git
git branch -M main
git push -u origin main
```

### 4. Criar projeto no Railway

1. No dashboard do Railway, clique em **"New Project"**
2. Selecione **"Deploy from GitHub repo"**
3. Escolha o repositório do seu projeto
4. O Railway detectará automaticamente que é um projeto Python/Django

### 5. Adicionar PostgreSQL ao projeto

1. No projeto Railway, clique em **"+ New"**
2. Selecione **"Database" → "Add PostgreSQL"**
3. O Railway criará automaticamente a variável `DATABASE_URL`

### 6. Configurar variáveis de ambiente

No Railway, vá em **Variables** e adicione:

```
SECRET_KEY=gere-uma-chave-secreta-forte-aqui
DEBUG=False
ALLOWED_HOSTS=.railway.app
CSRF_TRUSTED_ORIGINS=https://seu-app.railway.app
CORS_ALLOWED_ORIGINS=https://seu-frontend.com,http://localhost:3000
```

**Importante:** Para gerar um SECRET_KEY seguro, use:
```python
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

### 7. Deploy inicial

O Railway fará o deploy automaticamente após configurar as variáveis.

### 8. Executar migrações

Após o primeiro deploy, você precisa executar as migrações:

1. No Railway, abra o **terminal** do seu serviço
2. Execute:
```bash
python manage.py migrate
python manage.py createsuperuser  # Opcional: criar superusuário
```

Ou configure um script de deploy no `Procfile`:
```
release: python manage.py migrate
web: gunicorn Radio.wsgi --log-file -
```

### 9. Acessar sua aplicação

Após o deploy, o Railway fornecerá uma URL como:
```
https://seu-app.up.railway.app
```

### 10. Coletar arquivos estáticos (se necessário)

Se você tiver arquivos estáticos para servir:
```bash
python manage.py collectstatic --noinput
```

## Configurações Importantes

### CORS para Frontend
Se você tiver um frontend separado, adicione o domínio nas variáveis de ambiente:

```
CORS_ALLOWED_ORIGINS=https://seu-frontend.vercel.app,https://seu-frontend.netlify.app
CSRF_TRUSTED_ORIGINS=https://seu-app.railway.app,https://seu-frontend.vercel.app
```

### Logs e Monitoramento
- Acesse os logs em tempo real pelo dashboard do Railway
- Configure alertas para monitorar a saúde da aplicação

### Domínio Customizado (Opcional)
1. Vá em **Settings → Domains**
2. Adicione seu domínio personalizado
3. Configure os registros DNS conforme instruções do Railway

## Comandos Úteis

### Fazer redeploy após mudanças
```bash
git add .
git commit -m "Descrição das mudanças"
git push
```

O Railway fará redeploy automaticamente.

### Executar comandos Django no Railway
Use o terminal do Railway para executar comandos como:
```bash
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py shell
```

## Troubleshooting

### Erro: "Application failed to respond"
- Verifique se `gunicorn` está instalado no `requirements.txt`
- Verifique se o `Procfile` está correto
- Verifique os logs no Railway

### Erro: "Bad Request (400)"
- Adicione o domínio do Railway em `ALLOWED_HOSTS`
- Adicione em `CSRF_TRUSTED_ORIGINS`

### Erro de banco de dados
- Verifique se a variável `DATABASE_URL` está configurada
- Execute as migrações: `python manage.py migrate`

### Arquivos estáticos não carregam
- Verifique se `whitenoise` está instalado
- Execute `python manage.py collectstatic`
- Verifique `STATIC_ROOT` e `STATIC_URL` no settings.py

## Recursos Adicionais

- Documentação Railway: https://docs.railway.app
- Documentação Django Deploy: https://docs.djangoproject.com/en/6.0/howto/deployment/
- Suporte Railway: https://help.railway.app

## Notas Importantes

1. **Nunca comite o arquivo `.env`** - Use sempre `.env.example` como template
2. **Use sempre HTTPS em produção** - Railway fornece SSL automaticamente
3. **Configure DEBUG=False em produção** - Nunca deixe DEBUG=True
4. **Monitore os logs regularmente** - Para identificar problemas rapidamente
5. **Faça backup do banco de dados** - Railway oferece backups automáticos no plano pago

---

Seu projeto está pronto para deploy! Se tiver alguma dúvida, consulte a documentação do Railway ou abra uma issue no repositório.
