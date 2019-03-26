.PHONY: pop db

migrations:
	rm -r image_eval/migrations
	python3 manage.py makemigrations image_eval

pop: db
	python3 manage.py shell -c "from image_eval.tests.populate import populate; populate();"

db:
#	rm -rf ${VAR_DIR:-var}/*
	python3 manage.py migrate

static:
	python3 manage.py collectstatic
