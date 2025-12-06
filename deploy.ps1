$server = "root@77.73.232.142"
$target = "/root/referal"

Write-Host "=== Syncing project with $server ==="
# Create archive (exclude venv and __pycache__)
tar -czf deploy.tar.gz --exclude="venv" --exclude="__pycache__" --exclude="data" *

# Copy archive to server
scp deploy.tar.gz "${server}:${target}/"

# Extract on server and remove archive
ssh $server "cd $target && tar -xzf deploy.tar.gz && rm deploy.tar.gz"

Write-Host "=== Restarting container on server ==="
ssh $server "cd $target && docker-compose down && docker rm referal -f && docker-compose up -d --build"

Write-Host "=== Deploy finished successfully ==="
