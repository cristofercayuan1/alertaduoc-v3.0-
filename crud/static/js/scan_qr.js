// Crea elemento de video
const video = document.createElement("video");

// Nuestro canvas
const canvasElement = document.getElementById("qr-canvas");
const canvas = canvasElement.getContext("2d");

// Div donde llegará nuestro canvas
const btnScanQR = document.getElementById("btn-scan-qr");

// Lectura desactivada
let scanning = false;

// Función para encender la cámara
const encenderCamara = () => {
  navigator.mediaDevices
    .getUserMedia({ video: { facingMode: "environment" } })
    .then(function (stream) {
      scanning = true;
      btnScanQR.hidden = true;
      canvasElement.hidden = false;
      video.setAttribute("playsinline", true); // Required to tell iOS safari we don't want fullscreen
      video.srcObject = stream;
      video.play();
      tick();
      scan();
      // Mostrar el diseño del cuadrado
      document.getElementById('qr-overlay').style.display = 'block';
    });
};

// Funciones para levantar las funciones de encendido de la cámara
function tick() {
  canvasElement.height = video.videoHeight;
  canvasElement.width = video.videoWidth;
  canvas.drawImage(video, 0, 0, canvasElement.width, canvasElement.height);

  scanning && requestAnimationFrame(tick);
}

function scan() {
  try {
    qrcode.decode();
  } catch (e) {
    setTimeout(scan, 300);
  }
}

// Apagar la cámara
const cerrarCamara = () => {
  video.srcObject.getTracks().forEach((track) => {
    track.stop();
  });
  canvasElement.hidden = true;
  btnScanQR.hidden = false;
  // Ocultar el diseño del cuadrado
  document.getElementById('qr-overlay').style.display = 'none';
};

const activarSonido = () => {
  var audio = document.getElementById('audioScaner');
  audio.play();
}

// Decodifica el QR correctamente en UTF-8
function decodeQR(data) {
  try {
    return decodeURIComponent(escape(data));
  } catch (e) {
    return data;
  }
}

// Callback cuando termina de leer el código QR
qrcode.callback = (respuesta) => {
  if (respuesta) {
    // Decodifica la respuesta antes de redirigir
    const decodedData = decodeQR(respuesta);
    // Redireccionar a la página del formulario de alerta con el código QR como parámetro
    window.location.href = `/formulario_alerta/?qr_code=${encodeURIComponent(decodedData)}`;
  }
};

// Evento para mostrar la cámara sin el botón 
window.addEventListener('load', (e) => {
  encenderCamara();
});
