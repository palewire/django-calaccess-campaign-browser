.PHONY: bootstrap docs load runserver shell test

bootstrap:
	mysqladmin -h localhost -u root -pmysql drop campaign_finance
	mysqladmin -h localhost -u root -pmysql create campaign_finance
	python example/manage.py syncdb
	python example/manage.py build_campaign_finance
	python example/manage.py collectstatic --noinput
	python example/manage.py runserver

docs:
	cd docs && make livehtml

load:
	clear
	python example/manage.py loadcalaccesscampaignsummaries

runserver:
	python example/manage.py runserver

shell:
	python example/manage.py shell

test:
	pep8 campaign_finance
	pyflakes campaign_finance
	coverage run setup.py test
	coverage report -m
