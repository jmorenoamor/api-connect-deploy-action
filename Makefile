build:
	@docker build -t jmorenoamor/api-connect-deploy-action:latest .

test:
	@docker run --rm jmorenoamor/api-connect-deploy-action

ghtest:
	@docker run --rm -e INPUT_PRODUCTFILE -e INPUT_CATALOG -e INPUT_ORGANIZATION -e INPUT_MANAGERHOST -e INPUT_MANAGERUSERNAME -e INPUT_MANAGERPASSWORD -e INPUT_MANAGERREALM -e INPUT_SPACE jmorenoamor/api-connect-deploy-action
