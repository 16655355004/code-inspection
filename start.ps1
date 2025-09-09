Start-Process -NoNewWindow -FilePath "python" -ArgumentList "backend/main.py"
Start-Process -NoNewWindow -FilePath "npm" -ArgumentList "run dev" -WorkingDirectory "frontend" 