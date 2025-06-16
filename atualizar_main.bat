@echo off
REM --- entra na pasta do projeto ---
cd /d X:\Repos\appformiguinhasv2 || (
  echo ERRO: nao foi possivel entrar na pasta X:\Repos\appformiguinhasv2
  pause
  exit /b 1
)

echo Sincronizando com a branch main do GitHub...

REM atualiza referências, removendo branches deletadas
git fetch --prune origin

REM garante que estamos na main
git checkout main

REM descarta tudo e alinha com o remoto
git reset --hard origin/main

echo Atualização concluída!
pause
