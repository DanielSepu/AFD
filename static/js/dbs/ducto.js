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
        insertar_diametro();
    }
    //alert(valor_actual);
    

    $(tipo_ducto_select).on("change", function() {
        const tipo_ducto_value = $(this).val();
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

function calculate_area() {
    const base_value = parseFloat($("#base").val());
    const altura_value = parseFloat($("#altura").val());
    var area = (3.14159*((base_value/1000) * (altura_value/1000)))/4;
    $("#id_area").val(area.toFixed(2));

};

function insertar_diametro(){
    const item_initial = $("#id_t_ducto");
    var diametro_label = '<label for="diametro">Diámetro (mm):</label> '
    var diametro_input = $("#id_diametro");
    diametro_input.attr("type", "number");
    diametro_input.attr("class", "form-control");
    
    
    var combined_html = `
        <div id="value_diametro" class="row p-2">
            <div id="zona_diametro" class="col">
                ${diametro_label}
                
            </div>
        </div>`
    $(item_initial).after(combined_html);
    $("#id_diametro").detach().appendTo("#zona_diametro");
}

function insert_area(){
    const item_initial = $("#id_t_ducto");

    var base_input = '<input class="form-control" id="base" type="number" />'
    var altura_input = '<input class="form-control" id="altura" type="number" />'
    var area_input = $("#id_area");
    area_input.attr("type", "number");
    area_input.attr("class", "form-control");
    area_input.attr("readonly", "true");

    var area_label = '<label for="area" class="form-label">Área (m²):</label> '
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
            <div id="zona_area" class="col-3 m-2">
                ${area_label}
            </div>
        </div>`

    $(item_initial).after(combined_html);
    $("#id_area").detach().appendTo("#zona_area");
 
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
        if($("#value_diametro").length > 0) {
            $("#value_diametro").remove();  // Eliminar el diámetro si existe
        }
        if($("#value_area").length > 0) {
            $("#value_area").show();
            return true;
        }
    }
    return false;
}
