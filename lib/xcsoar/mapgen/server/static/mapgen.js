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

// Map widget code
var map;
$(function() {
    var vector;

    function drawRect(bottomLeft, topRight) {
        var rect = new OpenLayers.Geometry.LinearRing();
        rect.addPoint(new OpenLayers.Geometry.Point(bottomLeft.lon, bottomLeft.lat));
        rect.addPoint(new OpenLayers.Geometry.Point(bottomLeft.lon, topRight.lat));
        rect.addPoint(new OpenLayers.Geometry.Point(topRight.lon,   topRight.lat));
        rect.addPoint(new OpenLayers.Geometry.Point(topRight.lon,   bottomLeft.lat));
        vector.addFeatures([new OpenLayers.Feature.Vector(rect)]);
    }

    function updateRect() {
	var bounds = document.forms[0].elements;
	if (bounds.left.value != '' &&
	    bounds.right.value != '' &&
	    bounds.top.value != '' &&
	    bounds.bottom.value != '') {
            vector.removeAllFeatures();
            var src = new OpenLayers.Projection("EPSG:4326");
            var dest = new OpenLayers.Projection("EPSG:900913");
            var bottomLeft = new OpenLayers.LonLat(parseFloat(bounds.left.value), parseFloat(bounds.bottom.value)).transform(src, dest);
            var topRight = new OpenLayers.LonLat(parseFloat(bounds.right.value), parseFloat(bounds.top.value)).transform(src, dest);
	    drawRect(bottomLeft, topRight);
	}
    }

    map = new OpenLayers.Map({div: "map", projection: new OpenLayers.Projection("EPSG:900913")});
    map.addLayer(new OpenLayers.Layer.Google("Google Terrain", {type: google.maps.MapTypeId.TERRAIN}));
    vector = new OpenLayers.Layer.Vector('Selected Bounds');
    map.addLayer(vector);
    map.setCenter(new OpenLayers.LonLat(0, 20.0).transform(new OpenLayers.Projection("EPSG:4326"), new OpenLayers.Projection("EPSG:900913")), 2);

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
             var src = new OpenLayers.Projection("EPSG:900913");
             var dest = new OpenLayers.Projection("EPSG:4326");

             var bottomLeft = map.getLonLatFromPixel(new OpenLayers.Pixel(bounds.left, bounds.bottom));
             var topRight = map.getLonLatFromPixel(new OpenLayers.Pixel(bounds.right, bounds.top));
             drawRect(bottomLeft, topRight);

             bottomLeft = bottomLeft.transform(src, dest);
             topRight = topRight.transform(src, dest);

	     var bounds = document.forms[0].elements;
	     bounds.left.value = isNaN(bottomLeft.lon) ? '' : bottomLeft.lon;
	     bounds.right.value = isNaN(topRight.lon) ? '' : topRight.lon;
	     bounds.top.value = isNaN(topRight.lat) ? '' : topRight.lat;
	     bounds.bottom.value = isNaN(bottomLeft.lat) ? '' : bottomLeft.lat;
         }
    });

    map.addControl(control);
    updateRect();

    $('#left, #right, #bottom, #top').keypress(updateRect);
    $('#left, #right, #bottom, #top').change(updateRect);
    $("input[name='selection']").change(function() {
	var sel = $("input[name='selection']:checked").val();
	if (sel == 'waypoint') {
	    $('#waypoint_file_box').show();
	    $('#bounds_box').hide();
	} else if (sel == 'bounds') {
	    $('#waypoint_file_box').hide();
	    $('#bounds_box').show();
	} else {
	    $('#waypoint_file_box').show();
	    $('#bounds_box').show();
	}
    }).change();
});
