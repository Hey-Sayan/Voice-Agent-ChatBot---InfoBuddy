const WS_URL = "ws://127.0.0.1:8000/ws"; // change if your server runs elsewhere

const chat = document.getElementById("chat");
const form = document.getElementById("form");
const text = document.getElementById("text");
const micBtn = document.getElementById("mic");

const addMsg = (role, content) => {
  const el = document.createElement("div");
  el.className = `msg ${role === "user" ? "user" : "bot"}`;
  el.textContent = content;
  chat.appendChild(el);
  chat.scrollTop = chat.scrollHeight;
};

// --- WebSocket ---
let ws;
function connectWS() {
  ws = new WebSocket(WS_URL);
  ws.onopen = () => console.log("WS connected");
  ws.onclose = () => setTimeout(connectWS, 1000);
  ws.onmessage = (ev) => {
    try {
      const data = JSON.parse(ev.data);
      addMsg("bot", data.text || "(no text)");
      speak(data.text || "");
    } catch (e) {
      console.error(e);
    }
  };
}
connectWS();

// --- Send text ---
form.addEventListener("submit", (e) => {
  e.preventDefault();
  const q = text.value.trim();
  if (!q) return;
  addMsg("user", q);
  ws?.send(JSON.stringify({ text: q }));
  text.value = "";
});

// --- Hints ---
for (const btn of document.querySelectorAll(".hint")) {
  btn.addEventListener("click", () => {
    text.value = btn.dataset.q;
    form.dispatchEvent(new Event("submit"));
  });
}

// --- Speech-to-Text (Web Speech API) ---
let recog;
if ("webkitSpeechRecognition" in window) {
  const SR = window.webkitSpeechRecognition;
  recog = new SR();
  recog.continuous = false;
  recog.interimResults = true;
  recog.lang = "en-US";

  recog.onresult = (e) => {
    let final = "";
    for (let i = e.resultIndex; i < e.results.length; i++) {
      const chunk = e.results[i][0].transcript;
      if (e.results[i].isFinal) {
        final += chunk;
      } else {
        text.value = chunk; // show interim
      }
    }
    if (final) {
      text.value = final;
      form.dispatchEvent(new Event("submit"));
    }
  };
}

micBtn.addEventListener("click", () => {
  if (!recog) {
    alert("Speech Recognition not supported in this browser. Try Chrome.");
    return;
  }
  recog.start();
});

// --- Text-to-Speech ---
function speak(content) {
  if (!("speechSynthesis" in window)) return;
  const ut = new SpeechSynthesisUtterance(content);
  ut.rate = 1.0;
  ut.pitch = 1.0;
  ut.lang = "en-US";
  window.speechSynthesis.speak(ut);
}
