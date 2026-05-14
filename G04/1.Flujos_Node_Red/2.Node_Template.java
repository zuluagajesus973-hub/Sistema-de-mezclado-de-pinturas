<div style="text-align:center;">
  <h3>Selecciona un punto de la imagen</h3>
  <canvas id="canvas" width="640" height="480" style="border:1px solid #000;"></canvas>
  <p id="colorInfo">Haz clic en un punto de la imagen</p>
</div>

<script>
(function(scope) {
    const canvas = document.getElementById("canvas");
    const ctx = canvas.getContext("2d");
    const colorInfo = document.getElementById("colorInfo");
    let img = new Image();

    // Se ejecuta cada vez que llega un nuevo mensaje MQTT
    scope.$watch('msg.payload', function(data) {
        if (!data) return;

        // Dibujar la nueva imagen
        img = new Image();
        img.onload = function() {
            ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
        };
        img.src = data;  // base64 recibido desde MQTT
    });

    // Detectar clic y obtener color RGB y HEX
    canvas.addEventListener("click", function(event) {
        const rect = canvas.getBoundingClientRect();
        const x = event.clientX - rect.left;
        const y = event.clientY - rect.top;

        const pixel = ctx.getImageData(x, y, 1, 1).data;
        const rgb = `rgb(${pixel[0]}, ${pixel[1]}, ${pixel[2]})`;
        const hex = "#" + ((1 << 24) + (pixel[0] << 16) + (pixel[1] << 8) + pixel[2]).toString(16).slice(1).toUpperCase();

        colorInfo.innerText = `Coordenadas: (${Math.round(x)},${Math.round(y)}) - ${rgb} - ${hex}`;
        
        // Enviar el color a Node-RED
        scope.send({ payload: { x: x, y: y, rgb: rgb, hex: hex } });
    });
})(scope);
</script>