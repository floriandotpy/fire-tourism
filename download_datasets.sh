# Download all data in subfolder
DATASET_DIR=data
mkdir -p $DATASET_DIR

# Open street map data (one region only for now). Download size 75MB
wget -P $DATASET_DIR http://download.openstreetmap.fr/extracts/europe/spain/galicia.osm.pbf
