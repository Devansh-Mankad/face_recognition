const video = document.getElementById("video");
const captureBtn = document.getElementById("capture");
const resultP = document.getElementById("result");
const switchBtn = document.getElementById("switch"); // button to switch cameras

let usingBackCamera = false;
let currentStream = null;

// --- Start camera (front or back) ---
async function startCamera(back = false) {
  if (currentStream) {
    // Stop existing stream before switching
    currentStream.getTracks().forEach(track => track.stop());
  }

  try {
    const constraints = {
      video: back
        ? { facingMode: { exact: "environment" } } // back camera
        : { facingMode: "user" } // front camera
    };

    const stream = await navigator.mediaDevices.getUserMedia(constraints);
    currentStream = stream;
    video.srcObject = stream;
  } catch (err) {
    console.error("Error accessing camera:", err);
    // fallback if back camera not available
    if (back) startCamera(false);
  }
}

// --- Convert video frame to base64 ---
function getFrame(scale = 2) {
  const canvas = document.createElement("canvas");

  // make canvas bigger by scaling factor
  canvas.width = video.videoWidth * scale;
  canvas.height = video.videoHeight * scale;

  const ctx = canvas.getContext("2d");

  // scale the drawn video
  ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

  // return as JPEG (you can adjust quality too, 0.9 = 90%)
  return canvas.toDataURL("image/jpeg", 1.0);
}


// --- Capture button ---
let lastClick = 0;
captureBtn.addEventListener("click", () => {
  if (Date.now() - lastClick < 2000) return; // 2s debounce
  lastClick = Date.now();
  captureAndSendFrame();
});

// --- Switch camera button ---
switchBtn.addEventListener("click", () => {
  usingBackCamera = !usingBackCamera;
  startCamera(usingBackCamera);
});

// --- Send frame to server ---
function captureAndSendFrame() {
  const frame = getFrame();
  fetch("/upload", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ image: frame })
  })
  .then(res => res.json())
  .then(data => {
    resultP.textContent = "Result: " + data.result;
  })
  .catch(err => console.error("Error sending frame:", err));
}

// --- Start with front camera ---
startCamera(false);
