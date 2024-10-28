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

// Get the slider and slider value display elements
const slider = document.getElementById('number-slider');
const sliderValueDisplay = document.getElementById('slider-value');

const gradientBar = document.getElementById('gradient-container');

const projection = d3.geoMercator();
const path = d3.geoPath().projection(projection);

// Set up the color scale for population
const colorScale = d3.scaleLinear()
    .domain([0, 1000, 5000, 10000, 20000, 50000, 100000, 200000, 300000, 500000, 1000000, 2000000])
    .range(["#440154", "#481567", "#453781", "#3e4a89", "#31688e", "#26828e", "#1f9e89", "#35b779", "#6ece58", "#b5de2b", "#fde725", "#fee825"]);

// Get the gradient element
const gradient = document.getElementById('gradient-scale');

// Set the background to a linear gradient
gradient.style.background = `linear-gradient(to top, 
    ${colorScale(0)},
	${colorScale(1000)},
	${colorScale(5000)},
	${colorScale(10000)},
	${colorScale(20000)},
	${colorScale(50000)},
	${colorScale(100000)},
	${colorScale(200000)},
	${colorScale(300000)},
    ${colorScale(500000)},
    ${colorScale(1000000)},
    ${colorScale(2500000)})`;

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

	// margin in px
	const marginX = -(bound.width * scaleFactor - rect.width) / 2;
	const marginY = -(bound.height * scaleFactor - rect.height) / 2;
	gElement.attr("transform", `translate(${marginX}, ${marginY}) scale(${scaleFactor}, ${scaleFactor}) translate(${-bound.x}, ${-bound.y})`);

	// Recalculate and smoothly redraw paths
	gElement.selectAll("path").attr("d", path).attr("stroke-width", 1 / scaleFactor);
}

var yearToShow = 2010;

const backButton = d3.select("#back-button");

Promise.all([
	d3.json('geojson_files/comarques.geojson'),
	d3.json('geojson_files/municipis.geojson')
]).then(([comarquesData, municipisData]) => {

	 // Converts to valid JSON
	comarquesData.features.forEach(feature => {
        if (feature.properties.Total) {
            feature.properties.Total = JSON.parse(feature.properties.Total.replace(/([0-9]{4}):/g, '"$1":'));
        }
    });

	municipisData.features.forEach(feature => {
        if (feature.properties.Total) {
            feature.properties.Total = JSON.parse(feature.properties.Total.replace(/([0-9]{4}):/g, '"$1":'));
        }
    });

	const firstComarca = comarquesData.features[0];
	let years = Object.keys(firstComarca.properties.Total).map(year => parseInt(year, 10));

	const firstYear = years[0];
    const lastYear = years[years.length - 1];

	slider.min = firstYear;
	slider.max = lastYear;
	yearToShow = years[Math.floor(years.length / 2)];
	slider.value = yearToShow;

	sliderValueDisplay.textContent = yearToShow;

	slider.addEventListener('input', function() {
		sliderValueDisplay.textContent = this.value;
		yearToShow = this.value;
		// Update all colors
		d3.selectAll(".region")
			.attr("fill", d => colorScale(d.properties.Total[yearToShow]));
	});

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
			.attr("fill", d => colorScale(d.properties.Total[yearToShow]))
			.on("click", function(event, d) {
				renderComarca(d);
			})
			.on("mouseover", function(event, d) {
				d3.select(this) // Select the current path
      				.style("cursor", "pointer"); // Change cursor to pointer
				const population = d.properties.Total[yearToShow] || 0;
				const tooltip = d3.select("body").append("div")
					.attr("class", "tooltip")
					.html(`Comarca: ${d.properties.NOMCOMAR}<br>Poblacio: ${d3.format(",")(population)}`)
					.style("left", (event.pageX + 5) + "px")
					.style("top", (event.pageY - 28) + "px");
				
				const gradientRect = gradientBar.getBoundingClientRect();

				let i = 0;
				while (i < colorScale.domain().length)
				{
					if (population < colorScale.domain()[i])
						break;
					i++;
				}

				const normalizedPosition = ( 1 - (i / (colorScale.domain().length)));
				const positionOnGradient = gradientRect.height * normalizedPosition;
				const gradientTooltip = d3.select("#gradient-container").append("div")
					.attr("class", "gradient-tooltip")
					.html(`Poblacio: ${d3.format(",")(population)}`)
					.style("left", (gradientRect.left + (gradientRect.right - gradientRect.left) / 2) + "px")
					.style("top", (gradientRect.top + positionOnGradient) + "px");
			})
			.on("mouseout", () => {
				d3.selectAll(".tooltip").remove();
				d3.selectAll(".gradient-tooltip").remove();
			});

		// Then for each comarca inside comarques we create another g element
		comarquesData.features.forEach(element => {
			const nomcomar = element.properties.NOMCOMAR;
			createNewGElement(nomcomar);
			const comarca = gElementDict[nomcomar];

			const municipisToFind = element.properties.CODIMUNI;
			const municipisInComarca = municipisData.features.filter(municipi => 
				municipisToFind.includes(municipi.properties.CODIMUNI)
			);

			comarca.selectAll(".municipi")
				.data(municipisInComarca)
				.enter().append("path")
				.attr("class", "region municipi")
				.attr("d", path)
				.attr("fill", d => colorScale(d.properties.Total[yearToShow]))
				.on("mouseover", function(event, d) {
					const population = d.properties.Total[yearToShow] || 0;
					const tooltip = d3.select("body").append("div")
						.attr("class", "tooltip")
						.html(`Municipi: ${d.properties.NOMMUNI}<br>Poblacio: ${d3.format(",")(population)}`)
						.style("left", (event.pageX + 5) + "px")
						.style("top", (event.pageY - 28) + "px");
				
						const gradientRect = gradientBar.getBoundingClientRect();
		
						let i = 0;
						while (i < colorScale.domain().length)
						{
							if (population < colorScale.domain()[i])
								break;
							i++;
						}
		
						const normalizedPosition = ( 1 - (i / (colorScale.domain().length)));
						const positionOnGradient = gradientRect.height * normalizedPosition;
						const gradientTooltip = d3.select("#gradient-container").append("div")
							.attr("class", "gradient-tooltip")
							.html(`Poblacio: ${d3.format(",")(population)}`)
							.style("left", (gradientRect.left + (gradientRect.right - gradientRect.left) / 2) + "px")
							.style("top", (gradientRect.top + positionOnGradient) + "px");
					})
					.on("mouseout", () => {
						d3.selectAll(".tooltip").remove();
						d3.selectAll(".gradient-tooltip").remove();
					});
			
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
