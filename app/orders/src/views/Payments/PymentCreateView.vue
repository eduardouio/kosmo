<script setup>
</script>
<template>
  <div class="mx-auto" style="width: 80%;">
    <div class="row pt-2">
      <div class="col">
        <!-- Encabezado Principal -->
        <div class="container-fluid">
          <div class="row">
            <div class="col-12 rounded-1 shadow-sm p-2 bg-zinc-600 bg-gradient border-gray-300 text-white">
              <div class="row pb-3 mb-3">
                <div class="col-3 fs-4">
                </div>
                <div class="col-6 text-center fs-5 upper">
                  <span>Registro de Pagos y Cobros KosmoFlowers</span>
                </div>
                <div class="col-3 text-end fs-6">
                  <strong class="border-gray-500 rounded-1 bg-white text-dark ps-2 pe-2">
                    Fecha Registro: 01/07/2025 <span class="text-blue-700">16:30</span>
                  </strong>
                  <span class="pe-1 ps-1"></span>
                </div>
              </div>
              <div class="row">
                <div class="col-4">
                  <div class="row align-items-center">
                    <div class="col-4">
                      <label for="" class="text-nowrap">Tipo de Documento:</label>
                    </div>
                    <div class="col-8">
                      <select class="form-select form-select-sm">
                        <option value="all">Todas las Facturas</option>
                        <option value="sales">Facturas de Venta</option>
                        <option value="purchase">Facturas de Compra</option>
                      </select>
                    </div>
                  </div>
                </div>
                <div class="col-3"> </div>
                <div class="col-5">
                  <div class="row align-items-center">
                    <div class="col-3">
                      <label class="text-nowrap">Cliente:</label>
                    </div>
                    <div class="col-9">
                      <select class="form-select form-select-sm">
                        <option value="all">Todas las Facturas</option>
                        <option value="sales">Facturas de Venta</option>
                        <option value="purchase">Facturas de Compra</option>
                      </select>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Filtros adicionales -->
          <div class="row pb-2 pt-2 fw-bold border pt-2 pb-2 mt-2 mb-2 shadow-sm">
            <div class="col-4 text-start text-xl">
                Estadísticas Enero
            </div>
            <div class="col-8 text-end text-xl">
                <span class=""> Total facturas: 7 </span>
                <span class="text-muted ps-1 pe-1">|</span>
                <span class="text-cyan-800"> Total pendiente: $4,537.75 </span>
                <span class="text-muted ps-1 pe-1">|</span>
                <span class="text-danger"> Saldo Vencido: $2,201.25</span>
                <span class="text-muted ps-1 pe-1">|</span>
                <span class="text-yellow-600"> Por Vencer: $2,336.50</span>
            </div>
          </div>

          <!-- Encabezados de tabla -->
          <div class="row p-1 text-white">
            <div class="col-1 border-end bg-gray-400 text-center">Sel.</div>
            <div class="col-2 border-end bg-gray-400 text-center">Factura</div>
            <div class="col-2 border-end bg-gray-400 text-center">Cliente</div>
            <div class="col-1 border-end bg-gray-400 text-center">Fecha</div>
            <div class="col-1 border-end bg-gray-400 text-center">Vence</div>
            <div class="col-1 border-end bg-gray-400 text-center">Días</div>
            <div class="col-1 border-end bg-sky-500 text-center">Total</div>
            <div class="col-1 border-end bg-sky-500 text-center">Pagado</div>
            <div class="col-1 border-end bg-sky-500 text-center">Saldo</div>
            <div class="col-1 bg-lime-600 text-center">A Pagar</div>
          </div>

          <!-- Filas de facturas -->
          <div class="row mb-1 border my-hover-2 bg-gray">
            <div class="col-1 border-end d-flex align-items-center justify-content-center">
              <input type="checkbox" class="form-check-input">
            </div>
            <div class="col-2 border-end d-flex align-items-center">
              <div>
                <div class="fw-semibold">001-000001</div>
                <small class="text-muted">FAC_VENTA</small>
              </div>
            </div>
            <div class="col-2 border-end d-flex align-items-center">
              <div>
                <div class="fw-semibold">A&C Wholesle Flower</div>
                <small class="text-muted">390484522</small>
              </div>
            </div>
            <div class="col-1 border-end d-flex align-items-center text-center">
              2025-05-06
            </div>
            <div class="col-1 border-end d-flex align-items-center text-center">
              2025-06-05
            </div>
            <div class="col-1 border-end d-flex align-items-center text-center">
              <span class="badge bg-yellow-300 text-dark">30</span>
            </div>
            <div class="col-1 border-end d-flex align-items-center text-end">
              $1,203.75
            </div>
            <div class="col-1 border-end d-flex align-items-center text-end">
              $0.00
            </div>
            <div class="col-1 border-end d-flex align-items-center text-end">
              <span class="fw-semibold text-danger">$1,203.75</span>
            </div>
            <div class="col-1 d-flex align-items-center">
              <input type="number" step="0.01" class="form-control form-control-sm text-end" value="1203.75">
            </div>
          </div>

          <div class="row mb-1 border my-hover-2">
            <div class="col-1 border-end d-flex align-items-center justify-content-center">
              <input type="checkbox" class="form-check-input">
            </div>
            <div class="col-2 border-end d-flex align-items-center">
              <div>
                <div class="fw-semibold">001-000002</div>
                <small class="text-muted">FAC_VENTA</small>
              </div>
            </div>
            <div class="col-2 border-end d-flex align-items-center">
              <div>
                <div class="fw-semibold">Aliance Floral Co</div>
                <small class="text-muted">390484524</small>
              </div>
            </div>
            <div class="col-1 border-end d-flex align-items-center text-center">
              2025-05-27
            </div>
            <div class="col-1 border-end d-flex align-items-center text-center">
              2025-06-26
            </div>
            <div class="col-1 border-end d-flex align-items-center text-center">
              <span class="badge bg-green-600">11</span>
            </div>
            <div class="col-1 border-end d-flex align-items-center text-end">
              $903.75
            </div>
            <div class="col-1 border-end d-flex align-items-center text-end">
              $0.00
            </div>
            <div class="col-1 border-end d-flex align-items-center text-end">
              <span class="fw-semibold text-danger">$903.75</span>
            </div>
            <div class="col-1 d-flex align-items-center">
              <input type="number" step="0.01" class="form-control form-control-sm text-end" value="0.00">
            </div>
          </div>

          <div class="row mb-1 border my-hover-2 bg-gray">
            <div class="col-1 border-end d-flex align-items-center justify-content-center">
              <input type="checkbox" class="form-check-input" checked>
            </div>
            <div class="col-2 border-end d-flex align-items-center">
              <div>
                <div class="fw-semibold">100-000004</div>
                <small class="text-muted">FAC_VENTA</small>
              </div>
            </div>
            <div class="col-2 border-end d-flex align-items-center">
              <div>
                <div class="fw-semibold">Premier Floral Corp</div>
                <small class="text-muted">39048452</small>
              </div>
            </div>
            <div class="col-1 border-end d-flex align-items-center text-center">
              2025-05-27
            </div>
            <div class="col-1 border-end d-flex align-items-center text-center">
              2025-07-11
            </div>
            <div class="col-1 border-end d-flex align-items-center text-center">
              <span class="badge bg-red-600 text-white">-5</span>
            </div>
            <div class="col-1 border-end d-flex align-items-center text-end">
              $997.50
            </div>
            <div class="col-1 border-end d-flex align-items-center text-end">
              $0.00
            </div>
            <div class="col-1 border-end d-flex align-items-center text-end">
              <span class="fw-semibold text-danger">$997.50</span>
            </div>
            <div class="col-1 d-flex align-items-center">
              <input type="number" step="0.01" class="form-control form-control-sm text-end" value="997.50">
            </div>
          </div>

          <div class="row mb-1 border my-hover-2">
            <div class="col-1 border-end d-flex align-items-center justify-content-center">
              <input type="checkbox" class="form-check-input">
            </div>
            <div class="col-2 border-end d-flex align-items-center">
              <div>
                <div class="fw-semibold">100-000006</div>
                <small class="text-muted">FAC_VENTA</small>
              </div>
            </div>
            <div class="col-2 border-end d-flex align-items-center">
              <div>
                <div class="fw-semibold">Global Flowers</div>
                <small class="text-muted">390484526</small>
              </div>
            </div>
            <div class="col-1 border-end d-flex align-items-center text-center">
              2025-05-27
            </div>
            <div class="col-1 border-end d-flex align-items-center text-center">
              2025-06-11
            </div>
            <div class="col-1 border-end d-flex align-items-center text-center">
              <span class="badge bg-green-600">4</span>
            </div>
            <div class="col-1 border-end d-flex align-items-center text-end">
              $300.00
            </div>
            <div class="col-1 border-end d-flex align-items-center text-end">
              $0.00
            </div>
            <div class="col-1 border-end d-flex align-items-center text-end">
              <span class="fw-semibold text-danger">$300.00</span>
            </div>
            <div class="col-1 d-flex align-items-center">
              <input type="number" step="0.01" class="form-control form-control-sm text-end" value="0.00">
            </div>
          </div>

          <!-- Resumen de totales -->
          <div class="row">
            <div class="col-8">
              <div class="row shadow-sm p-2 border bg-transparent rounded-1 fs-5">
                <div class="col-3 text-end fw-semibold">Facturas seleccionadas:</div>
                <div class="col-2 text-end">2</div>
                <div class="col-3 text-end fw-semibold">Total a pagar:</div>
                <div class="col-4 text-end text-lime-600">$2,201.25</div>
              </div>
            </div>
            <div class="col-4">
              <div class="row bg-trasparent rounded-1 shadow-sm p-2 border">
                <div class="col-6 text-end border-end fs-5 text-danger fw-semibold">Saldo Total:</div>
                <div class="col-6 fs-5 text-danger text-end fw-semibold">
                  $4,537.75
                </div>
              </div>
            </div>
          </div>

          <!-- Formulario de Pago -->
          <div class="row mt-3 border-top pt-3">
            <div class="col-12">
              <div class="row bg-light border rounded-1 shadow-sm p-3">
                <div class="col-12 mb-3">
                  <h5 class="text-orange-700 fw-semibold mb-3">Información del Pago</h5>
                </div>
                
                <div class="col-3">
                  <label class="form-label fw-semibold">Fecha de Pago</label>
                  <input type="date" class="form-control" value="2025-01-07">
                </div>
                
                <div class="col-3">
                  <label class="form-label fw-semibold">Método de Pago</label>
                  <select class="form-select">
                    <option value="">Seleccionar...</option>
                    <option value="cash">Efectivo</option>
                    <option value="transfer">Transferencia</option>
                    <option value="check">Cheque</option>
                    <option value="card">Tarjeta</option>
                  </select>
                </div>
                
                <div class="col-3">
                  <label class="form-label fw-semibold">Referencia/Documento</label>
                  <input type="text" class="form-control" placeholder="Núm. cheque, transferencia...">
                </div>
                
                <div class="col-3">
                  <label class="form-label fw-semibold">Monto Total</label>
                  <input type="number" step="0.01" class="form-control text-end fw-semibold" value="2201.25" readonly>
                </div>
                
                <div class="col-6 mt-3">
                  <label class="form-label fw-semibold">Observaciones</label>
                  <textarea class="form-control" rows="2" placeholder="Observaciones adicionales..."></textarea>
                </div>
                
                <div class="col-6 mt-3">
                  <label class="form-label fw-semibold">Cuenta Bancaria</label>
                  <select class="form-select">
                    <option value="">Seleccionar cuenta...</option>
                    <option value="1">Banco de Bogotá - *****1234</option>
                    <option value="2">Bancolombia - *****5678</option>
                  </select>
                </div>
              </div>
            </div>
          </div>

          <!-- Botones de Acción -->
          <div class="row mt-3 border-top pt-3">
            <div class="col-6">
              <button type="button" class="btn btn-sm btn-default me-2">
                <span>🔄</span>
                Limpiar Selección
              </button>
              <button type="button" class="btn btn-sm btn-default">
                <span>📋</span>
                Guardar Borrador
              </button>
            </div>
            <div class="col-6 text-end d-flex gap-3 justify-content-end">
              <button type="button" class="btn btn-sm btn-default">
                <span>❌</span>
                Cancelar
              </button>
              <button type="button" class="btn btn-sm btn-default" disabled>
                <span>💰</span>
                Procesar Pago
              </button>
              <button type="button" class="btn btn-sm btn-default">
                <span>✅</span>
                Confirmar y Registrar
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
