$(document).ready(function() {
    
    setInterval(get_semaforo, 30000);
    
});

function get_semaforo() {
    $.ajax({
        url:"v1/semaforo",
        type: "GET",
        success: function(data) {
            var semaforo = data.detalle_semaforo;
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
        },
        error: function(xhr, status, error) {
            alert("Error: " + error);
        }
    });
}

function actualizarV1(v1) {
    $('#v1_estado').css('background-color', v1.color === 'verde' ? '#d4edda' : '#f8d7da');
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
    $('#v2_estado_min').text(v2.estado_min).css('background-color', v2.estado_min === 1 ? '#d4edda' : '#f8d7da');
    $('#v2_vel_aire_min').text(v2.Vmin);
    $('#v2_q_ventilador_min').text(v2.q_ventilador);
    $('#v2_estado_max').text(v2.estado_max).css('background-color', v2.estado_max === 1 ? '#d4edda' : '#f8d7da');
    $('#v2_vel_aire_max').text(v2.Vmax);
    $('#v2_q_frente').text(v2.q_frente);
    $('#v2_Q1').text(v2.Q1);
    $('#v2_area_galeria').text(v2.Area_galeria);
    $('#v2_vel_aire').text(v2.velocidad_del_aire);
    $('#v2_formula').text(v2.formula);

    const $semaforo = $('#v2_semaforo');
    if (v2.vel_aire >= 0.25 && v2.vel_aire <= 2.5) {
        $semaforo.css({'background-color': '#28a745', 'color': 'white'}).text('0.25 m/s < Velocidad del aire < 2.5 m/s');
    } else {
        $semaforo.css({'background-color': '#dc3545', 'color': 'white'}).text('Velocidad del aire fuera de rango');
    }
}

function actualizarV3(v3) {
    $('#v3_estado').css('background-color', v3.color ==="verde" ? 'green ' : 'red');
    $('#v3_tbs').text(v3.tbs);
    $('#v3_tbh').text(v3.tbh);
    $('#v3_min').text(v3.min);
    $('#v3_max').text(v3.max);
    
    $('#v3_tgbh').text(v3.tgbh);
    $('#v3_tgbh2').text(v3.tgbh);
    $('#v2_formula').text(v3.formula);

    const $semaforo = $('#v3_semaforo');
    if (v3.color =="verde") {
        $semaforo.css({'background-color': '#28a745', 'color': 'white'}).text('TGBH dentro del Rango de T°');
    } else {
        $semaforo.css({'background-color': '#dc3545', 'color': 'white'}).text('TGBH fuera del Rango de T°');
    }
}


function actualizarV4(v4) {
    //console.log(v4);
    $('#v4_estado').css('background-color', v4.color ==="verde" ? 'green ' : 'red');
    $('#v4_lc').text(v4.Lc);
    $('#v4_values').text(`
            Donde: \n
            L (${v4.L}) = Distancia entre sensores \n
            Q1 (${v4.Q1}); Q2 (${v4.Q1})= Caudales medidos \n
            pt1 (${v4.pt1}); pt2 (${v4.pt2})= Presiones totales medidas
        `);
    
    $('#v4_formula').text(v4.formula);

    const $semaforo = $('#v4_semaforo');
    if (v4.color =="verde") {
        $semaforo.css({'background-color': '#28a745', 'color': 'white'}).text('TGBH dentro del Rango de T°');
    } else {
        $semaforo.css({'background-color': '#dc3545', 'color': 'white'}).text('TGBH fuera del Rango de T°');
    }
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
    $('#v6_estado').css('background-color', v6.color === "verde" ? 'green' : 'red');
    
    // Actualizar los valores recibidos en la interfaz
    $('#v6_intervalo_segundos').text(v6["intervalo en segundos"]);
    $('#v6_presion_actual').text(v6["presion actual"]);
    $('#v6_presion_hace30m').text(v6["presion hace30m"]);
    $('#v6_porcentaje').text(v6["porcentaje"]);
    $('#v6_porcentaje2').text(v6["porcentaje"]);

    // Configurar el semáforo basado en el color
    const $semaforo = $('#v6_semaforo');
    if (v6.color === "verde") {
        $semaforo.css({'background-color': '#28a745', 'color': 'white'}).text('Presión dentro del rango');
    } else {
        $semaforo.css({'background-color': '#dc3545', 'color': 'white'}).text('Presión fuera del rango');
    }
}

function actualizarV7(v7) {
    // console.log(v7);
    
    // Actualizar los valores recibidos en la interfaz
    $('#v7_power').text(v7.power);
    $('#v7_potencia_consumida').text(v7.potencia_consumida);
    $('#v7_potencia_porcent').text(v7.potencia_porcent);

    // Actualizar el estado del semáforo según el color recibido
    const $semaforo = $('#v7_semaforo');
    if (v7.color === "verde") {
        $semaforo.css({'background-color': '#28a745', 'color': 'white'}).text('Potencia dentro del rango');
    } else {
        $semaforo.css({'background-color': '#dc3545', 'color': 'white'}).text('Potencia fuera del rango');
    }
}






