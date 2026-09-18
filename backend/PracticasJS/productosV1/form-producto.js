//backend\PracticasJS\productosV1\form-producto.js
// ============================================================================
// 1. IMPORTAR LA FUNCIÓN DE LA API
// ============================================================================
// Traemos la función 'crearProducto' que creamos en el archivo api.js.
// Esto separa responsabilidades: este archivo solo se encarga del formulario,
// y api.js solo se encarga de hablar con el servidor.
import { crearProducto } from '../api.js';


// ============================================================================
// 2. ESPERAR A QUE EL HTML ESTÉ LISTO
// ============================================================================
// 'DOMContentLoaded' es un evento que se dispara cuando todo el HTML se ha 
// cargado y dibujado en la pantalla. 
// ¿Por qué? Si intentamos buscar el formulario antes de que exista en el HTML, 
// JavaScript dará un error de "null". Esto lo previene.
document.addEventListener('DOMContentLoaded', () => {
    
    // Buscamos los elementos del HTML por su ID y los guardamos en variables
    const form = document.getElementById('formProducto');
    const mensajeDiv = document.getElementById('mensaje');

    // Protección: Si por alguna razón no encuentra el formulario, detenemos el código.
    if (!form) {
        console.error('No se encontró el formulario con id="formProducto"');
        return; 
    }


    // ========================================================================
    // 3. ESCUCHAR CUANDO EL USUARIO HACE CLIC EN "GUARDAR"
    // ========================================================================
    form.addEventListener('submit', async function(evento) {
        
        // ¡MUY IMPORTANTE! Evita que la página se recargue.
        // Por defecto, un formulario HTML recarga la página al enviarse.
        // Como queremos hacerlo con JavaScript (sin recargar), usamos preventDefault().
        evento.preventDefault();

        // Mostramos un mensaje temporal de "Procesando..."
        mensajeDiv.textContent = '⏳ Enviando datos al servidor...';
        mensajeDiv.className = 'mensaje info'; // Aplica estilos azules de info


        // ====================================================================
        // 4. RECOLECTAR Y CONVERTIR LOS DATOS DEL FORMULARIO
        // ====================================================================
        // OJO: Los inputs de HTML SIEMPRE devuelven TEXTO (Strings).
        // Pero nuestra API de Python espera NÚMEROS y BOOLEANOS. 
        // Por eso usamos parseInt, parseFloat y .checked para convertirlos.
        
        const datosProducto = {
            codigo: document.getElementById('codigo').value,
            nombre: document.getElementById('nombre').value,
            descripcion: document.getElementById('descripcion').value,
            marca: document.getElementById('marca').value,
            tipo: document.getElementById('tipo').value, // Ya es texto ("BIEN" o "SERVICIO")
            
            // Convertimos el texto a un número entero (ej: "5" -> 5)
            categoria_id: parseInt(document.getElementById('categoria_id').value), 
            
            // Para checkboxes NO usamos .value, usamos .checked (devuelve true o false)
            vendible_granel: document.getElementById('vendible_granel').checked, 
            
            // Convertimos el texto a un número con decimales (ej: "1.5" -> 1.5)
            qty_contenido: parseFloat(document.getElementById('qty_contenido').value), 
            
            // Objeto anidado para los precios (tal como lo pide el esquema de la API)
            precio: {
                precio_base: parseFloat(document.getElementById('precio_base').value),
                precio_costo: parseFloat(document.getElementById('precio_costo').value),
                precio_publico: parseFloat(document.getElementById('precio_publico').value),
                precio_iva: parseFloat(document.getElementById('precio_iva').value),
                precio_promo: parseFloat(document.getElementById('precio_promo').value),
                precio_descuento: parseFloat(document.getElementById('precio_descuento').value)
            }
        };


        // ====================================================================
        // 5. ENVIAR LOS DATOS A LA API (USANDO TRY...CATCH)
        // ====================================================================
        // 'try' intenta ejecutar el código. Si algo falla (ej: servidor apagado), 
        // salta automáticamente al bloque 'catch' en lugar de romper toda la página.
        try {
            // Llamamos a la función que importamos de api.js
            const respuesta = await crearProducto(datosProducto);

            // Verificamos si la respuesta del servidor fue exitosa (código 200 o 201)
            if (respuesta.ok) {
                mensajeDiv.textContent = '✅ ¡Producto guardado con éxito!';
                mensajeDiv.className = 'mensaje exito'; // Aplica estilos verdes
                
                // Limpiamos todos los campos del formulario para que quede listo de nuevo
                form.reset(); 
            } else {
                // Si el servidor responde con error (ej: 400 Bad Request, 401 Unauthorized)
                // Intentamos leer el mensaje de error que envía Python. Si falla, usamos un mensaje genérico.
                const errorDatos = await respuesta.json().catch(() => ({}));
                mensajeDiv.textContent = `❌ Error del servidor: ${respuesta.status} - ${errorDatos.detail || 'Revisa los datos'}`;
                mensajeDiv.className = 'mensaje error'; // Aplica estilos rojos
            }

        } catch (error) {
            // Este bloque se ejecuta si ni siquiera pudimos conectar con el servidor
            // (ej: el backend de Python está apagado o no hay internet).
            console.error('Detalle técnico del error:', error);
            mensajeDiv.textContent = '❌ Error de conexión. ¿Está encendido el backend?';
            mensajeDiv.className = 'mensaje error';
        }
    });

}); // Fin del evento DOMContentLoaded