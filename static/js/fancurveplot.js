// Márgenes y tablas auxiliares
const margin = { top: 20, right: 30, bottom: 40, left: 40 };

const toleranceTable = {
  "volume flow rate": { AN1: 0.01, AN2: 0.025, AN3: 0.05, AN4: 0.10 },
  "fan pressure":      { AN1: 0.01, AN2: 0.025, AN3: 0.05, AN4: 0.10 },
  "power":             { AN1: 0.02, AN2: 0.03,  AN3: 0.08, AN4: 0.16 }
};

const unidades = {
  presion: "Pa",
  caudal: "m³/s",
  potencia: "kW"
};

const capitalizeFirst = (str) => {
  if (!str) return str;
  return str.charAt(0).toUpperCase() + str.slice(1);
};

const getKeyWithUnit = (key) => {
  const base = unidades[key] ? `${key} (${unidades[key]})` : key;
  return capitalizeFirst(base);
};


function createFanChart(
  dataOriginal,
  dataAjustada,
  chart_type,
  promedios,
  toleranceGrade,
  toleranceParam
) {
  const graphContainer = document.getElementById(chart_type);
  graphContainer.innerHTML = "";

  const wrapper = document.getElementById("graphContainer");
  const width  = wrapper.clientWidth - margin.right;
  const height = wrapper.clientHeight;

  // Considerar ambos conjuntos de datos para escalas
  const allData = [...(dataOriginal || []), ...(dataAjustada || [])];
  if (!allData.length) return;

  // Asumimos que cada punto es objeto {xKey, yKey}; tomamos las 2 primeras claves
  const [xKey, yKey] = Object.keys(allData[0]);

  // Máximos considerando datos y promedios
  const maxXData = d3.max(allData, d => +d[xKey]) ?? 0;
  const maxYData = d3.max(allData, d => +d[yKey]) ?? 0;
  const maxX = Math.max(maxXData, promedios?.[0] ?? 0);
  const maxY = Math.max(maxYData, promedios?.[1] ?? 0);

  // === Holgura (padding) para que las líneas no terminen pegadas al borde ===
  const PAD_FRAC_X = 0.06; // 6% de holgura al final en X
  const PAD_FRAC_Y = 0.06; // 6% de holgura en Y 

  // Escalas con holgura y 'nice' para ejes bonitos
  const x = d3.scaleLinear()
    .domain([0, maxX * (1 + PAD_FRAC_X)])
    .nice()
    .range([margin.left * 2, width - margin.right]);

  const y = d3.scaleLinear()
    .domain([0, maxY * (1 + PAD_FRAC_Y)])
    .nice()
    .range([height - margin.bottom, margin.top]);

  const svg = d3.create("svg")
    .attr("width", width)
    .attr("height", height);

  // --- Gridlines ---
  function make_x_gridlines() {
    return d3.axisBottom(x).ticks(10);
  }
  function make_y_gridlines() {
    return d3.axisLeft(y).ticks(10);
  }

  // Gridlines horizontales
  svg.append("g")
    .attr("class", "grid")
    .attr("transform", `translate(0,${height - margin.bottom})`)
    .call(
      make_x_gridlines()
        .tickSize(-(height - margin.top - margin.bottom))
        .tickFormat("")
    );

  // Gridlines verticales
  svg.append("g")
    .attr("class", "grid")
    .attr("transform", `translate(${margin.left * 2},0)`)
    .call(
      make_y_gridlines()
        .tickSize(-(width - margin.left * 2 - margin.right))
        .tickFormat("")
    );

  // Ejes y etiquetas
  svg.append("g")
    .attr("transform", `translate(0,${height - margin.bottom})`)
    .call(d3.axisBottom(x));
  svg.append("g")
    .attr("transform", `translate(${margin.left * 2},0)`)
    .call(d3.axisLeft(y));

  svg.append("text")
    .attr("x", width / 2)
    .attr("y", height)
    .style("text-anchor", "middle")
    .text(getKeyWithUnit(xKey));

  svg.append("text")
    .attr("transform", "rotate(-90)")
    .attr("x", -height / 2)
    .attr("y", margin.left / 2)
    .style("text-anchor", "middle")
    .text(getKeyWithUnit(yKey));

  // Puntos de dataOriginal
  svg.selectAll(".dot-original")
    .data(dataOriginal || [])
    .enter()
    .append("circle")
    .attr("class", "dot-original")
    .attr("cx", d => x(d[xKey]))
    .attr("cy", d => y(d[yKey]))
    .attr("r", 5)
    .attr("fill", "#2074b7"); // Azul para original

  // Puntos de dataAjustada
  svg.selectAll(".dot-ajustada")
    .data(dataAjustada || [])
    .enter()
    .append("circle")
    .attr("class", "dot-ajustada")
    .attr("cx", d => x(d[xKey]))
    .attr("cy", d => y(d[yKey]))
    .attr("r", 5)
    .attr("fill", "#c72c41"); // Rojo para ajustada

  // Curva Original (azul)
  svg.append("path")
    .datum(dataOriginal || [])
    .attr("fill", "none")
    .attr("stroke", "#2074b7")
    .attr("stroke-width", 2)
    .attr("d",
      d3.line()
        .curve(d3.curveBasis)
        .x(d => x(d[xKey]))
        .y(d => y(d[yKey]))
    );

  // Curva Ajustada (roja, punteada)
  svg.append("path")
    .datum(dataAjustada || [])
    .attr("fill", "none")
    .attr("stroke", "#c72c41")
    .attr("stroke-width", 2)
    .attr("stroke-dasharray", "6,2")
    .attr("d",
      d3.line()
        .curve(d3.curveBasis)
        .x(d => x(d[xKey]))
        .y(d => y(d[yKey]))
    );

  // Punto promedio
  if (Array.isArray(promedios) && promedios.length >= 2) {
    const cx = x(promedios[0]);
    const cy = y(promedios[1]);
    svg.append("circle")
      .attr("cx", cx)
      .attr("cy", cy)
      .attr("r", 8)
      .attr("fill", "red");

    // Cuadro de tolerancia (usa toleranceParam para X y "fan pressure" para Y)
    const tolFracX = (toleranceTable[toleranceParam]?.[toleranceGrade] ?? 0) * promedios[0];
    const tolFracY = (toleranceTable["fan pressure"]?.[toleranceGrade] ?? 0) * promedios[1];

    const x0 = x(promedios[0] - tolFracX);
    const x1 = x(promedios[0] + tolFracX);
    const y0 = y(promedios[1] + tolFracY);
    const y1 = y(promedios[1] - tolFracY);

    svg.append("rect")
      .attr("x", x0)
      .attr("y", y0)
      .attr("width", x1 - x0)
      .attr("height", y1 - y0)
      .attr("fill", "none")
      .attr("stroke", "orange")
      .attr("stroke-width", 2)
      .attr("stroke-dasharray", "4 2");
  }

  // Leyenda
  svg.append("circle").attr("cx", width - 120).attr("cy", 30).attr("r", 6).attr("fill", "#2074b7");
  svg.append("text").attr("x", width - 110).attr("y", 35).text("Diseño").style("font-size", "12px").attr("alignment-baseline", "middle");
  svg.append("circle").attr("cx", width - 120).attr("cy", 50).attr("r", 6).attr("fill", "#c72c41");
  svg.append("text").attr("x", width - 110).attr("y", 55).text("Actual").style("font-size", "12px").attr("alignment-baseline", "middle");

  graphContainer.appendChild(svg.node());
}
