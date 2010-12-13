var BoxWithStartCallback = OpenLayers.Class(OpenLayers.Handler.Box, {
    initialize: function(control, callbacks, options) {
        OpenLayers.Handler.Box.prototype.initialize.apply(this, arguments);
    },
    startBox: function(xy) {
        OpenLayers.Handler.Box.prototype.startBox.apply(this, arguments);
        this.callback('start', []);
    },
    CLASS_NAME: 'BoxWithStartCallback'
});

(function() {
    map = new OpenLayers.Map('map');
    map.addLayer(new OpenLayers.Layer.WMS("Basic",
					  "http://vmap0.tiles.osgeo.org/wms/vmap0",
					  { layers: 'basic' }));

    var vector = new OpenLayers.Layer.Vector('Selected Bounds');
    map.addLayer(vector);
    map.setCenter(new OpenLayers.LonLat(0, 20.0), 2);

    function drawRect(bottomLeft, topRight) {
        var rect = new OpenLayers.Geometry.LinearRing();
        rect.addPoint(new OpenLayers.Geometry.Point(bottomLeft.lon, bottomLeft.lat));
        rect.addPoint(new OpenLayers.Geometry.Point(bottomLeft.lon, topRight.lat));
        rect.addPoint(new OpenLayers.Geometry.Point(topRight.lon,   topRight.lat));
        rect.addPoint(new OpenLayers.Geometry.Point(topRight.lon,   bottomLeft.lat));
        vector.addFeatures([new OpenLayers.Feature.Vector(rect)]);
    }

    function initRect() {
	var bounds = document.forms[0].elements;
	if (bounds.left.value != '' &&
	    bounds.right.value != '' &&
	    bounds.top.value != '' &&
	    bounds.bottom.value != '') {
            var bottomLeft = new OpenLayers.LonLat(parseFloat(bounds.left.value), parseFloat(bounds.bottom.value))
            var topRight = new OpenLayers.LonLat(parseFloat(bounds.right.value), parseFloat(bounds.top.value));
	    drawRect(bottomLeft, topRight);
	}
    }

    var control = new OpenLayers.Control();
    OpenLayers.Util.extend(control, {
         draw: function () {
             this.box = new BoxWithStartCallback(control,
                                                 { start: this.startBoundsSelection,
                                                   done: this.boundsSelected },
                                                 { keyMask: OpenLayers.Handler.MOD_CTRL });
             this.box.activate();
         },
         startBoundsSelection: function() {
             vector.removeAllFeatures();
         },
         boundsSelected: function(bounds) {
             var bottomLeft = map.getLonLatFromPixel(new OpenLayers.Pixel(bounds.left, bounds.bottom));
             var topRight = map.getLonLatFromPixel(new OpenLayers.Pixel(bounds.right, bounds.top));
	     drawRect(bottomLeft, topRight);

	     var bounds = document.forms[0].elements;
	     bounds.left.value = bottomLeft.lon;
	     bounds.right.value = topRight.lon;
	     bounds.top.value = topRight.lat;
	     bounds.bottom.value = bottomLeft.lat;
         }
    });

    map.addControl(control);
    initRect();
})();
