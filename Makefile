build:
	@docker build -t jmorenoamor/api-connect-deploy-action:latest .

test:
	@docker run --rm jmorenoamor/api-connect-deploy-action
