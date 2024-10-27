const svg = d3.select("#map"),
	width = +svg.attr("width"),
	height = +svg.attr("height");

// Here I create a g for every map I will have.
// (This should be done dynamically but it is to expensive, so for a better interactivity this is necessary)
const gElementDict = {};

function createNewGElement(name) {
	//console.log("Creating new g element name: ", name);
	const gElement = svg.append("g").attr("id", name);
	gElementDict[name] = gElement;
}

const projection = d3.geoMercator();
const path = d3.geoPath().projection(projection);

// Set up the color scale for population
const colorScale = d3.scaleLinear()
	.domain([0, 100000, 2500000]) // Define the domain (min, midpoint, max) adjust as needed
	.range(["#ffcccc", "#ff6666", "#ff0000"]); // Corresponding colors

var currentGeoData = null;
var isComarques = true;

// Adjust the map's dimensions and keep it centered on window resize
function resizeMap() {
	if (currentGeoData == null)
		return ;

	var gElement;
	if (isComarques)
		gElement = gElementDict[currentGeoData.name];
	else
		gElement = gElementDict[currentGeoData.properties.NOMCOMAR];

	const rect = document.getElementById("map").getBoundingClientRect();
	const bound = gElement.node().getBBox();

    const scaleFactor = Math.min(
        rect.width / bound.width, 
        rect.height / bound.height
    );

	console.log("Bounds g element:", bound);

	// margin in px
	const marginX = -(bound.width * scaleFactor - rect.width) / 2;
	const marginY = -(bound.height * scaleFactor - rect.height) / 2;
	gElement.attr("transform", `translate(${marginX}, ${marginY}) scale(${scaleFactor}, ${scaleFactor}) translate(${-bound.x}, ${-bound.y})`);

	// Recalculate and smoothly redraw paths
	gElement.selectAll("path").attr("d", path).attr("stroke-width", 1 / scaleFactor);
}

const backButton = d3.select("#back-button");

Promise.all([
	d3.json('geojson_files/comarques.geojson'),
	d3.json('geojson_files/municipis.geojson')
]).then(([comarquesData, municipisData]) => {
	// Only one call to this function
	function createAllRenderData() {
		// First we create a g element for the map of comarques
		createNewGElement(comarquesData.name);
		const comarques = gElementDict[comarquesData.name];

		// Then we add the information from the GeoJson
		comarques.selectAll(".comarca")
			.data(comarquesData.features)
			.enter().append("path")
			.attr("class", "region comarca")
			.attr("d", path)
			.attr("fill", d => colorScale(d.properties.Total))
			.on("click", function(event, d) {
				renderComarca(d);
			})
			.on("mouseover", function(event, d) {
				d3.select(this) // Select the current path
      				.style("cursor", "pointer"); // Change cursor to pointer
				const tooltip = d3.select("body").append("div")
					.attr("class", "tooltip")
					.html(`Comarca: ${d.properties.NOMCOMAR}<br>Total: ${d3.format(",")(d.properties.Total || 0)}`)
					.style("left", (event.pageX + 5) + "px")
					.style("top", (event.pageY - 28) + "px");
			})
			.on("mouseout", () => d3.selectAll(".tooltip").remove());

		// Then for each comarca inside comarques we create another g element
		comarquesData.features.forEach(element => {
			const nomcomar = element.properties.NOMCOMAR;
			createNewGElement(nomcomar);
			const comarca = gElementDict[nomcomar];

			const municipisToFind = element.properties.NOMMUNI;
			const municipisInComarca = municipisData.features.filter(municipi => 
				municipisToFind.includes(municipi.properties.NOMMUNI)
			);

			comarca.selectAll(".municipi")
				.data(municipisInComarca)
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
			
			// Hide the municipis bc for the moment I wont be showing them.
			comarca.selectAll(".municipi").style("visibility", "hidden");
		});
	}

	// Called when a comarca gets clicked
	function renderComarca(comarca) {
		const comarquesGElement = gElementDict[comarquesData.name];
		
		// Get the name of the comarca
		const nomcomar = comarca.properties.NOMCOMAR;
		const comarcaGElement = gElementDict[nomcomar];

		// Set only one comarca to visible
		comarcaGElement.selectAll(".municipi").style("visibility", "visible");

		// Set comarques to invisible
		comarquesGElement.selectAll(".comarca").style("visibility", "hidden");

		currentGeoData = comarca;

		isComarques = false;
		resizeMap();

		backButton.style("display", "block");
	}


	// Event listener to return to comarques view
	backButton.on("click", function() {
		var gElement = gElementDict[currentGeoData.properties.NOMCOMAR];
		gElement.selectAll(".municipi").style("visibility", "hidden");
		currentGeoData = comarquesData
		isComarques = true;
		resizeMap();
		//resizeMap();
		gElement = gElementDict[currentGeoData.name];
		gElement.selectAll(".comarca").style("visibility", "visible");
		backButton.style("display", "none");
	});

	backButton.style("display", "none");

	currentGeoData = comarquesData;
	
	createAllRenderData();

	resizeMap();

}).catch(error => {
	console.error('Error loading GeoJSON:', error);
});

window.addEventListener('resize', () => {
	resizeMap();
	//resizeMap();
});
