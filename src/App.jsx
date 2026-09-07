import React, { useState, useEffect, useMemo, useRef } from "react";

// ============================================================
// SUPABASE CONFIG
// ============================================================
const SUPABASE_URL = "https://mxopumjrhshlnjqsmqld.supabase.co";
const SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im14b3B1bWpyaHNobG5qcXNtcWxkIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODY4MTU2MTEsImV4cCI6MjEwMjM5MTYxMX0.BExnJivmo_-vZsJJwGvtcxEfZb4yoS_GzAPF_2Tb_yM";
const REST = `${SUPABASE_URL}/rest/v1`;
const AUTHV1 = `${SUPABASE_URL}/auth/v1`;
const EMAIL_DOMAIN = "bhagirathi.internal";

function slugify(name) {
  return name.trim().toLowerCase().replace(/[^a-z0-9]+/g, ".").replace(/^\.+|\.+$/g, "");
}
function dresserEmail(name) { return `${slugify(name)}@${EMAIL_DOMAIN}`; }

async function authRequest(path, body) {
  const res = await fetch(`${AUTHV1}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json", apikey: SUPABASE_ANON_KEY },
    body: JSON.stringify(body),
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.error_description || data.msg || data.error || "Authentication failed");
  return data;
}
async function authSignUp(email, password) { return authRequest("/signup", { email, password }); }
async function authSignIn(email, password) { return authRequest("/token?grant_type=password", { email, password }); }
async function authRefresh(refresh_token) { return authRequest("/token?grant_type=refresh_token", { refresh_token }); }
async function authUpdatePassword(token, password) {
  const res = await fetch(`${AUTHV1}/user`, {
    method: "PUT",
    headers: { "Content-Type": "application/json", apikey: SUPABASE_ANON_KEY, Authorization: `Bearer ${token}` },
    body: JSON.stringify({ password }),
  });
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.msg || "Could not update password");
  return data;
}

async function rest(path, token, opts = {}) {
  const headers = {
    "Content-Type": "application/json",
    apikey: SUPABASE_ANON_KEY,
    Authorization: `Bearer ${token || SUPABASE_ANON_KEY}`,
    ...(opts.headers || {}),
  };
  const res = await fetch(`${REST}${path}`, { ...opts, headers });
  if (res.status === 204) return null;
  const data = await res.json().catch(() => null);
  if (!res.ok) throw new Error((data && (data.message || data.hint)) || `Request failed (${res.status})`);
  return data;
}
const restGet = (path, token) => rest(path, token, { method: "GET" });
const restPost = (path, token, body, preferReturn = true) =>
  rest(path, token, { method: "POST", body: JSON.stringify(body), headers: preferReturn ? { Prefer: "return=representation" } : {} });
const restPatch = (path, token, body) =>
  rest(path, token, { method: "PATCH", body: JSON.stringify(body), headers: { Prefer: "return=representation" } });
const restDelete = (path, token) => rest(path, token, { method: "DELETE" });

// ---------- local device-only session cache ----------
function loadKey(key, fallback) {
  try {
    const raw = window.localStorage.getItem(key);
    return raw ? JSON.parse(raw) : fallback;
  } catch (e) {
    return fallback;
  }
}
function saveKey(key, value) {
  try {
    window.localStorage.setItem(key, JSON.stringify(value));
  } catch (e) {
    console.error("save failed", key, e);
  }
}
function deleteKey(key) {
  try { window.localStorage.removeItem(key); } catch (e) { /* ignore */ }
}

// ---------- Supabase Storage (case photos) ----------
function dataURLtoBlob(dataURL) {
  const [header, base64] = dataURL.split(",");
  const mime = header.match(/:(.*?);/)[1];
  const binary = atob(base64);
  const array = new Uint8Array(binary.length);
  for (let i = 0; i < binary.length; i++) array[i] = binary.charCodeAt(i);
  return new Blob([array], { type: mime });
}
async function uploadPhoto(token, path, dataURL) {
  const blob = dataURLtoBlob(dataURL);
  const res = await fetch(`${SUPABASE_URL}/storage/v1/object/case-photos/${path}`, {
    method: "POST",
    headers: { apikey: SUPABASE_ANON_KEY, Authorization: `Bearer ${token}`, "Content-Type": blob.type, "x-upsert": "true" },
    body: blob,
  });
  if (!res.ok) throw new Error("Photo upload failed");
  return true;
}
async function getSignedPhotoUrl(token, path) {
  try {
    const res = await fetch(`${SUPABASE_URL}/storage/v1/object/sign/case-photos/${path}`, {
      method: "POST",
      headers: { apikey: SUPABASE_ANON_KEY, Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
      body: JSON.stringify({ expiresIn: 3600 }),
    });
    const data = await res.json();
    return data.signedURL ? `${SUPABASE_URL}/storage/v1${data.signedURL}` : null;
  } catch (e) { return null; }
}

const uid = () => Math.random().toString(36).slice(2, 10);
const genPassword = () => String(Math.floor(100000 + Math.random() * 900000));
const todayISO = () => new Date().toISOString().slice(0, 10);
const fmtDate = (d) =>
  d ? new Date(d).toLocaleDateString("en-IN", { day: "2-digit", month: "short", year: "numeric" }) : "—";
const fmtMoney = (n) => "₹" + Number(n || 0).toLocaleString("en-IN");
const addDays = (dateStr, days) => {
  const d = new Date(dateStr);
  d.setDate(d.getDate() + Number(days || 0));
  return d.toISOString().slice(0, 10);
};
const daysBetween = (a, b) => Math.round((new Date(b) - new Date(a)) / 86400000);
const nowTimeHM = () => new Date().toTimeString().slice(0, 5);
const fmtTime = (t) => {
  if (!t) return "";
  const [h, m] = t.split(":").map(Number);
  const period = h >= 12 ? "PM" : "AM";
  const h12 = h % 12 === 0 ? 12 : h % 12;
  return `${h12}:${String(m).padStart(2, "0")} ${period}`;
};
const fmtRelative = (iso) => {
  if (!iso) return "never";
  const mins = Math.round((Date.now() - new Date(iso).getTime()) / 60000);
  if (mins < 1) return "just now";
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.round(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  return `${Math.round(hrs / 24)}d ago`;
};

const STATUS = {
  active: { label: "On Therapy", color: "#1B6B63", bg: "#E4F1EE" },
  stopped: { label: "Stopped", color: "#8A5A2B", bg: "#F5EBDC" },
  reapplied: { label: "Reapplied", color: "#3B5BA5", bg: "#E7ECF7" },
};
const PROTOCOLS = [5, 7];
const PAY_MODES = ["Cash", "Online", "Credit"];
const LOW_STOCK_THRESHOLD = 5;
const OWNER_WHATSAPP = "917507777127";
const PHOTO_STAGES = [
  { key: "debridement", label: "After Debridement" },
  { key: "application", label: "After Application" },
  { key: "completion", label: "Therapy Completion" },
];

// ---------- row <-> UI mappers ----------
function caseFromRow(r) {
  return {
    id: r.id,
    patientName: r.patient_name,
    patientMobile: r.patient_mobile,
    doctorName: r.doctor_name,
    dresserId: r.dresser_id,
    dresserName: (r.dresser && r.dresser.display_name) || "",
    protocolDays: r.protocol_days,
    machineSerial: r.machine_serial,
    product: r.product,
    applicationDate: r.application_date,
    applicationTime: r.application_time,
    status: r.status,
    endDate: r.end_date,
    billTo: r.bill_to,
    hospitalName: r.hospital_name,
    totalAmount: r.total_amount,
    notes: r.notes,
    photoFlags: r.photo_flags || {},
  };
}
function caseToRow(data) {
  return {
    patient_name: data.patientName,
    patient_mobile: data.patientMobile || null,
    doctor_name: data.doctorName,
    dresser_id: data.dresserId || null,
    protocol_days: Number(data.protocolDays) || 5,
    machine_serial: data.machineSerial || null,
    product: data.product || null,
    application_date: data.applicationDate,
    application_time: data.applicationTime || null,
    status: data.status || "active",
    end_date: data.endDate || null,
    bill_to: data.billTo || "Patient",
    hospital_name: data.hospitalName || null,
    total_amount: Number(data.totalAmount) || 0,
    notes: data.notes || null,
  };
}
function changeFromRow(r) {
  return {
    id: r.id,
    caseId: r.case_id,
    date: r.change_date,
    dresserId: r.dresser_id,
    dresserName: (r.dresser && r.dresser.display_name) || "",
    protocolDays: r.protocol_days,
    note: r.note,
  };
}
function paymentFromRow(r) {
  return { id: r.id, caseId: r.case_id, amount: r.amount, mode: r.mode, note: r.note, date: r.payment_date, screenshotPath: r.screenshot_path };
}
function productFromRow(r) {
  return { id: r.id, name: r.name, available: r.available, used: r.used, costPrice: r.cost_price };
}
function machineFromRow(r) { return { id: r.id, serial: r.serial, model: r.model }; }

function latestChange(c) {
  const list = c.dressingChanges || [];
  if (list.length === 0) {
    return { date: c.applicationDate, protocolDays: c.protocolDays || 5 };
  }
  return [...list].sort((a, b) => new Date(b.date) - new Date(a.date))[0];
}
function nextDueDate(c) {
  const last = latestChange(c);
  return addDays(last.date, last.protocolDays || 5);
}
function overdueDays(c) {
  if (c.status !== "active") return 0;
  const due = nextDueDate(c);
  const d = daysBetween(due, todayISO());
  return d > 0 ? d : 0;
}
function getCaseProducts(c) {
  if (Array.isArray(c.products) && c.products.length) return c.products;
  return c.product ? [c.product] : [];
}
function getCaseProducts(c) {
  if (Array.isArray(c.products) && c.products.length) return c.products;
  return c.product ? [c.product] : [];
}
function estimateProfit(c, products) {
  const names = getCaseProducts(c);
  const cost = names.reduce((sum, name) => {
    const prod = products.find((p) => p.name === name);
    return sum + (prod ? Number(prod.costPrice || 0) : 0);
  }, 0);
  return Number(c.totalAmount || 0) - cost;
}
}
function photoKey(caseId, stage) { return `photo-${caseId}-${stage}`; }
function paymentPhotoKey(paymentId) { return `paypic-${paymentId}`; }
function mapsLink(lat, lng) { return `https://www.google.com/maps?q=${lat},${lng}`; }
function waLink(number, text) { return `https://wa.me/${number}?text=${encodeURIComponent(text)}`; }

function getLocation() {
  return new Promise((resolve) => {
    if (!navigator.geolocation) { resolve(null); return; }
    navigator.geolocation.getCurrentPosition(
      (pos) => resolve({ lat: pos.coords.latitude, lng: pos.coords.longitude }),
      () => resolve(null),
      { timeout: 8000 }
    );
  });
}
function compressImage(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = (e) => {
      const img = new Image();
      img.onload = () => {
        const maxW = 640;
        const scale = Math.min(1, maxW / img.width);
        const canvas = document.createElement("canvas");
        canvas.width = Math.round(img.width * scale);
        canvas.height = Math.round(img.height * scale);
        const ctx = canvas.getContext("2d");
        ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
        resolve(canvas.toDataURL("image/jpeg", 0.55));
      };
      img.onerror = reject;
      img.src = e.target.result;
    };
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });
}

// ============================================================
// APP ROOT
// ============================================================
export default function App() {
  const [session, setSession] = useState(null); // { access_token, refresh_token, expires_at }
  const [profile, setProfile] = useState(null); // { id, display_name, role }
  const [cases, setCases] = useState([]);
  const [machines, setMachines] = useState([]);
  const [products, setProducts] = useState([]);
  const [dressers, setDressers] = useState([]); // profiles with role=dresser (owner only)
  const [booting, setBooting] = useState(true);
  const [authError, setAuthError] = useState("");

  useEffect(() => {
    document.title = "Bhagirathi Agency";
    try {
      const canvas = document.createElement("canvas");
      canvas.width = 180; canvas.height = 180;
      const ctx = canvas.getContext("2d");
      ctx.fillStyle = "#1B6B63";
      ctx.fillRect(0, 0, 180, 180);
      ctx.fillStyle = "#F6F5F0";
      ctx.font = "bold 100px 'Space Grotesk', sans-serif";
      ctx.textAlign = "center";
      ctx.textBaseline = "middle";
      ctx.fillText("B", 90, 98);
      const dataUrl = canvas.toDataURL("image/png");
      [
        { rel: "icon", sizes: "180x180" },
        { rel: "apple-touch-icon", sizes: "180x180" },
        { rel: "shortcut icon" },
      ].forEach(({ rel, sizes }) => {
        let link = document.querySelector(`link[rel="${rel}"]`);
        if (!link) { link = document.createElement("link"); link.rel = rel; document.head.appendChild(link); }
        if (sizes) link.sizes = sizes;
        link.href = dataUrl;
      });
    } catch (e) { /* best effort */ }
  }, []);

  const loadAllData = async (token, role) => {
    const [caseRows, machineRows, productRows] = await Promise.all([
      restGet(`/cases?select=*,dresser:profiles(display_name)&order=application_date.desc`, token),
      restGet(`/machines?select=*&order=serial.asc`, token),
      restGet(`/products?select=*&order=name.asc`, token),
    ]);
    const rawCases = caseRows || [];
    const [changeRows, paymentRows] = await Promise.all([
      restGet(`/dressing_changes?select=*,dresser:profiles(display_name)&order=change_date.desc`, token),
      role === "owner" ? restGet(`/payments?select=*`, token) : Promise.resolve([]),
    ]);
    const changesByCase = {};
    (changeRows || []).forEach((r) => {
      const cc = changeFromRow(r);
      (changesByCase[cc.caseId] = changesByCase[cc.caseId] || []).push(cc);
    });
    const paymentsByCase = {};
    (paymentRows || []).forEach((r) => {
      const pp = paymentFromRow(r);
      (paymentsByCase[pp.caseId] = paymentsByCase[pp.caseId] || []).push(pp);
    });
    const mergedCases = rawCases.map((r) => {
      const c = caseFromRow(r);
      c.dressingChanges = changesByCase[c.id] || [];
      c.payments = paymentsByCase[c.id] || [];
      return c;
    });
    setCases(mergedCases);
    setMachines((machineRows || []).map(machineFromRow));
    setProducts((productRows || []).map(productFromRow));
    if (role === "owner") {
      const dresserRows = await restGet(`/profiles?role=eq.dresser&select=*&order=display_name.asc`, token);
      setDressers(dresserRows || []);
    }
  };

  const establishSession = async (tokenSet) => {
    setSession(tokenSet);
    saveKey("wca-session", tokenSet);
    const profRows = await restGet(`/profiles?id=eq.${tokenSet.user_id}&select=*`, tokenSet.access_token);
    const prof = (profRows && profRows[0]) || null;
    setProfile(prof);
    if (prof) await loadAllData(tokenSet.access_token, prof.role);
    return prof;
  };

  useEffect(() => {
    (async () => {
      try {
        const cached = loadKey("wca-session", null);
        if (cached && cached.refresh_token) {
          try {
            const refreshed = await authRefresh(cached.refresh_token);
            const tokenSet = {
              access_token: refreshed.access_token,
              refresh_token: refreshed.refresh_token,
              user_id: refreshed.user.id,
            };
            await establishSession(tokenSet);
          } catch (e) {
            deleteKey("wca-session");
          }
        }
      } catch (e) { /* ignore boot errors, show login */ }
      setBooting(false);
    })();
  }, []);

  const doLogin = async (email, password) => {
    setAuthError("");
    const data = await authSignIn(email, password);
    const tokenSet = { access_token: data.access_token, refresh_token: data.refresh_token, user_id: data.user.id };
    const prof = await establishSession(tokenSet);
    if (!prof) throw new Error("No profile found for this account. Ask the owner to check your access.");
    return prof;
  };

  const doOwnerSignUp = async (email, password, displayName) => {
    const data = await authSignUp(email, password);
    if (!data.access_token) {
      throw new Error("Account created, but email confirmation is still required in Supabase settings. Ask your developer to disable 'Confirm email' under Authentication settings, then try logging in.");
    }
    const tokenSet = { access_token: data.access_token, refresh_token: data.refresh_token, user_id: data.user.id };
    await restPost(`/profiles`, tokenSet.access_token, { id: tokenSet.user_id, display_name: displayName, role: "owner" });
    await establishSession(tokenSet);
  };

  const logout = async () => {
    deleteKey("wca-session");
    setSession(null);
    setProfile(null);
    setCases([]); setMachines([]); setProducts([]); setDressers([]);
  };

  const refreshData = async () => { if (session && profile) await loadAllData(session.access_token, profile.role); };

  // ---------- data actions ----------
  const saveCase = async (data, editingId) => {
    const token = session.access_token;
    if (editingId) {
      await restPatch(`/cases?id=eq.${editingId}`, token, caseToRow(data));
    } else {
      const row = caseToRow(data);
      const created = await restPost(`/cases`, token, row);
      const newCase = created[0];
      await restPost(`/dressing_changes`, token, {
        case_id: newCase.id, dresser_id: data.dresserId || null,
        change_date: data.applicationDate, protocol_days: Number(data.protocolDays) || 5, note: "Initial application",
      });
      if (data.product) {
        const prod = products.find((p) => p.name === data.product);
        if (prod) await restPatch(`/products?id=eq.${prod.id}`, token, { available: Math.max(0, (prod.available || 0) - 1), used: (prod.used || 0) + 1 });
      }
    }
    await refreshData();
  };

  const deleteCase = async (id) => {
    const token = session.access_token;
    const target = cases.find((c) => c.id === id);
    await restDelete(`/cases?id=eq.${id}`, token);
    if (target && target.product) {
      const prod = products.find((p) => p.name === target.product);
      if (prod) await restPatch(`/products?id=eq.${prod.id}`, token, { available: (prod.available || 0) + 1, used: Math.max(0, (prod.used || 0) - 1) });
    }
    await refreshData();
  };

  const addPayment = async (caseId, payment) => {
    await restPost(`/payments`, session.access_token, {
      case_id: caseId, amount: payment.amount, mode: payment.mode, note: payment.note || null, payment_date: payment.date,
    });
    await refreshData();
  };

  const addDressingChange = async (caseId, entry) => {
    await restPost(`/dressing_changes`, session.access_token, {
      case_id: caseId, dresser_id: entry.dresserId || profile.id, change_date: entry.date,
      protocol_days: Number(entry.protocolDays) || 5, note: entry.note || null,
    });
    await refreshData();
  };

  const capturePhoto = async (caseId, stage, dataURL) => {
    await uploadPhoto(session.access_token, photoKey(caseId, stage), dataURL);
    const c = cases.find((cc) => cc.id === caseId);
    const flags = { ...(c ? c.photoFlags : {}), [stage]: true };
    await restPatch(`/cases?id=eq.${caseId}`, session.access_token, { photo_flags: flags });
    await refreshData();
  };
  const getPhotoUrl = (caseId, stage) => getSignedPhotoUrl(session.access_token, photoKey(caseId, stage));

  const changeOwnPassword = async (newPassword) => {
    await authUpdatePassword(session.access_token, newPassword);
  };

  const addDresserAccount = async (name, password) => {
    const email = dresserEmail(name);
    const signUpData = await authSignUp(email, password);
    if (!signUpData.user || !signUpData.user.id) throw new Error("Could not create the account. Try a different name.");
    await restPost(`/profiles`, session.access_token, { id: signUpData.user.id, display_name: name.trim(), role: "dresser" });
    await refreshData();
    return { email, password };
  };
  const removeDresserAccount = async (id) => {
    await restPatch(`/profiles?id=eq.${id}`, session.access_token, { active: false });
    await refreshData();
  };

  const updateDresserLocation = async (eventType = "checkin") => {
    const loc = await getLocation();
    if (loc && session) {
      try {
        await restPost(`/dresser_locations`, session.access_token, {
          dresser_id: profile.id, lat: loc.lat, lng: loc.lng, event_type: eventType,
        }, false);
      } catch (e) { /* best effort */ }
    }
    return loc;
  };

  const receiveStock = async (productId, qty, company) => {
    const token = session.access_token;
    const prod = products.find((p) => p.id === productId);
    if (!prod) return;
    await restPatch(`/products?id=eq.${productId}`, token, { available: (prod.available || 0) + qty });
    // receipts log kept minimal for now (available totals update immediately)
    await refreshData();
  };
  const addProduct = async (name, qty, cost) => {
    await restPost(`/products`, session.access_token, { name: name.trim(), available: Number(qty) || 0, used: 0, cost_price: Number(cost) || 0 });
    await refreshData();
  };
  const updateProductCost = async (productId, cost) => {
    await restPatch(`/products?id=eq.${productId}`, session.access_token, { cost_price: Number(cost) || 0 });
    await refreshData();
  };
  const removeProduct = async (productId) => {
    await restDelete(`/products?id=eq.${productId}`, session.access_token);
    await refreshData();
  };
  const addMachine = async (serial, model) => {
    await restPost(`/machines`, session.access_token, { serial: serial.trim(), model: model.trim() || "NPWT Unit" });
    await refreshData();
  };
  const removeMachine = async (id) => {
    await restDelete(`/machines?id=eq.${id}`, session.access_token);
    await refreshData();
  };

  if (booting) {
    return <div style={styles.loadingScreen}><div style={styles.loadingText}>Loading…</div></div>;
  }

  return (
    <div style={styles.app}>
      <style>{fontImport}</style>
      {!profile && (
        <RoleGate
          onOwnerLogin={doLogin}
          onOwnerSignUp={doOwnerSignUp}
          onDresserLogin={async (name, password) => { const p = await doLogin(dresserEmail(name), password); updateDresserLocation("login"); return p; }}
        />
      )}
      {profile && profile.role === "owner" && (
        <OwnerShell
          profile={profile} cases={cases} machines={machines} products={products}
          dressers={dressers}
          addDresserAccount={addDresserAccount} removeDresserAccount={removeDresserAccount}
          saveCase={saveCase} deleteCase={deleteCase} addPayment={addPayment} addDressingChange={addDressingChange}
          addProduct={addProduct} updateProductCost={updateProductCost} removeProduct={removeProduct} receiveStock={receiveStock}
          addMachine={addMachine} removeMachine={removeMachine}
          changeOwnPassword={changeOwnPassword}
          onLogout={logout}
          session={session}
        />
      )}
      {profile && profile.role === "dresser" && (
        <DresserShell
          profile={profile} cases={cases} machines={machines} products={products}
          saveCase={saveCase}
          addDressingChange={addDressingChange} capturePhoto={capturePhoto}
          updateDresserLocation={updateDresserLocation}
          onLogout={logout}
        />
      )}
    </div>
  );
}

// ================= ROLE GATE =================
function RoleGate({ onOwnerLogin, onOwnerSignUp, onDresserLogin }) {
  const [mode, setMode] = useState("dresser");
  const [tapCount, setTapCount] = useState(0);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  const [ownerEmail, setOwnerEmail] = useState("");
  const [ownerPassword, setOwnerPassword] = useState("");
  const [ownerName, setOwnerName] = useState("");
  const [ownerIsNew, setOwnerIsNew] = useState(false);

  const [dresserName, setDresserName] = useState("");
  const [dresserPassword, setDresserPassword] = useState("");

  const handleLogoTap = () => {
    const next = tapCount + 1;
    if (next >= 5) { setMode("owner"); setError(""); setTapCount(0); }
    else setTapCount(next);
  };

  const submitOwner = async () => {
    setError(""); setBusy(true);
    try {
      if (ownerIsNew) {
        if (!ownerName.trim() || !ownerEmail.trim() || ownerPassword.length < 6) { setError("Fill in your name, email, and a password (6+ characters)."); setBusy(false); return; }
        await onOwnerSignUp(ownerEmail.trim(), ownerPassword, ownerName.trim());
      } else {
        await onOwnerLogin(ownerEmail.trim(), ownerPassword);
      }
    } catch (e) { setError(e.message || "Something went wrong."); }
    setBusy(false);
  };

  const submitDresser = async () => {
    setError(""); setBusy(true);
    try {
      if (!dresserName.trim() || !dresserPassword) { setError("Enter your name and password."); setBusy(false); return; }
      await onDresserLogin(dresserName.trim(), dresserPassword);
    } catch (e) { setError("Login failed. Check your name and password, or ask the owner."); }
    setBusy(false);
  };

  return (
    <div style={styles.gateWrap}>
      <div style={styles.brandMarkLg} onClick={handleLogoTap}>B</div>
      <div style={styles.gateBrand}>Bhagirathi Agency</div>
      <div style={styles.brandSub}>Wound Care Tracker</div>

      {mode === "owner" && (
        <div style={styles.gateForm}>
          <div style={styles.gateHint}>{ownerIsNew ? "Create your owner account." : "Owner login."}</div>
          {ownerIsNew && <input placeholder="Your name" value={ownerName} onChange={(e) => setOwnerName(e.target.value)} style={styles.gateInput} />}
          <input type="email" placeholder="Email" value={ownerEmail} onChange={(e) => setOwnerEmail(e.target.value)} style={styles.gateInput} />
          <input type="password" placeholder="Password" value={ownerPassword} onChange={(e) => setOwnerPassword(e.target.value)} style={styles.gateInput} />
          {error && <div style={styles.gateError}>{error}</div>}
          <button style={styles.primaryBtn} onClick={submitOwner} disabled={busy}>{busy ? "Please wait…" : ownerIsNew ? "Create Account" : "Log In"}</button>
          <button style={styles.linkBtn} onClick={() => { setOwnerIsNew((s) => !s); setError(""); }}>{ownerIsNew ? "Already have an account? Log in" : "First time here? Create account"}</button>
          <button style={styles.linkBtn} onClick={() => { setMode("dresser"); setError(""); }}>Back</button>
        </div>
      )}

      {mode === "dresser" && (
        <div style={styles.gateForm}>
          <div style={styles.gateHint}>Enter the name and password given to you by the owner. Your location is recorded when you log in, log a change, and periodically while this app is open, for safety and record-keeping.</div>
          <input placeholder="Your name" value={dresserName} onChange={(e) => setDresserName(e.target.value)} style={styles.gateInput} />
          <input type="password" placeholder="Password" value={dresserPassword} onChange={(e) => setDresserPassword(e.target.value)} style={styles.gateInput} />
          {error && <div style={styles.gateError}>{error}</div>}
          <button style={styles.primaryBtn} onClick={submitDresser} disabled={busy}>{busy ? "Logging in…" : "Log In"}</button>
        </div>
      )}
    </div>
  );
}

// ================= OWNER SHELL =================
function OwnerShell({ profile, cases, machines, products, dressers, addDresserAccount, removeDresserAccount, saveCase, deleteCase, addPayment, addDressingChange, addProduct, updateProductCost, removeProduct, receiveStock, addMachine, removeMachine, changeOwnPassword, onLogout, session }) {
  const [tab, setTab] = useState("dashboard");
  const getPhotoUrl = (caseId, stage) => getSignedPhotoUrl(session.access_token, photoKey(caseId, stage));
  const [showPwForm, setShowPwForm] = useState(false);

  const machineInUse = (serial) => cases.some((c) => c.machineSerial === serial && c.status === "active");
  const outstandingTotal = useMemo(() => cases.reduce((sum, c) => {
    const paid = (c.payments || []).reduce((s, p) => s + Number(p.amount || 0), 0);
    return sum + Math.max(0, Number(c.totalAmount || 0) - paid);
  }, 0), [cases]);
  const activeCount = cases.filter((c) => c.status === "active").length;
  const machinesInUseCount = machines.filter((m) => machineInUse(m.serial)).length;
  const overdueCount = cases.filter((c) => overdueDays(c) > 0).length;

  const dresserStats = useMemo(() => {
    const tally = {};
    cases.forEach((c) => {
      const entries = (c.dressingChanges || []).length ? c.dressingChanges : [];
      entries.forEach((e) => {
        const name = (e.dresserName || "").trim();
        if (!name) return;
        tally[name] = (tally[name] || 0) + 1;
      });
    });
    return Object.entries(tally).map(([name, count]) => ({ name, count })).sort((a, b) => b.count - a.count);
  }, [cases]);

  const lowStock = products.filter((p) => (p.available || 0) <= LOW_STOCK_THRESHOLD);

  return (
    <>
      <header style={styles.header}>
        <div style={styles.headerInner}>
          <div style={styles.brandMark}>B</div>
          <div style={{ flex: 1 }}>
            <div style={styles.brandName}>Bhagirathi Agency</div>
            <div style={styles.brandSub}>Owner view · {profile.display_name}</div>
          </div>
          <div style={{ display: "flex", gap: 6 }}>
            <button style={styles.logoutBtn} onClick={() => setShowPwForm((s) => !s)}>Password</button>
            <button style={styles.logoutBtn} onClick={onLogout}>Switch User</button>
          </div>
        </div>
        {showPwForm && (
          <div style={styles.pinPanel}>
            <ChangePasswordForm onChangePassword={async (p) => { await changeOwnPassword(p); setShowPwForm(false); }} onDone={() => setShowPwForm(false)} />
          </div>
        )}
      </header>

      <nav style={styles.nav}>
        {[["dashboard", "Overview"], ["cases", "Cases"], ["inventory", "Inventory"], ["team", "Team"]].map(([key, label]) => (
          <button key={key} onClick={() => setTab(key)} style={{ ...styles.navBtn, ...(tab === key ? styles.navBtnActive : {}) }}>{label}</button>
        ))}
      </nav>

      <main style={styles.main}>
        {tab === "dashboard" && (
          <Dashboard cases={cases} machines={machines} outstandingTotal={outstandingTotal} activeCount={activeCount}
            machinesInUseCount={machinesInUseCount} overdueCount={overdueCount} dresserStats={dresserStats} lowStock={lowStock}
            products={products} setTab={setTab} />
        )}
        {tab === "cases" && (
          <CasesTab cases={cases} machines={machines} products={products} dressers={dressers} saveCase={saveCase} deleteCase={deleteCase}
            addPayment={addPayment} addDressingChange={addDressingChange} getPhotoUrl={getPhotoUrl} />
        )}
        {tab === "inventory" && (
          <InventoryTab machines={machines} addMachine={addMachine} removeMachine={removeMachine} machineInUse={machineInUse} cases={cases}
            products={products} addProduct={addProduct} updateProductCost={updateProductCost} removeProduct={removeProduct} receiveStock={receiveStock} />
        )}
        {tab === "team" && (
          <TeamTab dressers={dressers} addDresserAccount={addDresserAccount} removeDresserAccount={removeDresserAccount} dresserStats={dresserStats}
            cases={cases} products={products} outstandingTotal={outstandingTotal} overdueCount={overdueCount} lowStock={lowStock} />
        )}
      </main>
    </>
  );
}

function ChangePasswordForm({ onChangePassword, onDone }) {
  const [next, setNext] = useState("");
  const [confirm, setConfirm] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const submit = async () => {
    if (next.length < 6) { setError("Password must be at least 6 characters"); return; }
    if (next !== confirm) { setError("Passwords don't match"); return; }
    setBusy(true);
    try { await onChangePassword(next); } catch (e) { setError(e.message || "Could not update password"); }
    setBusy(false);
  };

  return (
    <div style={styles.formGrid}>
      <Field label="New Password"><input type="password" style={styles.input} value={next} onChange={(e) => setNext(e.target.value)} /></Field>
      <Field label="Confirm New Password"><input type="password" style={styles.input} value={confirm} onChange={(e) => setConfirm(e.target.value)} /></Field>
      {error && <div style={styles.gateError}>{error}</div>}
      <div style={styles.formActions}>
        <button style={styles.secondaryBtn} onClick={onDone}>Cancel</button>
        <button style={styles.primaryBtn} onClick={submit} disabled={busy}>{busy ? "Updating…" : "Update Password"}</button>
      </div>
    </div>
  );
}

// ================= DRESSER SHELL =================
function DresserShell({ profile, cases, machines, products, saveCase, addDressingChange, capturePhoto, updateDresserLocation, onLogout }) {
  const [sending, setSending] = useState(false);
  const [showNewCase, setShowNewCase] = useState(false);
  const [toast, setToast] = useState(null);
  const myCasesActive = cases.filter((c) => c.status === "active" && c.dresserId === profile.id);

  useEffect(() => {
    const interval = setInterval(() => { updateDresserLocation("periodic"); }, 5 * 60 * 1000);
    return () => clearInterval(interval);
    // eslint-disable-next-line
  }, []);

  useEffect(() => {
    if (!toast) return;
    const t = setTimeout(() => setToast(null), 3000);
    return () => clearTimeout(t);
  }, [toast]);

  const myChanges = useMemo(() => {
    const list = [];
    cases.forEach((c) => {
      (c.dressingChanges || []).forEach((e) => {
        if (e.dresserId === profile.id) list.push({ ...e, patientName: c.patientName });
      });
    });
    return list.sort((a, b) => new Date(b.date) - new Date(a.date));
  }, [cases, profile.id]);

  const sendSafetyAlert = async () => {
    setSending(true);
    const loc = await updateDresserLocation("safety_alert");
    const time = new Date().toLocaleString("en-IN");
    let msg = `SAFETY ALERT from ${profile.display_name}\nTime: ${time}`;
    msg += loc ? `\nLocation: ${mapsLink(loc.lat, loc.lng)}` : "\nLocation: unavailable (permission not granted)";
    window.open(waLink(OWNER_WHATSAPP, msg), "_blank");
    setSending(false);
  };

  return (
    <>
      <header style={styles.header}>
        <div style={styles.headerInner}>
          <div style={styles.brandMark}>B</div>
          <div style={{ flex: 1 }}>
            <div style={styles.brandName}>Bhagirathi Agency</div>
            <div style={styles.brandSub}>Hi, {profile.display_name}</div>
          </div>
          <button style={styles.logoutBtn} onClick={onLogout}>Switch User</button>
        </div>
      </header>

      <main style={styles.main}>
        <button style={styles.safetyBtn} onClick={sendSafetyAlert} disabled={sending}>
          {sending ? "Getting location…" : "🚨 Send Safety Alert"}
        </button>

        {showNewCase ? (
          <DresserNewCaseForm
            profile={profile} machines={machines} products={products}
            onCancel={() => setShowNewCase(false)}
            onSave={(data) => { saveCase({ ...data, dresserId: profile.id, dresserName: profile.display_name }, null); setShowNewCase(false); setToast(`New patient "${data.patientName}" added`); }}
          />
        ) : (
          <button style={styles.primaryBtn} onClick={() => setShowNewCase(true)}>+ Report New Patient</button>
        )}

        <SectionTitle>Cases on Therapy</SectionTitle>
        {myCasesActive.length === 0 ? <EmptyState text="No active cases right now." /> : (
          <div style={styles.list}>
            {myCasesActive.map((c) => (
              <DresserCaseRow key={c.id} c={c} profile={profile}
                onAddDressingChange={(e) => { addDressingChange(c.id, e); setToast(`Dressing change reported for ${c.patientName}`); }}
                onCapturePhoto={(stage, dataURL) => capturePhoto(c.id, stage, dataURL)} />
            ))}
          </div>
        )}

        <SectionTitle>Your Reporting</SectionTitle>
        <div style={styles.cardGrid}>
          <div style={{ ...styles.statCard, cursor: "default", borderColor: "#1B6B6333" }}>
            <div style={{ ...styles.statValue, color: "#1B6B63" }}>{myChanges.length}</div>
            <div style={styles.statLabel}>Total dressings logged</div>
          </div>
        </div>
        {myChanges.length === 0 ? <EmptyState text="Your dressing changes will show up here." /> : (
          <div style={styles.card}>
            {myChanges.slice(0, 15).map((e) => (
              <div key={e.id} style={styles.dresserLine}>
                <span style={{ flex: 1 }}>{e.patientName}</span>
                <span style={styles.mutedSmall}>{fmtDate(e.date)}</span>
              </div>
            ))}
          </div>
        )}
      </main>
      {toast && <div style={styles.toast}>✓ {toast}</div>}
    </>
  );
}

function DresserNewCaseForm({ profile, machines, products, onCancel, onSave }) {
  const [form, setForm] = useState({
    patientName: "", patientMobile: "", doctorName: "", protocolDays: 5,
    machineSerial: "", product: products[0] ? products[0].name : "",
    applicationDate: todayISO(), applicationTime: nowTimeHM(), notes: "",
  });
  const [showMore, setShowMore] = useState(false);
  const set = (k, v) => setForm((f) => ({ ...f, [k]: v }));

  const submit = () => {
    if (!form.patientName.trim() || !form.doctorName.trim()) return;
    onSave({ ...form, protocolDays: Number(form.protocolDays) || 5, status: "active", billTo: "Patient", totalAmount: 0 });
  };

  return (
    <div style={styles.card}>
      <div style={{ padding: 14 }}>
        <div style={styles.detailLabel}>Reporting as</div>
        <div style={{ fontWeight: 700, marginBottom: 10 }}>{profile.display_name}</div>
        <div style={styles.formGrid}>
          <Field label="Patient Name"><input style={styles.input} value={form.patientName} onChange={(e) => set("patientName", e.target.value)} /></Field>
          <Field label="Doctor Name"><input style={styles.input} value={form.doctorName} onChange={(e) => set("doctorName", e.target.value)} /></Field>
          <Field label="Products">
            <select style={styles.input} value={form.product} onChange={(e) => set("product", e.target.value)}>
              {products.map((p) => <option key={p.id} value={p.name}>{p.name}</option>)}
            </select>
          </Field>
          <Field label="Machine Serial No.">
            <select style={styles.input} value={form.machineSerial} onChange={(e) => set("machineSerial", e.target.value)}>
              <option value="">— None —</option>
              {machines.map((m) => <option key={m.id} value={m.serial}>{m.serial} ({m.model})</option>)}
            </select>
          </Field>
          <Field label="Therapy Protocol">
            <select style={styles.input} value={form.protocolDays} onChange={(e) => set("protocolDays", Number(e.target.value))}>
              {PROTOCOLS.map((p) => <option key={p} value={p}>Every {p} days</option>)}
            </select>
          </Field>
          {showMore && (
            <>
              <Field label="Patient Mobile Number"><input type="tel" style={styles.input} value={form.patientMobile} onChange={(e) => set("patientMobile", e.target.value)} /></Field>
              <Field label="Application Date"><input type="date" style={styles.input} value={form.applicationDate} onChange={(e) => set("applicationDate", e.target.value)} /></Field>
              <Field label="Application Time"><input type="time" style={styles.input} value={form.applicationTime} onChange={(e) => set("applicationTime", e.target.value)} /></Field>
              <Field label="Notes"><textarea style={{ ...styles.input, minHeight: 60 }} value={form.notes} onChange={(e) => set("notes", e.target.value)} /></Field>
            </>
          )}
          <button type="button" style={styles.linkBtn} onClick={() => setShowMore((s) => !s)}>{showMore ? "− Fewer details" : "+ More details"}</button>
        </div>
        <div style={styles.formActions}>
          <button style={styles.secondaryBtn} onClick={onCancel}>Cancel</button>
          <button style={styles.primaryBtn} onClick={submit}>Save Case</button>
        </div>
      </div>
    </div>
  );
}

function DresserCaseRow({ c, profile, onAddDressingChange, onCapturePhoto }) {
  const [open, setOpen] = useState(false);
  const [protocolDays, setProtocolDays] = useState(c.protocolDays || 5);
  const [note, setNote] = useState("");
  const [uploading, setUploading] = useState(null);
  const due = nextDueDate(c);
  const overdue = overdueDays(c);
  const flags = c.photoFlags || {};
  const doneCount = PHOTO_STAGES.filter((s) => flags[s.key]).length;

  const handleFile = async (stage, file) => {
    if (!file) return;
    setUploading(stage);
    try {
      const dataURL = await compressImage(file);
      onCapturePhoto(stage, dataURL);
    } catch (e) { console.error(e); }
    setUploading(null);
  };

  return (
    <div style={styles.card}>
      <div style={styles.cardTop} onClick={() => setOpen((o) => !o)}>
        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={styles.cardTitle}>{c.patientName}</div>
          <div style={styles.cardMeta}>Dr. {c.doctorName} · {c.product}</div>
          <div style={styles.cardMeta}>Machine {c.machineSerial || "—"} · {c.protocolDays || 5}-day protocol</div>
          <div style={styles.mutedSmall}>{doneCount}/3 photos captured</div>
        </div>
        <div style={{ display: "flex", flexDirection: "column", alignItems: "flex-end", gap: 6 }}>
          {overdue > 0 ? <span style={styles.overdueTag}>{overdue}d overdue</span> : <span style={styles.mutedSmall}>Due {fmtDate(due)}</span>}
        </div>
      </div>
      {open && (
        <div style={styles.cardExpanded}>
          <div style={styles.detailLabel}>Required photos</div>
          <div style={styles.photoRow}>
            {PHOTO_STAGES.map((s) => (
              <label key={s.key} style={{ ...styles.photoChip, ...(flags[s.key] ? styles.photoChipDone : {}) }}>
                {flags[s.key] ? "✓ " : ""}{s.label}
                {uploading === s.key && "…"}
                <input type="file" accept="image/*" capture="environment" style={{ display: "none" }}
                  onChange={(e) => handleFile(s.key, e.target.files[0])} />
              </label>
            ))}
          </div>

          <div style={{ ...styles.detailLabel, marginTop: 14 }}>Log a dressing change</div>
          <div style={styles.addPaymentRow}>
            <select value={protocolDays} onChange={(e) => setProtocolDays(Number(e.target.value))} style={styles.smallInput}>
              {PROTOCOLS.map((p) => <option key={p} value={p}>{p}d</option>)}
            </select>
          </div>
          <input type="text" placeholder="Note (optional)" value={note} onChange={(e) => setNote(e.target.value)}
            style={{ ...styles.smallInput, width: "100%", marginTop: 8, boxSizing: "border-box" }} />
          <button style={{ ...styles.smallBtn, width: "100%", marginTop: 8 }} onClick={() => {
            onAddDressingChange({ date: todayISO(), dresserId: profile.id, protocolDays, note });
            setNote(""); setOpen(false);
          }}>Log Today's Change</button>
        </div>
      )}
    </div>
  );
}

// ---------------- Dashboard ----------------
function Dashboard({ cases, machines, outstandingTotal, activeCount, machinesInUseCount, overdueCount, dresserStats, lowStock, products, setTab }) {
  const recentCases = [...cases].sort((a, b) => new Date(b.applicationDate) - new Date(a.applicationDate)).slice(0, 5);

  return (
    <div>
      <div style={styles.cardGrid}>
        <StatCard label="Active Cases" value={activeCount} accent="#1B6B63" onClick={() => setTab("cases")} />
        <StatCard label="Change Due / Overdue" value={overdueCount} accent="#B3542F" onClick={() => setTab("cases")} />
        <StatCard label="Outstanding" value={fmtMoney(outstandingTotal)} accent="#B3542F" onClick={() => setTab("cases")} />
        <StatCard label="Machines In Use" value={`${machinesInUseCount} / ${machines.length}`} accent="#3B5BA5" onClick={() => setTab("inventory")} />
      </div>

      {lowStock.length > 0 && (
        <>
          <SectionTitle>Stock Alerts</SectionTitle>
          <div style={styles.card}>
            {lowStock.map((p) => (
              <div key={p.id} style={styles.dresserLine}><span style={{ flex: 1, fontWeight: 600 }}>{p.name}</span><span style={{ color: "#B3542F", fontSize: 12, fontWeight: 700 }}>{p.available || 0} left</span></div>
            ))}
          </div>
        </>
      )}

      {dresserStats.length > 0 && (
        <>
          <SectionTitle>Dresser Workload</SectionTitle>
          <div style={styles.card}>
            {dresserStats.map((d, i) => (
              <div key={d.name} style={styles.dresserLine}><span style={styles.dresserRank}>{i + 1}</span><span style={{ flex: 1, fontWeight: 600 }}>{d.name}</span><span style={styles.mutedSmall}>{d.count} dressing{d.count > 1 ? "s" : ""}</span></div>
            ))}
          </div>
        </>
      )}

      <SectionTitle>Recent Cases</SectionTitle>
      {recentCases.length === 0 ? <EmptyState text="No cases yet. Add your first case from the Cases tab." /> : (
        <div style={styles.list}>{recentCases.map((c) => <CaseRow key={c.id} c={c} products={products} compact />)}</div>
      )}
    </div>
  );
}

function StatCard({ label, value, accent, onClick }) {
  return (
    <button onClick={onClick} style={{ ...styles.statCard, borderColor: accent + "33" }}>
      <div style={{ ...styles.statValue, color: accent }}>{value}</div>
      <div style={styles.statLabel}>{label}</div>
    </button>
  );
}
function SectionTitle({ children }) { return <div style={styles.sectionTitle}>{children}</div>; }
function EmptyState({ text }) { return <div style={styles.emptyState}>{text}</div>; }

// ---------------- Cases (Owner) ----------------
function CasesTab({ cases, machines, products, dressers, saveCase, deleteCase, addPayment, addDressingChange, getPhotoUrl }) {
  const [showForm, setShowForm] = useState(false);
  const [editing, setEditing] = useState(null);
  const [filter, setFilter] = useState("all");

  const filtered = cases.filter((c) => {
    if (filter === "all") return true;
    if (filter === "overdue") return overdueDays(c) > 0;
    return c.status === filter;
  });
  const sorted = [...filtered].sort((a, b) => new Date(b.applicationDate) - new Date(a.applicationDate));

  if (showForm) {
    return (
      <CaseForm machines={machines} products={products} dressers={dressers} initial={editing}
        onCancel={() => { setShowForm(false); setEditing(null); }}
        onSave={(data) => { saveCase(data, editing ? editing.id : null); setShowForm(false); setEditing(null); }} />
    );
  }

  return (
    <div>
      <div style={styles.filterRow}>
        {["all", "active", "overdue", "stopped", "reapplied"].map((f) => (
          <button key={f} onClick={() => setFilter(f)} style={{ ...styles.filterChip, ...(filter === f ? styles.filterChipActive : {}) }}>
            {f === "all" ? "All" : f === "overdue" ? "Change Due" : STATUS[f].label}
          </button>
        ))}
      </div>
      <button style={styles.primaryBtn} onClick={() => setShowForm(true)}>+ New Case</button>
      {sorted.length === 0 ? <EmptyState text="No cases match this filter." /> : (
        <div style={styles.list}>
          {sorted.map((c) => (
            <CaseRow key={c.id} c={c} products={products} getPhotoUrl={getPhotoUrl}
              onEdit={() => { setEditing(c); setShowForm(true); }}
              onDelete={() => deleteCase(c.id)}
              onAddPayment={(p) => addPayment(c.id, p)}
              onAddDressingChange={(e) => addDressingChange(c.id, e)} />
          ))}
        </div>
      )}
    </div>
  );
}

function CaseRow({ c, products = [], compact, getPhotoUrl, onEdit, onDelete, onAddPayment, onAddDressingChange }) {
  const [open, setOpen] = useState(false);
  const [payAmount, setPayAmount] = useState("");
  const [payNote, setPayNote] = useState("");
  const [payMode, setPayMode] = useState("Cash");
  const [changeProtocol, setChangeProtocol] = useState(c.protocolDays || 5);
  const [changeNote, setChangeNote] = useState("");
  const [photoData, setPhotoData] = useState({});

  const st = STATUS[c.status] || STATUS.active;
  const paid = (c.payments || []).reduce((s, p) => s + Number(p.amount || 0), 0);
  const outstanding = Math.max(0, Number(c.totalAmount || 0) - paid);
  const days = Math.max(0, daysBetween(c.applicationDate, c.status === "active" ? todayISO() : c.endDate || c.applicationDate));
  const due = nextDueDate(c);
  const overdue = overdueDays(c);
  const changes = (c.dressingChanges || []).slice().sort((a, b) => new Date(b.date) - new Date(a.date));
  const flags = c.photoFlags || {};
  const profit = estimateProfit(c, products);

  useEffect(() => {
    if (!open || compact) return;
    PHOTO_STAGES.forEach((s) => {
      if (flags[s.key] && !photoData[s.key]) {
        getPhotoUrl(c.id, s.key).then((url) => { if (url) setPhotoData((prev) => ({ ...prev, [s.key]: url })); });
      }
    });
    // eslint-disable-next-line
  }, [open]);

  return (
    <div style={styles.card}>
      <div style={styles.cardTop} onClick={() => !compact && setOpen((o) => !o)}>
        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={styles.cardTitle}>{c.patientName}</div>
          <div style={styles.cardMeta}>Dr. {c.doctorName} · {c.product} · {c.protocolDays || 5}-day protocol</div>
          <div style={styles.cardMeta}>Machine {c.machineSerial || "—"} · {fmtDate(c.applicationDate)}{c.applicationTime ? ` ${fmtTime(c.applicationTime)}` : ""} · {days}d</div>
          {c.dresserName && <div style={styles.cardMeta}>Dresser: {c.dresserName} · Bill to: {c.billTo || "Patient"}{c.billTo === "Hospital" && c.hospitalName ? ` (${c.hospitalName})` : ""}</div>}
        </div>
        <div style={{ display: "flex", flexDirection: "column", alignItems: "flex-end", gap: 6 }}>
          <span style={{ ...styles.badge, color: st.color, background: st.bg }}>{st.label}</span>
          {c.status === "active" && overdue > 0 && <span style={styles.overdueTag}>{overdue}d change overdue</span>}
          {c.status === "active" && overdue === 0 && <span style={styles.mutedSmall}>Due {fmtDate(due)}</span>}
          {outstanding > 0 ? <span style={styles.dueTag}>{fmtMoney(outstanding)} due</span> : <span style={styles.paidTag}>Paid up</span>}
        </div>
      </div>

      {!compact && open && (
        <div style={styles.cardExpanded}>
          <div style={styles.detailGrid}>
            <Detail label="Application" value={`${fmtDate(c.applicationDate)}${c.applicationTime ? ` · ${fmtTime(c.applicationTime)}` : ""}`} />
            <Detail label={c.status === "active" ? "Next Change Due" : "Stop / Reapply Date"} value={c.status === "active" ? fmtDate(due) : fmtDate(c.endDate)} highlight={c.status === "active" && overdue > 0} />
            <Detail label="Patient Mobile" value={c.patientMobile || "—"} />
            <Detail label="Bill To" value={c.billTo === "Hospital" ? (c.hospitalName || "Hospital") : "Patient"} />
            <Detail label="Total Amount" value={fmtMoney(c.totalAmount)} />
            <Detail label="Paid" value={fmtMoney(paid)} />
            <Detail label="Outstanding" value={fmtMoney(outstanding)} highlight={outstanding > 0} />
            <Detail label="Est. Profit" value={fmtMoney(profit)} highlight={profit < 0} />
          </div>

          {c.notes && <div style={styles.notesBox}><div style={styles.detailLabel}>Notes</div><div style={styles.notesText}>{c.notes}</div></div>}

          <div style={styles.detailLabel}>Verification photos</div>
          <div style={styles.photoRow}>
            {PHOTO_STAGES.map((s) => (
              <div key={s.key} style={styles.photoThumbWrap}>
                {photoData[s.key] ? (
                  <img src={photoData[s.key]} alt={s.label} style={styles.photoThumb} onClick={() => window.open(photoData[s.key], "_blank")} />
                ) : (
                  <div style={styles.photoThumbEmpty}>{flags[s.key] ? "…" : "Not captured"}</div>
                )}
                <div style={styles.mutedSmall}>{s.label}</div>
              </div>
            ))}
          </div>

          <div style={{ ...styles.paymentsSection, marginTop: 14 }}>
            <div style={styles.detailLabel}>Dressing change log</div>
            {changes.length === 0 ? <div style={styles.mutedSmall}>No dressing changes recorded.</div> : (
              changes.map((e) => (
                <div key={e.id} style={styles.paymentLine}><span>{fmtDate(e.date)}</span><span>{e.dresserName || "—"}</span><span style={styles.mutedSmall}>{e.protocolDays}d{e.note ? ` · ${e.note}` : ""}</span></div>
              ))
            )}
            {c.status === "active" && (
              <div style={styles.addPaymentRow}>
                <select value={changeProtocol} onChange={(e) => setChangeProtocol(Number(e.target.value))} style={styles.smallInput}>
                  {PROTOCOLS.map((p) => <option key={p} value={p}>{p}d</option>)}
                </select>
                <input type="text" placeholder="Note (optional)" value={changeNote} onChange={(e) => setChangeNote(e.target.value)} style={{ ...styles.smallInput, flex: 1 }} />
                <button style={styles.smallBtn} onClick={() => {
                  onAddDressingChange({ date: todayISO(), dresserId: c.dresserId, protocolDays: changeProtocol, note: changeNote });
                  setChangeNote("");
                }}>Log Change</button>
              </div>
            )}
          </div>

          <div style={{ ...styles.paymentsSection, marginTop: 14 }}>
            <div style={styles.detailLabel}>Payment history</div>
            {(c.payments || []).length === 0 ? <div style={styles.mutedSmall}>No payments recorded.</div> : (
              (c.payments || []).slice().sort((a, b) => new Date(b.date) - new Date(a.date)).map((p) => (
                <div key={p.id} style={styles.paymentLine}><span>{fmtDate(p.date)}</span><span>{fmtMoney(p.amount)}</span><span style={styles.mutedSmall}>{p.mode || "Cash"}{p.note ? ` · ${p.note}` : ""}</span></div>
              ))
            )}
            {outstanding > 0 && (
              <div style={styles.addPaymentRow}>
                <input type="number" placeholder="Amount" value={payAmount} onChange={(e) => setPayAmount(e.target.value)} style={styles.smallInput} />
                <select value={payMode} onChange={(e) => setPayMode(e.target.value)} style={styles.smallInput}>
                  {PAY_MODES.map((m) => <option key={m} value={m}>{m}</option>)}
                </select>
                <input type="text" placeholder="Note (optional)" value={payNote} onChange={(e) => setPayNote(e.target.value)} style={{ ...styles.smallInput, flex: 1 }} />
                <button style={styles.smallBtn} onClick={() => {
                  const amt = Number(payAmount);
                  if (!amt || amt <= 0) return;
                  onAddPayment({ amount: amt, mode: payMode, note: payNote, date: todayISO() });
                  setPayAmount(""); setPayNote("");
                }}>Add</button>
              </div>
            )}
          </div>

          <div style={styles.actionRow}>
            <button style={styles.linkBtn} onClick={onEdit}>Edit</button>
            <button style={{ ...styles.linkBtn, color: "#B3542F" }} onClick={onDelete}>Delete</button>
          </div>
        </div>
      )}
    </div>
  );
}

function Detail({ label, value, highlight }) {
  return <div><div style={styles.detailLabel}>{label}</div><div style={{ ...styles.detailValue, color: highlight ? "#B3542F" : "#1F2421" }}>{value}</div></div>;
}

function CaseForm({ machines, products, dressers, initial, onCancel, onSave }) {
  const [form, setForm] = useState(initial || {
    patientName: "", patientMobile: "", doctorName: "", dresserId: "", protocolDays: 5,
    machineSerial: "", product: products[0] ? products[0].name : "",
    applicationDate: todayISO(), applicationTime: nowTimeHM(), status: "active", endDate: "",
    billTo: "Patient", hospitalName: "", totalAmount: "", notes: "",
  });
  const [showMore, setShowMore] = useState(!!initial);
  const set = (k, v) => setForm((f) => ({ ...f, [k]: v }));

  const submit = () => {
    if (!form.patientName.trim() || !form.doctorName.trim()) return;
    onSave({ ...form, totalAmount: Number(form.totalAmount) || 0, protocolDays: Number(form.protocolDays) || 5 });
  };

  return (
    <div>
      <SectionTitle>{initial ? "Edit Case" : "New Case"}</SectionTitle>
      <div style={styles.formGrid}>
        <Field label="Patient Name"><input style={styles.input} value={form.patientName} onChange={(e) => set("patientName", e.target.value)} /></Field>
        <Field label="Doctor Name"><input style={styles.input} value={form.doctorName} onChange={(e) => set("doctorName", e.target.value)} /></Field>
        <Field label="Dresser (applied by)">
          <select style={styles.input} value={form.dresserId || ""} onChange={(e) => set("dresserId", e.target.value)}>
            <option value="">— None —</option>
            {dressers.map((d) => <option key={d.id} value={d.id}>{d.display_name}</option>)}
          </select>
        </Field>
        <Field label="Total Amount (₹)"><input type="number" style={styles.input} value={form.totalAmount} onChange={(e) => set("totalAmount", e.target.value)} /></Field>
       <Field label="Products">
  <div style={{ display: "flex", flexDirection: "column", gap: 4, border: "1px solid #ccc", borderRadius: 6, padding: 8, maxHeight: 140, overflowY: "auto" }}>
    {products.map((p) => (
      <label key={p.id} style={{ display: "flex", alignItems: "center", gap: 6, fontSize: 13 }}>
        <input
          type="checkbox"
          checked={(form.products || []).includes(p.name)}
          onChange={(e) => {
            const current = form.products || [];
            const next = e.target.checked ? [...current, p.name] : current.filter((n) => n !== p.name);
            set("products", next);
          }}
        />
        {p.name}
      </label>
    ))}
  </div>
</Field> {showMore && (
          <>
            <Field label="Patient Mobile Number"><input type="tel" style={styles.input} value={form.patientMobile} onChange={(e) => set("patientMobile", e.target.value)} placeholder="10-digit number" /></Field>
            <Field label="Therapy Protocol">
              <select style={styles.input} value={form.protocolDays} onChange={(e) => set("protocolDays", Number(e.target.value))}>
                {PROTOCOLS.map((p) => <option key={p} value={p}>Every {p} days</option>)}
              </select>
            </Field>
            <Field label="Machine Serial No.">
              <select style={styles.input} value={form.machineSerial} onChange={(e) => set("machineSerial", e.target.value)}>
                <option value="">— None —</option>
                {machines.map((m) => <option key={m.id} value={m.serial}>{m.serial} ({m.model})</option>)}
              </select>
            </Field>
            <Field label="Application Date"><input type="date" style={styles.input} value={form.applicationDate} onChange={(e) => set("applicationDate", e.target.value)} /></Field>
            <Field label="Application Time"><input type="time" style={styles.input} value={form.applicationTime} onChange={(e) => set("applicationTime", e.target.value)} /></Field>
            <Field label="Status">
              <select style={styles.input} value={form.status} onChange={(e) => set("status", e.target.value)}>
                <option value="active">On Therapy</option>
                <option value="stopped">Stopped</option>
                <option value="reapplied">Reapplied</option>
              </select>
            </Field>
            {form.status !== "active" && (
              <Field label={form.status === "stopped" ? "Stop Date" : "Reapply Date"}>
                <input type="date" style={styles.input} value={form.endDate} onChange={(e) => set("endDate", e.target.value)} />
              </Field>
            )}
            <Field label="Bill To">
              <select style={styles.input} value={form.billTo} onChange={(e) => set("billTo", e.target.value)}>
                <option value="Patient">Patient</option>
                <option value="Hospital">Hospital</option>
              </select>
            </Field>
            {form.billTo === "Hospital" && (
              <Field label="Hospital Name"><input style={styles.input} value={form.hospitalName} onChange={(e) => set("hospitalName", e.target.value)} /></Field>
            )}
            <Field label="Notes"><textarea style={{ ...styles.input, minHeight: 60 }} value={form.notes} onChange={(e) => set("notes", e.target.value)} /></Field>
          </>
        )}
        <button type="button" style={styles.linkBtn} onClick={() => setShowMore((s) => !s)}>{showMore ? "− Fewer details" : "+ More details"}</button>
      </div>
      <div style={styles.formActions}>
        <button style={styles.secondaryBtn} onClick={onCancel}>Cancel</button>
        <button style={styles.primaryBtn} onClick={submit}>Save Case</button>
      </div>
    </div>
  );
}

function Field({ label, children }) {
  return <div style={styles.field}><label style={styles.fieldLabel}>{label}</label>{children}</div>;
}

// ---------------- Inventory (Owner) ----------------
function InventoryTab({ machines, addMachine, removeMachine, machineInUse, cases, products, addProduct, updateProductCost, removeProduct, receiveStock }) {
  const [sub, setSub] = useState("machines");
  return (
    <div>
      <div style={styles.filterRow}>
        <button onClick={() => setSub("machines")} style={{ ...styles.filterChip, ...(sub === "machines" ? styles.filterChipActive : {}) }}>Machines</button>
        <button onClick={() => setSub("stock")} style={{ ...styles.filterChip, ...(sub === "stock" ? styles.filterChipActive : {}) }}>Stock</button>
      </div>
      {sub === "machines" && <MachinesTab machines={machines} addMachine={addMachine} removeMachine={removeMachine} machineInUse={machineInUse} cases={cases} />}
      {sub === "stock" && <StockTab products={products} addProduct={addProduct} updateProductCost={updateProductCost} removeProduct={removeProduct} receiveStock={receiveStock} />}
    </div>
  );
}

function MachinesTab({ machines, addMachine, removeMachine, machineInUse, cases }) {
  const [showForm, setShowForm] = useState(false);
  const [serial, setSerial] = useState("");
  const [model, setModel] = useState("");
  const submit = () => {
    if (!serial.trim()) return;
    addMachine(serial, model);
    setSerial(""); setModel(""); setShowForm(false);
  };

  return (
    <div>
      {showForm ? (
        <div style={styles.formGrid}>
          <Field label="Serial Number"><input style={styles.input} value={serial} onChange={(e) => setSerial(e.target.value)} /></Field>
          <Field label="Model / Type"><input style={styles.input} value={model} onChange={(e) => setModel(e.target.value)} placeholder="e.g. NPWT Unit" /></Field>
          <div style={styles.formActions}>
            <button style={styles.secondaryBtn} onClick={() => setShowForm(false)}>Cancel</button>
            <button style={styles.primaryBtn} onClick={submit}>Add Machine</button>
          </div>
        </div>
      ) : <button style={styles.primaryBtn} onClick={() => setShowForm(true)}>+ Add Machine</button>}

      {machines.length === 0 ? <EmptyState text="No machines added yet." /> : (
        <div style={styles.list}>
          {machines.map((m) => {
            const inUse = machineInUse(m.serial);
            const activeCase = cases.find((c) => c.machineSerial === m.serial && c.status === "active");
            return (
              <div key={m.id} style={styles.card}>
                <div style={styles.cardTop}>
                  <div style={{ flex: 1 }}>
                    <div style={styles.cardTitle}>{m.serial}</div>
                    <div style={styles.cardMeta}>{m.model}</div>
                    {inUse && activeCase && <div style={styles.mutedSmall}>With {activeCase.patientName} since {fmtDate(activeCase.applicationDate)}</div>}
                  </div>
                  <div style={{ display: "flex", flexDirection: "column", alignItems: "flex-end", gap: 6 }}>
                    <span style={{ ...styles.badge, color: inUse ? "#1B6B63" : "#5A6560", background: inUse ? "#E4F1EE" : "#EEF0EE" }}>{inUse ? "In Use" : "Available"}</span>
                    <button style={{ ...styles.linkBtn, color: "#B3542F" }} onClick={() => removeMachine(m.id)}>Remove</button>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

// ---------------- Stock ----------------
function StockTab({ products, addProduct, updateProductCost, removeProduct, receiveStock }) {
  const [name, setName] = useState("");
  const [initQty, setInitQty] = useState("");
  const [initCost, setInitCost] = useState("");
  const [receiveForm, setReceiveForm] = useState({});

  const submitAdd = () => {
    if (!name.trim() || products.some((p) => p.name === name.trim())) return;
    addProduct(name, initQty, initCost);
    setName(""); setInitQty(""); setInitCost("");
  };
  const setField = (id, field, val) => setReceiveForm((prev) => ({ ...prev, [id]: { ...prev[id], [field]: val } }));
  const doReceive = (id) => {
    const f = receiveForm[id] || {};
    const qty = Number(f.qty);
    if (!qty || qty <= 0) return;
    receiveStock(id, qty, f.company);
    setReceiveForm((prev) => ({ ...prev, [id]: { qty: "", company: "" } }));
  };

  return (
    <div>
      <SectionTitle>Add Product</SectionTitle>
      <div style={styles.formGrid}>
        <div style={styles.addPaymentRow}>
          <input style={{ ...styles.smallInput, flex: 1 }} placeholder="Product name" value={name} onChange={(e) => setName(e.target.value)} />
          <input style={{ ...styles.smallInput, width: 70 }} type="number" placeholder="Qty" value={initQty} onChange={(e) => setInitQty(e.target.value)} />
          <input style={{ ...styles.smallInput, width: 90 }} type="number" placeholder="Cost ₹" value={initCost} onChange={(e) => setInitCost(e.target.value)} />
        </div>
        <button style={styles.primaryBtn} onClick={submitAdd}>Add Product</button>
      </div>

      <SectionTitle>Inventory</SectionTitle>
      <div style={styles.list}>
        {products.map((p) => (
          <div key={p.id} style={styles.card}>
            <div style={styles.cardTop}>
              <div style={{ flex: 1 }}>
                <div style={styles.cardTitle}>{p.name}</div>
                <div style={styles.cardMeta}>{p.used || 0} used all-time</div>
              </div>
              <div style={{ display: "flex", flexDirection: "column", alignItems: "flex-end", gap: 6 }}>
                <span style={{ ...styles.badge, color: (p.available || 0) <= LOW_STOCK_THRESHOLD ? "#B3542F" : "#1B6B63", background: (p.available || 0) <= LOW_STOCK_THRESHOLD ? "#F5E4DC" : "#E4F1EE" }}>{p.available || 0} available</span>
                <button style={{ ...styles.linkBtn, color: "#B3542F" }} onClick={() => removeProduct(p.id)}>Remove</button>
              </div>
            </div>
            <div style={{ padding: "0 14px 14px" }}>
              <div style={styles.addPaymentRow}>
                <span style={styles.mutedSmall}>Cost price ₹</span>
                <input type="number" style={styles.smallInput} defaultValue={p.costPrice || 0} onBlur={(e) => updateProductCost(p.id, e.target.value)} />
              </div>
              <div style={styles.addPaymentRow}>
                <input type="number" placeholder="Qty received" value={(receiveForm[p.id] || {}).qty || ""} onChange={(e) => setField(p.id, "qty", e.target.value)} style={styles.smallInput} />
                <input type="text" placeholder="Company / supplier" value={(receiveForm[p.id] || {}).company || ""} onChange={(e) => setField(p.id, "company", e.target.value)} style={{ ...styles.smallInput, flex: 1 }} />
                <button style={styles.smallBtn} onClick={() => doReceive(p.id)}>Receive Stock</button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

// ---------------- Team (Owner) ----------------
function TeamTab({ dressers, addDresserAccount, removeDresserAccount, dresserStats, cases, products, outstandingTotal, overdueCount, lowStock }) {
  const [sub, setSub] = useState("dressers");
  return (
    <div>
      <div style={styles.filterRow}>
        <button onClick={() => setSub("dressers")} style={{ ...styles.filterChip, ...(sub === "dressers" ? styles.filterChipActive : {}) }}>Dressers</button>
        <button onClick={() => setSub("reports")} style={{ ...styles.filterChip, ...(sub === "reports" ? styles.filterChipActive : {}) }}>Reports</button>
      </div>
      {sub === "dressers" && <DressersTab dressers={dressers} addDresserAccount={addDresserAccount} removeDresserAccount={removeDresserAccount} dresserStats={dresserStats} />}
      {sub === "reports" && <ReportsTab cases={cases} products={products} dresserStats={dresserStats} dressers={dressers} outstandingTotal={outstandingTotal} overdueCount={overdueCount} lowStock={lowStock} />}
    </div>
  );
}

function DressersTab({ dressers, addDresserAccount, removeDresserAccount, dresserStats }) {
  const [name, setName] = useState("");
  const [password, setPassword] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [created, setCreated] = useState(null);
  const countFor = (n) => (dresserStats.find((d) => d.name.toLowerCase() === n.toLowerCase()) || {}).count || 0;

  const submit = async () => {
    setError(""); setCreated(null);
    if (!name.trim()) { setError("Enter a name"); return; }
    const pw = password.trim() || genPassword();
    setBusy(true);
    try {
      const result = await addDresserAccount(name, pw);
      setCreated({ name: name.trim(), password: pw });
      setName(""); setPassword("");
    } catch (e) { setError(e.message || "Could not create dresser account"); }
    setBusy(false);
  };

  return (
    <div>
      <SectionTitle>Add Dresser</SectionTitle>
      <div style={styles.formGrid}>
        <div style={styles.addPaymentRow}>
          <input style={{ ...styles.smallInput, flex: 1 }} placeholder="Dresser's name" value={name} onChange={(e) => setName(e.target.value)} />
          <input style={{ ...styles.smallInput, width: 120 }} placeholder="Password (or auto)" value={password} onChange={(e) => setPassword(e.target.value)} />
        </div>
        <button style={styles.primaryBtn} onClick={submit} disabled={busy}>{busy ? "Adding…" : "Add"}</button>
      </div>
      {error && <div style={styles.gateError}>{error}</div>}
      {created && (
        <div style={{ ...styles.notesBox, marginBottom: 14 }}>
          <div style={styles.detailLabel}>Tell {created.name}:</div>
          <div style={styles.notesText}>Name: <b>{created.name}</b><br />Password: <b>{created.password}</b></div>
        </div>
      )}
      <div style={styles.emptyState2}>Only accounts created here can log in. Passwords are shown once — write them down before adding the next person.</div>

      <SectionTitle>Team</SectionTitle>
      {dressers.length === 0 ? (
        <EmptyState text="No dressers added yet." />
      ) : (
        <div style={styles.list}>
          {dressers.map((d) => (
            <div key={d.id} style={styles.card}>
              <div style={styles.cardTop}>
                <div style={{ flex: 1 }}>
                  <div style={styles.cardTitle}>{d.display_name}</div>
                  <div style={styles.cardMeta}>{countFor(d.display_name)} dressing{countFor(d.display_name) === 1 ? "" : "s"} logged</div>
                </div>
                <button style={{ ...styles.linkBtn, color: "#B3542F" }} onClick={() => removeDresserAccount(d.id)}>Remove</button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

// ---------------- Reports (Owner) ----------------
function ReportsTab({ cases, products, dresserStats, dressers, outstandingTotal, overdueCount, lowStock }) {
  const [locations, setLocations] = useState({});
  const [expanded, setExpanded] = useState(null);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      const map = {};
      cases.forEach(() => {});
      if (!cancelled) setLocations(map);
    })();
    return () => { cancelled = true; };
  }, [dressers]);

  const totalBilled = cases.reduce((s, c) => s + Number(c.totalAmount || 0), 0);
  const totalCollected = cases.reduce((s, c) => s + (c.payments || []).reduce((a, p) => a + Number(p.amount || 0), 0), 0);
  const collectedByMode = useMemo(() => {
    const tally = { Cash: 0, Online: 0, Credit: 0 };
    cases.forEach((c) => (c.payments || []).forEach((p) => { tally[p.mode || "Cash"] = (tally[p.mode || "Cash"] || 0) + Number(p.amount || 0); }));
    return tally;
  }, [cases]);
  const totalProfit = cases.reduce((s, c) => s + estimateProfit(c, products), 0);

  const sendSummary = () => {
    let msg = `Bhagirathi Agency — Daily Summary\n`;
    msg += `Overdue changes: ${overdueCount}\nOutstanding: ${fmtMoney(outstandingTotal)}\n`;
    if (lowStock.length) msg += `Low stock: ${lowStock.map((p) => p.name).join(", ")}\n`;
    window.open(waLink(OWNER_WHATSAPP, msg), "_blank");
  };

  return (
    <div>
      <SectionTitle>Revenue</SectionTitle>
      <div style={styles.cardGrid}>
        <div style={styles.reportCard}><div style={styles.statValue}>{fmtMoney(totalBilled)}</div><div style={styles.statLabel}>Total Billed</div></div>
        <div style={styles.reportCard}><div style={{ ...styles.statValue, color: "#1B6B63" }}>{fmtMoney(totalCollected)}</div><div style={styles.statLabel}>Total Collected</div></div>
        <div style={styles.reportCard}><div style={{ ...styles.statValue, color: "#B3542F" }}>{fmtMoney(outstandingTotal)}</div><div style={styles.statLabel}>Outstanding</div></div>
        <div style={styles.reportCard}><div style={{ ...styles.statValue, color: "#3B5BA5" }}>{fmtMoney(totalProfit)}</div><div style={styles.statLabel}>Est. Profit</div></div>
      </div>

      <div style={styles.card}>
        {PAY_MODES.map((m) => (
          <div key={m} style={styles.dresserLine}><span style={{ flex: 1, fontWeight: 600 }}>{m}</span><span style={styles.mutedSmall}>{fmtMoney(collectedByMode[m] || 0)}</span></div>
        ))}
      </div>

      <button style={styles.primaryBtn} onClick={sendSummary}>Send Summary on WhatsApp</button>

      <SectionTitle>Stock Overview</SectionTitle>
      <div style={styles.card}>
        {products.map((p) => (
          <div key={p.id} style={styles.dresserLine}>
            <span style={{ flex: 1, fontWeight: 600 }}>{p.name}</span>
            <span style={styles.mutedSmall}>{p.available || 0} avail · {p.used || 0} used</span>
          </div>
        ))}
      </div>

      <SectionTitle>Dresser Workload</SectionTitle>
      {dresserStats.length === 0 ? <EmptyState text="No dressing changes logged yet." /> : (
        <div style={styles.card}>
          {dresserStats.map((d, i) => (
            <div key={d.name} style={styles.dresserLine}><span style={styles.dresserRank}>{i + 1}</span><span style={{ flex: 1, fontWeight: 600 }}>{d.name}</span><span style={styles.mutedSmall}>{d.count} dressings</span></div>
          ))}
        </div>
      )}

      <div style={styles.emptyState2}>Dresser location tracking will return in the next update — it now needs a live map view backed by the database instead of the old device storage.</div>
    </div>
  );
}

// ---------------- styles ----------------
const fontImport = `
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=IBM+Plex+Mono:wght@500;600&display=swap');
`;

const styles = {
  app: { fontFamily: "'IBM Plex Mono', ui-monospace, monospace", background: "#F6F5F0", minHeight: "100vh", color: "#1F2421", paddingBottom: 40 },
  loadingScreen: { minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center", background: "#F6F5F0" },
  loadingText: { fontFamily: "monospace", color: "#5A6560" },
  header: { background: "#16302E", padding: "18px 16px" },
  headerInner: { display: "flex", alignItems: "center", gap: 12, maxWidth: 640, margin: "0 auto" },
  brandMark: { width: 38, height: 38, borderRadius: 10, background: "#1B6B63", color: "#F6F5F0", display: "flex", alignItems: "center", justifyContent: "center", fontFamily: "'Space Grotesk', sans-serif", fontWeight: 700, fontSize: 18 },
  brandMarkLg: { width: 56, height: 56, borderRadius: 14, background: "#1B6B63", color: "#F6F5F0", display: "flex", alignItems: "center", justifyContent: "center", fontFamily: "'Space Grotesk', sans-serif", fontWeight: 700, fontSize: 26, margin: "60px auto 14px" },
  gateBrand: { textAlign: "center", color: "#16302E", fontFamily: "'Space Grotesk', sans-serif", fontWeight: 700, fontSize: 18 },
  brandName: { color: "#F6F5F0", fontFamily: "'Space Grotesk', sans-serif", fontWeight: 700, fontSize: 16 },
  brandSub: { color: "#9FC2BC", fontSize: 12, letterSpacing: 0.3, textAlign: "center" },
  logoutBtn: { background: "transparent", border: "1px solid #3A5854", color: "#9FC2BC", borderRadius: 20, padding: "6px 12px", fontSize: 11, fontWeight: 600, cursor: "pointer" },
  pinPanel: { maxWidth: 640, margin: "12px auto 0", background: "#fff", borderRadius: 12, padding: 14 },
  gateWrap: { maxWidth: 360, margin: "0 auto", padding: "0 20px", textAlign: "center" },
  gateOptions: { display: "flex", flexDirection: "column", gap: 10, marginTop: 40 },
  gateBtn: { background: "#1B6B63", color: "#fff", border: "none", borderRadius: 12, padding: "16px", fontSize: 15, fontWeight: 700, fontFamily: "'Space Grotesk', sans-serif", cursor: "pointer" },
  gateBtnAlt: { background: "#fff", color: "#1B6B63", border: "1px solid #1B6B63" },
  gateForm: { display: "flex", flexDirection: "column", gap: 10, marginTop: 30, textAlign: "left" },
  gateHint: { fontSize: 12, color: "#5A6560", textAlign: "center", marginBottom: 6 },
  gateInput: { border: "1px solid #DCD8CC", borderRadius: 10, padding: "12px 14px", fontSize: 15, fontFamily: "inherit", background: "#fff", textAlign: "center" },
  gateError: { color: "#B3542F", fontSize: 12, textAlign: "center" },
  nav: { display: "flex", gap: 6, padding: "10px 16px", maxWidth: 640, margin: "0 auto", overflowX: "auto" },
  navBtn: { border: "1px solid #DCD8CC", background: "#fff", color: "#5A6560", padding: "8px 14px", borderRadius: 20, fontSize: 13, fontFamily: "'Space Grotesk', sans-serif", fontWeight: 600, cursor: "pointer", whiteSpace: "nowrap" },
  navBtnActive: { background: "#1B6B63", color: "#fff", borderColor: "#1B6B63" },
  main: { maxWidth: 640, margin: "0 auto", padding: "8px 16px" },
  cardGrid: { display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10, margin: "8px 0 20px" },
  statCard: { textAlign: "left", border: "1px solid", background: "#fff", borderRadius: 12, padding: "14px 14px", cursor: "pointer" },
  reportCard: { textAlign: "left", border: "1px solid #E7E4D9", background: "#fff", borderRadius: 12, padding: "14px 14px" },
  statValue: { fontFamily: "'Space Grotesk', sans-serif", fontSize: 20, fontWeight: 700 },
  statLabel: { fontSize: 12, color: "#5A6560", marginTop: 4 },
  sectionTitle: { fontFamily: "'Space Grotesk', sans-serif", fontWeight: 700, fontSize: 13, textTransform: "uppercase", letterSpacing: 0.8, color: "#5A6560", margin: "18px 0 8px" },
  emptyState: { color: "#8A9490", fontSize: 13, padding: "24px 0", textAlign: "center", border: "1px dashed #DCD8CC", borderRadius: 12 },
  emptyState2: { color: "#8A9490", fontSize: 11, marginBottom: 8 },
  list: { display: "flex", flexDirection: "column", gap: 10 },
  card: { background: "#fff", border: "1px solid #E7E4D9", borderRadius: 12, overflow: "hidden" },
  cardTop: { display: "flex", padding: 14, gap: 10, cursor: "pointer", alignItems: "flex-start" },
  cardTitle: { fontFamily: "'Space Grotesk', sans-serif", fontWeight: 700, fontSize: 15 },
  cardMeta: { fontSize: 12, color: "#5A6560", marginTop: 2 },
  badge: { fontSize: 11, fontWeight: 700, padding: "4px 9px", borderRadius: 20 },
  dueTag: { fontSize: 11, color: "#B3542F", fontWeight: 700 },
  paidTag: { fontSize: 11, color: "#1B6B63", fontWeight: 700 },
  overdueTag: { fontSize: 11, color: "#fff", background: "#B3542F", fontWeight: 700, padding: "3px 8px", borderRadius: 20 },
  cardExpanded: { borderTop: "1px solid #EFEDE3", padding: 14 },
  detailGrid: { display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12, marginBottom: 10 },
  detailLabel: { fontSize: 10, color: "#8A9490", textTransform: "uppercase", letterSpacing: 0.5 },
  detailValue: { fontSize: 14, fontWeight: 600, marginTop: 2 },
  notesBox: { background: "#F6F5F0", borderRadius: 8, padding: 10, marginBottom: 10 },
  notesText: { fontSize: 13, marginTop: 4 },
  paymentsSection: { marginTop: 6 },
  paymentLine: { display: "flex", justifyContent: "space-between", gap: 8, fontSize: 12, padding: "6px 0", borderBottom: "1px solid #F0EEE3" },
  mutedSmall: { fontSize: 12, color: "#8A9490" },
  addPaymentRow: { display: "flex", gap: 6, marginTop: 10, flexWrap: "wrap" },
  smallInput: { border: "1px solid #DCD8CC", borderRadius: 8, padding: "8px 10px", fontSize: 13, fontFamily: "inherit", minWidth: 90 },
  smallBtn: { background: "#1B6B63", color: "#fff", border: "none", borderRadius: 8, padding: "8px 14px", fontSize: 13, fontWeight: 600, cursor: "pointer" },
  actionRow: { display: "flex", gap: 16, marginTop: 12 },
  linkBtn: { background: "none", border: "none", color: "#1B6B63", fontSize: 12, fontWeight: 700, cursor: "pointer", padding: 0, textDecoration: "none" },
  filterRow: { display: "flex", gap: 6, flexWrap: "wrap", marginBottom: 10 },
  filterChip: { border: "1px solid #DCD8CC", background: "#fff", color: "#5A6560", padding: "6px 12px", borderRadius: 16, fontSize: 12, cursor: "pointer" },
  filterChipActive: { background: "#16302E", color: "#fff", borderColor: "#16302E" },
  primaryBtn: { background: "#1B6B63", color: "#fff", border: "none", borderRadius: 10, padding: "12px 16px", fontSize: 14, fontWeight: 700, fontFamily: "'Space Grotesk', sans-serif", cursor: "pointer", width: "100%", margin: "6px 0 16px" },
  secondaryBtn: { background: "#fff", color: "#5A6560", border: "1px solid #DCD8CC", borderRadius: 10, padding: "12px 16px", fontSize: 14, fontWeight: 600, cursor: "pointer", flex: 1 },
  safetyBtn: { background: "#B3542F", color: "#fff", border: "none", borderRadius: 12, padding: "16px", fontSize: 15, fontWeight: 700, fontFamily: "'Space Grotesk', sans-serif", cursor: "pointer", width: "100%", margin: "10px 0 20px" },
  formGrid: { display: "flex", flexDirection: "column", gap: 12, marginBottom: 16 },
  field: { display: "flex", flexDirection: "column", gap: 4 },
  fieldLabel: { fontSize: 11, color: "#5A6560", fontWeight: 600, textTransform: "uppercase", letterSpacing: 0.4 },
  input: { border: "1px solid #DCD8CC", borderRadius: 8, padding: "10px 12px", fontSize: 14, fontFamily: "inherit", background: "#fff" },
  formActions: { display: "flex", gap: 10 },
  dresserLine: { display: "flex", alignItems: "center", gap: 10, padding: "10px 14px", borderBottom: "1px solid #F0EEE3" },
  dresserRank: { fontFamily: "'Space Grotesk', sans-serif", fontWeight: 700, color: "#8A9490", fontSize: 12, width: 16 },
  photoRow: { display: "flex", gap: 8, flexWrap: "wrap", marginTop: 8 },
  photoChip: { border: "1px solid #DCD8CC", borderRadius: 20, padding: "8px 12px", fontSize: 11, fontWeight: 600, color: "#5A6560", cursor: "pointer", background: "#fff" },
  photoChipDone: { background: "#E4F1EE", color: "#1B6B63", borderColor: "#1B6B63" },
  photoThumbWrap: { textAlign: "center", width: 90 },
  photoThumb: { width: 90, height: 90, objectFit: "cover", borderRadius: 8, cursor: "pointer", border: "1px solid #DCD8CC" },
  photoThumbEmpty: { width: 90, height: 90, borderRadius: 8, border: "1px dashed #DCD8CC", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 10, color: "#8A9490", textAlign: "center" },
  toast: { position: "fixed", left: "50%", bottom: 24, transform: "translateX(-50%)", background: "#16302E", color: "#F6F5F0", padding: "12px 20px", borderRadius: 30, fontSize: 13, fontWeight: 600, boxShadow: "0 6px 20px rgba(0,0,0,0.25)", zIndex: 50, maxWidth: "90%", textAlign: "center" },
};
