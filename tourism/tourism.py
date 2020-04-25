"""
Tourism tags: {'aquarium', 'yes', 'chalet', 'alpine_hut', 'motel', 'attraction', 'viewpoint', 'museum',
'zoo', 'camp_site', 'hotel', 'theme_park', 'spa_resort', 'hostel', 'caravan_site', 'picnic_site',
'information', 'camp_pitch', 'apartment', 'guest_house', 'ruins', 'wilderness_hut', 'wine_cellar', 
'artwork', 'gallery'}
"""

# Library for loading open street map data
# Introduction docs: https://github.com/osmcode/pyosmium/blob/master/doc/intro.rst
import osmium


class TourismCounterHandler(osmium.SimpleHandler):
    def __init__(self):
        super().__init__()
        self.num_nodes = 0
        self.num_uncounted = 0
        self.tourism_tags = set()
        self.tourism_points = []

    def node(self, node):
        if node.tags.get('tourism'):
            point = (node.location.lat, node.location.lon)
            self.tourism_points.append(point)

    def way(self, w):
        # TODO: include ways by finding a mean location or something
        if w.tags.get('tourism'):
            self.num_uncounted += 1

    def relation(self, r):
        # TODO: include relation by finding a mean location or something
        if r.tags.get('tourism'):
            self.num_uncounted += 1



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

    print("Number of tourism nodes: {}".format(len(h.tourism_points)))
    print("Uncounted tourism locations %d" % h.num_uncounted)

    return h


if __name__ == "__main__":
    load('../data/galicia.osm.pbf')