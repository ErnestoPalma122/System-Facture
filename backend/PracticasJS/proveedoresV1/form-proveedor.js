// ============================================================================
// 1. IMPORTAR LA FUNCIÓN DE LA API
// ============================================================================
import { crearProveedor } from './api.js';


// ============================================================================
// 2. ESPERAR A QUE EL HTML ESTÉ LISTO
// ============================================================================
document.addEventListener('DOMContentLoaded', () => {

    const form = document.getElementById('formProveedor');
    const mensajeDiv = document.getElementById('mensaje');

    if (!form) {
        console.error('No se encontró el formulario con id="formProveedor"');
        return;
    }


    // ========================================================================
    // 3. ESCUCHAR CUANDO EL USUARIO HACE CLIC EN "GUARDAR"
    // ========================================================================
    form.addEventListener('submit', async function(evento) {

        evento.preventDefault();

        mensajeDiv.textContent = '⏳ Enviando datos al servidor...';
        mensajeDiv.className = 'mensaje info';


        // ====================================================================
        // 4. RECOLECTAR LOS DATOS DEL FORMULARIO
        // ====================================================================
        // A diferencia del formulario de productos, aquí TODOS los campos son
        // texto (String) según el schema de la API — no hay que convertir
        // nada con parseInt/parseFloat, ni hay objetos anidados ni checkboxes.

        const datosProveedor = {
            nombre: document.getElementById('nombre').value,
            direccion: document.getElementById('direccion').value,
            contacto: document.getElementById('contacto').value,
            email: document.getElementById('email').value,
            telefono1: document.getElementById('telefono1').value,
            telefono2: document.getElementById('telefono2').value,
            observaciones: document.getElementById('observaciones').value
        };


        // ====================================================================
        // 5. ENVIAR LOS DATOS A LA API
        // ====================================================================
        try {
            const respuesta = await crearProveedor(datosProveedor);

            if (respuesta.ok) {
                mensajeDiv.textContent = '✅ ¡Proveedor guardado con éxito!';
                mensajeDiv.className = 'mensaje exito';
                form.reset();
            } else {
                const errorDatos = await respuesta.json().catch(() => ({}));
                mensajeDiv.textContent = `❌ Error del servidor: ${respuesta.status} - ${errorDatos.detail || 'Revisa los datos'}`;
                mensajeDiv.className = 'mensaje error';
            }

        } catch (error) {
            console.error('Detalle técnico del error:', error);
            mensajeDiv.textContent = '❌ Error de conexión. ¿Está encendido el backend?';
            mensajeDiv.className = 'mensaje error';
        }
    });

});