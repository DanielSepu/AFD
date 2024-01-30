$("#id_curva_diseno").attr('disabled',false);
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
/*var a = 0;
setInterval(function(){
alert('Sorpresa '+a)
a = a +1;
},5000)*/