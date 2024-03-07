      // Config Grafico
      const margin = { top: 20, right: 30, bottom: 40, left: 40 };
      //const containerHeight = graphContainer.clientHeight;

      function  createFanChart(data, chart_type, promedios, data2) {
         // Get the dimensions of the container
         const containerWidth = graphContainer.clientWidth - margin.right;
         const containerHeight = graphContainer.clientHeight;
         //const containerHeight = 500;
         const keys = Object.keys(data[0]);
         // Declare the x (horizontal position) scale for "Q1".
            const x = d3.scaleLinear()
            .domain([0, d3.max(data, function(d) { return d[keys[0]]; })])
            .range([margin.left*2, containerWidth - margin.right]);

         // Declare the y (vertical position) scale for "Pt1".
            const y = d3.scaleLinear()
            .domain([0, d3.max(data, function(d) { return d[keys[1]]; })])
            .range([containerHeight - margin.bottom, margin.top]);

         // Create the SVG container.
         const svg = d3.create("svg")
            .attr("width", containerWidth)
            .attr("height", containerHeight);

         // Add the x-axis.
         svg.append("g")
         .attr("transform", `translate(0,${containerHeight - margin.bottom})`)
         .call(d3.axisBottom(x));

         // Add the y-axis.
         svg.append("g")
         .attr("transform", `translate(${margin.left*2},0)`)
         .call(d3.axisLeft(y));

         // Add x-axis title.
         svg.append("text")
            .attr("x", containerWidth / 2)
            .attr("y", containerHeight )
            .style("text-anchor", "middle")
            .text(keys[0]);

         // Add y-axis title.
         svg.append("text")
            .attr("transform", "rotate(-90)")
            .attr("x", 0 - containerHeight / 2)
            .attr("y", margin.left / 2)
            .style("text-anchor", "middle")
            .text(keys[1]);

         // Add the scatter plot points.
            svg.selectAll("circle")
            .data(data)
            .enter().append("circle")
            .attr("cx", function(d) { return x(d[keys[0]]); })
            .attr("cy", function(d) { return y(d[keys[1]]); })
            .attr("r", 5); // Tamaño de los puntos
            
         // Agregar punto de promedio  
         // Valores de ejemplo 
         svg.append("circle")
         .attr("cx", x(promedios[0]))
         .attr("cy", y(promedios[1]))
         .attr("r", 8) 
         .attr("fill", "red");
      

         // se ha agregado la linea   
            svg.append("path")
               .datum(data)
               .attr("fill", "none")
               .attr("stroke", "black")
               .attr("stroke-width", 1.5)
               .attr("d", d3.line()
               .curve(d3.curveBasis) // Just add that to have a curve instead of segments
               .x(function(d) { return x(d[keys[0]]); })
               .y(function(d) { return y(d[keys[1]]); })
            )
            
            svg.append("path")
               .datum(data2)
               .attr("fill", "none")
               .attr("stroke", "black")
               .attr("stroke-width", 1.5)
               .attr("d", d3.line()
               .curve(d3.curveBasis) // Just add that to have a curve instead of segments
               .x(function(d) { return x(d[keys[0]]); })
               .y(function(d) { return y(d[keys[1]]); })
            )


         // Append the SVG element.
         //graphContainer.innerHTML = ""; // Limpiar el contenedor antes de agregar el nuevo gráfico
         graphContainer.appendChild(svg.node());
      }

      // Function to update chart dimensions based on container size
      function updateFanChart(data) {
         console.log("resize");

         const keys = Object.keys(data[0]);
         
         // Get the dimensions of the container
         const containerWidth = graphContainer.clientWidth - margin.right;
         //const containerHeight = graphContainer.clientHeight;
         const containerHeight = 500;
         // Declare the x (horizontal position) scale for "Q1".
         const x = d3.scaleLinear()
         .domain([0, 120])
         .range([margin.left*2, containerWidth - margin.right]);
         // Declare the y (vertical position) scale for "Pt1".
         const y = d3.scaleLinear()
         .domain([0, d3.max(data, function(d) { return d[keys[1]]; })])
         .range([containerHeight - margin.bottom, margin.top]);
         // Remove any existing chart elements
         d3.select("#graphContainer").selectAll("*").remove()
         // Create the SVG container.
         const svg = d3.create("svg")
         .attr("width", containerWidth)
         .attr("height", containerHeight)
         // Add the x-axis.
         svg.append("g")
         .attr("transform", `translate(0,${containerHeight - margin.bottom})`)
         .call(d3.axisBottom(x))
         // Add the y-axis.
         svg.append("g")
            .attr("transform", `translate(${margin.left*2},0)`)
            .call(d3.axisLeft(y))
         // Add x-axis title.
         svg.append("text")
            .attr("x", containerWidth / 2)
            .attr("y", containerHeight )
            .style("text-anchor", "middle")
            .text(keys[0]);
         // Add y-axis title.
         svg.append("text")
            .attr("transform", "rotate(-90)")
            .attr("x", 0 - containerHeight / 2)
            .attr("y", margin.left / 2)
            .style("text-anchor", "middle")
            .text(keys[1]);
         // Add the scatter plot points.
         svg.selectAll("circle")
         .data(data)
         .enter().append("circle")
         .attr("cx", function(d) { return x(d[keys[0]]); })
         .attr("cy", function(d) { return y(d[keys[1]]); })
         .attr("r", 5); // Tamaño de los punto
         // Append the SVG element.
         graphContainer.appendChild(svg.node());
      }




      // Con imagen de fondo
      function  createFanChartImg(data, chart_type) {
         let imgPath;
         if(chart_type === 'total_pressure'){
            imgPath="../../media/img/FanCurveAXN.png";
         } else {
            imgPath = "../../media/img/FanCurveAXN.png";
         }
         // Get the dimensions of the container
         const containerWidth = graphContainer.clientWidth - margin.right;
         const containerHeight = graphContainer.clientHeight;
         //const containerHeight = 500;
         const keys = Object.keys(data[0]);
         // Declare the x (horizontal position) scale for "Q1".
         const x = d3.scaleLinear()
         .domain([0, d3.max(data, function(d) { return d[keys[0]]; })])
         .range([margin.left*2, containerWidth - margin.right]);

         // Declare the y (vertical position) scale for "Pt1".
         const y = d3.scaleLinear()
         .domain([0, d3.max(data, function(d) { return d[keys[1]]; })])
         .range([containerHeight - margin.bottom, margin.top]);

         // Create the SVG container.
         const svg = d3.create("svg")
            .attr("width", containerWidth)
            .attr("height", containerHeight);

         // Add pattern for the background image.
         svg.append("defs").append("pattern")
            .attr("id", "background-image")
            .attr("width", "100%")
            .attr("height", "100%")
            .attr("patternContentUnits", "objectBoundingBox")
            .append("image")
            .attr("width", 1)
            .attr("height", 1)
            .attr("preserveAspectRatio", "none")
            .attr("href", imgPath);

         // Add a rectangle with the pattern as the background.
         svg.append("rect")
            .attr("width", containerWidth - margin.left*2 - margin.right)
            .attr("height", containerHeight - margin.top - margin.bottom)
            .attr("x", margin.right*2.65)
            .attr("y", margin.top)
            .style("fill", "url(#background-image)");

         // Add the x-axis.
         svg.append("g")
         .attr("transform", `translate(0,${containerHeight - margin.bottom})`)
         .call(d3.axisBottom(x));

         // Add the y-axis.
         svg.append("g")
         .attr("transform", `translate(${margin.left*2},0)`)
         .call(d3.axisLeft(y));

         // Add x-axis title.
         svg.append("text")
            .attr("x", containerWidth / 2)
            .attr("y", containerHeight )
            .style("text-anchor", "middle")
            .text(keys[0]);

         // Add y-axis title.
         svg.append("text")
            .attr("transform", "rotate(-90)")
            .attr("x", 0 - containerHeight / 2)
            .attr("y", margin.left / 2)
            .style("text-anchor", "middle")
            .text(keys[1]);

         // Add the scatter plot points.
         svg.selectAll("circle")
         .data(data)
         .enter().append("circle")
         .attr("cx", function(d) { return x(d[keys[0]]); })
         .attr("cy", function(d) { return y(d[keys[1]]); })
         .attr("r", 5); // Tamaño de los puntos

         // Append the SVG element.
         //graphContainer.innerHTML = ""; // Limpiar el contenedor antes de agregar el nuevo gráfico
         graphContainer.appendChild(svg.node());
      }

      function updateFanChartImg(data) {
         console.log("resize");

         const keys = Object.keys(data[0]);
         
         // Get the dimensions of the container
         const containerWidth = graphContainer.clientWidth - margin.right;
         //const containerHeight = graphContainer.clientHeight;
         const containerHeight = 500;
         // Declare the x (horizontal position) scale for "Q1".
         const x = d3.scaleLinear()
         .domain([0, 120])
         .range([margin.left*2, containerWidth - margin.right]);
         // Declare the y (vertical position) scale for "Pt1".
         const y = d3.scaleLinear()
         .domain([0, d3.max(data, function(d) { return d[keys[1]]; })])
         .range([containerHeight - margin.bottom, margin.top]);
         // Remove any existing chart elements
         d3.select("#graphContainer").selectAll("*").remove()
         // Create the SVG container.
         const svg = d3.create("svg")
         .attr("width", containerWidth)
         .attr("height", containerHeight)
         // Add pattern for the background image.
         svg.append("defs").append("pattern")
            .attr("id", "background-image")
            .attr("width", "100%")
            .attr("height", "100%")
            .attr("patternContentUnits", "objectBoundingBox")
            .append("image")
            .attr("width", 1)
            .attr("height", 1)
            .attr("preserveAspectRatio", "none")
            .attr("href", "../../media/img/FanCurveAXN.png");
         // Add a rectangle with the pattern as the background.
         svg.append("rect")
            .attr("width", containerWidth - margin.left*2 - margin.right)
            .attr("height", containerHeight - margin.top - margin.bottom)
            .attr("x", margin.right*2.65)
            .attr("y", margin.top)
            .style("fill", "url(#background-image)");
         // Add the x-axis.
         svg.append("g")
         .attr("transform", `translate(0,${containerHeight - margin.bottom})`)
         .call(d3.axisBottom(x))
         // Add the y-axis.
         svg.append("g")
            .attr("transform", `translate(${margin.left*2},0)`)
            .call(d3.axisLeft(y))
         // Add x-axis title.
         svg.append("text")
            .attr("x", containerWidth / 2)
            .attr("y", containerHeight )
            .style("text-anchor", "middle")
            .text(keys[0]);
         // Add y-axis title.
         svg.append("text")
            .attr("transform", "rotate(-90)")
            .attr("x", 0 - containerHeight / 2)
            .attr("y", margin.left / 2)
            .style("text-anchor", "middle")
            .text(keys[1]);
         // Add the scatter plot points.
         svg.selectAll("circle")
         .data(data)
         .enter().append("circle")
         .attr("cx", function(d) { return x(d[keys[0]]); })
         .attr("cy", function(d) { return y(d[keys[1]]); })
         .attr("r", 5); // Tamaño de los punto
         // Append the SVG element.
         graphContainer.appendChild(svg.node());
      }