
  const API_FIELDS = '/api/historial/fields/';

  // Lista de campos que queremos como opciones
  const OPCIONES = [
    'qf', 'q1', 'pe_v', 'pd_v', 'presion_t', 'tbs', 'tbh', 'lc', 'tgbh'
  ];

  // Crea un <div class="col-4"> con input+label
  function crearOpcionRadio(name, verbose) {
    const col = document.createElement('div');
    col.className = 'col-4';
    
    const input = document.createElement('input');
    input.type = 'radio';
    input.className = 'btn-check';
    input.name = 'tipo';
    input.id = `tipo_${name}`;
    input.setAttribute('data-nombre', verbose);
    input.value = name;
    
    input.autocomplete = 'off';
    const label = document.createElement('label');
    // text-nowrap evita saltos de línea
    label.className = 'grafico-card p-2 border rounded d-block text-nowrap';
    label.htmlFor = input.id;
    label.textContent = verbose;  // sin <br>, todo en la misma línea
    col.appendChild(input);
    col.appendChild(label);
    return col;
  }

  document.addEventListener('DOMContentLoaded', () => {
    fetch(API_FIELDS)
      .then(res => res.json())
      .then(fields => {
        const container = document.getElementById('tipoContainer');
        OPCIONES.forEach(key => {
          const campo = fields.find(f => f.name === key);
          if (campo) {
            container.appendChild(crearOpcionRadio(campo.name, campo.verbose_name));
          }
        });
      })
      .catch(err => console.error('Error cargando campos:', err));
  });

