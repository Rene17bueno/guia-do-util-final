@echo off
git add .
git commit -m "Auto commit: %date% %time%"
git push origin main
echo Projeto atualizado com sucesso no GitHub!
pause