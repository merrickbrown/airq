var margin = {top: 20, right: 30, bottom: 0, left: 10},
    width = 860 - margin.left - margin.right,
    height = 800 - margin.top - margin.bottom;

// append the svg object to the body of the page
const svg = d3.select("#graph")
  .append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
  .append("g")
    .attr("transform",
          "translate(" + margin.left + "," + margin.top + ")");

// Parse the Data
fetch('/data').then(res => res.json()).then(raw => {

  const columns = [
    "time",
    "particles 03um",
    "particles 05um",
    "particles 10um",
    "particles 25um",
    "particles 50um",
    "particles 100um"
  ]

  // consider converting wide to long
  // http://jonathansoma.com/tutorials/d3/wide-vs-long-data/
  let data = raw.records.map(({
    "time": time,
    "particles 03um": p03,
    "particles 05um": p05,
    "particles 10um": p10,
    "particles 25um": p25,
    "particles 50um": p50,
    "particles 100um": p100
  }) => {return {
    "time": new Date(time).getTime()/1000,
    "particles 03um": p03,
    "particles 05um": p05,
    "particles 10um": p10,
    "particles 25um": p25,
    "particles 50um": p50,
    "particles 100um": p100}});
  
  // TODO what is data.y for?
  data.columns = columns;
  data.y = "Particles";

  // List of groups = header of the csv files
  var keys = data.columns.slice(1)

  // Add X axis
  var x = d3.scaleLinear()
    .domain(d3.extent(data, function(d) { return d.time; }))
    .range([ 0, width ]);

  svg.append("g")
    .attr("transform", "translate(0," + height*0.8 + ")")
    .select(".domain").remove()
  // Customization
  svg.selectAll(".tick line").attr("stroke", "#b8b8b8")

  // Add X axis label:
  svg.append("text")
      .attr("text-anchor", "end")
      .attr("x", width)
      .attr("y", height-height/20)
      .text("Time");

  // Add Y axis
  var y = d3.scaleLinear()
    // scale to max sum of particles. unclear why reverse map in range is
    // needed for right-side-up plot
    .domain([0, 1.1 * d3.max(data, function(d) { return d["particles 03um"] +
        d["particles 05um"] + d["particles 10um"] + d["particles 25um"] +
        d["particles 50um"] + d["particles 100um"] })])
    .range([ height, 0 ]);

  // color palette
  var color = d3.scaleOrdinal()
    .domain(keys)
    .range(d3.schemeDark2);

  //stack the data?
  var stackedData = d3.stack()
    .order(d3.stackOrderReverse)
    // note this change means you'll want to adjust the y domain, Time label
    //.offset(d3.stackOffsetSilhouette)
    .offset(d3.stackOffsetNone)
    .keys(keys)
    (data)

  // create a tooltip
  var Tooltip = svg
    .append("text")
    .attr("x", 0)
    .attr("y", 0)
    .style("opacity", 0)
    .style("font-size", 17)

  // Three function that change the tooltip when user hover / move / leave a cell
  var mouseover = function(d) {
    Tooltip.style("opacity", 1)
    d3.selectAll(".myArea").style("opacity", .3)
    d3.select(this)
      .style("stroke", "black")
      .style("opacity", 1)
  }
  var mousemove = function(d,i) {
    grp = keys[i]
    Tooltip.text(grp)
  }
  var mouseleave = function(d) {
    Tooltip.style("opacity", 0)
    d3.selectAll(".myArea").style("opacity", 1).style("stroke", "none")
   }

  // Area generator
  var area = d3.area()
    .x(function(d) { return x(d.data.time); })
    .y0(function(d) { return y(d[0]); })
    .y1(function(d) { return y(d[1]); })

  // Show the areas
  svg
    .selectAll("mylayers")
    .data(stackedData)
    .enter()
    .append("path")
      .attr("class", "myArea")
      .style("fill", function(d) { return color(d.key); })
      .attr("d", area)
      .on("mouseover", mouseover)
      .on("mousemove", mousemove)
      .on("mouseleave", mouseleave)

})
