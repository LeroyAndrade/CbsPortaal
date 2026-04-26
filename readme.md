# Eerste keer setup (EENMALIG)

> python3.14 -m venv macenv
>
> source macenv/bin/activate
> 
> pip install -r requirements.txt

> docker compose up --build -d

# Migraties eerste keer
> docker compose exec app flask db init
> 
> docker compose exec app flask db migrate -m "initial migration"
> 
> docker compose exec app flask db upgrade

# NORMAAL STARTEN
> docker compose up -d

# HERSTART
> docker compose restart app

# REBUILD (als je requirements of Dockerfile aanpast)

> docker compose build --no-cache
> docker compose up -d

# MIGRATIES (tijdens ontwikkeling)
> docker compose exec app flask db migrate -m "jouw bericht"
docker compose exec app flask db upgrade
docker compose restart app


# FULL RESET (alles weg, begin opnieuw)
> docker compose down -v
> 
> docker compose up --build -d

# LOGS
> docker compose logs -f app

# STOP
> docker compose down

# HANDIG OP MAC (na Python upgrade)

> deactivate
> 
> rm -rf macenv
> 
> /Library/Frameworks/Python.framework/Versions/3.14/bin/python3.14 -m venv macenv
> 
> source macenv/bin/activate
> 
> pip install -r requirements.txt

# KILL PORT 5002
> sudo kill -9 $(lsof -t -i:5002) 2>/dev/null || echo "Geen proces op poort 5002"

# MySQL
> docker exec -it cbs_portal_db psql -U cbs -d cbs_portal

# Push feature, in diezelfde featurebranch
> git push origin naamVanFeature

# Haal die feature op
> git fetch origin
> git checkout feature_cbs-data-opslag