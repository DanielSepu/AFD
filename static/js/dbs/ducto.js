$(document).ready(function() {
    const tipo_ducto_select = $("#id_t_ducto");
    var item_initial = tipo_ducto_select.val();

    valor_actual = 0;
    if (item_initial === "ovalado") {
        valor_actual = $("#id_area").val();
        insert_area();
        
    }
    if (item_initial === "circular") {
        valor_actual = $("#id_diametro").val();
        //insertar_diametro();
    }
    //alert(valor_actual);
    

    $(tipo_ducto_select).on("change", function() {
        const tipo_ducto_value = $(this).val();
        $('#value_diametro').remove();
        if (tipo_ducto_value == "circular") {
            estado = check_if_exist("circular");
            if(!estado){
                insertar_diametro();
            }
        }
        if (tipo_ducto_value == "ovalado") {
            estado = check_if_exist("ovalado");
            if(!estado){
                insert_area();
            }
            
        }
    });
});


$(document).on("change","#base", function() {
    calculate_area();
});
$(document).on("change","#altura", function() {

    calculate_area();
});
$(document).on("change", "#id_diametro", function() {
    calculate_area_from_diameter();
});
function calculate_area() {
    const base_value = parseFloat($("#base").val());
    const altura_value = parseFloat($("#altura").val());
    var area = (3.14159*((base_value/1000) * (altura_value/1000)))/4;
    $("#id_area").val(area.toFixed(2));

};

function calculate_area_from_diameter() {
    const diametro_value = parseFloat($("#id_diametro").val());

    if (!isNaN(diametro_value) && diametro_value > 0) {
        var area = (Math.PI * Math.pow(diametro_value / 100, 2)) / 4; // Convertir cm y calcular área
        $("#id_area").val(area.toFixed(2)); // Ajuste de precisión para evitar redondeos excesivos
    } else {
        $("#id_area").val(""); // Limpiar si el valor no es válido
    }
}



function insertar_diametro() {
    const item_initial = $("#id_t_ducto");

    // Crear el contenedor si no existe
    if ($("#value_diametro").length === 0) {
        var combined_html = `
            <div id="value_diametro" class="row p-2">
                <div id="zona_diametro" class="col">
                    <label for="id_diametro">Diámetro (mm):</label>
                </div>
            </div>`;
        $(item_initial).after(combined_html);
    }

    // Verifica si el input existe, si no, lo crea
    var diametro_input = $("#id_diametro");
    if (diametro_input.length === 0) {
        diametro_input = $('<input>')
            .attr("type", "number")
            .attr("id", "id_diametro")
            .attr("name", "diametro")
            .attr("class", "form-control");
    }

    // Asegurar que el input esté dentro del contenedor correcto
    diametro_input.detach().appendTo("#zona_diametro");
}


function insert_area(){
    const item_initial = $("#id_t_ducto");

    var base_input = '<input class="form-control" id="base" type="number" />'
    var altura_input = '<input class="form-control" id="altura" type="number" />'

    var base_label = '<label class="form-label" for="base">Base (mm):</label>'
    var altura_label = '<label class="form-label" for="altura">Altura (mm):</label> '
    

    var combined_html = `
        <div id="value_area" class="row p-2">
            <div class="col-3 m-2">
                ${base_label}
                ${base_input}
            </div>
            <div class="col-3 m-2">
                ${altura_label}
                ${altura_input}
            </div>
        </div>`

    $(item_initial).after(combined_html);
    //$("#id_area").detach().appendTo("#zona_area");
 
}

function check_if_exist(tipo){
    if(tipo == "circular"){
        if($("#value_area").length > 0) {
            $("#value_area").remove();  // Eliminar el área si existe
        }
        if($("#value_diametro").length > 0) {
            $("#value_diametro").show();
            return true;
        }
    }
    if(tipo == "ovalado"){
        if($("#id_diametro").length > 0) {
            $("#id_diametro").remove();  // Eliminar el diámetro si existe
            const labelDiametro = document.querySelector('label[for="id_diametro"]');
            if (labelDiametro) {
                labelDiametro.remove();
            }
        }

        if($("#value_area").length > 0) {
            $("#value_area").show();
            return true;
        }
    }
    return false;
}
