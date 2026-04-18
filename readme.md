# 1. naar je project gaan
cd ~/Documents/code/Python/cbsPortaal

# 2. containers starten (eerste keer of na wijzigingen)
docker compose up --build -d

# 3. checken of alles draait
docker ps

# 4. logs bekijken 
docker compose logs -f

# 5. end
docker compose down