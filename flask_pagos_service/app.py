import uuid
from datetime import datetime, timezone
from flask import Flask, request, jsonify

app = Flask(__name__)

pagos_db = []
pago_id_counter = 0

METODOS_PAGO = ['tarjeta', 'transferencia', 'efectivo']

TRANSICIONES_VALIDAS = {
    'pendiente': ['en_proceso', 'cancelado'],
    'en_proceso': ['completado', 'cancelado'],
    'completado': [],
    'cancelado': [],
}


def _buscar_pago(pk):
    return next((p for p in pagos_db if p['id'] == pk), None)


def _transicionar(pago, nuevo_estado):
    permitidos = TRANSICIONES_VALIDAS.get(pago['estado'], [])
    if nuevo_estado not in permitidos:
        return False, f"Transición inválida: {pago['estado']} → {nuevo_estado}"
    pago['estado'] = nuevo_estado
    pago['updated_at'] = datetime.now(timezone.utc).isoformat()
    return True, None


@app.errorhandler(404)
def not_found(e):
    return jsonify({'error': 'Recurso no encontrado'}), 404


@app.errorhandler(500)
def internal_error(e):
    return jsonify({'error': 'Error interno del servidor'}), 500


@app.route('/api/v2/pagos/', methods=['GET'])
def listar_pagos():
    return jsonify(pagos_db), 200


@app.route('/api/v2/pagos/', methods=['POST'])
def crear_pago():
    global pago_id_counter
    data = request.get_json(silent=True)

    if not data or 'monto' not in data:
        return jsonify({'error': 'El campo "monto" es requerido.'}), 400

    try:
        monto = float(data['monto'])
    except (ValueError, TypeError):
        return jsonify({'error': f"Monto inválido: {data['monto']}"}), 400

    if monto <= 0:
        return jsonify({'error': 'El monto debe ser mayor a cero.'}), 400

    metodo = data.get('metodo_pago', 'tarjeta')
    if metodo not in METODOS_PAGO:
        return jsonify({
            'error': f"Método de pago inválido: {metodo}. Opciones: {METODOS_PAGO}"
        }), 400

    pago_id_counter += 1
    pago = {
        'id': pago_id_counter,
        'referencia': str(uuid.uuid4()),
        'monto': monto,
        'metodo_pago': metodo,
        'estado': 'pendiente',
        'created_at': datetime.now(timezone.utc).isoformat(),
        'updated_at': datetime.now(timezone.utc).isoformat(),
    }
    pagos_db.append(pago)
    return jsonify(pago), 201


@app.route('/api/v2/pagos/<int:pk>/', methods=['GET'])
def detalle_pago(pk):
    pago = _buscar_pago(pk)
    if not pago:
        return jsonify({'error': f'Pago con id {pk} no encontrado.'}), 404
    return jsonify(pago), 200


@app.route('/api/v2/pagos/<int:pk>/procesar/', methods=['POST'])
def procesar_pago(pk):
    pago = _buscar_pago(pk)
    if not pago:
        return jsonify({'error': f'Pago con id {pk} no encontrado.'}), 404

    ok, error = _transicionar(pago, 'en_proceso')
    if not ok:
        return jsonify({'error': error}), 409

    return jsonify({
        'exito': True,
        'mensaje': f"Pago procesado exitosamente (ref: {pago['referencia']})",
        'pago': pago,
    }), 200


@app.route('/api/v2/pagos/<int:pk>/confirmar/', methods=['POST'])
def confirmar_pago(pk):
    pago = _buscar_pago(pk)
    if not pago:
        return jsonify({'error': f'Pago con id {pk} no encontrado.'}), 404

    ok, error = _transicionar(pago, 'completado')
    if not ok:
        return jsonify({'error': error}), 409

    return jsonify(pago), 200


@app.route('/api/v2/pagos/<int:pk>/cancelar/', methods=['POST'])
def cancelar_pago(pk):
    pago = _buscar_pago(pk)
    if not pago:
        return jsonify({'error': f'Pago con id {pk} no encontrado.'}), 404

    ok, error = _transicionar(pago, 'cancelado')
    if not ok:
        return jsonify({'error': error}), 409

    return jsonify(pago), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
