/* Cálculos documentales: funciones puras, sin consultas ni datos enviados. */
(() => {
  const format = value => new Intl.NumberFormat('es-AR', {maximumFractionDigits: 2}).format(value);
  const result = (title, body) => ({title, body});
  const invalid = () => result('Revisá los datos', 'Completá los campos con números finitos dentro del rango indicado.');
  function checkReadiness(checks, checked) {
    const pending = checks.filter((_, i) => checked[i] !== true).map(item => item[0]);
    const completed = checks.length - pending.length;
    return pending.length
      ? result(`${completed} de ${checks.length} comprobaciones registradas`, `Pendientes: ${pending.join(' · ')}. Marcá solo datos cotejados en documentos de la unidad.`)
      : result('Todas las comprobaciones registradas', 'La lista reúne lo que declaraste haber cotejado. No certifica compatibilidad, protección ni resultado de uso; conservá los documentos y seguí las instrucciones correspondientes.');
  }
  function calculate(kind, values, loads = []) {
    if (Object.values(values).some(value => value === '' || value === null || (typeof value === 'number' && (!Number.isFinite(value) || value < 0)))) return invalid();
    if (kind === 'rpm') {
      if (values.tool <= 0 || values.accessory <= 0) return invalid();
      const difference = values.accessory - values.tool;
      return difference < 0
        ? result('El accesorio queda por debajo del máximo del equipo', `Diferencia: ${format(-difference)} rpm. Este cruce no supera el filtro de velocidad; cotejá etiqueta y manual.`)
        : result('Se cumple solo la comparación de máximos de rpm', `Accesorio − herramienta = ${format(difference)} rpm. Todavía faltan pinza, diámetro, material y aplicación; no es una validación de compatibilidad.`);
    }
    if (kind === 'air') {
      if ([values.supply, values.supplyPressure, values.demand, values.demandPressure].some(value => value <= 0)) return invalid();
      if (Math.abs(values.supplyPressure - values.demandPressure) > 0.000001) return result('Las presiones no coinciden', 'No se calcula diferencia de caudal entre puntos de presión distintos. Pedí salida y consumo a la misma presión; no interpolamos fichas.');
      const delta = values.supply - values.demand;
      return result(delta < 0 ? 'El dato de salida queda por debajo del consumo' : delta === 0 ? 'Los caudales ingresados coinciden' : 'El dato de salida supera el consumo ingresado', `${format(values.supply)} − ${format(values.demand)} = ${format(delta)} L/min a ${format(values.supplyPressure)} bar. Esta resta no valida continuidad: faltan ciclo de trabajo y pérdidas.`);
    }
    if (kind === 'water') {
      if (values.flow <= 0 || values.minutes <= 0) return invalid();
      return result(`${format(values.flow * values.minutes)} litros teóricos`, `${format(values.flow)} L/min × ${format(values.minutes)} min con salida activa. No equivale a autonomía ni a tiempo de limpieza de una superficie.`);
    }
    if (kind === 'weight') {
      if (values.battery <= 0) return invalid();
      const total = 1.7 + values.battery;
      const difference = 3.6 - total;
      return result(`${format(total)} kg: cuerpo y batería ingresada`, `1,7 + ${format(values.battery)} = ${format(total)} kg. Frente a los 3,6 kg publicados para GSA 1100 E: ${difference >= 0 ? format(difference) + ' kg menos' : format(-difference) + ' kg más'}. No incluye otros accesorios ni evalúa ergonomía.`);
    }
    if (kind === 'mitre') {
      if (![values.width, values.height].every(value => Number.isFinite(value) && value > 0)) return invalid();
      const candidates = [['TC-MS 2112', 120, 55], ['TC-SM 2131/2 Dual', 310, 62]];
      const included = candidates.filter(([, width, height]) => values.width <= width && values.height <= height);
      return result(included.length ? 'La sección entra en estos máximos a 90° × 90°' : 'La sección supera al menos un límite de cada modelo',
        `${format(values.width)} × ${format(values.height)} mm. ${included.length ? included.map(([name, width, height]) => `${name}: hasta ${width} × ${height} mm`).join(' · ') + '.' : 'No hay candidato dentro de los dos límites documentados.'} El filtro no valida material, hoja, sujeción ni otro ángulo de corte.`);
    }
    if (kind === 'blind-hole') {
      if (![values.board, values.depth].every(value => Number.isFinite(value) && value > 0)) return invalid();
      const remaining = values.board - values.depth;
      return remaining <= 0
        ? result('La profundidad objetivo iguala o supera el tablero', `${format(values.board)} − ${format(values.depth)} = ${format(remaining)} mm. El cálculo no deja espesor restante positivo; no incluye punta ni tolerancias.`)
        : result(`${format(remaining)} mm de espesor restante teórico`, `${format(values.board)} − ${format(values.depth)} = ${format(remaining)} mm. No incluye la penetración de la punta central, tolerancias ni el mínimo que exige el herraje; no es una validación de la perforación.`);
    }
    if (kind === 'cut' || kind === 'hammer' || kind === 'jigsaw') {
      const requested = kind === 'hammer' ? values.diameter : values.thickness;
      if (requested <= 0) return invalid();
      if (kind === 'jigsaw' && !['wood', 'steel'].includes(values.material)) return result('Elegí madera o acero', 'Usá un material identificado en las fichas. Los 6 mm de BES603-B2 están publicados como metal, sin identificar acero.');
      const models = kind === 'cut' ? [['Stanley SC16-AR', 65], ['Bosch GKS 150', 64], ['Lüsqtoff CSL1500-8', 63.5]]
        : kind === 'hammer' ? [['Bosch GBH 220', 22], ['Bosch GBH 2-26 DRE', 26], ['Einhell TE-RH 28 5F', 28]]
        : values.material === 'steel' ? [['TC-JS 85', 8], ['TE-JS 100', 10]] : [['BES603-B2', 65], ['TC-JS 85', 85], ['TE-JS 100', 100]];
      const included = models.filter(([, maximum]) => requested <= maximum).map(([name, maximum]) => `${name}: máximo ${format(maximum)} mm`);
      const scope = kind === 'jigsaw' && values.material === 'steel' ? ' BES603-B2 no se evalúa para acero: su ficha identifica metal sin precisar ese material.' : '';
      return result(included.length ? 'El dato entra en estos máximos de ficha' : 'Supera todos los máximos de esta selección', (included.length ? `${included.join(' · ')}. El filtro no garantiza resultado, continuidad o compatibilidad de hoja/broca; cotejá las condiciones del manual.` : `Para ${format(requested)} mm no hay candidato dentro de los límites documentados de esta selección. No extrapolamos capacidades.`) + scope);
    }
    if (kind === 'cost') {
      if (values.priceA <= 0 || values.priceB <= 0) return result('Ingresá el precio confirmado de ambas ofertas', 'Usá los importes de las publicaciones que estás comparando. Envío y extras pueden ser cero si ya están incluidos.');
      const a = values.priceA + values.shippingA + values.extrasA;
      const b = values.priceB + values.shippingB + values.extrasB;
      return result(`Total A: $${format(a)} · Total B: $${format(b)}`, `Diferencia absoluta: $${format(Math.abs(a - b))}. Revisá que sean la misma variante y configuración; el cálculo no compara prestaciones ni financiación.`);
    }
    if (kind === 'house') {
      const selected = loads.filter(load => load.name.trim() || load.run !== '' || load.start !== '');
      if (!selected.length) return result('Agregá una carga documentada', 'Completá nombre, watts de marcha y de arranque del aparato concreto.');
      if (selected.some(load => !load.name.trim() || load.run === '' || load.start === '' || !Number.isFinite(Number(load.run)) || !Number.isFinite(Number(load.start)) || Number(load.run) <= 0 || Number(load.start) < Number(load.run))) return result('Faltan datos de una carga o hay un arranque menor que la marcha', 'Cada fila utilizada requiere nombre, marcha positiva y arranque documentado igual o mayor. Sin el dato de arranque no estimamos el pico.');
      const running = selected.reduce((sum, load) => sum + Number(load.run), 0);
      const extra = Math.max(...selected.map(load => Number(load.start) - Number(load.run)));
      return result(`Marcha: ${format(running)} W · escenario de pico: ${format(running + extra)} W`, `Pico explorado = ${format(running)} + ${format(extra)} W adicionales; supone un arranque a la vez y el resto en marcha. No convierte W a VA ni valida un generador o conexión a la vivienda.`);
    }
    return invalid();
  }
  if (typeof module !== 'undefined' && module.exports) module.exports = {calculate, checkReadiness};
  if (typeof document === 'undefined') return;
  document.querySelectorAll('.editorial-resource').forEach(section => {
    const config = JSON.parse(section.querySelector('.resource-config').textContent);
    if (config.kind === 'table') return;
    const title = section.querySelector('[data-result-title]');
    const body = section.querySelector('[data-result-body]');
    function update() {
      let answer;
      if (config.kind === 'checklist') {
        answer = checkReadiness(config.checks, [...section.querySelectorAll('[data-resource-check]')].map(input => input.checked));
      } else if (config.kind === 'selector') {
        const option = config.options[Number(section.querySelector('select').value)];
        answer = result(option[1], option[2]);
      } else {
        const fields = [...section.querySelectorAll('[data-resource-input]')];
        const values = Object.fromEntries(fields.map(input => [input.dataset.resourceInput, input.tagName === 'SELECT' ? input.value : input.value.trim() === '' ? '' : Number(input.value)]));
        const loads = [...section.querySelectorAll('fieldset')].map(row => Object.fromEntries([...row.querySelectorAll('[data-load]')].map(input => [input.dataset.load, input.value])));
        answer = fields.some(input => input.tagName === 'INPUT' && !input.validity.valid) ? invalid() : calculate(config.kind, values, loads);
      }
      title.textContent = answer.title;
      body.textContent = answer.body;
    }
    section.addEventListener('input', update);
    section.addEventListener('change', update);
    update();
  });
})();
