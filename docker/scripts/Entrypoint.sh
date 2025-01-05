echo 'Running Migrations'
#alembic current || alembic stamp head
alembic upgrade head



echo 'Running Server'
python src/main.py