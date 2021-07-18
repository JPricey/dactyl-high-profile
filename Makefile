.PHONY: watch
watch: run
	watchmedo shell-command --patterns="*.py" --recursive --command='python src/main.py' src

.PHONY: run
run:
	mkdir -p things
	python src/main.py
