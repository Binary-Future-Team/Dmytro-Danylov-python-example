build:
	@docker compose -f local.yml --parallel 4 build

ps:
	@docker compose -f local.yml ps

up:
	@docker compose -f local.yml up -d --remove-orphans

down:
	@docker compose -f local.yml down

restart:
	@make -s down
	@make -s up

rebuild:
	@make -s down
	@make -s build
	@make -s up

bash:
	@docker compose -f local.yml exec -it app bash

shell:
	@docker compose -f local.yml exec -it app python ./manage.py shell

db:
	@docker compose -f local.yml exec -it mysql mysql --host localhost --user=root --password=Qwwr4SlKxR ***_db

stat:
	@docker compose -f local.yml stat

migrate:
	-docker compose -f local.yml exec -it app ./manage.py migrate

# If the first argument is "logs"...
ifeq (logs,$(firstword $(MAKECMDGOALS)))
  # use the rest as arguments for "logs"
  RUN_ARGS := $(wordlist 2,$(words $(MAKECMDGOALS)),$(MAKECMDGOALS))
  # ...and turn them into do-nothing targets
  $(eval $(RUN_ARGS):;@:)
endif
logs:
	@docker compose -f local.yml logs -f $(RUN_ARGS)

linters:
	-docker compose -f local.yml exec -it app exec isort $BASE_DIR
	-docker compose -f local.yml exec -it app exec bandit $BASE_DIR -r --silent
	-docker compose -f local.yml exec -it app exec flake8 $BASE_DIR
	-docker compose -f local.yml exec -it app exec pylint $BASE_DIR

test:
	docker compose -f local.yml exec app ./manage.py test --failfast

local:
	python app/manage.py runserver
