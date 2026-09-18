// api.js — COMPARTIDO por toda la app
// ============================================================================

const API_BASE_URL = 'http://127.0.0.1:8000';

/**
 * Función genérica para enviar datos por POST a cualquier endpoint.
 * Toda la lógica de fetch vive AQUÍ UNA SOLA VEZ.
 * @param {string} endpoint - Ej: '/productos/crear' o '/proveedores/crear'
 * @param {Object} datos - El objeto a enviar como JSON
 * @returns {Promise<Response>}
 */
async function postJSON(endpoint, datos) {
    return await fetch(`${API_BASE_URL}${endpoint}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        credentials: 'include',
        body: JSON.stringify(datos)
    });
}

// ============================================================================
// FUNCIONES ESPECÍFICAS POR RECURSO — cada una es una línea, solo delega
// ============================================================================

export async function crearProducto(datosProducto) {
    return await postJSON('/productos/crear', datosProducto);
}

export async function crearProveedor(datosProveedor) {
    return await postJSON('/proveedores/crear', datosProveedor);
}