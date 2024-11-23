$(document).ready(function() {
    $("input[type='checkbox'][name^='eq_']").change(function() {
        var valor_actual_checkbox = $(this).data('value');
        var caudal_requerido_input = $("#id_caudal_requerido");
        
        var actual_caudal = caudal_requerido_input.val();
        if (!actual_caudal){
            actual_caudal = 0;
            
        }
        if(this.checked) {
            var sumatoria = parseInt(actual_caudal)+parseInt(valor_actual_checkbox);
            $(caudal_requerido_input).val(sumatoria);
            
        }
        else {
            if (parseInt(actual_caudal) >= parseInt(valor_actual_checkbox)){
                var resta = parseInt(actual_caudal)- parseInt(valor_actual_checkbox);
                $(caudal_requerido_input).val(resta);
            }

        }
    });
});



$(document).on('change','#id_ventilador',function(e){
    e.preventDefault(); 
    $.ajax({ 
        type:'POST', 
        url: "/settings/?type=new_project_2",
        data: 
        { 
            task:$("#id_ventilador").val(), 
            csrfmiddlewaretoken:$('input[name=csrfmiddlewaretoken]').val() 
        }, 
        success:function(response){
            $("#id_curva_diseno").attr('disabled',false);
            $("#id_curva_diseno").find('option').remove();
            $.each(response.cdpk, function(i, obj) {
                $("#id_curva_diseno").append('<option value=' + obj.pk + '>' + obj.fields['idu'] + '</option>');
            });
        } 
    }) 
});
$(document).on('change','#id_ancho_galeria',function(e){
    e.preventDefault();
    const a = $('#id_ancho_galeria').val();
    const b = $('#id_alto_galeria').val();
    const c = $('#id_factor').val()/100;
    $('#id_area_galeria').val((a*b)*c);
})
$(document).on('change','#id_alto_galeria',function(e){
    e.preventDefault();
    const a = $('#id_ancho_galeria').val();
    const b = $('#id_alto_galeria').val();
    const c = $('#id_factor').val()/100;
    $('#id_area_galeria').val((a*b)*c);
})     
$(document).on('change','#id_factor',function(e){
    e.preventDefault();
    const a = $('#id_ancho_galeria').val();
    const b = $('#id_alto_galeria').val();
    const c = $('#id_factor').val()/100;
    $('#id_area_galeria').val((a*b)*c);
})     
$(document).on('change','#id_equipamientos',function(e){
    e.preventDefault();
    $.ajax({ 
        type:'POST', 
        url: "/settings/?type=new_project_3", 
        data: 
        { 
            task:$("#id_equipamientos").val(), 
            csrfmiddlewaretoken:$('input[name=csrfmiddlewaretoken]').val() 
        }, 
        success:function(response){
            $('#id_caudal_requerido').val(response.sumatoria);
        }
    })
})