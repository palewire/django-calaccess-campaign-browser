.PHONY: bootstrap docs reload rs runserver shell test

bootstrap:
	mysqladmin -h localhost -u root -pmysql drop campaign_finance
	mysqladmin -h localhost -u root -pmysql create campaign_finance
	python example/manage.py syncdb
	python example/manage.py build_campaign_finance
	python example/manage.py collectstatic --noinput
	python example/manage.py runserver

docs:
	cd docs && make livehtml

reload:
	clear
	python example/manage.py dropcalaccesscampaignbrowser
	python example/manage.py migrate --noinput
	python example/manage.py loadcalaccesscampaignfilers

rs:
	python example/manage.py runserver

runserver:
	python example/manage.py runserver

shell:
	python example/manage.py shell

test:
	pep8 campaign_finance
	pyflakes campaign_finance
	coverage run setup.py test
	coverage report -m
