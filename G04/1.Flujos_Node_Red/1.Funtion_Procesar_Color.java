// espera msg.payload = el objeto enviado desde el nodo template
let info = msg.payload || {};
let hex = info.hex || "#000000";
let rgb = info.rgb || [0,0,0];

// Prepara dos mensajes:
// msg1 para el color picker (payload = hex string)
// msg2 para debug o visualización (objeto completo)
let msgColor = { payload: hex };         // el ui_colour_picker espera una string "#RRGGBB"
let msgDebug = { payload: { hex: hex, rgb: rgb, coords: {x: info.x, y: info.y} } };

// Envío en 2 salidas: salida 1 -> color picker, salida 2 -> debug/tabla
return [msgColor, msgDebug];