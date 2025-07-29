// Función para cambiar el color de la luz del semáforo
$(document).ready(function() {
    
    var semaforoInterval = $('#semaforo').data('interval');
    var semaforoIntervalmili = semaforoInterval*1000
    
    var countdown = semaforoInterval;
    $('#countdownDisplay').text('Próxima actualización en ' + countdown + ' segundos.');
    // Actualizar la cuenta regresiva cada 1 segundo
    

    // Si el intervalo es cero, null, undefined o 'none', usar 1 minuto (60000 ms) por defecto
    if (!semaforoInterval || semaforoInterval === 'none') {
        semaforoInterval = 60;
        semaforoIntervalmili = 60000;
    }
    // Se inicia el intervalo usando el valor obtenido
    setInterval(get_semaforo, semaforoIntervalmili);
    
});

function cambiarSemaforo(color) {
    // Apagar todas las luces
    document.getElementById('luz-roja').classList.remove('bg-danger');
    document.getElementById('luz-amarilla').classList.remove('bg-warning');
    document.getElementById('luz-verde').classList.remove('bg-success');

    // Poner en estado inactivo (gris)
    document.getElementById('luz-roja').classList.add('bg-secondary');
    document.getElementById('luz-amarilla').classList.add('bg-secondary');
    document.getElementById('luz-verde').classList.add('bg-secondary');

    // Encender la luz correspondiente según el color pasado
    if (color === 'rojo') {
      document.getElementById('luz-roja').classList.remove('bg-secondary');
      document.getElementById('luz-roja').classList.add('bg-danger');
    } else if (color === 'amarillo') {
      document.getElementById('luz-amarilla').classList.remove('bg-secondary');
      document.getElementById('luz-amarilla').classList.add('bg-warning');
    } else if (color === 'verde') {
      document.getElementById('luz-verde').classList.remove('bg-secondary');
      document.getElementById('luz-verde').classList.add('bg-success');
    }
  }

  // Función para mostrar el contenido adecuado en el modal
  function mostrarContenidoModal(color) {
    get_semaforo()
    let contenidoModal = document.getElementById('contenidoModal');
    let modalLabel = document.getElementById('modalSemaforoLabel');

      modalLabel.textContent = 'Color ' + color;
      
  }
  function actualizarColorCuadros(colorData) {
    // colorData es un objeto con pares de id de tarjeta y color
    for (let [elementId, color] of Object.entries(colorData)) {
        // Obtener el elemento de cuadro de color usando el ID
        const colorBox = document.getElementById(elementId);
        if (!colorBox) continue;

        // Asignar el color correspondiente al cuadro
        switch (color.toLowerCase()) {
            case 'verde':
                colorBox.style.backgroundColor = 'green';
                break;
            case 'amarillo':
                colorBox.style.backgroundColor = 'yellow';
                break;
            case 'rojo':
                colorBox.style.backgroundColor = 'red';
                break;
            default:
                console.error('Color no válido para el elemento con ID:', elementId);
        }
    }
}

function get_semaforo() {
    $.ajax({
        url: "v1/semaforo",
        type: "GET",
        success: function(data) {
            // Si la respuesta contiene un error, mostrar el mensaje debajo del semáforo
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
            cambiarSemaforo(semaforo.color)
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
            // Actualiza los colores de los cuadros de las tarjetas
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


function actualizarV1(v1) {
    $('#v1_estado').css('background-color', v1.color === 'verde' ? 'green' : 'red');
    $('#color-caudal-frente').css('background-color', v1.color === 'verde' ? 'green' : 'red');
    $('#v1_Q2').text(v1.Q2);
    $('#v1_q_frente').text(v1.Qf);
    $('#v1_pt2').text(v1.pt2);
    $('#v1_lc').text(v1.lc);
    $('#v1_lf').text(v1.lf);
    $('#v1_formula').text(v1.formula);

    const $semaforo = $('#v1_semaforo');
    if (v1.color === 'verde') {
        $semaforo.css({'background-color': '#28a745', 'color': 'white'}).text('Caudal sobre requerimiento');
    } else {
        $semaforo.css({'background-color': '#dc3545', 'color': 'white'}).text('Caudal bajo requerimiento');
    }
}



function actualizarV2(v2) {
    $('#v2_estado').css('background-color', v2.color === 'verde' ? 'green' : 'red');
    
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
    $('#v3_estado').css('background-color', v3.color ==="verde" ? 'green ' : 'red');
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
    //console.log(v4);
    $('#v4_estado').css('background-color', v4.color ==="verde" ? 'green ' : 'red');
    $('#v4_lc').text(v4.Lc);
    $('#v4_values').css('white-space', 'pre').text(`
    L: ${v4.L}    Q1: ${v4.Q1} \n
    Q2: ${v4.Q1}  pt1: ${v4.pt1} \n
    pt2: ${v4.pt2}
    `);
    
    $('#v4_formula').text(v4.formula);

}


function actualizarV5(v5) {
    // console.log(v5);
    $('#v5_estado').css('background-color', v5.color ==="verde" ? 'green ' : 'red');
    $('#v5_pt2').text(v5.pt2);
    $('#v5_presion_maxima').text(v5.presion_maxima);
    $('#v5_formula').text(v5.formula);
    $('#v5_stall').text(v5.stall);

    const $semaforo = $('#v5_semaforo');
    if (v5.color =="verde") {
        $semaforo.css({'background-color': '#28a745', 'color': 'white'}).text('TGBH dentro del Rango de T°');
    } else {
        $semaforo.css({'background-color': '#dc3545', 'color': 'white'}).text('TGBH fuera del Rango de T°');
    }
}


function actualizarV6(v6) {
    // console.log(v6);
    // Actualizar el estado del semáforo según el color recibido
    
    if (v6.color === "verde") {
        $('#v6_estado').css('background-color', 'green');
        $('#semaforo_messages')
            .text("")
            .removeClass('text-success text-danger text-warning');
    } else if (v6.color === "amarillo") {
        $('#v6_estado').css('background-color', 'yellow');
        $('#v6_message').text(v6["message"]);
        $('#semaforo_messages')
            .text(v6["message"])
            .removeClass('text-success text-danger text-warning')
            .addClass('text-warning');

    } else if (v6.color === "rojo") {
        $('#v6_estado').css('background-color', 'red');

        $('#v6_message').text(v6["message"]);
        $('#semaforo_messages')
            .text(v6["message"])
            .removeClass('text-success text-danger text-warning')
            .addClass('text-danger');

    }
    
    // Actualizar los valores recibidos en la interfaz
    $('#v6_intervalo_segundos').text(v6["intervalo en segundos"]);
    $('#v6_presion_actual').text(v6["presion actual"]);
    $('#v6_presion_hace30m').text(v6["presion hace30m"]);
    $('#v6_porcentaje').text(v6["porcentaje"]);
    $('#v6_porcentaje2').text(v6["porcentaje"]);
    

}

function actualizarV7(v7) {
    // console.log(v7);
    
    // Actualizar los valores recibidos en la interfaz
    if (v7.color === "verde") {
        $('#v7_estado').css('background-color', 'green');
    } else if (v7.color === "amarillo") {
        $('#v7_estado').css('background-color', 'yellow');
    } else if (v7.color === "rojo") {
        $('#v7_estado').css('background-color', 'red');
    }
    $('#v7_power').text(v7.power);
    $('#v7_potencia_consumida').text(v7.potencia_consumida);
    $('#v7_potencia_porcent').text(v7.potencia_porcent);
    $('#v7_formula').text(v7.formula);

    // Actualizar el estado del semáforo según el color recibido
    const $semaforo = $('#v7_semaforo');
    if (v7.color === "verde") {
        $semaforo.css({'background-color': '#28a745', 'color': 'white'}).text('Potencia dentro del rango');
    } else {
        $semaforo.css({'background-color': '#dc3545', 'color': 'white'}).text('Potencia fuera del rango');
    }
}




