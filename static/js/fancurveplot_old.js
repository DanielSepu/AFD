// --- Tabla de tolerancias según ANi y parámetro ---
const toleranceTable = {
  "volume flow rate": { AN1: 0.01, AN2: 0.025, AN3: 0.05, AN4: 0.10 },
  "fan pressure":      { AN1: 0.01, AN2: 0.025, AN3: 0.05, AN4: 0.10 },
  "power":             { AN1: 0.02, AN2: 0.03,  AN3: 0.08, AN4: 0.16 }
};

const margin = { top: 20, right: 30, bottom: 40, left: 40 };

function createFanChart(data, chart_type, promedios, data2, toleranceGrade, toleranceParam) {
  const graphContainer = document.getElementById(chart_type);
  graphContainer.innerHTML = "";
  const wrapper = document.getElementById("graphContainer");
  const width  = wrapper.clientWidth  - margin.right;
  const height = wrapper.clientHeight;
  
  const [xKey, yKey] = Object.keys(data[0]);

  // --- escalas incluyendo el punto promedio ---
  const maxX = Math.max(d3.max(data, d => d[xKey]), promedios[0]);
  const maxY = Math.max(d3.max(data, d => d[yKey]), promedios[1]);
  const x = d3.scaleLinear().domain([0, maxX]).range([margin.left*2, width - margin.right]);
  const y = d3.scaleLinear().domain([0, maxY]).range([height - margin.bottom, margin.top]);

  const svg = d3.create("svg").attr("width", width).attr("height", height);

  // ejes y etiquetas
  svg.append("g").attr("transform", `translate(0,${height - margin.bottom})`).call(d3.axisBottom(x));
  svg.append("g").attr("transform", `translate(${margin.left*2},0)`).call(d3.axisLeft(y));
  svg.append("text").attr("x", width/2).attr("y", height).style("text-anchor","middle").text(xKey);
  svg.append("text").attr("transform","rotate(-90)").attr("x",-height/2).attr("y",margin.left/2).style("text-anchor","middle").text(yKey);

  // puntos originales y curvas
  svg.selectAll(".dot").data(data).enter().append("circle")
     .attr("class","dot").attr("cx", d=> x(d[xKey])).attr("cy", d=> y(d[yKey])).attr("r",5);

  [data, data2].forEach(ds => {
    svg.append("path")
       .datum(ds)
       .attr("fill","none").attr("stroke","black").attr("stroke-width",1.5)
       .attr("d", d3.line().curve(d3.curveBasis).x(d=> x(d[xKey])).y(d=> y(d[yKey])));
  });

  // punto promedio
  const cx = x(promedios[0]), cy = y(promedios[1]);
  svg.append("circle").attr("cx", cx).attr("cy", cy).attr("r",8).attr("fill","red");

  // --- cuadro de tolerancia ---
  const tolFracX = (toleranceTable[toleranceParam]?.[toleranceGrade] ?? 0) * promedios[0];
  const tolFracY = (toleranceTable["fan pressure"]?.[toleranceGrade] ?? 0) * promedios[1];
  // en datos absolutos, ±tolFracX y ±tolFracY
  const x0 = x(promedios[0] - tolFracX), x1 = x(promedios[0] + tolFracX);
  const y0 = y(promedios[1] + tolFracY), y1 = y(promedios[1] - tolFracY);

  svg.append("rect")
     .attr("x", x0)
     .attr("y", y0)
     .attr("width", x1 - x0)
     .attr("height", y1 - y0)
     .attr("fill", "none")
     .attr("stroke", "orange")
     .attr("stroke-width", 2)
     .attr("stroke-dasharray", "4 2");

  graphContainer.appendChild(svg.node());
}

function updateFanChart(data, chart_type, promedios, data2, toleranceGrade, toleranceParam) {
  // idéntico a createFanChart: podrías extraer la lógica común
  createFanChart(data, chart_type, promedios, data2, toleranceGrade, toleranceParam);
}
