param(
  [string]$ComposeFile = "docker-compose.yml"
)

docker compose -f $ComposeFile up --build
