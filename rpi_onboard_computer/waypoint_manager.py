from lxml import etree

class WaypointManager:
    def __init__(self, kml_path):
        self.kml_path = kml_path
        self.waypoints = []

    def load_waypoints(self):
        tree = etree.parse(self.kml_path)
        namespace = {'kml': 'http://www.opengis.net/kml/2.2'}
        placemarks = tree.xpath('//kml:Placemark', namespaces=namespace)

        for pm in placemarks:
            coords = pm.xpath('.//kml:coordinates', namespaces=namespace)
            if coords:
                coord_text = coords[0].text.strip()
                lon, lat, alt = coord_text.split(',')
                self.waypoints.append((float(lat), float(lon), float(alt)))
        return self.waypoints
