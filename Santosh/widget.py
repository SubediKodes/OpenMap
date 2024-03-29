import sys
import os
import io

from PySide6.QtWidgets import QApplication
from PySide6.QtUiTools import loadUiType
from PySide6.QtWebEngineWidgets import QWebEngineView
import folium
from folium.features import DivIcon
import overpy
import osmnx as ox

api = overpy.Overpass()
text = 'Circle'

current_dir = os.path.dirname(os.path.abspath(__file__))
Form, Base = loadUiType(os.path.join(current_dir, "form.ui"))


def gebiedanalyse():
    breedte, lengte = 51.2232747408709, 2.980362630411266  # ingeven breedte en lengte coordinaten
    result = ox.geometries_from_point((breedte, lengte), {"landuse": True},
                                      dist=(100))  # command dat "landuse" gegevens ophaalt uit osm

    # maken van lijst voor gebiedsanalye
    f = list()  # maken van een lijst van alle areas "landuse"
    x = result['landuse']
    for i in x:
        f.append(i)

    r = list()  # lijst die elke soort "landuse" maar een keer bevat
    for i in f:
        if i in r:
            continue
        if i not in r:
            r.append(i)
    print(f)
    print(r)

    # berekenen van som van de oppervlakte van de gebiedstypes
    w = {}  # directory creeren
    for i in r:
        tags = {'landuse': i}  # tags veranderen naar betrevende soort landuse waarvoor oppervlakte berekend moet worden
        result = ox.geometries_from_point((breedte, lengte), tags, dist=100)

        result.crs = 'epsg:4328'  # assign correct CRS in the correct format here

        gebied = sum(result.area)  # berekenen van som van de oppervlakten
        w[i] = gebied
    grootste_gebied = max(w, key=w.get)  # geeft het grootse landuse oppervlakte
    print(w)

    # printen van resultaat
    print("This area is a", grootste_gebied, "area")


def clicked():
    print("Button clicked!!!!!!")



class OCR(Base, Form):
    def __init__(self, parent=None):
        super(self.__class__, self).__init__(parent)
        self.setupUi(self)
        # self.button.clicked.connect(lambda: clicked())
        self.button.clicked.connect(self.calculate)
        self.testbutton.clicked.connect(lambda: gebiedanalyse())
        self.map(51.0557409, 3.7218855, 500)

        self.longitude.setText("51.0557409")
        self.latitude.setText("3.7218855")

        self.slider_radius.setRange(10, 1000)
        self.slider_radius.setSingleStep(10)
        self.slider_radius.setValue(500)
        self.radius.setText(str(self.slider_radius.value()))
        self.slider_radius.valueChanged.connect(lambda: self.radius.setText(str(self.slider_radius.value())))

    def calculate(self):
        longitude = self.longitude.text()
        latitude = self.latitude.text()
        radius = str(self.slider_radius.value())
        # if not longitude or not latitude or not radius:
        print("longitude: " + longitude + " latitude: " + latitude + " radius: " + radius)
        amenity = api.query(
            'way(around:' + str(radius) + ',' + longitude + ',' + latitude + ')["amenity"="pub"]; (._;>;); out geom;')

        self.result.setText("The number of amenities found in the selected area: Pubs =  " + str(len(amenity.nodes)))

        print(len(amenity.nodes))
        if amenity.nodes:
            id = amenity.nodes[0].id

        self.map(float(longitude), float(latitude), radius)

    def testValue(self):
        self.longitude.setText("51.0557409")
        self.latitude.setText("3.7218855")

    def map(self, lon, lat, rad):
        m = folium.Map(location=[lon, lat], tiles="OpenStreetMap", zoom_start=14, min_zoom=8, max_zoom=25)

        folium.Circle([lon, lat], rad, fill=True).add_to(m)

        folium.map.Marker([lon + 0.5, lat - 1.6], icon=DivIcon(icon_size=(150, 36), icon_anchor=(0, 0),
                                                               html='<div style=""font-size: 24pt">%s</div>' % text, )).add_to(
            m)
        m.add_child(folium.LatLngPopup())

        data = io.BytesIO()
        m.save(data, close_file=False)
        webview = QWebEngineView()
        webview.setHtml(data.getvalue().decode())
        layout = self.mapbox
        if layout.count():
            layout.takeAt(0)
        layout.addWidget(webview)


if __name__ == "__main__":
    app = QApplication([])
    widget = OCR()
    widget.show()
    sys.exit(app.exec())

