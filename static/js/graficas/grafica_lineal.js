let graficoModalInstance = null;
let miGrafico = null;
// Generate random data
var date = new Date();
date.setHours(0, 0, 0, 0);

document.getElementById('graficoModal').addEventListener('hidden.bs.modal', function () {
  // Limpiar manualmente backdrop si queda
  const backdrop = document.querySelector('.modal-backdrop');
  if (backdrop) {
    backdrop.remove();
  }

  // Liberar memoria del gráfico 
  if (window.am5 && am5.registry.rootElements.length > 0) {
    am5.registry.rootElements.forEach(root => {
      root.dispose(); // libera recursos del gráfico
    });
  }

  // Reiniciar instancia de modal si se quiere forzar recarga futura
  graficoModalInstance = null;
});

function seleccionarGrafico(element, campo) {
  campoSeleccionado = campo;

  // Quitar selección visual de todos los recuadros
  document.querySelectorAll(".grafico-card").forEach(card => {
    card.classList.remove("bg-primary", "text-white");
  });

  // Aplicar selección visual al actual
  element.classList.add("bg-primary", "text-white");
}

function aplicarFiltro(event) {
  event.preventDefault();

  const campoSeleccionado = document.querySelector('input[name="tipo"]:checked');
  if (!campoSeleccionado) {
    alert("Por favor selecciona un tipo de gráfica.");
    return false;
  }

  const tipo = campoSeleccionado.value;
  const nombreDescriptivo = campoSeleccionado.getAttribute("data-nombre");
  const inicio = document.getElementById("fechaInicio").value;
  const fin = document.getElementById("fechaFin").value;

   // Actualizar el título del modal
   const tituloModal = document.getElementById("graficoModalLabel");
   if (tituloModal) {
     tituloModal.textContent = `Gráfico: ${nombreDescriptivo}`;
   }

  let url = `/api/grafico/?tipo=${tipo}`;
  if (inicio) url += `&inicio=${inicio}`;
  if (fin) url += `&fin=${fin}`;

  mostrarModal();

  fetch(url)
    .then(response => response.json())
    .then(data => {
      mostrarModal();
      
      window.initGraficoAmCharts(data); 
    })
    .catch(error => {
      console.error("Error al obtener datos del gráfico:", error);
    });


  return false;
}


function mostrarModal() {
  const modalEl = document.getElementById('graficoModal');

  if (!graficoModalInstance) {
    graficoModalInstance = bootstrap.Modal.getOrCreateInstance(modalEl);
  }

  graficoModalInstance.show();
}


am5.ready(function () {
  let root, chart, series;

  // Inicializar gráfico una sola vez
  function inicializarGrafico() {
    root = am5.Root.new("chartdiv");

    root.setThemes([
      am5themes_Animated.new(root)
    ]);

    chart = root.container.children.push(am5xy.XYChart.new(root, {
      panX: true,
      panY: true,
      wheelX: "panX",
      wheelY: "zoomX",
      pinchZoomX: true,
      paddingLeft: 0
    }));

    const cursor = chart.set("cursor", am5xy.XYCursor.new(root, {
      behavior: "none"
    }));
    cursor.lineY.set("visible", false);

    const xAxis = chart.xAxes.push(am5xy.DateAxis.new(root, {
      baseInterval: { timeUnit: "minute", count: 1 },
      renderer: am5xy.AxisRendererX.new(root, { minorGridEnabled: true }),
      tooltip: am5.Tooltip.new(root, {})
    }));

    const yAxis = chart.yAxes.push(am5xy.ValueAxis.new(root, {
      renderer: am5xy.AxisRendererY.new(root, { pan: "zoom" })
    }));

    series = chart.series.push(am5xy.LineSeries.new(root, {
      name: "Serie dinámica",
      xAxis: xAxis,
      yAxis: yAxis,
      valueYField: "value",
      valueXField: "date",
      tooltip: am5.Tooltip.new(root, {
        labelText: "{valueY}"
      })
    }));


    series.appear(1000);
    chart.appear(1000, 100);
  }

  // Función para actualizar el gráfico con nuevos datos
  function renderizarGrafico(data) {
    const datosFormateados = data.labels.map((label, i) => {
      // Conversión de fecha básica (se puede ajustar según formato)
      const date = new Date(`${label} ${new Date().getFullYear()}`);
      return {
        date: date.getTime(),
        value: data.data[i]
      };
    });

    series.data.setAll(datosFormateados);
    series.set("name", data.label || "Datos");
  }

  // Hacer la función accesible desde afuera
  window.initGraficoAmCharts = function(data) {
    // Si no hay ningún root en el registro, (re)inicializamos
    if (!window.am5.registry.rootElements.length) {
      inicializarGrafico();
    }
    renderizarGrafico(data);
  };
  
});

