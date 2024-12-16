.PHONY: db_clean, db_view, help, debug, run

help:
	@echo "db_clean: Clean up the database"
	@echo "db_view: View the database"

db_clean:
	echo "Cleaning up the database"
	@rm -f src/database/data/*.db
	echo "Database cleaned up"

db_view:
	@sqlite_web --foreign-keys src/database/data/database.db -p 8080

run:
	@clear && python3 src/main.py

run_clean:
	@clear && make db_clean && python3 src/main.py


debug:
	@clear && python3 src/main_debug.py

debug_clean:
	@clear && make db_clean && python3 src/main_debug.py
