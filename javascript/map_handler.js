const svg = d3.select("#map"),
	width = +svg.attr("width"),
	height = +svg.attr("height");

const g = svg.append("g");
const projection = d3.geoMercator()
	.center([0, 0])
	.scale(150)
	.translate([svg.attr("width") / 2, svg.attr("height") / 2]);
const path = d3.geoPath().projection(projection);

// Set up the color scale for population
const colorScale = d3.scaleLinear()
	.domain([0, 100000, 2500000]) // Define the domain (min, midpoint, max) adjust as needed
	.range(["#ffcccc", "#ff6666", "#ff0000"]); // Corresponding colors

var currentGeoData = null;
var comarquesCentroid = null;
var isComarques = false;

// Adjust the map's dimensions and keep it centered on window resize
function resizeMap() {
	if (currentGeoData == null)
		return ;

	// If it is the main map, we dont calculate the centroid again.
	let centroid;
	if (isComarques)
		centroid = comarquesCentroid;
	else
		centroid = d3.geoCentroid(currentGeoData);

	const bounds = d3.geoBounds(currentGeoData);
	const longitudesSpan = bounds[1][0] - bounds[0][0];
    const latitudesSpan = bounds[1][1] - bounds[0][1];

	// must use this, other ways change
	const rect = document.getElementById("map").getBoundingClientRect();
	
    const scaleFactor = Math.min(
        rect.width / longitudesSpan, 
        rect.height / latitudesSpan
    );
	console.log("ScaleFactor:", scaleFactor);
	//const scale = 5000;

	projection
		.center(centroid)
		.scale(scaleFactor * 50);
	
	// Recalculate and smoothly redraw paths
	g.selectAll("path").attr("d", path);

	const bbox = g.node().getBBox();
	console.log("G BBox:", bbox);

	// margin in px
	const margin = 40;

	g.attr("transform", `translate(${-bbox.x + margin}, ${-bbox.y + margin})`);
}

const backButton = d3.select("#back-button");

Promise.all([
	d3.json('geojson_files/comarques.geojson'),
	d3.json('geojson_files/municipis.geojson')
]).then(([comarquesData, municipisData]) => {
	// Only one call to this function
	function renderAllData() {
		backButton.style("display", "none");
		g.selectAll(".comarca")
			.data(comarquesData.features)
			.enter().append("path")
			.attr("class", "region comarca")
			.attr("d", path)
			.attr("fill", d => colorScale(d.properties.Total))
			.on("click", function(event, d) {
				renderMunicipis(d);
			})
			.on("mouseover", function(event, d) {
				const tooltip = d3.select("body").append("div")
					.attr("class", "tooltip")
					.html(`Comarca: ${d.properties.NOMCOMAR}<br>Total: ${d3.format(",")(d.properties.Total || 0)}`)
					.style("left", (event.pageX + 5) + "px")
					.style("top", (event.pageY - 28) + "px");
			})
			.on("mouseout", () => d3.selectAll(".tooltip").remove());

		g.selectAll(".municipi")
			.data(municipisData.features)
			.enter().append("path")
			.attr("class", "region municipi")
			.attr("d", path)
			.attr("fill", d => colorScale(d.properties.Total))  // Color by Total population
			.on("mouseover", function(event, d) {
				const tooltip = d3.select("body").append("div")
					.attr("class", "tooltip")
					.html(`Municipi: ${d.properties.NOMMUNI}<br>Total: ${d3.format(",")(d.properties.Total || 0)}`)
					.style("left", (event.pageX + 5) + "px")
					.style("top", (event.pageY - 28) + "px");
			})
			.on("mouseout", () => d3.selectAll(".tooltip").remove());

		g.selectAll(".comarca").style("visibility", "hidden");
		g.selectAll(".municipi").style("visibility", "hidden");

		//TODO : initial animation to show comarques
		g.selectAll(".comarca").style("visibility", "visible");
	}

	// Zoom into a selected comarca and display municipalities
	function renderMunicipis(comarca) {

		const municipisToFind = comarca.properties.NOMMUNI;

		// Find entries in municipisData geojson
		const municipisInComarca = municipisData.features.filter(municipi => 
			municipisToFind.includes(municipi.properties.NOMMUNI)
		);

		g.selectAll(".municipi")
			.filter(function(d) {
				return municipisInComarca.some(mun => mun.properties.NOMMUNI === d.properties.NOMMUNI);
			})
			.style("visibility", "visible");

			g.selectAll(".comarca").style("visibility", "hidden");

			currentGeoData = comarca
			isComarques = false;
			resizeMap();

			backButton.style("display", "block");
	}

	// Event listener to return to comarques view
	backButton.on("click", function() {
		currentGeoData = comarquesData
		isComarques = true;
		resizeMap();
		g.selectAll(".comarca").style("visibility", "visible");
		g.selectAll(".municipi").style("visibility", "hidden");
		backButton.style("display", "none");
	});

	// Calculate only once the centroid of comarquesData
	currentGeoData = comarquesData;
	comarquesCentroid = d3.geoCentroid(currentGeoData);

	// Render the comarques initially
	renderAllData();

	// Ajust map to size
	isComarques = true;
	resizeMap();

}).catch(error => {
	console.error('Error loading GeoJSON:', error);
});

window.addEventListener('resize', resizeMap);
