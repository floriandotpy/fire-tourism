"""
Tourism tags: {'aquarium', 'yes', 'chalet', 'alpine_hut', 'motel', 'attraction', 'viewpoint', 'museum',
'zoo', 'camp_site', 'hotel', 'theme_park', 'spa_resort', 'hostel', 'caravan_site', 'picnic_site',
'information', 'camp_pitch', 'apartment', 'guest_house', 'ruins', 'wilderness_hut', 'wine_cellar', 
'artwork', 'gallery'}
"""

# Library for loading open street map data
# Introduction docs: https://github.com/osmcode/pyosmium/blob/master/doc/intro.rst
import osmium
import pandas as pd


class TourismCounterHandler(osmium.SimpleHandler):
    def __init__(self):
        super().__init__()
        
        # collect geo points while traversing through the loaded data
        self.geo_points = []

        # track how many data points we currently still ignore
        self.num_uncounted = 0
        
    def node(self, node):
        tourism_tag = node.tags.get('tourism')

        # TODO: also add non-tourism nodes, but determine their type and subtype correctly
        if tourism_tag:
            node_type = 'tourism'
            node_subtype = tourism_tag
            point = (node.location.lat, node.location.lon, node_type, node_subtype)
            self.geo_points.append(point)

    def way(self, w):
        # TODO: include ways by finding a mean location or something
        if w.tags.get('tourism'):
            self.num_uncounted += 1

    def relation(self, r):
        # TODO: include relation by finding a mean location or something
        if r.tags.get('tourism'):
            self.num_uncounted += 1

    def get_dataframe(self):
        """
        Return a pandas dataframe of the aggregated geo data
        """
        return pd.DataFrame(data=self.geo_points,
                            columns=['lat', 'lon', 'type', 'subtype'])



def get_tourist_activity(lat, lng, when, radius=5):
    """
    Determine the tourism activity at a given location.
    """
    raise NotImplementedError


def load(fname):
    h = TourismCounterHandler()

    h.apply_file(fname, 
                 locations=True,  # enable processing geometries of ways and areas
                 idx='flex_mem')  # cache that works for mid-sized data. Won;t be enough for Europe or planet

    print(f"Number of tourism nodes: {len(h.geo_points)}")
    print(f"Uncounted tourism locations: {h.num_uncounted}")

    return h


if __name__ == "__main__":
    load('../data/galicia.osm.pbf')