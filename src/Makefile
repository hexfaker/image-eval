
.PHONY: pop db

pop: db
	python manage.py shell -c "from image_eval.tests.populate import populate; populate();"

db:
	rm -rf var/*
	python manage.py migrate
