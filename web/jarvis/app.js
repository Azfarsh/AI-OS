const voiceBtn = document.getElementById("voice-btn");
const stopBtn = document.getElementById("stop-btn");
const refreshBtn = document.getElementById("refresh-btn");
const voiceState = document.getElementById("voice-state");
const briefingText = document.getElementById("briefing-text");
const activityLog = document.getElementById("activity-log");
const statusDate = document.getElementById("status-date");
const statusPill = document.getElementById("status-pill");
const clientCount = document.getElementById("client-count");
const connectedCount = document.getElementById("connected-count");
const connectionsList = document.getElementById("connections-list");
const clientsList = document.getElementById("clients-list");
const commandsList = document.getElementById("commands-list");

let conversation = null;
let ConversationModule = null;

function log(message, level = "info") {
  const time = new Date().toLocaleTimeString();
  const entry = document.createElement("div");
  entry.className = "log-entry";
  entry.innerHTML = `<span class="time">[${time}]</span> ${message}`;
  activityLog.prepend(entry);
  if (level === "error") {
    voiceState.textContent = message;
  }
}

function setVoiceMode(mode) {
  voiceBtn.classList.remove("listening", "working");
  if (mode) voiceBtn.classList.add(mode);
}

async function loadStatus() {
  const res = await fetch("/api/status");
  const data = await res.json();
  statusDate.textContent = data.date;
  statusPill.textContent = `${data.connected_count} integrations live`;
  clientCount.textContent = data.client_count;
  connectedCount.textContent = data.connected_count;
  briefingText.textContent = data.spoken;

  connectionsList.innerHTML = "";
  data.connections.forEach((row) => {
    const li = document.createElement("li");
    const statusClass = row.status === "connected" ? "connected" : row.status;
    li.textContent = `${row.service}: ${statusClass}`;
    connectionsList.appendChild(li);
  });

  clientsList.innerHTML = "";
  if (!data.clients.length) {
    clientsList.innerHTML = "<li>No clients yet</li>";
  } else {
    data.clients.forEach((client) => {
      const li = document.createElement("li");
      li.textContent = `${client.name} (${client.status})`;
      clientsList.appendChild(li);
    });
  }

  commandsList.innerHTML = "";
  data.command_phrases.forEach((phrase) => {
    const li = document.createElement("li");
    li.textContent = phrase;
    li.title = "Click to copy";
    li.addEventListener("click", async () => {
      await navigator.clipboard.writeText(phrase);
      log(`Copied command: ${phrase}`);
    });
    commandsList.appendChild(li);
  });
}

async function loadConversationModule() {
  if (ConversationModule) return ConversationModule;
  const mod = await import("https://esm.sh/@elevenlabs/client@0.1.7");
  ConversationModule = mod.Conversation;
  return ConversationModule;
}

function buildClientTools() {
  const toolNames = [
    "run_report",
    "run_onboard_client",
    "run_proposal",
    "list_clients",
    "get_connections",
  ];

  const tools = {};
  toolNames.forEach((name) => {
    tools[name] = async (parameters) => {
      setVoiceMode("working");
      voiceState.textContent = `Running ${name.replace(/_/g, " ")}...`;
      log(`Tool call: ${name}`);
      const res = await fetch(`/api/tools/${name}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(parameters || {}),
      });
      const payload = await res.json();
      if (payload.spoken_receipt) {
        log(payload.spoken_receipt);
      } else if (payload.message) {
        log(payload.message);
      } else {
        log(JSON.stringify(payload));
      }
      setVoiceMode("listening");
      voiceState.textContent = "Listening...";
      return JSON.stringify(payload);
    };
  });
  return tools;
}

async function startVoiceSession() {
  if (conversation) return;

  try {
    voiceState.textContent = "Connecting voice...";
    setVoiceMode("working");
    const signedRes = await fetch("/api/signed-url");
    const signedData = await signedRes.json();
    if (signedData.status !== "ok") {
      throw new Error(signedData.message || "Could not get signed URL. Check .env ElevenLabs keys.");
    }

    const Conversation = await loadConversationModule();
    conversation = await Conversation.startSession({
      signedUrl: signedData.signed_url,
      clientTools: buildClientTools(),
      onConnect: () => {
        setVoiceMode("listening");
        voiceState.textContent = "Listening... say report, onboard, or proposal";
        stopBtn.disabled = false;
        voiceBtn.disabled = true;
        log("Voice session connected.");
      },
      onDisconnect: () => {
        setVoiceMode("");
        voiceState.textContent = "Tap to talk to Agency OS";
        stopBtn.disabled = true;
        voiceBtn.disabled = false;
        conversation = null;
        log("Voice session ended.");
      },
      onError: (error) => {
        log(`Voice error: ${error}`, "error");
        setVoiceMode("");
        voiceBtn.disabled = false;
        stopBtn.disabled = true;
        conversation = null;
      },
      onModeChange: (mode) => {
        if (mode.mode === "speaking") {
          setVoiceMode("working");
          voiceState.textContent = "Agent speaking...";
        } else if (mode.mode === "listening") {
          setVoiceMode("listening");
          voiceState.textContent = "Listening...";
        }
      },
    });
  } catch (error) {
    log(error.message || String(error), "error");
    setVoiceMode("");
    voiceBtn.disabled = false;
    stopBtn.disabled = true;
    conversation = null;
  }
}

async function stopVoiceSession() {
  if (!conversation) return;
  await conversation.endSession();
  conversation = null;
}

voiceBtn.addEventListener("click", startVoiceSession);
stopBtn.addEventListener("click", stopVoiceSession);
refreshBtn.addEventListener("click", async () => {
  await loadStatus();
  log("Status refreshed.");
});

loadStatus()
  .then(() => log("Agency OS dashboard ready."))
  .catch((error) => log(error.message || String(error), "error"));
