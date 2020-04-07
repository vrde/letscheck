.PHONY: help foo

.DEFAULT_GOAL := help


#############################
# Open a URL in the browser #
#############################
define BROWSER_PYSCRIPT
import os, webbrowser, sys
try:
	from urllib import pathname2url
except:
	from urllib.request import pathname2url

webbrowser.open("file://" + pathname2url(os.path.abspath(sys.argv[1])))
endef
export BROWSER_PYSCRIPT


##################################
# Display help for this makefile #
##################################
define PRINT_HELP_PYSCRIPT
import re, sys

print("LetsCheck developer toolbox")
print("---------------------------")
print("Usage: make COMMAND")
print("")
print("Commands:")
for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("    %-16s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

##################
# Basic commands #
##################
DOCKER := docker
DC := docker-compose
BROWSER := python -c "$$BROWSER_PYSCRIPT"
HELP := python -c "$$PRINT_HELP_PYSCRIPT"
ECHO := /usr/bin/env echo

IS_DOCKER_COMPOSE_INSTALLED := $(shell command -v docker-compose 2> /dev/null)

################
# Main targets #
################

help: ## Show this help
	$(HELP) < $(MAKEFILE_LIST)

build: ## Create docker image for the project
	${DOCKER} build --tag letscheck:dev -f docker/Dockerfile .
