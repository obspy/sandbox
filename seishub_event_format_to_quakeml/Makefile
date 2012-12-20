all: clean fetch convert

clean:
	rm all_resource_names
	rm -rf all_resources converted_files

fetch:
	mkdir all_resources
	python fetch_all_seishub_events.py
	bash fetch_all_seishub_events.sh

convert:
	mkdir converted_files
	python run_on_all_resources_subfolder.py
