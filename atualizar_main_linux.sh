#!/bin/bash

# Caminho do projeto
PROJECT_DIR="$HOME/repos/appformiguinhasv2"

# Entra na pasta do projeto
cd "$PROJECT_DIR" || {
  echo "❌ ERRO: não foi possível entrar na pasta $PROJECT_DIR"
  exit 1
}

echo "🔄 Sincronizando com a branch main do GitHub..."

# Atualiza referências, removendo branches deletadas
git fetch --prune origin

# Garante que estamos na main
git checkout main

# Descarta tudo e alinha com o remoto
git reset --hard origin/main

echo "✅ Atualização concluída!"
