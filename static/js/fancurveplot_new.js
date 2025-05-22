function createFanChart(data, chartType, promedios, data2) {
  // 1) Destruye cualquier chart previo
  if (am5.Root._roots[chartType]) {
    am5.Root._roots[chartType].dispose();
  }

  // 2) Crea el root y tema
  var root = am5.Root.new(chartType);
  root.setThemes([ am5themes_Animated.new(root) ]);

  // 3) XYChart con zoomX y panX habilitados
  var chart = root.container.children.push(
    am5xy.XYChart.new(root, {
      panX: true,
      panY: true,
      wheelX: "panX",
      wheelY: "zoomX",
      pinchZoomX: true,
      layout: root.verticalLayout
    })
  );

  // 4) Detecta dinámicamente los campos X e Y
  var keys = Object.keys(data[0]);
  var fieldX = keys[0];
  var fieldY = keys[1];

  // 5) Crea ejes numéricos, incluyendo el promedio en los dominios
  var maxX = Math.max(d3.max(data, d => d[fieldX]), promedios[0]);
  var maxY = Math.max(d3.max(data, d => d[fieldY]), promedios[1]);

  var xAxis = chart.xAxes.push(
    am5xy.ValueAxis.new(root, {
      renderer: am5xy.AxisRendererX.new(root, { minGridDistance: 50 }),
      min: 0,
      max: maxX,
      strictMinMax: true
    })
  );
  var yAxis = chart.yAxes.push(
    am5xy.ValueAxis.new(root, {
      renderer: am5xy.AxisRendererY.new(root, { minGridDistance: 30 }),
      min: 0,
      max: maxY,
      strictMinMax: true
    })
  );

  // 6) Serie principal (curva suavizada)
  var series = chart.series.push(
    am5xy.SmoothedXLineSeries.new(root, {
      name: "Curva",
      xAxis: xAxis,
      yAxis: yAxis,
      valueXField: fieldX,
      valueYField: fieldY,
      stroke: am5.color(0x000000),
      strokeWidth: 2,
      sequencedInterpolation: true
    })
  );
  series.bullets.push(function() {
    return am5.Bullet.new(root, {
      sprite: am5.Circle.new(root, {
        radius: 4,
        fill: series.get("stroke"),
        stroke: root.interfaceColors.get("background"),
        strokeWidth: 2
      })
    });
  });
  series.data.setAll(data);

  // 7) Segunda serie opcional (data2)
  if (Array.isArray(data2) && data2.length) {
    var series2 = chart.series.push(
      am5xy.SmoothedXLineSeries.new(root, {
        name: "Curva 2",
        xAxis: xAxis,
        yAxis: yAxis,
        valueXField: fieldX,
        valueYField: fieldY,
        stroke: am5.color(0x666666),
        strokeWidth: 1.5,
        strokeDasharray: [4,4]
      })
    );
    series2.data.setAll(data2);
  }

  // 8) Punto de promedio (solo un bullet rojo)
  var avgSeries = chart.series.push(
    am5xy.LineSeries.new(root, {
      name: "Promedio",
      xAxis: xAxis,
      yAxis: yAxis,
      valueXField: fieldX,
      valueYField: fieldY,
      strokeOpacity: 0  // sin línea
    })
  );
  avgSeries.bullets.push(function() {
    return am5.Bullet.new(root, {
      sprite: am5.Circle.new(root, {
        radius: 8,
        fill: am5.color(0xFF0000),
        stroke: am5.color(0xFFFFFF),
        strokeWidth: 2
      })
    });
  });
  avgSeries.data.setAll([
    { [fieldX]: promedios[0], [fieldY]: promedios[1] }
  ]);

  // 9) Cursor
  var cursor = chart.set("cursor", am5xy.XYCursor.new(root, { behavior: "none" }));
  cursor.lineY.set("visible", false);

  // 10) Scrollbar X
  chart.set("scrollbarX", am5.Scrollbar.new(root, { orientation: "horizontal" }));

  // 11) Animaciones de entrada
  series.appear(1000);
  if (series2) series2.appear(1000);
  avgSeries.appear(1000);

  return root;
}

function updateFanChart(data, chartType, promedios, data2) {
  return createFanChartAm(data, chartType, promedios, data2);
}
