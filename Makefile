# Usage:
# make migrate      -> create migration
# make upgrade      -> apply migration
# make downgrade    -> rollback
# make history      -> show migration history
# make reset        -> reset to base state (drop all applied revisions)

.PHONY: migrate upgrade downgrade history

migrate:
	alembic revision --autogenerate -m "$(m)"

upgrade:
	alembic upgrade head

n ?= 1
downgrade:
	alembic downgrade -$(n)

history:
	alembic history --verbose

reset:
	alembic downgrade base