// Configuración común
const margin = { top: 20, right: 30, bottom: 40, left: 40 };

function createFanChart(data, chart_type, promedios, data2) {
  const graphContainer = document.getElementById(chart_type);
  graphContainer.innerHTML = "";

  const wrapper = document.getElementById("graphContainer");
  const width  = wrapper.clientWidth  - margin.right;
  const height = wrapper.clientHeight;

  const keys = Object.keys(data[0]);

  // —— Aquí ajustamos el dominio incluyendo promedios[0] ——  
  const maxX = Math.max(
    d3.max(data, d => d[keys[0]]),
    promedios[0]
  );
  const x = d3.scaleLinear()
    .domain([0, maxX])
    .range([margin.left*2, width - margin.right]);

  // —— Igual para el eje Y, incluimos promedios[1] ——  
  const maxY = Math.max(
    d3.max(data, d => d[keys[1]]),
    promedios[1]
  );
  const y = d3.scaleLinear()
    .domain([0, maxY])
    .range([height - margin.bottom, margin.top]);

  const svg = d3.create("svg")
    .attr("width", width)
    .attr("height", height);

  // ejes, títulos y scatter original
  svg.append("g")
     .attr("transform", `translate(0,${height - margin.bottom})`)
     .call(d3.axisBottom(x));
  svg.append("g")
     .attr("transform", `translate(${margin.left*2},0)`)
     .call(d3.axisLeft(y));
  svg.append("text")
     .attr("x", width/2).attr("y", height)
     .style("text-anchor","middle")
     .text(keys[0]);
  svg.append("text")
     .attr("transform","rotate(-90)")
     .attr("x",-height/2).attr("y",margin.left/2)
     .style("text-anchor","middle")
     .text(keys[1]);
  svg.selectAll(".dot")
     .data(data)
     .enter().append("circle")
       .attr("class","dot")
       .attr("cx", d=> x(d[keys[0]]))
       .attr("cy", d=> y(d[keys[1]]))
       .attr("r", 5);

  // líneas
  svg.append("path")
     .datum(data)
     .attr("fill","none").attr("stroke","black").attr("stroke-width",1.5)
     .attr("d", d3.line()
       .curve(d3.curveBasis)
       .x(d=> x(d[keys[0]]))
       .y(d=> y(d[keys[1]]))
     );
  svg.append("path")
     .datum(data2)
     .attr("fill","none").attr("stroke","black").attr("stroke-width",1.5)
     .attr("d", d3.line()
       .curve(d3.curveBasis)
       .x(d=> x(d[keys[0]]))
       .y(d=> y(d[keys[1]]))
     );

  // punto de promedio (ahora dentro del dominio)
  svg.append("circle")
     .attr("cx", x(promedios[0]))
     .attr("cy", y(promedios[1]))
     .attr("r", 8)
     .attr("fill","red");

  graphContainer.appendChild(svg.node());
}


function updateFanChart(data, chart_type, promedios, data2) {
  const graphContainer = document.getElementById(chart_type);
  graphContainer.innerHTML = "";

  const wrapper = document.getElementById("graphContainer");
  const width  = wrapper.clientWidth  - margin.right;
  const height = wrapper.clientHeight;

  const keys = Object.keys(data[0]);

  // —— Dominio X incluyendo promedio ——  
  const maxX = Math.max(
    d3.max(data, d => d[keys[0]]),
    promedios[0]
  );
  const x = d3.scaleLinear()
    .domain([0, maxX])
    .range([margin.left*2, width - margin.right]);

  // —— Dominio Y incluyendo promedio ——  
  const maxY = Math.max(
    d3.max(data, d => d[keys[1]]),
    promedios[1]
  );
  const y = d3.scaleLinear()
    .domain([0, maxY])
    .range([height - margin.bottom, margin.top]);

  const svg = d3.create("svg")
    .attr("width", width)
    .attr("height", height);

  svg.append("g")
     .attr("transform", `translate(0,${height - margin.bottom})`)
     .call(d3.axisBottom(x));
  svg.append("g")
     .attr("transform", `translate(${margin.left*2},0)`)
     .call(d3.axisLeft(y));
  svg.append("text")
     .attr("x", width/2).attr("y", height)
     .style("text-anchor","middle")
     .text(keys[0]);
  svg.append("text")
     .attr("transform","rotate(-90)")
     .attr("x",-height/2).attr("y",margin.left/2)
     .style("text-anchor","middle")
     .text(keys[1]);
  svg.selectAll(".dot")
     .data(data)
     .enter().append("circle")
       .attr("class","dot")
       .attr("cx", d=> x(d[keys[0]]))
       .attr("cy", d=> y(d[keys[1]]))
       .attr("r",5);

  svg.append("path")
     .datum(data)
     .attr("fill","none").attr("stroke","black").attr("stroke-width",1.5)
     .attr("d", d3.line()
       .curve(d3.curveBasis)
       .x(d=> x(d[keys[0]]))
       .y(d=> y(d[keys[1]]))
     );
  svg.append("path")
     .datum(data2)
     .attr("fill","none").attr("stroke","black").attr("stroke-width",1.5)
     .attr("d", d3.line()
       .curve(d3.curveBasis)
       .x(d=> x(d[keys[0]]))
       .y(d=> y(d[keys[1]]))
     );

  svg.append("circle")
     .attr("cx", x(promedios[0]))
     .attr("cy", y(promedios[1]))
     .attr("r",8)
     .attr("fill","red");

  graphContainer.appendChild(svg.node());
}
