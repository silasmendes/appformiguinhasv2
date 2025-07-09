#!/bin/bash

# Configurações
APP_NAME="appformiguinhas"
RESOURCE_GROUP="rgformiguinhasbr"
ACR_NAME="crssm01docker"
IMAGE_NAME="${APP_NAME}:latest"
ACR_IMAGE="${ACR_NAME}.azurecr.io/${IMAGE_NAME}"
WEBAPP_NAME="appformiguinhasweb"

echo "🚧 Iniciando build da imagem..."
docker build -t $APP_NAME .

echo "🏷️  Tagueando imagem para o ACR..."
docker tag $APP_NAME $ACR_IMAGE

echo "🚀 Enviando imagem para o ACR..."
docker push $ACR_IMAGE

echo "🔄 Reiniciando o App Service..."
az webapp restart --name $WEBAPP_NAME --resource-group $RESOURCE_GROUP

echo "✅ Deploy concluído com sucesso!"
