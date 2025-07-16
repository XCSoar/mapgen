// OpenLayers 3.7
var source = new ol.source.Vector()

var vector_layer = new ol.layer.Vector({
  source: source,
  style: new ol.style.Style({
    fill: new ol.style.Fill({
      color: 'rgba(255, 255, 255, 0.2)'
    }),
    stroke: new ol.style.Stroke({
      color: '#ffcc33',
      width: 2
    }),
    image: new ol.style.Circle({
      radius: 7,
      fill: new ol.style.Fill({
        color: '#ffcc33'
      })
    })
  })
});

var map = new ol.Map({
  layers: [
    new ol.layer.Tile({ source: new ol.source.OSM() }),
    vector_layer
    ],
  view: new ol.View({
    center: [0,0],
    zoom: 2
  }),
  target: 'map'
});

geometryFunction = function(coordinates, geometry) {
  if (!geometry) {
    geometry = new ol.geom.Polygon(null);
  }
  var start = coordinates[0];
  var end = coordinates[1];
  geometry.setCoordinates([
    [start, [start[0], end[1]], end, [end[0], start[1]], start]
  ]);
  return geometry;
};

draw_box = new ol.interaction.Draw({
  source: source,
  type: "LineString",
  geometryFunction: geometryFunction,
  maxPoints: 2
});
map.addInteraction(draw_box);

draw_box.on("drawstart", function(draw_event){
  box_coords = draw_event.feature.getGeometry().getCoordinates()[0];
  fill_boxes([box_coords[0],box_coords[2]]);
});

draw_box.on("drawend", function(draw_event){
  source.clear();
  box_corners = draw_event.feature.getGeometry().getCoordinates()[0];
  fill_boxes([box_corners[0],box_corners[2]]);
});

function fill_boxes(box_coords) {
  var coords = [[],[]];
  for (i = 0; i < 2; i++) {
        coords[i] = ol.proj.transform(box_coords[i],"EPSG:900913","EPSG:4326");
      }

  var dirs = [["#left","#right"],["#bottom","#top"]];

if (Array.isArray(coords) && coords.length === 2 && Array.isArray(dirs) && dirs.length === 2) {
    for (let i = 0; i < 2; i++) {
        if (typeof coords[0][i] === 'number' && typeof coords[1][i] === 'number') {
            if (coords[0][i] < coords[1][i]) {
                const dir1 = dirs[i][0];
                const dir2 = dirs[i][1];

                // Validate dir1 and dir2 to ensure they are safe selectors
                if (isValidSelector(dir1) && isValidSelector(dir2)) {
                    document.querySelector(dir1).value = coords[0][i];
                    document.querySelector(dir2).value = coords[1][i];
                } else {
                    console.error("Invalid selector:", dir1, dir2);
                }
            } else {
              console.error("Coordinates one not smaller than coordinates two");
            }
        } else {
            console.error("Invalid coordinate values");
        }
    }
} else {
    console.error("Invalid input data");
}

// Function to validate CSS selectors
function isValidSelector(selector) {
    try {
        document.querySelector(selector);
        return true;
    } catch (e) {
        return false;
    }
}
}
