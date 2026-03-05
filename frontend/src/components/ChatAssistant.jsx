import React, { useState, useRef, useEffect } from "react";
import { useTranslation } from "react-i18next";

// ─── Keyword intelligence maps ─────────────────────────────────────────────────
const QUICK_REPLIES_KEYS = [
  "water", "electricity", "gas", "bike", "ac", "phone"
];

const SERVICE_MAP = {
  "water":        { cat: "Plumber",           urgency: "Medium",   icon: "🔧", risk: 45 },
  "leak":         { cat: "Plumber",           urgency: "High",     icon: "🔧", risk: 60 },
  "burst":        { cat: "Plumber",           urgency: "Critical", icon: "🔧", risk: 90 },
  "flood":        { cat: "Plumber",           urgency: "Critical", icon: "🔧", risk: 88 },
  "pipe":         { cat: "Plumber",           urgency: "Medium",   icon: "🔧", risk: 35 },
  "tap":          { cat: "Plumber",           urgency: "Low",      icon: "🔧", risk: 15 },
  "electricity":  { cat: "Electrician",       urgency: "Medium",   icon: "⚡", risk: 55 },
  "electric":     { cat: "Electrician",       urgency: "Medium",   icon: "⚡", risk: 55 },
  "power":        { cat: "Electrician",       urgency: "High",     icon: "⚡", risk: 70 },
  "no power":     { cat: "Electrician",       urgency: "High",     icon: "⚡", risk: 72 },
  "spark":        { cat: "Electrician",       urgency: "Critical", icon: "⚡", risk: 92 },
  "short circuit":{ cat: "Electrician",       urgency: "Critical", icon: "⚡", risk: 95 },
  "shock":        { cat: "Electrician",       urgency: "Critical", icon: "⚡", risk: 100},
  "gas":          { cat: "Gas Service",       urgency: "Critical", icon: "🔥", risk: 93 },
  "gas smell":    { cat: "Gas Service",       urgency: "Critical", icon: "🔥", risk: 100},
  "hissing":      { cat: "Gas Service",       urgency: "Critical", icon: "🔥", risk: 88 },
  "fire":         { cat: "Gas Service",       urgency: "Critical", icon: "🔥", risk: 100},
  "bike":         { cat: "Bike Mechanic",     urgency: "Medium",   icon: "🏍️", risk: 30 },
  "motorcycle":   { cat: "Bike Mechanic",     urgency: "Medium",   icon: "🏍️", risk: 30 },
  "puncture":     { cat: "Bike Mechanic",     urgency: "High",     icon: "🏍️", risk: 50 },
  "breakdown":    { cat: "Bike Mechanic",     urgency: "High",     icon: "🏍️", risk: 55 },
  "ac":           { cat: "AC Technician",     urgency: "Low",      icon: "❄️", risk: 20 },
  "not cooling":  { cat: "AC Technician",     urgency: "Medium",   icon: "❄️", risk: 28 },
  "air condition":{ cat: "AC Technician",     urgency: "Low",      icon: "❄️", risk: 18 },
  "phone":        { cat: "Mobile Technician", urgency: "Low",      icon: "📱", risk: 12 },
  "screen":       { cat: "Mobile Technician", urgency: "Low",      icon: "📱", risk: 12 },
  "mobile":       { cat: "Mobile Technician", urgency: "Low",      icon: "📱", risk: 10 },
  "clean":        { cat: "Cleaning Service",  urgency: "Low",      icon: "🧹", risk:  5 },
  "paint":        { cat: "Painter",           urgency: "Low",      icon: "🎨", risk:  5 },
  "wood":         { cat: "Carpenter",         urgency: "Low",      icon: "🪚", risk:  8 },
  "furniture":    { cat: "Carpenter",         urgency: "Low",      icon: "🪚", risk:  8 },
};

const SEVERITY_STYLE = {
  Critical: { color: "#EF4444", bg: "rgba(239,68,68,0.12)", icon: "🔴", label: "CRITICAL" },
  High:     { color: "#F97316", bg: "rgba(249,115,22,0.12)", icon: "🟠", label: "HIGH" },
  Medium:   { color: "#F59E0B", bg: "rgba(245,158,11,0.12)", icon: "🟡", label: "MEDIUM" },
  Low:      { color: "#10B981", bg: "rgba(16,185,129,0.10)", icon: "🟢", label: "LOW" },
};

function detectIntent(text) {
  const lower = text.toLowerCase();
  const EXTRA_EMERGENCY = ["urgent", "emergency", "immediately", "quick", "asap", "danger"];
  const forceHigh = EXTRA_EMERGENCY.some((w) => lower.includes(w));

  // Sort by keyword length descending (longer = more specific)
  const sorted = Object.entries(SERVICE_MAP).sort((a, b) => b[0].length - a[0].length);
  for (const [keyword, info] of sorted) {
    if (lower.includes(keyword)) {
      let risk = info.risk;
      let urgency = info.urgency;
      if (forceHigh && urgency !== "Critical") {
        risk = Math.min(100, risk + 25);
        urgency = urgency === "High" ? "Critical" : "High";
      }
      return { ...info, risk, urgency };
    }
  }
  if (forceHigh) return { cat: null, urgency: "High", icon: "⚠️", risk: 70 };
  return null;
}

function getRiskLevel(risk) {
  if (risk >= 75) return "Critical";
  if (risk >= 50) return "High";
  if (risk >= 25) return "Medium";
  return "Low";
}

function getBotResponse(userText, t) {
  const intent = detectIntent(userText);
  if (!intent) {
    return {
      text: t('chat.help'),
      riskLevel: null,
      risk: 0,
      intent: null,
    };
  }

  const level = getRiskLevel(intent.risk);

  if (level === "Critical") {
    return {
      text: t('chat.emergency.critical', {
        risk: intent.risk,
        cat: intent.cat,
        icon: intent.icon
      }),
      riskLevel: level,
      risk: intent.risk,
      intent,
    };
  }
  if (level === "High") {
    return {
      text: t('chat.emergency.high', {
        risk: intent.risk,
        cat: intent.cat,
        icon: intent.icon
      }),
      riskLevel: level,
      risk: intent.risk,
      intent,
    };
  }
  return {
    text: t('chat.emergency.normal', {
      risk: intent.risk,
      cat: intent.cat,
      icon: intent.icon,
      level: level
    }),
    riskLevel: level,
    risk: intent.risk,
    intent,
  };
}

// ─── Message render helper ────────────────────────────────────────────────────
function RiskIndicator({ riskLevel, risk }) {
  if (!riskLevel || risk === 0) return null;
  const s = SEVERITY_STYLE[riskLevel];
  return (
    <div style={{
      display: "inline-flex", alignItems: "center", gap: 5,
      padding: "3px 9px", borderRadius: 100,
      background: s.bg, border: `1px solid ${s.color}25`,
      fontSize: 11, color: s.color, fontWeight: 700,
      marginTop: 6,
    }}>
      {s.icon} {risk}% Risk · {s.label}
    </div>
  );
}

function ChatMessage({ msg }) {
  const lines = msg.text.split("\n");
  return (
    <div className={`chat-msg ${msg.role}`}>
      {msg.role === "bot" && <div className="chat-msg-avatar">🛠️</div>}
      <div>
        <div
          className={`chat-bubble ${msg.riskLevel === "Critical" ? "emergency" : ""}`}
          style={msg.riskLevel === "Critical" ? { borderLeft: "3px solid #EF4444" } :
                 msg.riskLevel === "High"     ? { borderLeft: "3px solid #F97316" } : {}}
        >
          {lines.map((line, i) => {
            // Bold **text**
            const parts = line.split(/\*\*(.*?)\*\*/g);
            return (
              <span key={i}>
                {parts.map((p, j) =>
                  j % 2 === 1 ? <strong key={j}>{p}</strong> : p
                )}
                {i < lines.length - 1 && <br />}
              </span>
            );
          })}
        </div>
        {msg.role === "bot" && <RiskIndicator riskLevel={msg.riskLevel} risk={msg.risk} />}
      </div>
    </div>
  );
}

// ─── Main Component ───────────────────────────────────────────────────────────
export default function ChatAssistant() {
  const { t } = useTranslation();
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState(() => [
    {
      id: 1, role: "bot",
      text: "வணக்கம்! 👋 I'm your Sevai Hub Intelligence Assistant.\n\nDescribe your problem and I'll:\n• Score your emergency risk\n• Find nearest verified technician\n• Show Trust Index + ETA",
      riskLevel: null, risk: 0,
    },
  ]);
  const [input, setInput]     = useState("");
  const [typing, setTyping]   = useState(false);
  const bottomRef             = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, typing]);

  const sendMessage = (text) => {
    const userMsg = text || input.trim();
    if (!userMsg) return;
    setInput("");

    setMessages((prev) => [...prev, { id: `u-${prev.length}`, role: "user", text: userMsg, riskLevel: null, risk: 0 }]);
    setTyping(true);

    setTimeout(() => {
      const response = getBotResponse(userMsg, t);
      setMessages((prev) => [...prev, { id: `b-${prev.length}`, role: "bot", ...response }]);
      setTyping(false);
    }, 700);
  };

  // Count unread critical messages
  const hasCritical = messages.some((m) => m.riskLevel === "Critical");

  return (
    <>
      <button
        id="chat-fab"
        className="chat-fab"
        onClick={() => setOpen((o) => !o)}
        title="Open Sevai Hub Intelligence Assistant"
        style={hasCritical ? { animation: "pulse 1.5s ease infinite" } : {}}
      >
        {open ? "✕" : "💬"}
        {hasCritical && !open && (
          <span style={{
            position: "absolute", top: -4, right: -4,
            width: 14, height: 14, background: "#EF4444",
            borderRadius: "50%", border: "2px solid #0A0A0F",
            display: "block",
          }} />
        )}
      </button>

      {open && (
        <div className="chat-window">
          {/* Header */}
          <div className="chat-header">
            <div className="chat-avatar">🛠️</div>
            <div className="chat-header-info">
              <h4>Sevai Hub Intelligence</h4>
              <p>● Online · Emergency-Aware · TTI-Powered</p>
            </div>
            <button className="chat-close" onClick={() => setOpen(false)}>✕</button>
          </div>

          {/* Messages */}
          <div className="chat-messages">
            {messages.map((msg) => (
              <ChatMessage key={msg.id} msg={msg} />
            ))}

            {/* Quick replies — show only on first message */}
            {messages.length === 1 && (
              <div className="chat-quick-replies">
                {QUICK_REPLIES_KEYS.map((key) => {
                  const label = t(`chat.quickReplies.${key}`);
                  return (
                    <button key={key} className="quick-reply" onClick={() => sendMessage(label)}>
                      {label}
                    </button>
                  );
                })}
              </div>
            )}

            {/* Typing indicator */}
            {typing && (
              <div className="chat-msg bot">
                <div className="chat-msg-avatar">🛠️</div>
                <div className="chat-bubble" style={{ padding: "10px 16px" }}>
                  <span style={{ display: "inline-flex", gap: 4 }}>
                    {[0, 1, 2].map((i) => (
                      <span key={i} style={{
                        width: 6, height: 6, borderRadius: "50%",
                        background: "var(--text-muted)",
                        animation: `bounce 1s ease ${i * 0.15}s infinite`,
                        display: "inline-block",
                      }} />
                    ))}
                  </span>
                </div>
              </div>
            )}

            <div ref={bottomRef} />
          </div>

          {/* Input */}
          <div className="chat-input-area">
            <input
              id="chat-input"
              className="chat-input"
              placeholder="Describe your problem..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && sendMessage()}
            />
            <button id="chat-send" className="chat-send" onClick={() => sendMessage()}>➤</button>
          </div>
        </div>
      )}
    </>
  );
}
