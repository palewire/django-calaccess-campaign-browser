
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

sh:
	python example/manage.py shell_plus

test:
	clear
	pep8 --exclude='*/migrations' calaccess_campaign_browser
	pyflakes calaccess_campaign_browser
	coverage run setup.py test
	coverage report -m

downloaddb:
	echo "Downloading database archive"
	curl -O https://dl.dropboxusercontent.com/u/3640647/nicar15/ccdc.sql.gz
	echo "Creating local database named 'calaccess'"
	mysqladmin -h localhost -u root -p create calaccess
	echo "Installing database archive to local database"
	gunzip < ccdc.sql.gz | mysql calaccess -u root -p
	echo "Deleting database archive"
	rm ccdc.sql.gz
	echo "Success!"
