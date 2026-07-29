# PowerShell скрипт для создания репозитория и деплоя на Railway
# Запусти от имени администратора

$repoName = "freelance-monitor-bot"
$githubUser = "sashacvitko1977"

Write-Host "Создаём новый проект на Railway..." -ForegroundColor Green

# 1. Инициализируем git
git init
git branch -M main

# 2. Добавляем файлы
git add .
git commit -m "Initial commit - Freelance.ru Monitor Bot"

# 3. Заливаем на GitHub
git remote add origin "https://github.com/$githubUser/$repoName.git"
git push -u origin main

Write-Host "Проект залит на GitHub!" -ForegroundColor Green
Write-Host "Теперь перейди на Railway и подключи этот репозиторий" -ForegroundColor Green
Write-Host "или просто нажми Deploy" -ForegroundColor Green