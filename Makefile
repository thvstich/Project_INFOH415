# Var
POSTGRES_DB=landsat8
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres

# Paths
DATA_DIR=./data/tiles
BENCHMARK_DIR=./benchmark
IMPORT_LOG= ./benchmark/import_times.log


.PHONY: all import_postgis import_rasdaman benchmark clean


all: import_postgis import_rasdaman benchmark


# PostGIS
import_postgis:
	PGPASSWORD=$(POSTGRES_PASSWORD) psql \
		-h localhost -p 5435 \
		-U $(POSTGRES_USER) \
		-d $(POSTGRES_DB) \
		-c "CREATE EXTENSION IF NOT EXISTS postgis;"
	PGPASSWORD=$(POSTGRES_PASSWORD) psql \
		-h localhost -p 5435 \
		-U $(POSTGRES_USER) \
		-d $(POSTGRES_DB) \
		-c "CREATE EXTENSION IF NOT EXISTS postgis_raster;"

	@echo "Importing 256_B4..."
	@start=$$(date +%s); \
	raster2pgsql -s 4326 -I -C -M $(DATA_DIR)_256/B4/*.tif landsat_256_b4 \
	| PGPASSWORD=$(POSTGRES_PASSWORD) psql \
	  -h localhost -p 5435 \
	  -U $(POSTGRES_USER) -d $(POSTGRES_DB); \
	end=$$(date +%s); \
	echo "256_B4 Time taken: $$((end - start)) seconds" >> $(IMPORT_LOG)

	@echo "Importing 256_B5..."
	@start=$$(date +%s); \
	raster2pgsql -s 4326 -I -C -M $(DATA_DIR)_256/B5/*.tif landsat_256_b5 \
	| PGPASSWORD=$(POSTGRES_PASSWORD) psql \
	  -h localhost -p 5435 \
	  -U $(POSTGRES_USER) -d $(POSTGRES_DB); \
	end=$$(date +%s); \
	echo "256_B5 Time taken: $$((end - start)) seconds" >> $(IMPORT_LOG)

	@echo "Importing 64_B5..."
	@start=$$(date +%s); \
	raster2pgsql -s 4326 -I -C -M $(DATA_DIR)_64/B5/*.tif landsat_64_b5 \
	| PGPASSWORD=$(POSTGRES_PASSWORD) psql \
	  -h localhost -p 5435 \
	  -U $(POSTGRES_USER) -d $(POSTGRES_DB); \
	 end=$$(date +%s); \
	 echo "64_B5 Time taken: $$((end - start)) seconds" >> $(IMPORT_LOG)

	@echo "Importing 64_B4..." 
	@start=$$(date +%s); \
	raster2pgsql -s 4326 -I -C -M $(DATA_DIR)_64/B4/*.tif landsat_64_b4 \
	| PGPASSWORD=$(POSTGRES_PASSWORD) psql \
	  -h localhost -p 5435 \
	  -U $(POSTGRES_USER) -d $(POSTGRES_DB); \
	end=$$(date +%s); \
	echo "64_B4 Time taken: $$((end - start)) seconds" >> $(IMPORT_LOG)



# Rasdaman
import_rasdaman:
	@start=$$(date +%s); \
	sudo /opt/rasdaman/bin/wcst_import.sh -u rasadmin /home/thomas/Documents/project_db/rasdaman/import_256_B4.json; \
	end=$$(date +%s); \
	echo "ras_256_B4 Time taken: $$((end - start)) seconds" >> $(IMPORT_LOG)

	@start=$$(date +%s); \
	sudo /opt/rasdaman/bin/wcst_import.sh -u rasadmin /home/thomas/Documents/project_db/rasdaman/import_64_B4.json; \
	end=$$(date +%s); \
	echo "ras_64_B4 Time taken: $$((end - start)) seconds" >> $(IMPORT_LOG)

	@start=$$(date +%s); \
	sudo /opt/rasdaman/bin/wcst_import.sh -u rasadmin /home/thomas/Documents/project_db/rasdaman/import_256_B5.json; \
	end=$$(date +%s); \
	echo "ras_256_B5 Time taken: $$((end - start)) seconds" >> $(IMPORT_LOG)

	@start=$$(date +%s); \
	sudo /opt/rasdaman/bin/wcst_import.sh -u rasadmin /home/thomas/Documents/project_db/rasdaman/import_64_B5.json; \
	end=$$(date +%s); \
	echo "ras_64_B5 Time taken: $$((end - start)) seconds" >> $(IMPORT_LOG)


# benchmark
benchmark:
	python3 $(BENCHMARK_DIR)/run_postgis.py
	python3 $(BENCHMARK_DIR)/run_rasdaman.py
	

clean:
	rm -rf benchmark/results/*.csv
