.PHONY: pop db

migrations:
	rm -r image_eval/migrations
	python manage.py makemigrations image_eval

pop: db
	python manage.py shell -c "from image_eval.tests.populate import populate; populate();"

db:
	rm -rf var/*
	python manage.py migrate
