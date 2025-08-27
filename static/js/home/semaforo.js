// Utilidades de color
const COLOR_CLASSES = 'bg-semaforo-verde bg-semaforo-amarillo bg-semaforo-rojo bg-neutral';
const colorToClass = (c) => {
  const key = (c || '').toString().toLowerCase();
  if (key === 'verde')   return 'bg-semaforo-verde';
  if (key === 'amarillo')return 'bg-semaforo-amarillo';
  if (key === 'rojo')    return 'bg-semaforo-rojo';
  return 'bg-neutral';
};
const setColorClass = ($el, color) => $el.removeClass(COLOR_CLASSES).addClass(colorToClass(color));

// Inicio
$(document).ready(function() {
  var semaforoInterval = $('#semaforo').data('interval');
  var semaforoIntervalmili = semaforoInterval * 1000;

  var countdown = semaforoInterval;
  $('#countdownDisplay').text('Próxima actualización en ' + countdown + ' segundos.');

  if (!semaforoInterval || semaforoInterval === 'none') {
    semaforoInterval = 60;
    semaforoIntervalmili = 60000;
  }
  setInterval(get_semaforo, semaforoIntervalmili);
});

// Cambiar luces del semáforo (roja/amarilla/verde)
function cambiarSemaforo(color) {
  // Poner todas en neutral
  setColorClass($('#luz-roja'),     'neutral');
  setColorClass($('#luz-amarilla'), 'neutral');
  setColorClass($('#luz-verde'),    'neutral');

  // Encender la correspondiente
  if (color === 'rojo')      setColorClass($('#luz-roja'), 'rojo');
  else if (color === 'amarillo') setColorClass($('#luz-amarilla'), 'amarillo');
  else if (color === 'verde')    setColorClass($('#luz-verde'), 'verde');
}

// Modal
function mostrarContenidoModal(color) {
  get_semaforo();
  let modalLabel = document.getElementById('modalSemaforoLabel');
  modalLabel.textContent = 'Color ' + color;
}

// Tarjetas “cuadros de color” (usa clases)
function actualizarColorCuadros(colorData) {
  for (let [elementId, color] of Object.entries(colorData)) {
    const $box = $('#' + elementId);
    if ($box.length === 0) continue;
    setColorClass($box, color);
  }
}

// AJAX (igual que lo tienes)
function get_semaforo() {
  $.ajax({
    url: "v1/semaforo",
    type: "GET",
    success: function(data) {
      if (data && data.error) {
        if ($('#mensaje-error-semaforo').length === 0) {
          $('#semaforo').after('<div id="mensaje-error-semaforo" class="text-danger mt-2">' + data.error + '</div>');
        } else {
          $('#mensaje-error-semaforo').text(data.error);
        }
        return;
      } else {
        $('#mensaje-error-semaforo').remove();
      }

      var semaforo = data.data.detalle_semaforo;
      var v1 = semaforo.v1;

      cambiarSemaforo(semaforo.color);
      actualizarV1(v1);
      actualizarV2(semaforo.v2);
      actualizarV3(semaforo.v3);
      actualizarV4(semaforo.v4);
      actualizarV5(semaforo.v5);
      actualizarV6(semaforo.v6);
      actualizarV7(semaforo.v7);

      $("#sensor").html(semaforo.sensor);
      $("#sensor table").addClass("table");
      $("#vdf").html(semaforo.vdf);
      $("#vdf table").addClass("table");

      const colorData = {
        'color-caudal-frente': v1.color,
        'color-velocidad-aire': semaforo.v2.color,
        'color-tgbh': semaforo.v3.color,
        'color-leakage-coefficient': semaforo.v4.color,
        'color-punto-stall': semaforo.v5.color,
        'color-fugas': semaforo.v6.color,
        'color-potencia': semaforo.v7.color
      };
      const tooltipValues = {
        'tooltip-caudal-frente': v1.message,
        'tooltip-velocidad-aire': semaforo.v2.message,
        'tooltip-tgbh': semaforo.v3.message,
        'tooltip-leakage-coefficient': semaforo.v4.message,
        'tooltip-punto-stall': semaforo.v5.message,
        'tooltip-fugas': semaforo.v6.message,
        'tooltip-potencia': semaforo.v7.message
      };

      actualizarColorCuadros(colorData);
      aplicarTooltips(tooltipValues);
    },
    error: function(xhr, status, error) {
      let errorMsg = "Error: ";
      if (xhr.responseJSON && xhr.responseJSON.error) {
        errorMsg += xhr.responseJSON.error;
      } else {
        errorMsg += error;
      }
      if ($('#mensaje-error-semaforo').length === 0) {
        $('#semaforo').after('<div id="mensaje-error-semaforo" class="text-danger mt-2">' + errorMsg + '</div>');
      } else {
        $('#mensaje-error-semaforo').text(errorMsg);
      }
    }
  });
}

function aplicarTooltips(tooltipValues) {
  for (const [id, tooltip] of Object.entries(tooltipValues)) {
    const elemento = document.getElementById(id);
    if (elemento) {
      elemento.title = tooltip;
    } else {
      console.warn(`Elemento con id "${id}" no encontrado para tooltip.`);
    }
  }
}

// ---- Actualizadores V1..V7 usando clases ----

function actualizarV1(v1) {
  setColorClass($('#v1_estado'), v1.color);
  setColorClass($('#color-caudal-frente'), v1.color);

  $('#v1_Q2').text(v1.Q2);
  $('#v1_q_frente').text(v1.Qf);
  $('#v1_pt2').text(v1.pt2);
  $('#v1_lc').text(v1.lc);
  $('#v1_lf').text(v1.lf);
  $('#v1_formula').text(v1.formula);

  const $semaforo = $('#v1_semaforo');
  if (v1.color === 'verde') {
    setColorClass($semaforo, 'verde');
    $semaforo.text('Caudal sobre requerimiento');
  } else {
    setColorClass($semaforo, 'rojo');
    $semaforo.text('Caudal bajo requerimiento');
  }
}

function actualizarV2(v2) {
  setColorClass($('#v2_estado'), v2.color);
  $('#v2_vel_aire_min').text(v2.Vmin);
  $('#v2_q_ventilador_min').text(v2.q_ventilador);
  $('#v2_vel_aire_max').text(v2.Vmax);
  $('#v2_q_frente').text(v2.q_frente);
  $('#v2_Q1').text(v2.Q1);
  $('#v2_area_galeria').text(v2.Area_galeria);
  $('#v2_vel_aire').text(v2.velocidad_del_aire);
  $('#v2_formula').text(v2.formula);
}

function actualizarV3(v3) {
  setColorClass($('#v3_estado'), v3.color);
  $('#v3_tbs').text(v3.tbs);
  $('#v3_tbh').text(v3.tbh);
  $('#v3_min').text(v3.min);
  $('#v3_max').text(v3.max);
  $('#v3_nivel_carga').text(v3.nivel_carga);
  $('#v3_tgbh').text(v3.tgbh);
  $('#v3_tgbh2').text(v3.tgbh);
  $('#v3_formula').text(v3.formula);
}

function actualizarV4(v4) {
  setColorClass($('#v4_estado'), v4.color);
  $('#v4_lc').text(v4.Lc);

  const info = 
`L: ${v4.L}      Q1: ${v4.Q1}
Q2: ${v4.Q2}     pt1: ${v4.pt1}
pt2: ${v4.pt2}`;
  $('#v4_values').css('white-space', 'pre').text(info);
  $('#v4_formula').text(v4.formula);
}

function actualizarV5(v5) {
  setColorClass($('#v5_estado'), v5.color);
  $('#v5_pt2').text(v5.pt2);
  $('#v5_presion_maxima').text(v5.presion_maxima);
  $('#v5_formula').text(v5.formula);
  $('#v5_stall').text(v5.stall);

  const $semaforo = $('#v5_semaforo');
  if (v5.color === 'verde') {
    setColorClass($semaforo, 'verde');
    $semaforo.text('TGBH dentro del Rango de T°');
  } else {
    setColorClass($semaforo, 'rojo');
    $semaforo.text('TGBH fuera del Rango de T°');
  }
}

function actualizarV6(v6) {
  setColorClass($('#v6_estado'), v6.color);

  if (v6.color === "verde") {
    $('#semaforo_messages').text("").removeClass('text-success text-danger text-warning');
  } else if (v6.color === "amarillo") {
    $('#v6_message').text(v6["message"]);
    $('#semaforo_messages').text(v6["message"])
      .removeClass('text-success text-danger text-warning')
      .addClass('text-warning');
  } else if (v6.color === "rojo") {
    $('#v6_message').text(v6["message"]);
    $('#semaforo_messages').text(v6["message"])
      .removeClass('text-success text-danger text-warning')
      .addClass('text-danger');
  }

  $('#v6_intervalo_segundos').text(v6["intervalo en segundos"]);
  $('#v6_presion_actual').text(v6["presion actual"]);
  $('#v6_presion_hace30m').text(v6["presion hace30m"]);
  $('#v6_porcentaje').text(v6["porcentaje"]);
  $('#v6_porcentaje2').text(v6["porcentaje"]);
}

function actualizarV7(v7) {
  setColorClass($('#v7_estado'), v7.color);

  $('#v7_power').text(v7.power);
  $('#v7_potencia_consumida').text(v7.potencia_consumida);
  $('#v7_potencia_porcent').text(v7.potencia_porcent);
  $('#v7_formula').text(v7.formula);

  const $semaforo = $('#v7_semaforo');
  if (v7.color === "verde") {
    setColorClass($semaforo, 'verde');
    $semaforo.text('Potencia dentro del rango');
  } else {
    setColorClass($semaforo, 'rojo');
    $semaforo.text('Potencia fuera del rango');
  }
}
