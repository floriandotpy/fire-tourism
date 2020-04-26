# Download all data in subfolder
DATASET_DIR=data
mkdir -p $DATASET_DIR

# Open street map data
# -N only downloads if server has newer file than present on disk
wget -N -P $DATASET_DIR http://download.openstreetmap.fr/extracts/europe/spain/galicia.osm.pbf  # 75MB
wget -N -P $DATASET_DIR http://download.openstreetmap.fr/extracts/europe/spain/asturias.osm.pbf  # 28M
wget -N -P $DATASET_DIR http://download.openstreetmap.fr/extracts/europe/spain/castilla_y_leon.osm.pbf  # 109M

wget -N -P $DATASET_DIR http://download.openstreetmap.fr/extracts/asia/myanmar.osm.pbf  # 133M
wget -N -P $DATASET_DIR http://download.openstreetmap.fr/extracts/north-america/us-west/california.osm.pbf  # 909M