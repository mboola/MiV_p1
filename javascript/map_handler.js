const svg = d3.select("#map"),
	width = +svg.attr("width"),
	height = +svg.attr("height");

const g = svg.append("g");
const projection = d3.geoMercator();
const path = d3.geoPath().projection(projection);

const zoom = d3.zoom()
	.scaleExtent([1, 3]) // Set the minimum and maximum zoom scale
	.on("zoom", (event) => {
		g.attr("transform", event.transform);
	});

// Set up the color scale for population
const colorScale = d3.scaleLinear()
	.domain([0, 100000, 2500000]) // Define the domain (min, midpoint, max) adjust as needed
	.range(["#ffcccc", "#ff6666", "#ff0000"]); // Corresponding colors

var currentGeoData = null;

// Adjust the map's dimensions and keep it centered on window resize
function resizeMap() {
	if (currentGeoData == null)
		return ;

	const rect = d3.select("#rectangle").node().getBoundingClientRect(); // Get the size of the #rectangle div
	const rectWidth = rect.width;
	const rectHeight = rect.height;

	const margin = 20;

	// Update projection to keep it centered
	projection.fitSize([rectWidth - margin * 2, rectHeight - margin * 2], currentGeoData);

	// Animate the transition for resizing
	g.transition().duration(750) // 750ms animation duration
		.attr("transform", `translate(${margin}, ${margin})`);

	// Recalculate and smoothly redraw paths
	g.selectAll("path")
		.transition()
		.duration(750) // Add smooth transition for path resizing
		.attr("d", path);
}

window.addEventListener('resize', resizeMap);

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
		
		currentGeoData = comarquesData;
		resizeMap();
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
			resizeMap();

			backButton.style("display", "block");
	}

	// Event listener to return to comarques view
	backButton.on("click", function() {
		currentGeoData = comarquesData
		resizeMap();
		g.selectAll(".comarca").style("visibility", "visible");
		g.selectAll(".municipi").style("visibility", "hidden");
		backButton.style("display", "none");
	});

	// Render the comarques initially
	renderAllData();
}).catch(error => {
	console.error('Error loading GeoJSON:', error);
});