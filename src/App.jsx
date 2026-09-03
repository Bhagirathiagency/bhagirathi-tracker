import React, { useState, useEffect, useMemo, useRef } from "react";

// ---------- storage helpers ----------
import { createClient } from "@supabase/supabase-js";
import jsPDF from "jspdf";
import html2canvas from "html2canvas";
import { ResponsiveContainer, LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from "recharts";

const supabase = createClient(
  import.meta.env.VITE_SUPABASE_URL,
  import.meta.env.VITE_SUPABASE_ANON_KEY
);

async function loadKey(key, fallback) {
  try {
    const { data, error } = await supabase
      .from("app_kv")
      .select("value")
      .eq("key", key)
      .maybeSingle();
    if (error || !data) return fallback;
    return data.value;
  } catch (e) {
    return fallback;
  }
}
async function saveKey(key, value) {
  try {
    await supabase
      .from("app_kv")
      .upsert({ key, value, updated_at: new Date().toISOString() });
  } catch (e) {
    console.error("save failed", key, e);
  }
}

const BUSINESSES = [
  { id: "bhagirathi", name: "Bhagirathi Agency", tagline: "Wound Care & NPWT" },
  { id: "leelavac", name: "Leela Medical", tagline: "Wound Care & NPWT" },
];
// Bhagirathi keeps its original, unprefixed keys (that's the live production data already in Supabase).
// Any other business gets its own namespaced keys so nothing overlaps or gets overwritten.
function bkey(businessId, key) {
  return businessId === "bhagirathi" ? key : `${businessId}-${key}`;
}

const uid = () => Math.random().toString(36).slice(2, 10);
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
  active: { label: "VAC Therapy Applied", color: "#D9720A", bg: "#FBEAD3" },
  stopped: { label: "VAC Therapy Stop", color: "#8A5A2B", bg: "#F5EBDC" },
  reapplied: { label: "VAC Therapy Continue", color: "#3B5BA5", bg: "#E7ECF7" },
};
const PROTOCOLS = [5, 7];
const PAY_MODES = ["Cash", "Online", "Credit"];
const DEFAULT_PRODUCTS = [{ id: uid(), name: "Material", available: 0, used: 0, costPrice: 0, receipts: [] }];
const LOW_STOCK_THRESHOLD = 5;
const OWNER_WHATSAPP = "917507777127";
const PHOTO_STAGES = [
  { key: "debridement", label: "After Debridement" },
  { key: "application", label: "After Application" },
  { key: "completion", label: "Therapy Completion" },
];
const QUOTE_STATUS = {
  draft: { label: "Draft", color: "#5B6864", bg: "#EEF1EC" },
  sent: { label: "Sent", color: "#3B5BA5", bg: "#E7ECF7" },
  accepted: { label: "Accepted", color: "#D9720A", bg: "#FBEAD3" },
  rejected: { label: "Rejected", color: "#E1483C", bg: "#FCE7E4" },
};
const DEFAULT_TERMS =
  "1. Prices are in INR and exclusive of GST unless stated otherwise.\n" +
  "2. Delivery / installation within 3-5 working days of confirmation.\n" +
  "3. Payment: 50% advance, balance on delivery/completion.\n" +
  "4. Consumables billed as per actual usage beyond quoted quantity.\n" +
  "5. This quotation is valid till the date mentioned above.";
function nextQuoteNumber(quotations) {
  const year = new Date().getFullYear();
  const prefix = `BA/Q/${year}/`;
  const seq = quotations.filter((q) => (q.quoteNo || "").startsWith(prefix)).length + 1;
  return prefix + String(seq).padStart(3, "0");
}
function quoteTotals(q) {
  const items = q.items || [];
  const subtotal = items.reduce((s, it) => s + Number(it.qty || 0) * Number(it.rate || 0), 0);
  const discount = Number(q.discount || 0);
  const taxable = Math.max(0, subtotal - discount);
  const gstAmount = (taxable * Number(q.gstPercent || 0)) / 100;
  const total = taxable + gstAmount;
  return { subtotal, discount, taxable, gstAmount, total };
}

function latestChange(c) {
  const list = c.dressingChanges || [];
  if (list.length === 0) {
    return { date: c.applicationDate, protocolDays: c.protocolDays || 5, dresserName: c.dresserName };
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
function normalizeProducts(raw) {
  if (!Array.isArray(raw)) return DEFAULT_PRODUCTS;
  return raw.map((p) =>
    typeof p === "string"
      ? { id: uid(), name: p, available: 0, used: 0, costPrice: 0, mrp: 0, receipts: [], variants: [] }
      : { available: 0, used: 0, costPrice: 0, mrp: 0, receipts: [], variants: [], ...p, variants: Array.isArray(p.variants) ? p.variants : [] }
  );
}
function productCompany(p) {
  const receipts = p.receipts || [];
  if (!receipts.length) return "Unspecified";
  const latest = [...receipts].sort((a, b) => new Date(b.date) - new Date(a.date))[0];
  return (latest.company || "Unspecified").trim() || "Unspecified";
}
function groupProductsByCompany(products) {
  const groups = {};
  products.forEach((p) => {
    const co = productCompany(p);
    if (!groups[co]) groups[co] = [];
    groups[co].push(p);
  });
  return Object.entries(groups).sort((a, b) => a[0].localeCompare(b[0]));
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

    return Number(c.totalAmount || 0) + Number(c.machineRentalAmount || 0) - cost - Number(c.doctorCommission || 0);
}
function photoKey(caseId, stage) { return `photo-${caseId}-${stage}`; }
function locKey(businessId, name) { return `${bkey(businessId, "wca-loc")}-${name.trim().toLowerCase().replace(/[^a-z0-9]+/g, "_")}`; }
function mapsLink(lat, lng) { return `https://www.google.com/maps?q=${lat},${lng}`; }
function waLink(number, text) { return `https://wa.me/${number}?text=${encodeURIComponent(text)}`; }

const DAILY_THOUGHTS = [
  "Every dressing you change is a step closer to someone's healing. Thank you for showing up.",
  "Patients remember the hands that cared for them gently. You make that difference today.",
  "Consistency heals. One careful change at a time, you're rebuilding someone's health.",
  "Your work today may not always be seen, but it is always felt.",
  "Small acts of care, done daily, add up to remarkable recoveries. Keep going.",
  "Behind every wound closing is a dresser who showed up on time, every time. That's you.",
  "Precision and patience — the two things you bring to work every single day.",
  "A calm hand and a kind word can be as healing as any dressing. You bring both.",
  "Someone's healing timeline depends on your punctuality today. Thank you for being reliable.",
  "The best care is quiet, steady, and consistent — exactly like the care you give.",
  "Every patient you visit today is one step closer to going home well. Well done.",
  "Great outcomes are built one careful, on-time visit at a time.",
  "Your attention to detail today could be the reason a wound heals without complication.",
  "Trust is earned dressing change by dressing change. You've earned a lot of it.",
  "Take pride in the quiet, essential work you do — it changes lives.",
];
function todaysThought() {
  const day = Math.floor(Date.now() / 86400000);
  return DAILY_THOUGHTS[day % DAILY_THOUGHTS.length];
}
function timeGreeting() {
  const h = new Date().getHours();
  if (h < 12) return "Good morning";
  if (h < 17) return "Good afternoon";
  return "Good evening";
}

// ---------------- icon set (minimal line icons, currentColor) ----------------
function Icon({ name, size = 20 }) {
  const common = { width: size, height: size, viewBox: "0 0 24 24", fill: "none", stroke: "currentColor", strokeWidth: 1.8, strokeLinecap: "round", strokeLinejoin: "round" };
  switch (name) {
    case "overview":
      return <svg {...common}><rect x="3.5" y="3.5" width="7" height="7" rx="1.6" /><rect x="13.5" y="3.5" width="7" height="7" rx="1.6" /><rect x="3.5" y="13.5" width="7" height="7" rx="1.6" /><rect x="13.5" y="13.5" width="7" height="7" rx="1.6" /></svg>;
    case "cases":
      return <svg {...common}><rect x="4.5" y="5" width="15" height="16" rx="2" /><path d="M9 5V4a2 2 0 0 1 2-2h2a2 2 0 0 1 2 2v1" /><path d="M8.5 12h7M8.5 16h5" /></svg>;
    case "quotes":
      return <svg {...common}><path d="M6.5 2.5h8l4 4V20a1.5 1.5 0 0 1-1.5 1.5h-11A1.5 1.5 0 0 1 5 20V4a1.5 1.5 0 0 1 1.5-1.5Z" /><path d="M14 2.5V7h4.5" /><path d="M8.3 12.3h7.4M8.3 15.6h4.7" /></svg>;
    case "machines":
      return <svg {...common}><path d="M3 12h3.2l2-5.5 3.6 11 2.4-9 1.8 3.5H21" /></svg>;
    case "stock":
      return <svg {...common}><path d="M3.5 7.5 12 3l8.5 4.5v9L12 21l-8.5-4.5Z" /><path d="M3.5 7.5 12 12l8.5-4.5" /><path d="M12 12v9" /></svg>;
    case "dressers":
      return <svg {...common}><circle cx="9" cy="8" r="3.2" /><path d="M2.8 20c.6-3.6 3.2-6 6.2-6s5.6 2.4 6.2 6" /><circle cx="17" cy="8.5" r="2.4" /><path d="M15.5 14.4c2.4.2 4.4 2.4 4.9 5.6" /></svg>;
    case "reports":
      return <svg {...common}><path d="M4 20V10M11 20V4M18 20v-7" /><path d="M2.5 20.5h19" /></svg>;
    case "pin":
      return <svg {...common}><path d="M12 2.5c3.6 0 6.5 2.8 6.5 6.6 0 4.8-6.5 12.4-6.5 12.4S5.5 13.9 5.5 9.1C5.5 5.3 8.4 2.5 12 2.5Z" /><circle cx="12" cy="9" r="2.3" /></svg>;
    case "logout":
      return <svg {...common}><path d="M9 21H5.5A1.5 1.5 0 0 1 4 19.5v-15A1.5 1.5 0 0 1 5.5 3H9" /><path d="M16 16l5-4-5-4" /><path d="M21 12H9" /></svg>;
    case "download":
      return <svg {...common}><path d="M12 3v12" /><path d="M7 10l5 5 5-5" /><path d="M4.5 19.5h15" /></svg>;
    default:
      return null;
  }
}
function blobToBase64(blob) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result.split(",")[1]);
    reader.onerror = reject;
    reader.readAsDataURL(blob);
  });
}
async function quotePdfBlob(node) {
  const canvas = await html2canvas(node, { scale: 2, backgroundColor: "#ffffff", useCORS: true });
  const imgData = canvas.toDataURL("image/png");
  const pdf = new jsPDF({ unit: "pt", format: "a4" });
  const pageW = pdf.internal.pageSize.getWidth();
  const pageH = pdf.internal.pageSize.getHeight();
  const imgW = pageW;
  const imgH = (canvas.height * imgW) / canvas.width;
  let heightLeft = imgH;
  let y = 0;
  pdf.addImage(imgData, "PNG", 0, y, imgW, imgH);
  heightLeft -= pageH;
  while (heightLeft > 0) {
    y = heightLeft - imgH;
    pdf.addPage();
    pdf.addImage(imgData, "PNG", 0, y, imgW, imgH);
    heightLeft -= pageH;
  }
  return pdf.output("blob");
}

let _cachedLocation = null;
let _cachedLocationAt = 0;
let _locationDenied = false;
function getLocation() {
  return new Promise((resolve) => {
    if (!navigator.geolocation) { resolve(null); return; }
    if (_locationDenied) { resolve(null); return; }
    if (_cachedLocation && Date.now() - _cachedLocationAt < 120000) { resolve(_cachedLocation); return; }
    navigator.geolocation.getCurrentPosition(
      (pos) => {
        const loc = { lat: pos.coords.latitude, lng: pos.coords.longitude };
        _cachedLocation = loc; _cachedLocationAt = Date.now();
        resolve(loc);
      },
      (err) => {
        if (err && err.code === 1) _locationDenied = true; // PERMISSION_DENIED — stop asking again this session
        resolve(null);
      },
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

export default function App() {
  const [businessId, setBusinessId] = useState(() => {
    try { return localStorage.getItem("wca-active-business") || "bhagirathi"; } catch (e) { return "bhagirathi"; }
  });
  const business = BUSINESSES.find((b) => b.id === businessId) || BUSINESSES[0];
  const switchBusiness = (id) => {
    if (id === businessId) return;
    try { localStorage.setItem("wca-active-business", id); } catch (e) { /* ignore */ }
    setRole(null);
    setLoaded(false);
    setBusinessId(id);
  };

  const [role, setRole] = useState(null);
  const [pin, setPin] = useState(null);
  const [cases, setCases] = useState([]);
  const [machines, setMachines] = useState([]);
  const [products, setProducts] = useState(DEFAULT_PRODUCTS);
  const [dressers, setDressers] = useState([]);
  const [dresserPins, setDresserPins] = useState({});
  const [dresserStockAccess, setDresserStockAccessState] = useState({});
  const [ownerLogins, setOwnerLogins] = useState([]);
  const [dresserProfiles, setDresserProfiles] = useState({});
  const [quotations, setQuotations] = useState([]);
  const [doctorCalls, setDoctorCalls] = useState([]);
  const [loaded, setLoaded] = useState(false);
  const [dresserBusinessAccess, setDresserBusinessAccessState] = useState({});
  const [businessAccessLoaded, setBusinessAccessLoaded] = useState(false);

  // Global (not per-business) — which businesses each dresser name is allowed into. Loaded once, independent of the active business.
  useEffect(() => {
    (async () => {
      const raw = await loadKey("wca-dresser-business-access", {});
      const access = raw && typeof raw === "object" ? { ...raw } : {};
      const allBusinessIds = BUSINESSES.map((b) => b.id);
      if (access["jayesh"] === undefined) access["jayesh"] = allBusinessIds;
      if (access["devashish"] === undefined) access["devashish"] = allBusinessIds;
      if (access["pratik"] === undefined) access["pratik"] = ["bhagirathi"];
      setDresserBusinessAccessState(access);
      setBusinessAccessLoaded(true);
    })();
  }, []);
  useEffect(() => { if (businessAccessLoaded) saveKey("wca-dresser-business-access", dresserBusinessAccess); }, [dresserBusinessAccess, businessAccessLoaded]);
  const setDresserBusinessAccess = (name, businessIds) => {
    const key = name.trim().toLowerCase();
    setDresserBusinessAccessState((prev) => ({ ...prev, [key]: businessIds }));
  };
  const businessesFor = (name) => {
    const key = (name || "").trim().toLowerCase();
    const list = dresserBusinessAccess[key];
    return Array.isArray(list) && list.length > 0 ? list : [businessId];
  };

  useEffect(() => {
    document.title = business.name;
    try {
      const dataUrl = "/bhagirathi-logo.png";
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
    } catch (e) { /* icon injection best-effort only */ }
  }, [business.name]);

  useEffect(() => {
    setLoaded(false);
    (async () => {
      const [c, m, p, ownerPin, drs, qts, drPins, dcalls, olog, dprofiles, dstock] = await Promise.all([
        loadKey(bkey(businessId, "wca-cases"), []),
        loadKey(bkey(businessId, "wca-machines"), []),
        loadKey(bkey(businessId, "wca-products"), DEFAULT_PRODUCTS),
        loadKey(bkey(businessId, "wca-owner-pin"), null),
        loadKey(bkey(businessId, "wca-dressers"), []),
        loadKey(bkey(businessId, "wca-quotations"), []),
        loadKey(bkey(businessId, "wca-dresser-pins"), {}),
        loadKey(bkey(businessId, "wca-doctor-calls"), []),
        loadKey(bkey(businessId, "wca-owner-logins"), []),
        loadKey(bkey(businessId, "wca-dresser-profiles"), {}),
        loadKey(bkey(businessId, "wca-dresser-stock-access"), {}),
      ]);
      setCases(c);
      setMachines(m);
      setProducts(normalizeProducts(p));
      setPin(ownerPin);
      setDressers(drs);
      setQuotations(qts);
      setDresserPins(drPins && typeof drPins === "object" ? drPins : {});
      setDoctorCalls(Array.isArray(dcalls) ? dcalls : []);
      setOwnerLogins(Array.isArray(olog) ? olog : []);
      setDresserProfiles(dprofiles && typeof dprofiles === "object" ? dprofiles : {});
      {
        const stockAccess = dstock && typeof dstock === "object" ? { ...dstock } : {};
        if (businessId === "bhagirathi") {
          const devashish = (drs || []).find((n) => n.trim().toLowerCase() === "devashish");
          if (devashish && stockAccess[devashish] === undefined) stockAccess[devashish] = true;
        }
        setDresserStockAccessState(stockAccess);
      }
      setLoaded(true);
    })();
  }, [businessId]);

  useEffect(() => { if (loaded) saveKey(bkey(businessId, "wca-cases"), cases); }, [cases, loaded, businessId]);
  useEffect(() => { if (loaded) saveKey(bkey(businessId, "wca-machines"), machines); }, [machines, loaded, businessId]);
  useEffect(() => { if (loaded) saveKey(bkey(businessId, "wca-products"), products); }, [products, loaded, businessId]);
  useEffect(() => { if (loaded) saveKey(bkey(businessId, "wca-dressers"), dressers); }, [dressers, loaded, businessId]);
  useEffect(() => { if (loaded) saveKey(bkey(businessId, "wca-quotations"), quotations); }, [quotations, loaded, businessId]);
  useEffect(() => { if (loaded) saveKey(bkey(businessId, "wca-dresser-pins"), dresserPins); }, [dresserPins, loaded, businessId]);
  useEffect(() => { if (loaded) saveKey(bkey(businessId, "wca-doctor-calls"), doctorCalls); }, [doctorCalls, loaded, businessId]);
  useEffect(() => { if (loaded) saveKey(bkey(businessId, "wca-dresser-profiles"), dresserProfiles); }, [dresserProfiles, loaded, businessId]);
  useEffect(() => { if (loaded) saveKey(bkey(businessId, "wca-owner-logins"), ownerLogins); }, [ownerLogins, loaded, businessId]);
  useEffect(() => { if (loaded) saveKey(bkey(businessId, "wca-dresser-stock-access"), dresserStockAccess); }, [dresserStockAccess, loaded, businessId]);

  const saveCase = (data, editingId) => {
    if (editingId) {
      setCases((prev) => prev.map((c) => (c.id === editingId ? { ...c, ...data } : c)));
      return;
    }
    const initialEntry = { id: uid(), date: data.applicationDate, dresserName: data.dresserName, protocolDays: data.protocolDays, note: "Initial application" };
    const initialAmountReceived = Number(data.amountReceived) || 0;
    const initialPayments = initialAmountReceived > 0
      ? [{ id: uid(), amount: initialAmountReceived, mode: "Cash", note: "Initial payment", date: data.applicationDate }]
      : [];
    setCases((prev) => [...prev, { id: uid(), payments: initialPayments, dressingChanges: [initialEntry], photoFlags: {}, ...data }]);
     const usedNames = getCaseProducts(data);
    if (usedNames.length) {
      setProducts((prev) => prev.map((p) => usedNames.includes(p.name) ? { ...p, available: Math.max(0, (p.available || 0) - 1), used: (p.used || 0) + 1 } : p));
    }
  };

   const deleteCase = (id) => {
    const target = cases.find((c) => c.id === id);
    setCases((prev) => prev.filter((c) => c.id !== id));
    const usedNames = target ? getCaseProducts(target) : [];
    if (usedNames.length) {
      setProducts((prev) => prev.map((p) => usedNames.includes(p.name) ? { ...p, available: (p.available || 0) + 1, used: Math.max(0, (p.used || 0) - 1) } : p));
    }
  };

  const addPayment = (caseId, payment) => {
    setCases((prev) => prev.map((c) => c.id === caseId ? { ...c, payments: [...(c.payments || []), { id: uid(), ...payment }] } : c));
  };
  const addDressingChange = (caseId, entry) => {
    setCases((prev) => prev.map((c) => c.id === caseId ? { ...c, dressingChanges: [...(c.dressingChanges || []), { id: uid(), ...entry }] } : c));
  };
  const addAdditionalItem = (caseId, entry) => {
    const qty = Number(entry.qty) || 1;
    setCases((prev) => prev.map((c) => c.id === caseId ? {
      ...c,
      additionalItems: [...(c.additionalItems || []), { id: uid(), date: todayISO(), ...entry, qty }],
      totalAmount: Number(c.totalAmount || 0) + (Number(entry.extraCharge) || 0),
    } : c));
    if (entry.name) {
      setProducts((prev) => prev.map((p) => p.name === entry.name
        ? { ...p, available: Math.max(0, (p.available || 0) - qty), used: (p.used || 0) + qty }
        : p));
    }
  };
  const capturePhoto = async (caseId, stage, dataURL) => {
    await saveKey(photoKey(caseId, stage), dataURL);
    setCases((prev) => prev.map((c) => c.id === caseId ? { ...c, photoFlags: { ...(c.photoFlags || {}), [stage]: true } } : c));
  };
  const setOwnerPin = (newPin) => { setPin(newPin); saveKey(bkey(businessId, "wca-owner-pin"), newPin); };
  const addDresser = (name, dresserPin) => {
    const trimmed = name.trim();
    if (!trimmed || dressers.some((d) => d.toLowerCase() === trimmed.toLowerCase())) return;
    setDressers((prev) => [...prev, trimmed]);
    if (dresserPin) setDresserPins((prev) => ({ ...prev, [trimmed]: String(dresserPin) }));
  };
  const removeDresser = (name) => {
    setDressers((prev) => prev.filter((d) => d !== name));
    setDresserPins((prev) => { const next = { ...prev }; delete next[name]; return next; });
  };
  const setDresserPin = (name, newPin) => setDresserPins((prev) => ({ ...prev, [name]: newPin ? String(newPin) : undefined }));
  const updateDresserLocation = async (name) => {
    const loc = await getLocation();
    if (loc) {
      const entry = { ...loc, ts: new Date().toISOString() };
      const existing = await loadKey(locKey(businessId, name), []);
      const trail = Array.isArray(existing) ? existing : []; // migrate old single-object format
      const updated = [...trail, entry].slice(-100);
      await saveKey(locKey(businessId, name), updated);
    }
    return loc;
  };
  const saveQuotation = (data, editingId) => {
    if (editingId) {
      setQuotations((prev) => prev.map((q) => (q.id === editingId ? { ...q, ...data } : q)));
      return editingId;
    }
    const id = uid();
    setQuotations((prev) => [...prev, { id, status: "draft", createdAt: todayISO(), ...data }]);
    return id;
  };
  const deleteQuotation = (id) => setQuotations((prev) => prev.filter((q) => q.id !== id));
  const setQuotationStatus = (id, status) =>
    setQuotations((prev) => prev.map((q) => (q.id === id ? { ...q, status } : q)));
  const receiveStock = (productId, qty, company, receivedBy) => {
    setProducts((prev) => prev.map((p) => p.id === productId ? {
      ...p,
      available: (p.available || 0) + qty,
      receipts: [...(p.receipts || []), { id: uid(), date: todayISO(), time: new Date().toLocaleTimeString("en-IN"), qty, company: company || "Unspecified", receivedBy: receivedBy || "Owner" }],
    } : p));
  };
  const resetTestData = () => { setCases([]); setProducts([]); };
  const logOwnerLogin = () => {
    const ua = navigator.userAgent || "";
    let device = "Unknown device";
    if (/iPhone|iPad/.test(ua)) device = "iPhone/iPad";
    else if (/Android/.test(ua)) device = "Android device";
    else if (/Windows/.test(ua)) device = "Windows PC";
    else if (/Macintosh/.test(ua)) device = "Mac";
    const browser = /Chrome/.test(ua) ? "Chrome" : /Safari/.test(ua) ? "Safari" : /Firefox/.test(ua) ? "Firefox" : "Browser";
    setOwnerLogins((prev) => [...prev.slice(-49), { id: uid(), date: todayISO(), time: new Date().toLocaleTimeString("en-IN"), device: `${device} · ${browser}` }]);
  };
  const setDresserProfile = (name, data) => setDresserProfiles((prev) => ({ ...prev, [name]: { ...prev[name], ...data } }));
  const setDresserStockAccess = (name, allowed) => setDresserStockAccessState((prev) => ({ ...prev, [name]: !!allowed }));
  const clearAllOutstanding = () => {
    setCases((prev) => prev.map((c) => {
      const paid = (c.payments || []).reduce((s, p) => s + Number(p.amount || 0), 0);
      const outstanding = Math.max(0, Number(c.totalAmount || 0) - paid);
      if (outstanding <= 0) return c;
      return {
        ...c,
        payments: [...(c.payments || []), { id: uid(), amount: outstanding, mode: "Adjustment", note: "Outstanding cleared", date: todayISO() }],
      };
    }));
  };
  const addDoctorCall = (entry) => setDoctorCalls((prev) => [...prev, { id: uid(), date: todayISO(), ...entry }]);

  if (!loaded) {
    return <div style={styles.loadingScreen}><div style={styles.loadingText}>Loading {business.name}…</div></div>;
  }

  return (
    <div style={styles.app}>
      <style>{fontImport}</style>
      <style>{printStyles}</style>
      {!role && (
        <RoleGate
          pin={pin}
          dressers={dressers}
          dresserPins={dresserPins}
          onSetPin={setOwnerPin}
          onOwnerLogin={() => { logOwnerLogin(); setRole({ type: "owner" }); }}
          onDresserLogin={(name) => { setRole({ type: "dresser", name }); updateDresserLocation(name); }}
          businesses={BUSINESSES} businessId={businessId} business={business} onSwitchBusiness={switchBusiness}
        />
      )}
      {role && role.type === "owner" && (
        <OwnerShell
          cases={cases} machines={machines} setMachines={setMachines}
          products={products} setProducts={setProducts} receiveStock={receiveStock}
          dressers={dressers} addDresser={addDresser} removeDresser={removeDresser}
          dresserPins={dresserPins} setDresserPin={setDresserPin}
          dresserProfiles={dresserProfiles} dresserStockAccess={dresserStockAccess} setDresserStockAccess={setDresserStockAccess}
          dresserBusinessAccess={dresserBusinessAccess} setDresserBusinessAccess={setDresserBusinessAccess}
          saveCase={saveCase} deleteCase={deleteCase} addPayment={addPayment} addDressingChange={addDressingChange} addAdditionalItem={addAdditionalItem}
          quotations={quotations} saveQuotation={saveQuotation} deleteQuotation={deleteQuotation} setQuotationStatus={setQuotationStatus}
          resetTestData={resetTestData} clearAllOutstanding={clearAllOutstanding}
          ownerLogins={ownerLogins}
          doctorCalls={doctorCalls}
          businessId={businessId} business={business} businesses={BUSINESSES} onSwitchBusiness={switchBusiness}
          pin={pin} onChangePin={setOwnerPin}
          onLogout={() => setRole(null)}
        />
      )}
      {role && role.type === "dresser" && (
        <DresserShell
          name={role.name} cases={cases} machines={machines} products={products} setProducts={setProducts} receiveStock={receiveStock} saveCase={saveCase}
          addDressingChange={addDressingChange} addAdditionalItem={addAdditionalItem} capturePhoto={capturePhoto}
          updateDresserLocation={updateDresserLocation}
          quotations={quotations} saveQuotation={saveQuotation} deleteQuotation={deleteQuotation} setQuotationStatus={setQuotationStatus}
          doctorCalls={doctorCalls} addDoctorCall={addDoctorCall}
          profile={dresserProfiles[role.name]} setDresserProfile={setDresserProfile}
          canManageStock={!!dresserStockAccess[role.name]}
          business={business} businessId={businessId} businesses={BUSINESSES}
          myBusinesses={businessesFor(role.name)} onSwitchBusiness={switchBusiness}
          onLogout={() => setRole(null)}
        />
      )}
    </div>
  );
}

// ================= ROLE GATE =================
function RoleGate({ pin, dressers, dresserPins, onSetPin, onOwnerLogin, onDresserLogin, businesses, businessId, business, onSwitchBusiness }) {
  const [mode, setMode] = useState("dresser");
  const [input, setInput] = useState("");
  const [confirmInput, setConfirmInput] = useState("");
  const [error, setError] = useState("");
  const [tapCount, setTapCount] = useState(0);
  const [pendingDresser, setPendingDresser] = useState(null);
  const [dresserPinInput, setDresserPinInput] = useState("");
  const [dresserError, setDresserError] = useState("");

  const submitOwner = () => {
    if (!pin) {
      if (input.length < 4) { setError("PIN must be at least 4 digits"); return; }
      if (input !== confirmInput) { setError("PINs don't match"); return; }
      onSetPin(input); onOwnerLogin(); return;
    }
    if (input === pin) onOwnerLogin();
    else { setError("Incorrect PIN"); setInput(""); }
  };

  const handleLogoTap = () => {
    const next = tapCount + 1;
    if (next >= 5) { setMode("owner"); setError(""); setTapCount(0); }
    else setTapCount(next);
  };

  const selectDresser = (d) => {
    if (!dresserPins[d]) { onDresserLogin(d); return; } // no PIN set yet — allow in, but owner should set one
    setPendingDresser(d);
    setDresserPinInput("");
    setDresserError("");
  };
  const submitDresserPin = () => {
    if (dresserPinInput === dresserPins[pendingDresser]) {
      onDresserLogin(pendingDresser);
    } else {
      setDresserError("Incorrect PIN");
      setDresserPinInput("");
    }
  };

  return (
    <div style={styles.gateWrap}>
      <img src="/bhagirathi-logo.png" alt={business.name} style={styles.brandMarkLg} onClick={handleLogoTap} />
      <div style={styles.gateBrand}>{business.name}</div>
      <div style={styles.brandSub}>Wound Care Tracker</div>

      {mode === "owner" && (
        <div style={styles.gateForm}>
          {!pin && <div style={styles.gateHint}>First time — set an owner PIN to protect billing & reports.</div>}
          <input type="password" inputMode="numeric" placeholder={pin ? "Enter PIN" : "Set a PIN (4+ digits)"} value={input} onChange={(e) => setInput(e.target.value)} style={styles.gateInput} />
          {!pin && <input type="password" inputMode="numeric" placeholder="Confirm PIN" value={confirmInput} onChange={(e) => setConfirmInput(e.target.value)} style={styles.gateInput} />}
          {error && <div style={styles.gateError}>{error}</div>}
          <button style={styles.primaryBtn} onClick={submitOwner}>{pin ? "Unlock" : "Set PIN & Continue"}</button>
          <button style={styles.linkBtn} onClick={() => { setMode("dresser"); setError(""); }}>Back</button>
        </div>
      )}

      {mode === "dresser" && !pendingDresser && (
        <div style={styles.gateForm}>
          <div style={{ background: "#FBEAD3", borderRadius: 14, padding: 14, textAlign: "center", marginBottom: 4 }}>
            <div style={{ fontFamily: "'Space Grotesk', sans-serif", fontWeight: 700, fontSize: 14, color: "#D9720A" }}>{timeGreeting()}!</div>
            <div style={{ fontSize: 12.5, color: "#5B6864", marginTop: 4, lineHeight: 1.5 }}>{todaysThought()}</div>
          </div>
          {dressers.length === 0 ? (
            <div style={styles.gateHint}>No dressers have been added yet. Ask the owner to add your name in the Dressers tab.</div>
          ) : (
            <div style={{ ...styles.gateOptions, marginTop: 4 }}>
              {dressers.map((d) => (
                <button key={d} style={{ ...styles.gateBtn, ...styles.gateBtnAlt }} onClick={() => selectDresser(d)}>{d}</button>
              ))}
            </div>
          )}
        </div>
      )}

      {mode === "dresser" && pendingDresser && (
        <div style={styles.gateForm}>
          <div style={styles.gateHint}>Enter {pendingDresser}'s PIN</div>
          <input type="password" inputMode="numeric" placeholder="PIN" autoFocus value={dresserPinInput}
            onChange={(e) => setDresserPinInput(e.target.value)}
            onKeyDown={(e) => { if (e.key === "Enter") submitDresserPin(); }}
            style={styles.gateInput} />
          {dresserError && <div style={styles.gateError}>{dresserError}</div>}
          <button style={styles.primaryBtn} onClick={submitDresserPin}>Unlock</button>
          <button style={styles.linkBtn} onClick={() => setPendingDresser(null)}>Back</button>
        </div>
      )}
    </div>
  );
}

// ================= OWNER SHELL =================
function OwnerShell({ cases, machines, setMachines, products, setProducts, receiveStock, dressers, addDresser, removeDresser, dresserPins, setDresserPin, dresserProfiles, dresserStockAccess, setDresserStockAccess, dresserBusinessAccess, setDresserBusinessAccess, saveCase, deleteCase, addPayment, addDressingChange, addAdditionalItem, quotations, saveQuotation, deleteQuotation, setQuotationStatus, resetTestData, clearAllOutstanding, doctorCalls, ownerLogins, businessId, business, businesses, onSwitchBusiness, pin, onChangePin, onLogout }) {
  const [tab, setTab] = useState("dashboard");
  const [showPinForm, setShowPinForm] = useState(false);

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
      const entries = (c.dressingChanges || []).length ? c.dressingChanges : [{ dresserName: c.dresserName }];
      entries.forEach((e) => {
        const name = (e.dresserName || "").trim();
        if (!name) return;
        tally[name] = (tally[name] || 0) + 1;
      });
    });
    return Object.entries(tally).map(([name, count]) => ({ name, count })).sort((a, b) => b.count - a.count);
  }, [cases]);

  const lowStock = products.filter((p) => (p.available || 0) < LOW_STOCK_THRESHOLD);

  return (
    <>
      <header style={styles.header}>
        <div style={styles.headerInner}>
          <div style={styles.brandMark}><img src="/bhagirathi-logo.png" alt={business.name} style={styles.brandMarkImg} /></div>
          <div style={{ flex: 1 }}>
            <div style={styles.brandName}>{business.name}</div>
            <div style={styles.brandSub}>Owner view</div>
          </div>
          <div style={{ display: "flex", gap: 6 }}>
            <button style={styles.logoutBtn} onClick={() => setShowPinForm((s) => !s)}><Icon name="pin" size={15} /> PIN</button>
            <button style={styles.logoutBtn} onClick={onLogout}><Icon name="logout" size={15} /> Switch</button>
          </div>
        </div>
        {showPinForm && (
          <div style={styles.pinPanel}>
            <ChangePinForm pin={pin} onChangePin={(p) => { onChangePin(p); setShowPinForm(false); }} onDone={() => setShowPinForm(false)} />
          </div>
        )}
      </header>

      {businesses && businesses.length > 1 && (
        <div style={{ display: "flex", gap: 6, padding: "10px 16px 0", maxWidth: 640, margin: "0 auto", overflowX: "auto" }}>
          {businesses.map((b) => (
            <button key={b.id} onClick={() => onSwitchBusiness(b.id)}
              style={{ ...styles.filterChip, ...(b.id === businessId ? styles.filterChipActive : {}) }}>
              {b.name}
            </button>
          ))}
        </div>
      )}

      <nav style={styles.nav}>
        {[["dashboard", "Command Center", "overview"], ["cases", "Cases", "cases"], ["quotations", "Quotes", "quotes"], ["machines", "Machines", "machines"], ["stock", "Stock", "stock"], ["dressers", "Dressers", "dressers"], ["reports", "Reports", "reports"]].map(([key, label, icon]) => (
          <button key={key} onClick={() => setTab(key)} style={{ ...styles.navBtn, ...(tab === key ? styles.navBtnActive : {}) }}>
            <Icon name={icon} size={16} />{label}
          </button>
        ))}
      </nav>

      <main style={styles.main}>
        {tab === "dashboard" && (
          <Dashboard cases={cases} machines={machines} outstandingTotal={outstandingTotal} activeCount={activeCount}
            machinesInUseCount={machinesInUseCount} overdueCount={overdueCount} dresserStats={dresserStats} lowStock={lowStock}
            products={products} setTab={setTab} />
        )}
        {tab === "cases" && (
          <CasesTab cases={cases} machines={machines} products={products} saveCase={saveCase} deleteCase={deleteCase}
            addPayment={addPayment} addDressingChange={addDressingChange} addAdditionalItem={addAdditionalItem} />
        )}
        {tab === "quotations" && (
          <QuotationsTab quotations={quotations} products={products} saveQuotation={saveQuotation}
            deleteQuotation={deleteQuotation} setQuotationStatus={setQuotationStatus} businessName={business.name} />
        )}
        {tab === "machines" && <MachinesTab machines={machines} setMachines={setMachines} machineInUse={machineInUse} cases={cases} />}
        {tab === "stock" && <StockTab products={products} setProducts={setProducts} receiveStock={receiveStock} />}
        {tab === "dressers" && <DressersTab dressers={dressers} addDresser={addDresser} removeDresser={removeDresser} dresserPins={dresserPins} setDresserPin={setDresserPin} dresserStats={dresserStats} dresserProfiles={dresserProfiles} dresserStockAccess={dresserStockAccess} setDresserStockAccess={setDresserStockAccess} dresserBusinessAccess={dresserBusinessAccess} setDresserBusinessAccess={setDresserBusinessAccess} businesses={businesses} businessId={businessId} />}
        {tab === "reports" && <ReportsTab cases={cases} products={products} dresserStats={dresserStats} dressers={dressers} outstandingTotal={outstandingTotal} overdueCount={overdueCount} lowStock={lowStock} resetTestData={resetTestData} clearAllOutstanding={clearAllOutstanding} doctorCalls={doctorCalls} quotations={quotations} ownerLogins={ownerLogins} businessId={businessId} businessName={business.name} />}
      </main>
    </>
  );
}

function ChangePinForm({ pin, onChangePin, onDone }) {
  const [current, setCurrent] = useState("");
  const [next, setNext] = useState("");
  const [confirm, setConfirm] = useState("");
  const [error, setError] = useState("");

  const submit = () => {
    if (current !== pin) { setError("Current PIN is incorrect"); return; }
    if (next.length < 4) { setError("New PIN must be at least 4 digits"); return; }
    if (next !== confirm) { setError("New PINs don't match"); return; }
    onChangePin(next);
  };

  return (
    <div style={styles.formGrid}>
      <Field label="Current PIN"><input type="password" inputMode="numeric" style={styles.input} value={current} onChange={(e) => setCurrent(e.target.value)} /></Field>
      <Field label="New PIN"><input type="password" inputMode="numeric" style={styles.input} value={next} onChange={(e) => setNext(e.target.value)} /></Field>
      <Field label="Confirm New PIN"><input type="password" inputMode="numeric" style={styles.input} value={confirm} onChange={(e) => setConfirm(e.target.value)} /></Field>
      {error && <div style={styles.gateError}>{error}</div>}
      <div style={styles.formActions}>
        <button style={styles.secondaryBtn} onClick={onDone}>Cancel</button>
        <button style={styles.primaryBtn} onClick={submit}>Update PIN</button>
      </div>
    </div>
  );
}

// ================= DRESSER SHELL =================
function DresserProfileForm({ name, profile, setDresserProfile }) {
  const [phone, setPhone] = useState((profile && profile.phone) || "");
  const [bio, setBio] = useState((profile && profile.bio) || "");
  const [uploading, setUploading] = useState(false);
  const photo = profile && profile.photo;

  const handlePhoto = async (file) => {
    if (!file) return;
    setUploading(true);
    try {
      const dataURL = await compressImage(file);
      setDresserProfile(name, { photo: dataURL });
    } catch (e) { console.error(e); }
    setUploading(false);
  };

  const save = () => setDresserProfile(name, { phone: phone.trim(), bio: bio.trim() });

  return (
    <div>
      <div style={{ display: "flex", alignItems: "center", gap: 14, marginBottom: 14 }}>
        <label style={{ cursor: "pointer" }}>
          {photo ? (
            <img src={photo} alt={name} style={{ width: 72, height: 72, borderRadius: 16, objectFit: "cover", border: "1px solid #DCE4DF" }} />
          ) : (
            <div style={{ width: 72, height: 72, borderRadius: 16, border: "1px dashed #DCE4DF", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 10, color: "#8A9A96", textAlign: "center" }}>
              {uploading ? "…" : "Add photo"}
            </div>
          )}
          <input type="file" accept="image/*" capture="user" style={{ display: "none" }} onChange={(e) => handlePhoto(e.target.files[0])} />
        </label>
        <div>
          <div style={{ fontFamily: "'Space Grotesk', sans-serif", fontWeight: 700, fontSize: 16 }}>{name}</div>
          <div style={styles.mutedSmall}>Tap the photo to {photo ? "change" : "add"} it</div>
        </div>
      </div>
      <div style={styles.formGrid}>
        <Field label="Phone Number"><input type="tel" style={styles.input} value={phone} onChange={(e) => setPhone(e.target.value)} placeholder="10-digit number" /></Field>
        <Field label="About / Bio (optional)"><textarea style={{ ...styles.input, minHeight: 60 }} value={bio} onChange={(e) => setBio(e.target.value)} placeholder="e.g. years of experience, specialization" /></Field>
      </div>
      <button style={styles.smallBtn} onClick={save}>Save Profile</button>
    </div>
  );
}

function DresserShell({ name, cases, machines, products, setProducts, receiveStock, saveCase, addDressingChange, addAdditionalItem, capturePhoto, updateDresserLocation, quotations, saveQuotation, deleteQuotation, setQuotationStatus, doctorCalls, addDoctorCall, profile, setDresserProfile, canManageStock, business, businessId, businesses, myBusinesses, onSwitchBusiness, onLogout }) {
  const [showForm, setShowForm] = useState(false);
  const myCasesActive = cases.filter((c) => c.status === "active");

  useEffect(() => {
    const interval = setInterval(() => { updateDresserLocation(name); }, 5 * 60 * 1000);
    return () => clearInterval(interval);
    // eslint-disable-next-line
  }, [name]);

  const myChanges = useMemo(() => {
    const list = [];
    cases.forEach((c) => {
      (c.dressingChanges || []).forEach((e) => {
        if ((e.dresserName || "").trim().toLowerCase() === name.trim().toLowerCase()) list.push({ ...e, patientName: c.patientName });
      });
    });
    return list.sort((a, b) => new Date(b.date) - new Date(a.date));
  }, [cases, name]);

  const myOutstandingTotal = useMemo(() => cases
    .filter((c) => (c.dresserName || "").trim().toLowerCase() === name.trim().toLowerCase())
    .reduce((s, c) => {
      const paid = (c.payments || []).reduce((a, p) => a + Number(p.amount || 0), 0);
      return s + Math.max(0, Number(c.totalAmount || 0) - paid);
    }, 0), [cases, name]);

  if (showForm) {
    return (
      <CaseForm machines={machines} products={products} presetDresserName={name}
        onCancel={() => setShowForm(false)}
        onSave={(data) => { saveCase(data, null); setShowForm(false); }} />
    );
  }

  return (
    <>
      <header style={styles.header}>
        <div style={styles.headerInner}>
          {profile && profile.photo ? (
            <img src={profile.photo} alt={name} style={{ width: 40, height: 40, borderRadius: 12, objectFit: "cover" }} />
          ) : (
            <div style={styles.brandMark}><img src="/bhagirathi-logo.png" alt={business.name} style={styles.brandMarkImg} /></div>
          )}
          <div style={{ flex: 1 }}>
            <div style={styles.brandName}>{business.name}</div>
            <div style={styles.brandSub}>Hi, {name}</div>
          </div>
          <button style={styles.logoutBtn} onClick={onLogout}><Icon name="logout" size={15} /> Switch</button>
        </div>
      </header>

      {myBusinesses && myBusinesses.length > 1 && businesses && (
        <div style={{ display: "flex", gap: 6, padding: "10px 16px 0", maxWidth: 640, margin: "0 auto", overflowX: "auto" }}>
          {businesses.filter((b) => myBusinesses.includes(b.id)).map((b) => (
            <button key={b.id} onClick={() => onSwitchBusiness(b.id)}
              style={{ ...styles.filterChip, ...(b.id === businessId ? styles.filterChipActive : {}) }}>
              {b.name}
            </button>
          ))}
        </div>
      )}

      <main style={styles.main}>
        <CollapsibleSection title="My Profile" defaultOpen={!profile || !profile.photo}>
          <DresserProfileForm name={name} profile={profile} setDresserProfile={setDresserProfile} />
        </CollapsibleSection>

        <button style={styles.primaryBtn} onClick={() => setShowForm(true)}>+ New Case</button>

        <CollapsibleSection title="Cases on Therapy" defaultOpen>
          {myCasesActive.length === 0 ? <EmptyState text="No active cases right now." /> : (
            <div style={styles.list}>
              {myCasesActive.map((c) => (
                <DresserCaseRow key={c.id} c={c} dresserName={name} products={products}
                  onAddDressingChange={(e) => addDressingChange(c.id, e)}
                  onAddAdditionalItem={(e) => addAdditionalItem(c.id, e)}
                  onCapturePhoto={(stage, dataURL) => capturePhoto(c.id, stage, dataURL)} />
              ))}
            </div>
          )}
        </CollapsibleSection>

        <CollapsibleSection title="Your Reporting">
          <div style={styles.cardGrid}>
            <div style={{ ...styles.statCard, cursor: "default", borderColor: "#D9720A33" }}>
              <div style={{ ...styles.statValue, color: "#D9720A" }}>{myChanges.length}</div>
              <div style={styles.statLabel}>Total dressings logged</div>
            </div>
            <div style={{ ...styles.statCard, cursor: "default", borderColor: myOutstandingTotal > 0 ? "#E1483C33" : "#D9720A33" }}>
              <div style={{ ...styles.statValue, color: myOutstandingTotal > 0 ? "#E1483C" : "#D9720A" }}>{fmtMoney(myOutstandingTotal)}</div>
              <div style={styles.statLabel}>Outstanding on your cases</div>
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
        </CollapsibleSection>

        <CollapsibleSection title="My Quotations">
          <QuotationsTab quotations={quotations} products={products} saveQuotation={saveQuotation}
            deleteQuotation={deleteQuotation} setQuotationStatus={setQuotationStatus}
            creatorName={name} restrictToCreator businessName={business.name} />
        </CollapsibleSection>

        <CollapsibleSection title="Doctor Calls">
          <DoctorCallTab name={name} products={products} doctorCalls={doctorCalls} addDoctorCall={addDoctorCall} />
        </CollapsibleSection>

        {canManageStock && (
          <CollapsibleSection title="Stock">
            <StockTab products={products} setProducts={setProducts} receiveStock={receiveStock} actorName={name} />
          </CollapsibleSection>
        )}
      </main>
    </>
  );
}

function DoctorCallTab({ name, products, doctorCalls, addDoctorCall }) {
  const [doctorName, setDoctorName] = useState("");
  const [doctorMobile, setDoctorMobile] = useState("");
  const [speciality, setSpeciality] = useState("");
  const [selectedProducts, setSelectedProducts] = useState([]);
  const [date, setDate] = useState(todayISO());
  const [notes, setNotes] = useState("");
  const productsByCompany = useMemo(() => groupProductsByCompany(products), [products]);

  const myCalls = useMemo(
    () => doctorCalls.filter((c) => (c.dresserName || "").trim().toLowerCase() === name.trim().toLowerCase())
      .sort((a, b) => new Date(b.date) - new Date(a.date)),
    [doctorCalls, name]
  );

  const toggleProduct = (pName) => {
    setSelectedProducts((prev) => prev.includes(pName) ? prev.filter((n) => n !== pName) : [...prev, pName]);
  };

  const submit = () => {
    if (!doctorName.trim()) return;
    addDoctorCall({
      dresserName: name, doctorName: doctorName.trim(), doctorMobile: doctorMobile.trim(),
      speciality: speciality.trim(), products: selectedProducts, date, notes: notes.trim(),
    });
    setDoctorName(""); setDoctorMobile(""); setSpeciality(""); setSelectedProducts([]); setNotes("");
  };

  return (
    <div>
      <div style={styles.formGrid}>
        <Field label="Doctor Name"><input style={styles.input} value={doctorName} onChange={(e) => setDoctorName(e.target.value)} /></Field>
        <Field label="Doctor Mobile Number"><input type="tel" style={styles.input} value={doctorMobile} onChange={(e) => setDoctorMobile(e.target.value)} placeholder="10-digit number" /></Field>
        <Field label="Speciality"><input style={styles.input} value={speciality} onChange={(e) => setSpeciality(e.target.value)} placeholder="e.g. General Surgeon, Orthopedician" /></Field>
        <Field label="Product(s) Discussed">
          <div style={{ display: "flex", flexDirection: "column", gap: 4, border: "1px solid #DCE4DF", borderRadius: 10, padding: 8, maxHeight: 220, overflowY: "auto" }}>
            {products.length === 0 ? <span style={styles.mutedSmall}>No products in stock yet.</span> : productsByCompany.map(([company, prods]) => (
              <div key={company}>
                <div style={{ fontSize: 11, fontWeight: 700, color: "#8A9A96", margin: "6px 0 2px" }}>{company}</div>
                {prods.map((p) => (
                  <label key={p.id} style={{ display: "flex", alignItems: "center", gap: 6, fontSize: 14, padding: "3px 0" }}>
                    <input type="checkbox" checked={selectedProducts.includes(p.name)} onChange={() => toggleProduct(p.name)} />
                    {p.name}
                  </label>
                ))}
              </div>
            ))}
          </div>
        </Field>
        <Field label="Date"><input type="date" style={styles.input} value={date} onChange={(e) => setDate(e.target.value)} /></Field>
        <Field label="Notes (optional)"><textarea style={{ ...styles.input, minHeight: 50 }} value={notes} onChange={(e) => setNotes(e.target.value)} /></Field>
      </div>
      <button style={styles.primaryBtn} onClick={submit}>Log Doctor Call</button>

      <SectionTitle>Your Doctor Calls</SectionTitle>
      {myCalls.length === 0 ? <EmptyState text="No doctor calls logged yet." /> : (
        <div style={styles.list}>
          {myCalls.map((c) => (
            <div key={c.id} style={styles.card}>
              <div style={{ padding: 14 }}>
                <div style={styles.cardTitle}>{c.doctorName}</div>
                <div style={styles.cardMeta}>{c.speciality || "—"} · {c.doctorMobile || "no number"}</div>
                <div style={{ ...styles.mutedSmall, marginTop: 6 }}>{fmtDate(c.date)}{(c.products || []).length > 0 ? ` · ${c.products.join(", ")}` : ""}</div>
                {c.notes && <div style={{ ...styles.notesText, marginTop: 6 }}>{c.notes}</div>}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function AdditionalItemsBlock({ c, products, onAddAdditionalItem }) {
  const [name, setName] = useState("");
  const [qty, setQty] = useState(1);
  const [extraCharge, setExtraCharge] = useState("");
  const [note, setNote] = useState("");
  const items = c.additionalItems || [];
  const productsByCompany = useMemo(() => groupProductsByCompany(products), [products]);

  const submit = () => {
    if (!name) return;
    onAddAdditionalItem({ name, qty: Number(qty) || 1, extraCharge: Number(extraCharge) || 0, note: note.trim() });
    setName(""); setQty(1); setExtraCharge(""); setNote("");
  };

  return (
    <div style={{ marginTop: 14 }}>
      <div style={styles.detailLabel}>Additional items used (e.g. extra canister, foam)</div>
      {items.length > 0 && (
        <div style={{ ...styles.card, margin: "6px 0" }}>
          {items.map((it) => (
            <div key={it.id} style={styles.dresserLine}>
              <span style={{ flex: 1 }}>{it.name} × {it.qty}</span>
              <span style={styles.mutedSmall}>{fmtDate(it.date)}</span>
              {Number(it.extraCharge) > 0 && <span style={{ fontWeight: 700, color: "#D9720A" }}>+{fmtMoney(it.extraCharge)}</span>}
            </div>
          ))}
        </div>
      )}
      <div style={styles.addPaymentRow}>
        <select style={{ ...styles.smallInput, flex: 2 }} value={name} onChange={(e) => setName(e.target.value)}>
          <option value="">Select item…</option>
          {productsByCompany.map(([company, prods]) => (
            <optgroup key={company} label={company}>
              {prods.map((p) => <option key={p.id} value={p.name}>{p.name}</option>)}
            </optgroup>
          ))}
        </select>
        <input type="number" min="1" style={{ ...styles.smallInput, width: 55 }} value={qty} onChange={(e) => setQty(e.target.value)} placeholder="Qty" />
        <input type="number" style={{ ...styles.smallInput, width: 90 }} value={extraCharge} onChange={(e) => setExtraCharge(e.target.value)} placeholder="Extra ₹" />
      </div>
      <input type="text" placeholder="Note (optional)" value={note} onChange={(e) => setNote(e.target.value)}
        style={{ ...styles.smallInput, width: "100%", marginTop: 8, boxSizing: "border-box" }} />
      <button style={{ ...styles.smallBtn, width: "100%", marginTop: 8 }} onClick={submit} disabled={!name}>+ Add Item</button>
    </div>
  );
}

function DresserCaseRow({ c, dresserName, products, onAddDressingChange, onAddAdditionalItem, onCapturePhoto }) {
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
          <div style={styles.cardMeta}>Dr. {c.doctorName} · {getCaseProducts(c).join(", ")}</div>
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
            <input style={{ ...styles.smallInput, flex: 1 }} value={dresserName} disabled />
            <select value={protocolDays} onChange={(e) => setProtocolDays(Number(e.target.value))} style={styles.smallInput}>
              {PROTOCOLS.map((p) => <option key={p} value={p}>{p}d</option>)}
            </select>
          </div>
          <input type="text" placeholder="Note (optional)" value={note} onChange={(e) => setNote(e.target.value)}
            style={{ ...styles.smallInput, width: "100%", marginTop: 8, boxSizing: "border-box" }} />
          <button style={{ ...styles.smallBtn, width: "100%", marginTop: 8 }} onClick={() => {
            onAddDressingChange({ date: todayISO(), dresserName, protocolDays, note });
            setNote(""); setOpen(false);
          }}>Log Today's Change</button>

          <AdditionalItemsBlock c={c} products={products} onAddAdditionalItem={onAddAdditionalItem} />
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
        <StatCard label="Active Cases" value={activeCount} accent="#D9720A" icon="cases" onClick={() => setTab("cases")} />
        <StatCard label="Change Due / Overdue" value={overdueCount} accent="#E1483C" icon="reports" onClick={() => setTab("cases")} />
        <StatCard label="Outstanding" value={fmtMoney(outstandingTotal)} accent="#D98D2B" icon="quotes" onClick={() => setTab("cases")} />
        <StatCard label="Machines In Use" value={`${machinesInUseCount} / ${machines.length}`} accent="#3B5BA5" icon="machines" onClick={() => setTab("machines")} />
      </div>

      {lowStock.length > 0 && (
        <CollapsibleSection title="Stock Alerts" right={<span style={{ fontSize: 12, fontWeight: 700, color: "#E1483C" }}>{lowStock.length}</span>}>
          <div style={styles.card}>
            {lowStock.map((p) => (
              <div key={p.id} style={styles.dresserLine}><span style={{ flex: 1, fontWeight: 600 }}>{p.name}</span><span style={{ color: "#E1483C", fontSize: 12, fontWeight: 700 }}>{p.available || 0} left</span></div>
            ))}
          </div>
        </CollapsibleSection>
      )}

      {dresserStats.length > 0 && (
        <CollapsibleSection title="Dresser Workload">
          <div style={styles.card}>
            {dresserStats.map((d, i) => (
              <div key={d.name} style={styles.dresserLine}><span style={styles.dresserRank}>{i + 1}</span><span style={{ flex: 1, fontWeight: 600 }}>{d.name}</span><span style={styles.mutedSmall}>{d.count} dressing{d.count > 1 ? "s" : ""}</span></div>
            ))}
          </div>
        </CollapsibleSection>
      )}

      <CollapsibleSection title="Recent Cases" defaultOpen>
        {recentCases.length === 0 ? <EmptyState text="No cases yet. Add your first case from the Cases tab." /> : (
          <div style={styles.list}>{recentCases.map((c) => <CaseRow key={c.id} c={c} products={products} compact />)}</div>
        )}
      </CollapsibleSection>
    </div>
  );
}

function StatCard({ label, value, accent, icon, onClick }) {
  return (
    <button onClick={onClick} style={{ ...styles.statCard, borderColor: accent + "26" }}>
      {icon && (
        <div style={{ width: 32, height: 32, borderRadius: 9, background: accent + "1A", color: accent, display: "flex", alignItems: "center", justifyContent: "center", marginBottom: 10 }}>
          <Icon name={icon} size={17} />
        </div>
      )}
      <div style={{ ...styles.statValue, color: accent }}>{value}</div>
      <div style={styles.statLabel}>{label}</div>
    </button>
  );
}
function SectionTitle({ children }) { return <div style={styles.sectionTitle}>{children}</div>; }
function EmptyState({ text }) { return <div style={styles.emptyState}>{text}</div>; }

// ---------------- Cases (Owner) ----------------
function CasesTab({ cases, machines, products, saveCase, deleteCase, addPayment, addDressingChange, addAdditionalItem }) {
  const [showForm, setShowForm] = useState(false);
  const [editing, setEditing] = useState(null);
  const [filter, setFilter] = useState("all"); const [search, setSearch] = useState("");

  const filtered = cases.filter((c) => {
    if (filter === "all") return true;
    if (filter === "overdue") return overdueDays(c) > 0;
    return c.status === filter;
  });
  const searched = search.trim() ? filtered.filter((c) => (c.patientName||"").toLowerCase().includes(search.trim().toLowerCase()) || (c.doctorName||"").toLowerCase().includes(search.trim().toLowerCase())) : filtered; const sorted = [...searched].sort((a, b) => new Date(b.applicationDate) - new Date(a.applicationDate));

  if (showForm) {
    return (
      <CaseForm machines={machines} products={products} initial={editing}
        onCancel={() => { setShowForm(false); setEditing(null); }}
        onSave={(data) => { saveCase(data, editing ? editing.id : null); setShowForm(false); setEditing(null); }} />
    );
  }

  return (
    <div>
      <input style={{...styles.input, marginBottom: 10}} placeholder="Search by patient or doctor name..." value={search} onChange={(e) => setSearch(e.target.value)} /><div style={styles.filterRow}>
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
            <CaseRow key={c.id} c={c} products={products}
              onEdit={() => { setEditing(c); setShowForm(true); }}
              onDelete={() => deleteCase(c.id)}
              onAddPayment={(p) => addPayment(c.id, p)}
              onAddDressingChange={(e) => addDressingChange(c.id, e)}
              onAddAdditionalItem={(e) => addAdditionalItem(c.id, e)} />
          ))}
        </div>
      )}
    </div>
  );
}

function CaseRow({ c, products = [], compact, onEdit, onDelete, onAddPayment, onAddDressingChange, onAddAdditionalItem }) {
  const [open, setOpen] = useState(false);
  const [payAmount, setPayAmount] = useState("");
  const [payNote, setPayNote] = useState("");
  const [payMode, setPayMode] = useState("Cash");
  const [changeDresser, setChangeDresser] = useState(c.dresserName || "");
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
        loadKey(photoKey(c.id, s.key), null).then((url) => { if (url) setPhotoData((prev) => ({ ...prev, [s.key]: url })); });
      }
    });
    // eslint-disable-next-line
  }, [open]);

  return (
    <div style={styles.card}>
      <div style={styles.cardTop} onClick={() => !compact && setOpen((o) => !o)}>
        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={styles.cardTitle}>{c.patientName}</div>
          <div style={styles.cardMeta}>Dr. {c.doctorName} · {getCaseProducts(c).join(", ")} · {c.protocolDays || 5}-day protocol</div>
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
            {Number(c.machineRentalAmount) > 0 && <Detail label="Machine Rental" value={fmtMoney(c.machineRentalAmount)} />}
            {Number(c.doctorCommission) > 0 && <Detail label="Doctor Commission" value={fmtMoney(c.doctorCommission)} />}
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
                <input type="text" placeholder="Dresser name" value={changeDresser} onChange={(e) => setChangeDresser(e.target.value)} style={{ ...styles.smallInput, flex: 1 }} />
                <select value={changeProtocol} onChange={(e) => setChangeProtocol(Number(e.target.value))} style={styles.smallInput}>
                  {PROTOCOLS.map((p) => <option key={p} value={p}>{p}d</option>)}
                </select>
                <button style={styles.smallBtn} onClick={() => {
                  if (!changeDresser.trim()) return;
                  onAddDressingChange({ date: todayISO(), dresserName: changeDresser.trim(), protocolDays: changeProtocol, note: changeNote });
                  setChangeNote("");
                }}>Log Change</button>
              </div>
            )}
          </div>

          {c.status === "active" && onAddAdditionalItem && (
            <AdditionalItemsBlock c={c} products={products} onAddAdditionalItem={onAddAdditionalItem} />
          )}

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
            <button style={{ ...styles.linkBtn, color: "#E1483C" }} onClick={onDelete}>Delete</button>
          </div>
        </div>
      )}
    </div>
  );
}

function Detail({ label, value, highlight }) {
  return <div><div style={styles.detailLabel}>{label}</div><div style={{ ...styles.detailValue, color: highlight ? "#E1483C" : "#182322" }}>{value}</div></div>;
}

function CaseForm({ machines, products, initial, onCancel, onSave, presetDresserName }) {
  const productsByCompany = useMemo(() => groupProductsByCompany(products), [products]);
  const [form, setForm] = useState(initial || {
    patientName: "", patientMobile: "", doctorName: "", doctorCommission: "", dresserName: presetDresserName || "", protocolDays: 5,
       machineSerial: "", products: products[0] ? [products[0].name] : [],
    applicationDate: todayISO(), applicationTime: nowTimeHM(), status: "active", endDate: "",
    billTo: "Patient", hospitalName: "", totalAmount: "", amountReceived: "", machineRentalAmount: "", notes: "",
  });
  const [customProtocol, setCustomProtocol] = useState(!PROTOCOLS.includes(Number(form.protocolDays)));
  const [amountTouched, setAmountTouched] = useState(!!initial);
  const set = (k, v) => setForm((f) => ({ ...f, [k]: v }));

  const mrpTotal = useMemo(
    () => (form.products || []).reduce((s, n) => s + Number(products.find((p) => p.name === n)?.mrp || 0), 0),
    [form.products, products]
  );

  // For a brand-new case, keep Total Amount following the selected products' MRP
  // until the person types their own number — then it's fully manual from there.
  useEffect(() => {
    if (!initial && !amountTouched) set("totalAmount", mrpTotal || "");
  }, [mrpTotal, initial, amountTouched]);

  const submit = () => {
    if (!form.patientName.trim() || !form.doctorName.trim()) return;
    onSave({ ...form, totalAmount: Number(form.totalAmount) || 0, machineRentalAmount: Number(form.machineRentalAmount) || 0, doctorCommission: Number(form.doctorCommission) || 0, protocolDays: Number(form.protocolDays) || 5 });
  };

  return (
    <div>
      <SectionTitle>{initial ? "Edit Case" : "New Case"}</SectionTitle>
      <div style={styles.formGrid}>
        <Field label="Patient Name"><input style={styles.input} value={form.patientName} onChange={(e) => set("patientName", e.target.value)} /></Field>
        <Field label="Patient Mobile Number"><input type="tel" style={styles.input} value={form.patientMobile} onChange={(e) => set("patientMobile", e.target.value)} placeholder="10-digit number" /></Field>
        <Field label="Doctor Name"><input style={styles.input} value={form.doctorName} onChange={(e) => set("doctorName", e.target.value)} /></Field>
        <Field label="Doctor Commission (₹, optional)">
          <input type="number" style={styles.input} value={form.doctorCommission} onChange={(e) => set("doctorCommission", e.target.value)} placeholder="0 if none" />
        </Field>
        <Field label="Dresser Name (applied by)"><input style={styles.input} value={form.dresserName} onChange={(e) => set("dresserName", e.target.value)} /></Field>
        <Field label="Therapy Protocol">
          {!customProtocol ? (
            <select style={styles.input} value={form.protocolDays} onChange={(e) => { if (e.target.value === "custom") setCustomProtocol(true); else set("protocolDays", Number(e.target.value)); }}>
              {PROTOCOLS.map((p) => <option key={p} value={p}>Every {p} days</option>)}
              <option value="custom">Custom…</option>
            </select>
          ) : (
            <div style={{ display: "flex", gap: 6 }}>
              <input type="number" style={styles.input} value={form.protocolDays} onChange={(e) => set("protocolDays", e.target.value)} placeholder="Days" />
              <button type="button" style={styles.smallBtn} onClick={() => { setCustomProtocol(false); set("protocolDays", 5); }}>Use standard</button>
            </div>
          )}
        </Field>
                <Field label="Product(s)">
          <div style={{ display: "flex", flexDirection: "column", gap: 4, border: "1px solid #DCE4DF", borderRadius: 10, padding: 8, maxHeight: 220, overflowY: "auto" }}>
            {productsByCompany.map(([company, prods]) => (
              <div key={company}>
                <div style={{ fontSize: 11, fontWeight: 700, color: "#8A9A96", margin: "6px 0 2px" }}>{company}</div>
                {prods.map((p) => (
                  <label key={p.id} style={{ display: "flex", alignItems: "center", gap: 6, fontSize: 14, padding: "3px 0" }}>
                    <input
                      type="checkbox"
                      checked={(form.products || []).includes(p.name)}
                      onChange={(e) => {
                        const current = form.products || [];
                        const next = e.target.checked
                          ? [...current, p.name]
                          : current.filter((n) => n !== p.name);
                        set("products", next);
                      }}
                    />
                    {p.name}
                  </label>
                ))}
              </div>
            ))}
          </div>
        </Field>
        <Field label="Machine Serial No.">
          <select style={styles.input} value={form.machineSerial} onChange={(e) => set("machineSerial", e.target.value)}>
            <option value="">— None —</option>
            {machines.map((m) => <option key={m.id} value={m.serial}>{m.serial} ({m.model})</option>)}
          </select>
        </Field>
        {form.machineSerial && (
          <Field label="Machine Rental Amount (₹)">
            <input type="number" style={styles.input} value={form.machineRentalAmount} onChange={(e) => set("machineRentalAmount", e.target.value)} placeholder="0 if no rental charged" />
          </Field>
        )}
        <Field label="Application Date"><input type="date" style={styles.input} value={form.applicationDate} onChange={(e) => set("applicationDate", e.target.value)} /></Field>
        <Field label="Application Time"><input type="time" style={styles.input} value={form.applicationTime} onChange={(e) => set("applicationTime", e.target.value)} /></Field>
        <Field label="Status">
          <select style={styles.input} value={form.status} onChange={(e) => set("status", e.target.value)}>
            <option value="active">VAC Therapy Applied</option>
            <option value="stopped">VAC Therapy Stop</option>
            <option value="reapplied">VAC Therapy Continue</option>
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
        <Field label="Total Amount (₹)">
          <input type="number" style={styles.input} value={form.totalAmount}
            onChange={(e) => { setAmountTouched(true); set("totalAmount", e.target.value); }} />
          {mrpTotal > 0 && (
            <span style={styles.mutedSmall}>
              MRP for selected item(s): {fmtMoney(mrpTotal)}
              {Number(form.totalAmount) !== mrpTotal && (
                <> · <span style={{ ...styles.linkBtn, fontSize: 11 }} onClick={() => { setAmountTouched(false); set("totalAmount", mrpTotal); }}>use MRP</span></>
              )}
            </span>
          )}
        </Field>
        <Field label="Amount Received (₹)"><input type="number" style={styles.input} value={form.amountReceived} onChange={(e) => set("amountReceived", e.target.value)} placeholder="0 if none yet" /></Field>
        <Field label="Notes"><textarea style={{ ...styles.input, minHeight: 60 }} value={form.notes} onChange={(e) => set("notes", e.target.value)} /></Field>
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

// ---------------- Machines ----------------
// ================= QUOTATIONS =================
function QuotationsTab({ quotations, products, saveQuotation, deleteQuotation, setQuotationStatus, creatorName = "Owner", restrictToCreator = false, businessName = "Bhagirathi Agency" }) {
  const [showForm, setShowForm] = useState(false);
  const [editing, setEditing] = useState(null);
  const [viewing, setViewing] = useState(null);
  const [search, setSearch] = useState("");
  const [openId, setOpenId] = useState(null);

  const visible = restrictToCreator
    ? quotations.filter((q) => (q.createdBy || "Owner").trim().toLowerCase() === creatorName.trim().toLowerCase())
    : quotations;
  const sorted = [...visible].sort((a, b) => new Date(b.date || b.createdAt) - new Date(a.date || a.createdAt));
  const filtered = sorted.filter((q) => {
    const t = search.trim().toLowerCase();
    if (!t) return true;
    return (q.customerName || "").toLowerCase().includes(t) || (q.quoteNo || "").toLowerCase().includes(t);
  });

  if (viewing) {
    return (
      <QuotationView q={viewing} onBack={() => setViewing(null)}
        onEdit={() => { setEditing(viewing); setViewing(null); setShowForm(true); }}
        onStatus={(s) => { setQuotationStatus(viewing.id, s); setViewing({ ...viewing, status: s }); }}
        businessName={businessName} />
    );
  }

  return (
    <div>
      {!showForm && (
        <>
          <button style={styles.primaryBtn} onClick={() => { setEditing(null); setShowForm(true); }}>+ New Quotation</button>
          <input style={{ ...styles.input, marginBottom: 12 }} placeholder="Search by customer or quote no."
            value={search} onChange={(e) => setSearch(e.target.value)} />
        </>
      )}
      {showForm && (
        <QuotationForm products={products} initial={editing} quotations={quotations}
          onCancel={() => { setShowForm(false); setEditing(null); }}
          onSave={(data) => {
            saveQuotation({ ...data, createdBy: editing ? (editing.createdBy || creatorName) : creatorName }, editing?.id);
            setShowForm(false); setEditing(null);
          }} />
      )}
      {!showForm && (
        filtered.length === 0 ? <EmptyState text={restrictToCreator ? "You haven't created any quotations yet." : "No quotations yet"} /> : (
          <div style={styles.list}>
            {filtered.map((q) => {
              const { total } = quoteTotals(q);
              const st = QUOTE_STATUS[q.status] || QUOTE_STATUS.draft;
              const open = openId === q.id;
              return (
                <div key={q.id} style={styles.card}>
                  <div style={styles.cardTop} onClick={() => setOpenId(open ? null : q.id)}>
                    <div style={{ flex: 1 }}>
                      <div style={styles.cardTitle}>{q.customerName || "Untitled"}</div>
                      <div style={styles.cardMeta}>{q.quoteNo} · {fmtDate(q.date)}{!restrictToCreator ? ` · by ${q.createdBy || "Owner"}` : ""}</div>
                    </div>
                    <div style={{ textAlign: "right" }}>
                      <div style={{ fontWeight: 700, fontFamily: "'Space Grotesk', sans-serif" }}>{fmtMoney(total)}</div>
                      <span style={{ ...styles.badge, color: st.color, background: st.bg }}>{st.label}</span>
                    </div>
                  </div>
                  {open && (
                    <div style={{ display: "flex", gap: 16, padding: "0 14px 12px" }}>
                      <button style={styles.linkBtn} onClick={() => setViewing(q)}>View / Print</button>
                      <button style={styles.linkBtn} onClick={() => { setEditing(q); setShowForm(true); }}>Edit</button>
                      <button style={{ ...styles.linkBtn, color: "#E1483C" }}
                        onClick={() => { if (window.confirm("Delete this quotation?")) deleteQuotation(q.id); }}>Delete</button>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )
      )}
    </div>
  );
}

function QuotationForm({ products, initial, quotations, onCancel, onSave }) {
  const productsByCompany = useMemo(() => groupProductsByCompany(products), [products]);
  const [form, setForm] = useState(initial || {
    quoteNo: nextQuoteNumber(quotations),
    date: todayISO(),
    validTill: addDays(todayISO(), 15),
    customerName: "", phone: "", address: "",
    items: [{ id: uid(), name: "", productName: "", variant: "", qty: 1, rate: 0, custom: products.length === 0 }],
    discount: 0, gstPercent: 0,
    notes: "", terms: DEFAULT_TERMS,
  });

  const set = (k, v) => setForm((f) => ({ ...f, [k]: v }));
  const setItem = (id, k, v) => setForm((f) => ({ ...f, items: f.items.map((it) => it.id === id ? { ...it, [k]: v } : it) }));
  const addItem = () => setForm((f) => ({ ...f, items: [...f.items, { id: uid(), name: "", productName: "", variant: "", qty: 1, rate: 0, custom: products.length === 0 } ] }));
  const removeItem = (id) => setForm((f) => ({ ...f, items: f.items.filter((it) => it.id !== id) }));
  const pickFromStock = (id, name) => {
    const prod = products.find((p) => p.name === name);
    setForm((f) => ({
      ...f,
      items: f.items.map((it) => it.id === id ? {
        ...it, name, productName: name, variant: "", custom: false,
        rate: Number(it.rate) > 0 ? it.rate : (prod ? prod.costPrice || 0 : it.rate),
      } : it),
    }));
  };
  const pickVariant = (id, variant) => {
    setForm((f) => ({
      ...f,
      items: f.items.map((it) => it.id === id ? {
        ...it, variant, name: variant ? `${it.productName} (${variant})` : it.productName,
      } : it),
    }));
  };
  const { subtotal, taxable, gstAmount, total } = quoteTotals(form);

  return (
    <div>
      <div style={styles.formGrid}>
        <div style={styles.field}><span style={styles.fieldLabel}>Customer Name</span>
          <input style={styles.input} value={form.customerName} onChange={(e) => set("customerName", e.target.value)} placeholder="Patient / customer / hospital name" /></div>
        <div style={styles.field}><span style={styles.fieldLabel}>Phone</span>
          <input style={styles.input} value={form.phone} onChange={(e) => set("phone", e.target.value)} /></div>
        <div style={styles.field}><span style={styles.fieldLabel}>Email</span>
          <input style={styles.input} type="email" value={form.email || ""} onChange={(e) => set("email", e.target.value)} placeholder="customer@example.com" /></div>
        <div style={styles.field}><span style={styles.fieldLabel}>Address</span>
          <input style={styles.input} value={form.address} onChange={(e) => set("address", e.target.value)} /></div>
        <div style={styles.detailGrid}>
          <div style={styles.field}><span style={styles.fieldLabel}>Date</span>
            <input type="date" style={styles.input} value={form.date} onChange={(e) => set("date", e.target.value)} /></div>
          <div style={styles.field}><span style={styles.fieldLabel}>Valid Till</span>
            <input type="date" style={styles.input} value={form.validTill} onChange={(e) => set("validTill", e.target.value)} /></div>
        </div>

        <SectionTitle>Items</SectionTitle>
        {form.items.map((it) => {
          const selectedProduct = products.find((p) => p.name === it.productName);
          const hasVariants = selectedProduct && (selectedProduct.variants || []).length > 0;
          return (
          <div key={it.id} style={{ marginBottom: 6, border: "1px solid #EEF1EC", borderRadius: 8, padding: 6 }}>
            <div style={{ display: "flex", gap: 6, alignItems: "center", flexWrap: "wrap" }}>
              {it.custom ? (
                <div style={{ display: "flex", flex: 3, minWidth: 160, gap: 4, alignItems: "center" }}>
                  <input style={{ ...styles.input, flex: 1 }} placeholder="Custom item name"
                    value={it.name} onChange={(e) => setItem(it.id, "name", e.target.value)} />
                  {products.length > 0 && (
                    <button style={{ ...styles.linkBtn, fontSize: 11 }} onClick={() => setItem(it.id, "custom", false)}>stock</button>
                  )}
                </div>
              ) : (
                <select style={{ ...styles.input, flex: 3, minWidth: 160 }} value={it.productName || ""}
                  onChange={(e) => e.target.value === "__new__" ? setItem(it.id, "custom", true) : pickFromStock(it.id, e.target.value)}>
                  <option value="" disabled>Select item…</option>
                  {productsByCompany.map(([company, prods]) => (
                    <optgroup key={company} label={company}>
                      {prods.map((p) => (
                        <option key={p.id} value={p.name}>{p.name} ({p.available || 0} in stock)</option>
                      ))}
                    </optgroup>
                  ))}
                  <option value="__new__">+ New item (not in stock)</option>
                </select>
              )}
              <input style={{ ...styles.input, flex: 1, minWidth: 60 }} type="number" placeholder="Qty"
                value={it.qty} onChange={(e) => setItem(it.id, "qty", e.target.value)} />
              <input style={{ ...styles.input, flex: 1.3, minWidth: 70 }} type="number" placeholder="Rate ₹"
                value={it.rate} onChange={(e) => setItem(it.id, "rate", e.target.value)} />
              <button style={{ ...styles.linkBtn, color: "#E1483C" }} onClick={() => removeItem(it.id)}>✕</button>
            </div>
            {hasVariants && (
              <div style={{ marginTop: 6 }}>
                <select style={{ ...styles.input, maxWidth: 220 }} value={it.variant || ""}
                  onChange={(e) => pickVariant(it.id, e.target.value)}>
                  <option value="">Select size / variant…</option>
                  {selectedProduct.variants.map((v) => <option key={v} value={v}>{v}</option>)}
                </select>
              </div>
            )}
          </div>
          );
        })}
        <button style={styles.secondaryBtn} onClick={addItem}>+ Add Item</button>


        <div style={styles.detailGrid}>
          <div style={styles.field}><span style={styles.fieldLabel}>Discount (₹)</span>
            <input style={styles.input} type="number" value={form.discount} onChange={(e) => set("discount", e.target.value)} /></div>
          <div style={styles.field}><span style={styles.fieldLabel}>GST %</span>
            <input style={styles.input} type="number" value={form.gstPercent} onChange={(e) => set("gstPercent", e.target.value)} /></div>
        </div>

        <div style={styles.notesBox}>
          <div style={{ display: "flex", justifyContent: "space-between", fontSize: 13 }}><span>Subtotal</span><span>{fmtMoney(subtotal)}</span></div>
          <div style={{ display: "flex", justifyContent: "space-between", fontSize: 13 }}><span>After discount</span><span>{fmtMoney(taxable)}</span></div>
          <div style={{ display: "flex", justifyContent: "space-between", fontSize: 13 }}><span>GST</span><span>{fmtMoney(gstAmount)}</span></div>
          <div style={{ display: "flex", justifyContent: "space-between", fontWeight: 700, marginTop: 4 }}><span>Total</span><span>{fmtMoney(total)}</span></div>
        </div>

        <div style={styles.field}><span style={styles.fieldLabel}>Notes (optional)</span>
          <textarea style={{ ...styles.input, minHeight: 50 }} value={form.notes} onChange={(e) => set("notes", e.target.value)} /></div>
        <div style={styles.field}><span style={styles.fieldLabel}>Terms & Conditions</span>
          <textarea style={{ ...styles.input, minHeight: 110 }} value={form.terms} onChange={(e) => set("terms", e.target.value)} /></div>
      </div>
      <div style={styles.formActions}>
        <button style={styles.secondaryBtn} onClick={onCancel}>Cancel</button>
        <button style={{ ...styles.smallBtn, flex: 1 }}
          disabled={!form.customerName.trim()}
          onClick={() => onSave({ ...form, items: form.items.filter((it) => it.name.trim()) })}>Save Quotation</button>
      </div>
    </div>
  );
}

function QuotationView({ q, onBack, onEdit, onStatus, businessName = "Bhagirathi Agency" }) {
  const { subtotal, discount, gstAmount, total } = quoteTotals(q);
  const sheetRef = useRef(null);
  const [busy, setBusy] = useState("");
  const shareText = `${businessName} — Quotation ${q.quoteNo}\nTo: ${q.customerName}\nTotal: ${fmtMoney(total)}\nValid till: ${fmtDate(q.validTill)}`;
  const fileName = `Quotation-${(q.quoteNo || "BA").replace(/\//g, "-")}.pdf`;

  const makeFile = async () => {
    const blob = await quotePdfBlob(sheetRef.current);
    return new File([blob], fileName, { type: "application/pdf" });
  };

  const downloadPdf = async () => {
    setBusy("download");
    try {
      const file = await makeFile();
      const url = URL.createObjectURL(file);
      const a = document.createElement("a");
      a.href = url; a.download = fileName; a.click();
      URL.revokeObjectURL(url);
    } finally { setBusy(""); }
  };

  const sharePdf = async () => {
    setBusy("share");
    try {
      const file = await makeFile();
      if (navigator.canShare && navigator.canShare({ files: [file] })) {
        await navigator.share({ files: [file], title: `Quotation ${q.quoteNo}`, text: shareText });
      } else {
        // Desktop / unsupported: download the file, then open WhatsApp with the text so it can be attached manually.
        const url = URL.createObjectURL(file);
        const a = document.createElement("a");
        a.href = url; a.download = fileName; a.click();
        URL.revokeObjectURL(url);
        window.open(waLink(q.phone ? q.phone.replace(/\D/g, "") : OWNER_WHATSAPP, shareText), "_blank");
        alert("PDF downloaded. Your browser can't attach it automatically here — attach the downloaded file in the WhatsApp chat that just opened.");
      }
    } catch (e) {
      if (e?.name !== "AbortError") alert("Couldn't share. Try Download instead.");
    } finally { setBusy(""); }
  };

  const emailPdf = async () => {
    const to = (q.email || "").trim() || window.prompt("Customer email address to send this quotation to:", "");
    if (!to) return;
    setBusy("email");
    try {
      const file = await makeFile();
      const pdfBase64 = await blobToBase64(file);
      const subject = `Quotation ${q.quoteNo} — ${businessName}`;
      const body = `Dear ${q.customerName || ""},\n\nPlease find attached our quotation ${q.quoteNo} dated ${fmtDate(q.date)}, valid till ${fmtDate(q.validTill)}.\nTotal: ${fmtMoney(total)}\n\nRegards,\n${businessName}`;
      const resp = await fetch("/api/send-quote-email", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ to, subject, text: body, pdfBase64, filename: fileName }),
      });
      if (!resp.ok) {
        const err = await resp.json().catch(() => ({}));
        throw new Error(err.error || "send failed");
      }
      alert(`Quotation emailed to ${to}.`);
    } catch (e) {
      // Backend not set up yet, or send failed — fall back to a manual mailto draft with the PDF downloaded.
      const file = await makeFile();
      const url = URL.createObjectURL(file);
      const a = document.createElement("a");
      a.href = url; a.download = fileName; a.click();
      URL.revokeObjectURL(url);
      const subject = encodeURIComponent(`Quotation ${q.quoteNo} — ${businessName}`);
      const body = encodeURIComponent(`Dear ${q.customerName || ""},\n\nPlease find attached our quotation ${q.quoteNo} dated ${fmtDate(q.date)}, valid till ${fmtDate(q.validTill)}.\nTotal: ${fmtMoney(total)}\n\nRegards,\n${businessName}`);
      window.location.href = `mailto:${encodeURIComponent(to)}?subject=${subject}&body=${body}`;
      alert("Couldn't auto-send (email sending isn't set up yet on the server). PDF downloaded — attach it to the email draft that just opened.");
    } finally { setBusy(""); }
  };

  return (
    <div>
      <div className="no-print" style={{ display: "flex", gap: 8, flexWrap: "wrap", marginBottom: 14 }}>
        <button style={styles.linkBtn} onClick={onBack}>← Back</button>
        <div style={{ flex: 1 }} />
        {Object.keys(QUOTE_STATUS).map((s) => (
          <button key={s} onClick={() => onStatus(s)}
            style={{ ...styles.filterChip, ...(q.status === s ? styles.filterChipActive : {}) }}>{QUOTE_STATUS[s].label}</button>
        ))}
      </div>
      <div className="no-print" style={{ display: "flex", gap: 8, marginBottom: 16, flexWrap: "wrap" }}>
        <button style={styles.secondaryBtn} onClick={onEdit}>Edit</button>
        <button style={{ ...styles.smallBtn, background: "#3B5BA5", flex: 1 }} disabled={!!busy} onClick={downloadPdf}>
          {busy === "download" ? "Preparing…" : "Download PDF"}
        </button>
        <button style={{ ...styles.smallBtn, background: "#25D366", flex: 1 }} disabled={!!busy} onClick={sharePdf}>
          {busy === "share" ? "Preparing…" : "WhatsApp"}
        </button>
        <button style={{ ...styles.smallBtn, background: "#E1483C", flex: 1 }} disabled={!!busy} onClick={emailPdf}>
          {busy === "email" ? "Preparing…" : "Email"}
        </button>
      </div>

      <div style={styles.quoteSheet} ref={sheetRef}>
        <div style={styles.quoteHeader}>
          <img src="/bhagirathi-logo.png" alt={businessName} style={{ width: 46, height: 46, objectFit: "contain" }} />
          <div>
            <div style={{ fontFamily: "'Space Grotesk', sans-serif", fontWeight: 700, fontSize: 17 }}>{businessName}</div>
            <div style={{ fontSize: 11, color: "#5B6864" }}>Wound Care & NPWT Supplies</div>
          </div>
        </div>
        <div style={{ display: "flex", justifyContent: "space-between", margin: "14px 0", fontSize: 13 }}>
          <div><strong>Quotation No.</strong><br />{q.quoteNo}</div>
          <div><strong>Date</strong><br />{fmtDate(q.date)}</div>
          <div><strong>Valid Till</strong><br />{fmtDate(q.validTill)}</div>
        </div>
        <div style={{ marginBottom: 14, fontSize: 13 }}>
          <strong>To:</strong> {q.customerName}<br />
          {q.phone && <>{q.phone}<br /></>}
          {q.email && <>{q.email}<br /></>}
          {q.address}
        </div>
        <table style={styles.quoteTable}>
          <thead><tr><th style={styles.quoteTh}>#</th><th style={styles.quoteTh}>Item</th><th style={styles.quoteTh}>Qty</th><th style={styles.quoteTh}>Rate</th><th style={styles.quoteTh}>Amount</th></tr></thead>
          <tbody>
            {(q.items || []).map((it, i) => (
              <tr key={it.id}>
                <td style={styles.quoteTd}>{i + 1}</td>
                <td style={styles.quoteTd}>{it.name}</td>
                <td style={styles.quoteTd}>{it.qty}</td>
                <td style={styles.quoteTd}>{fmtMoney(it.rate)}</td>
                <td style={styles.quoteTd}>{fmtMoney(Number(it.qty || 0) * Number(it.rate || 0))}</td>
              </tr>
            ))}
          </tbody>
        </table>
        <div style={{ marginLeft: "auto", width: 220, marginTop: 10, fontSize: 13 }}>
          <div style={{ display: "flex", justifyContent: "space-between" }}><span>Subtotal</span><span>{fmtMoney(subtotal)}</span></div>
          {discount > 0 && <div style={{ display: "flex", justifyContent: "space-between" }}><span>Discount</span><span>-{fmtMoney(discount)}</span></div>}
          {Number(q.gstPercent) > 0 && <div style={{ display: "flex", justifyContent: "space-between" }}><span>GST ({q.gstPercent}%)</span><span>{fmtMoney(gstAmount)}</span></div>}
          <div style={{ display: "flex", justifyContent: "space-between", fontWeight: 700, borderTop: "1px solid #DCE4DF", marginTop: 4, paddingTop: 4 }}><span>Total</span><span>{fmtMoney(total)}</span></div>
        </div>
        {q.notes && <div style={{ marginTop: 16, fontSize: 12 }}><strong>Notes:</strong><br />{q.notes}</div>}
        {q.terms && <div style={{ marginTop: 16, fontSize: 11, color: "#5B6864", whiteSpace: "pre-line" }}><strong>Terms & Conditions</strong><br />{q.terms}</div>}
        <div style={{ marginTop: 40, fontSize: 12 }}>For {businessName}<br /><br /><br />Authorised Signatory</div>
      </div>
    </div>
  );
}

function MachinesTab({ machines, setMachines, machineInUse, cases }) {
  const [showForm, setShowForm] = useState(false);
  const [serial, setSerial] = useState("");
  const [model, setModel] = useState("");
  const [openId, setOpenId] = useState(null);
  const addMachine = () => {
    if (!serial.trim()) return;
    setMachines((prev) => [...prev, { id: uid(), serial: serial.trim(), model: model.trim() || "NPWT Unit" }]);
    setSerial(""); setModel(""); setShowForm(false);
  };
  const removeMachine = (id) => setMachines((prev) => prev.filter((m) => m.id !== id));

  return (
    <div>
      {showForm ? (
        <div style={styles.formGrid}>
          <Field label="Serial Number"><input style={styles.input} value={serial} onChange={(e) => setSerial(e.target.value)} /></Field>
          <Field label="Model / Type"><input style={styles.input} value={model} onChange={(e) => setModel(e.target.value)} placeholder="e.g. NPWT Unit" /></Field>
          <div style={styles.formActions}>
            <button style={styles.secondaryBtn} onClick={() => setShowForm(false)}>Cancel</button>
            <button style={styles.primaryBtn} onClick={addMachine}>Add Machine</button>
          </div>
        </div>
      ) : <button style={styles.primaryBtn} onClick={() => setShowForm(true)}>+ Add Machine</button>}

      {machines.length === 0 ? <EmptyState text="No machines added yet." /> : (
        <div style={styles.list}>
          {machines.map((m) => {
            const inUse = machineInUse(m.serial);
            const activeCase = cases.find((c) => c.machineSerial === m.serial && c.status === "active");
            const open = openId === m.id;
            return (
              <div key={m.id} style={styles.card}>
                <div style={styles.cardTop} onClick={() => setOpenId(open ? null : m.id)}>
                  <div style={{ flex: 1 }}>
                    <div style={styles.cardTitle}>{m.serial}</div>
                    <div style={styles.cardMeta}>{m.model}</div>
                  </div>
                  <div style={{ display: "flex", flexDirection: "column", alignItems: "flex-end", gap: 6 }}>
                    <span style={{ ...styles.badge, color: inUse ? "#D9720A" : "#5B6864", background: inUse ? "#FBEAD3" : "#EEF0EE" }}>{inUse ? "In Use" : "Available"}</span>
                    <span style={{ fontSize: 11, color: "#8A9A96" }}>{open ? "▲ hide" : "▼ details"}</span>
                  </div>
                </div>
                {open && (
                  <div style={{ padding: "0 14px 14px" }}>
                    {inUse && activeCase ? (
                      <div style={styles.mutedSmall}>With {activeCase.patientName} since {fmtDate(activeCase.applicationDate)}</div>
                    ) : (
                      <div style={styles.mutedSmall}>Not currently assigned to a case.</div>
                    )}
                    <button style={{ ...styles.linkBtn, color: "#E1483C", marginTop: 12 }} onClick={() => removeMachine(m.id)}>Remove Machine</button>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

// ---------------- Stock ----------------
const PRICE_LIST_IMPORT = [
  // ---- MedSkin Solutions: MatriDerm ----
  { company: "MedSkin Solutions", name: "MatriDerm Dermal Matrix A4 297x210x2mm", ref: "83400-200", mrp: 361350 },
  { company: "MedSkin Solutions", name: "MatriDerm Dermal Matrix A4 297x210x1mm", ref: "83500-200", mrp: 328500 },
  { company: "MedSkin Solutions", name: "MatriDerm Dermal Matrix A6 148x105x2mm", ref: "83401-200", mrp: 94854 },
  { company: "MedSkin Solutions", name: "MatriDerm Dermal Matrix A6 148x105x1mm", ref: "83403-200", mrp: 86231 },
  { company: "MedSkin Solutions", name: "MatriDerm Dermal Matrix A8 74x52x1mm", ref: "83404-200", mrp: 37125 },
  { company: "MedSkin Solutions", name: "MatriDerm Dermal Matrix A9 52x37x1mm", ref: "83405-200", mrp: 20250 },
  { company: "MedSkin Solutions", name: "MatriDerm Flex A4 297x210x1mm", ref: "83440-200", mrp: 344925 },
  { company: "MedSkin Solutions", name: "MatriDerm Flex A4 297x210x2mm", ref: "83460-200", mrp: 379418 },
  { company: "MedSkin Solutions", name: "MatriDerm Flex A4 297x210x3mm", ref: "83470-200", mrp: 417359 },
  { company: "MedSkin Solutions", name: "MatriDerm Flex A6 148x105x1mm", ref: "83441-200", mrp: 90543 },
  { company: "MedSkin Solutions", name: "MatriDerm Flex A6 148x105x2mm", ref: "83461-200", mrp: 99597 },
  { company: "MedSkin Solutions", name: "MatriDerm Flex A6 148x105x3mm", ref: "83471-200", mrp: 109557 },
  { company: "MedSkin Solutions", name: "MatriDerm Flex A8 74x52x1mm", ref: "83442-200", mrp: 38906 },
  { company: "MedSkin Solutions", name: "MatriDerm Flex A8 74x52x2mm", ref: "83462-200", mrp: 42844 },
  { company: "MedSkin Solutions", name: "MatriDerm Flex A8 74x52x3mm", ref: "83472-200", mrp: 47063 },
  { company: "MedSkin Solutions", name: "MatriDerm Flex A9 52x37x1mm", ref: "83443-200", mrp: 21281 },
  { company: "MedSkin Solutions", name: "MatriDerm Flex A9 52x37x2mm", ref: "83463-200", mrp: 23344 },
  { company: "MedSkin Solutions", name: "MatriDerm Flex A9 52x37x3mm", ref: "83473-200", mrp: 25688 },
  { company: "MedSkin Solutions", name: "MatriDerm Fenestrated A4 297x210x1mm", ref: "83410-200", mrp: 344925 },
  { company: "MedSkin Solutions", name: "MatriDerm Fenestrated A4 297x210x2mm", ref: "83420-200", mrp: 379418 },
  { company: "MedSkin Solutions", name: "MatriDerm Fenestrated A4 297x210x3mm", ref: "83430-200", mrp: 417359 },
  { company: "MedSkin Solutions", name: "MatriDerm Fenestrated A6 148x105x1mm", ref: "83411-200", mrp: 90543 },
  { company: "MedSkin Solutions", name: "MatriDerm Fenestrated A6 148x105x2mm", ref: "83421-200", mrp: 99597 },
  { company: "MedSkin Solutions", name: "MatriDerm Fenestrated A6 148x105x3mm", ref: "83431-200", mrp: 109557 },
  { company: "MedSkin Solutions", name: "MatriDerm Fenestrated A8 74x52x1mm", ref: "83412-200", mrp: 38906 },
  { company: "MedSkin Solutions", name: "MatriDerm Fenestrated A8 74x52x2mm", ref: "83422-200", mrp: 42844 },
  { company: "MedSkin Solutions", name: "MatriDerm Fenestrated A8 74x52x3mm", ref: "83432-200", mrp: 47063 },
  { company: "MedSkin Solutions", name: "MatriDerm Fenestrated A9 52x37x1mm", ref: "83413-200", mrp: 21281 },
  { company: "MedSkin Solutions", name: "MatriDerm Fenestrated A9 52x37x2mm", ref: "83423-200", mrp: 23344 },
  { company: "MedSkin Solutions", name: "MatriDerm Fenestrated A9 52x37x3mm", ref: "83433-200", mrp: 25688 },
  // ---- Solventum: VAC / Prevena (per unit — no pack-size duplicates) ----
  { company: "Solventum", name: "SensaTRAC Small Granufoam Dressing", ref: "M8275051", mrp: 9380 },
  { company: "Solventum", name: "SensaTRAC Medium Granufoam Dressing", ref: "M8275052", mrp: 11240 },
  { company: "Solventum", name: "SensaTRAC Large Granufoam Dressing", ref: "M8275053", mrp: 14230 },
  { company: "Solventum", name: "ActiV.A.C. Canister with Gel", ref: "M8275058", mrp: 2980 },
  { company: "Solventum", name: "500ml Canister with Gel, InfoVAC", ref: "M8275063", mrp: 3760 },
  { company: "Solventum", name: "SensaTRAC Thin Granufoam Dressing", ref: "M8275081", mrp: 7420 },
  { company: "Solventum", name: "InfoV.A.C. 1000ml Canister", ref: "M8275093", mrp: 5560 },
  { company: "Solventum", name: "V.A.C.Ulta Therapy Unit (1yr warranty)", ref: "ULTDEV01/IN", mrp: 820313 },
  { company: "Solventum", name: "ActiVAC Therapy Unit (1yr warranty)", ref: "340123", mrp: 492188 },
  { company: "Solventum", name: "AB Thera Sensa T.R.A.C", ref: "M8275026", mrp: 40781 },
  { company: "Solventum", name: "VAC Granufoam Bridge Dressing", ref: "M8275042", mrp: 7875 },
  { company: "Solventum", name: "SensaTRAC Small Silver Granufoam Dressing", ref: "M8275098", mrp: 10219 },
  { company: "Solventum", name: "SensaTRAC Medium Silver Granufoam Dressing", ref: "M8275096", mrp: 12281 },
  { company: "Solventum", name: "SensaTRAC Large Silver Granufoam Dressing", ref: "M8275099", mrp: 15563 },
  { company: "Solventum", name: "VAC Standard Drape", ref: "M6275009", mrp: 394 },
  { company: "Solventum", name: "SensaTRAC Pad", ref: "M8275057", mrp: 1875 },
  { company: "Solventum", name: "VAC ATS TRAC Y Connector", ref: "M6275066", mrp: 375 },
  { company: "Solventum", name: "VAC ATS TRAC Tubing Cap", ref: "M6275069", mrp: 403 },
  { company: "Solventum", name: "VAC Veraflo Small Dressing", ref: "ULTVFL05SM", mrp: 11063 },
  { company: "Solventum", name: "VAC Veraflo Medium Dressing", ref: "ULTVFL05MD", mrp: 13313 },
  { company: "Solventum", name: "VAC Veraflo Large Dressing", ref: "ULTVFL05LG", mrp: 16781 },
  { company: "Solventum", name: "VAC Veraflo Cleanse Medium Dressing", ref: "ULTVCL05MD", mrp: 14438 },
  { company: "Solventum", name: "VAC Veraflo Cleanse Choice Medium Dressing", ref: "ULTVCC05MD", mrp: 18094 },
  { company: "Solventum", name: "VAC Veraflo Cleanse Choice Large Dressing", ref: "ULTVCC05LG", mrp: 19781 },
  { company: "Solventum", name: "VAC VeraLINK", ref: "ULTLNK0500", mrp: 3750 },
  { company: "Solventum", name: "Prevena Peel & Place Dressing 20cm", ref: "PRE1055", mrp: 23090 },
  { company: "Solventum", name: "Prevena Peel & Place Dressing 13cm", ref: "PRE1155", mrp: 19345 },
  { company: "Solventum", name: "Prevena Peel & Place Dressing 35cm", ref: "PRE3255", mrp: 27188 },
  { company: "Solventum", name: "Prevena Plus Customizable Dressing 90cm", ref: "PRE4055", mrp: 30000 },
  { company: "Solventum", name: "Prevena 125 Incision Management System 20cm", ref: "PRE1001", mrp: 50000 },
  { company: "Solventum", name: "Prevena 125 Incision Management System 13cm", ref: "PRE1101", mrp: 50000 },
  { company: "Solventum", name: "Prevena Plus 125 Incision Management System 35cm", ref: "PRE3201", mrp: 75000 },
  { company: "Solventum", name: "Prevena Plus 125 Customizable Incision Mgmt System 90cm", ref: "PRE4001", mrp: 66700 },
  { company: "Solventum", name: "Prevena 125 45ml Canister", ref: "PRE1095", mrp: 4840 },
  { company: "Solventum", name: "Prevena Plus 150ml Canister", ref: "PRE4095", mrp: 5650 },
];

// Old pack-labeled names (from an earlier import) -> new per-unit name, so duplicates like
// "...10 Pack" and "...5 Pack" merge into a single per-unit product.
const PACK_NAME_CLEANUP = {
  "sensatrac small granufoam dressing 10 pack": "SensaTRAC Small Granufoam Dressing",
  "sensatrac small granufoam dressing 5 pack": "SensaTRAC Small Granufoam Dressing",
  "sensatrac medium granufoam dressing 10 pack": "SensaTRAC Medium Granufoam Dressing",
  "sensatrac medium granufoam dressing 5 pack": "SensaTRAC Medium Granufoam Dressing",
  "sensatrac large granufoam dressing 10 pack": "SensaTRAC Large Granufoam Dressing",
  "sensatrac large granufoam dressing 5 pack": "SensaTRAC Large Granufoam Dressing",
  "activ.a.c. canister with gel 10/case": "ActiV.A.C. Canister with Gel",
  "activ.a.c. canister with gel 5/case": "ActiV.A.C. Canister with Gel",
  "500ml canister with gel 10 pack, infovac": "500ml Canister with Gel, InfoVAC",
  "500ml canister with gel 5 pack, infovac": "500ml Canister with Gel, InfoVAC",
  "sensatrac thin granufoam dressing 10 pack": "SensaTRAC Thin Granufoam Dressing",
  "sensatrac thin granufoam dressing 5 pack": "SensaTRAC Thin Granufoam Dressing",
  "infov.a.c. 1000ml canister 5 pack": "InfoV.A.C. 1000ml Canister",
  "vac granufoam bridge dressing 10 pack": "VAC Granufoam Bridge Dressing",
  "sensatrac small silver granufoam dressing 10 pack": "SensaTRAC Small Silver Granufoam Dressing",
  "sensatrac medium silver granufoam dressing 10 pack": "SensaTRAC Medium Silver Granufoam Dressing",
  "sensatrac large silver granufoam dressing 10 pack": "SensaTRAC Large Silver Granufoam Dressing",
  "vac standard drape 10 pack": "VAC Standard Drape",
  "sensatrac pad 10 pack": "SensaTRAC Pad",
  "vac ats trac y connector 10 pack": "VAC ATS TRAC Y Connector",
  "vac ats trac tubing cap 10 pack": "VAC ATS TRAC Tubing Cap",
  "vac veraflo small dressing 5 pack": "VAC Veraflo Small Dressing",
  "vac veraflo medium dressing 5 pack": "VAC Veraflo Medium Dressing",
  "vac veraflo large dressing 5 pack": "VAC Veraflo Large Dressing",
  "vac veraflo cleanse medium dressing 5 pack": "VAC Veraflo Cleanse Medium Dressing",
  "vac veraflo cleanse choice medium dressing 5 pack": "VAC Veraflo Cleanse Choice Medium Dressing",
  "vac veraflo cleanse choice large dressing 5 pack": "VAC Veraflo Cleanse Choice Large Dressing",
  "vac veralink 5 pack": "VAC VeraLINK",
  "prevena peel & place dressing 20cm 5/pk": "Prevena Peel & Place Dressing 20cm",
  "prevena peel & place dressing 13cm 5/pk": "Prevena Peel & Place Dressing 13cm",
  "prevena peel & place dressing 35cm 5/pk": "Prevena Peel & Place Dressing 35cm",
  "prevena plus customizable dressing 90cm 5/pk": "Prevena Plus Customizable Dressing 90cm",
  "prevena 125 incision management system 20cm kit": "Prevena 125 Incision Management System 20cm",
  "prevena 125 incision management system 13cm kit": "Prevena 125 Incision Management System 13cm",
  "prevena plus 125 incision management system 35cm kit": "Prevena Plus 125 Incision Management System 35cm",
  "prevena plus 125 customizable incision mgmt system 90cm kit": "Prevena Plus 125 Customizable Incision Mgmt System 90cm",
  "prevena 125 45ml canister 5/pk": "Prevena 125 45ml Canister",
  "prevena plus 150ml canister 5/pk": "Prevena Plus 150ml Canister",
};

function StockTab({ products, setProducts, receiveStock, actorName = "Owner" }) {
  const [name, setName] = useState("");
  const [initQty, setInitQty] = useState("");
  const [initCost, setInitCost] = useState("");
  const [initMrp, setInitMrp] = useState("");
  const [receiveForm, setReceiveForm] = useState({});
  const [variantInput, setVariantInput] = useState({});
  const [openId, setOpenId] = useState(null);
  const productsByCompany = useMemo(() => groupProductsByCompany(products), [products]);

  const addProduct = () => {
    if (!name.trim() || products.some((p) => p.name === name.trim())) return;
    const qty = Number(initQty) || 0;
    setProducts((prev) => [...prev, {
      id: uid(), name: name.trim(), available: qty, used: 0, costPrice: Number(initCost) || 0, mrp: Number(initMrp) || 0,
      receipts: qty > 0 ? [{ id: uid(), date: todayISO(), time: new Date().toLocaleTimeString("en-IN"), qty, company: "Unspecified", receivedBy: actorName }] : [],
      variants: [],
    }]);
    setName(""); setInitQty(""); setInitCost(""); setInitMrp("");
  };
  const remove = (id) => setProducts((prev) => prev.filter((p) => p.id !== id));
  const updateCost = (id, cost) => setProducts((prev) => prev.map((p) => p.id === id ? { ...p, costPrice: Number(cost) || 0 } : p));
  const updateMrp = (id, mrp) => setProducts((prev) => prev.map((p) => p.id === id ? { ...p, mrp: Number(mrp) || 0 } : p));
  const updateAvailable = (id, qty) => setProducts((prev) => prev.map((p) => p.id === id ? { ...p, available: Math.max(0, Number(qty) || 0) } : p));
  const setField = (id, field, val) => setReceiveForm((prev) => ({ ...prev, [id]: { ...prev[id], [field]: val } }));
  const doReceive = (id) => {
    const f = receiveForm[id] || {};
    const qty = Number(f.qty);
    if (!qty || qty <= 0) return;
    receiveStock(id, qty, f.company, actorName);
    setReceiveForm((prev) => ({ ...prev, [id]: { qty: "", company: "" } }));
  };
  const addVariant = (id) => {
    const val = (variantInput[id] || "").trim();
    if (!val) return;
    setProducts((prev) => prev.map((p) => p.id === id
      ? { ...p, variants: (p.variants || []).includes(val) ? p.variants : [...(p.variants || []), val] }
      : p));
    setVariantInput((prev) => ({ ...prev, [id]: "" }));
  };
  const removeVariant = (id, v) => setProducts((prev) => prev.map((p) => p.id === id
    ? { ...p, variants: (p.variants || []).filter((x) => x !== v) } : p));

  const [importDone, setImportDone] = useState(false);
  const importPriceList = () => {
    const existingNames = new Set(products.map((p) => p.name.toLowerCase()));
    const toAdd = PRICE_LIST_IMPORT.filter((item) => !existingNames.has(item.name.toLowerCase()));
    if (toAdd.length === 0) { setImportDone(true); return; }
    const newProducts = toAdd.map((item) => ({
      id: uid(),
      name: item.name,
      available: 0,
      used: 0,
      costPrice: 0,
      mrp: item.mrp,
      variants: [],
      receipts: [{ id: uid(), date: todayISO(), qty: 0, company: item.company }],
    }));
    setProducts((prev) => [...prev, ...newProducts]);
    setImportDone(true);
  };
  const newImportCount = PRICE_LIST_IMPORT.filter((item) => !products.some((p) => p.name.toLowerCase() === item.name.toLowerCase())).length;

  const packDupCount = products.filter((p) => PACK_NAME_CLEANUP[p.name.toLowerCase()]).length;
  const cleanupPackDuplicates = () => {
    const merged = {}; // target name (lowercase) -> merged product
    const untouched = [];
    products.forEach((p) => {
      const target = PACK_NAME_CLEANUP[p.name.toLowerCase()];
      if (!target) { untouched.push(p); return; }
      const key = target.toLowerCase();
      if (!merged[key]) {
        merged[key] = { ...p, name: target };
      } else {
        const m = merged[key];
        merged[key] = {
          ...m,
          available: (m.available || 0) + (p.available || 0),
          used: (m.used || 0) + (p.used || 0),
          costPrice: m.costPrice || p.costPrice || 0,
          mrp: m.mrp || p.mrp || 0,
          receipts: [...(m.receipts || []), ...(p.receipts || [])],
          variants: Array.from(new Set([...(m.variants || []), ...(p.variants || [])])),
        };
      }
    });
    setProducts([...untouched, ...Object.values(merged)]);
  };

  return (
    <div>
      {packDupCount > 0 && (
        <div style={{ ...styles.card, padding: 14, marginBottom: 16, border: "1px solid #FCE7E4" }}>
          <div style={{ fontSize: 13, marginBottom: 8 }}>
            <strong>{packDupCount} item{packDupCount > 1 ? "s" : ""}</strong> still have "5 Pack"/"10 Pack" in the name from an earlier import. Since you sell per unit, this merges any duplicates (like the 5-pack and 10-pack of the same dressing) into one per-unit product, combining their stock counts.
          </div>
          <button style={{ ...styles.smallBtn, background: "#E1483C" }} onClick={cleanupPackDuplicates}>Clean Up Pack-Size Duplicates ({packDupCount})</button>
        </div>
      )}
      {newImportCount > 0 && (
        <div style={{ ...styles.card, padding: 14, marginBottom: 16, border: "1px solid #FBEAD3" }}>
          <div style={{ fontSize: 13, marginBottom: 8 }}>
            <strong>{newImportCount} product{newImportCount > 1 ? "s" : ""}</strong> from the MedSkin Solutions (MatriDerm) and Solventum (VAC/Prevena) price lists can be imported with their MRP and company tagged — set your cost price and opening stock after.
          </div>
          <button style={styles.primaryBtn} onClick={importPriceList}>Import Price List ({newImportCount})</button>
        </div>
      )}
      {importDone && newImportCount === 0 && (
        <div style={{ ...styles.emptyState2, marginBottom: 10, color: "#128577" }}>All MedSkin Solutions &amp; Solventum items are imported.</div>
      )}
      <SectionTitle>Add Product</SectionTitle>
      <div style={styles.formGrid}>
        <div style={styles.addPaymentRow}>
          <input style={{ ...styles.smallInput, flex: 1 }} placeholder="Product name" value={name} onChange={(e) => setName(e.target.value)} />
          <input style={{ ...styles.smallInput, width: 70 }} type="number" placeholder="Qty" value={initQty} onChange={(e) => setInitQty(e.target.value)} />
          <input style={{ ...styles.smallInput, width: 90 }} type="number" placeholder="Cost ₹" value={initCost} onChange={(e) => setInitCost(e.target.value)} />
          <input style={{ ...styles.smallInput, width: 90 }} type="number" placeholder="MRP ₹" value={initMrp} onChange={(e) => setInitMrp(e.target.value)} />
        </div>
        <button style={styles.primaryBtn} onClick={addProduct}>Add Product</button>
      </div>

      <SectionTitle>Inventory</SectionTitle>
      {products.length === 0 ? <EmptyState text="No products added yet." /> : (
        <div>
          {productsByCompany.map(([company, prods]) => (
            <CollapsibleSection key={company} title={company} defaultOpen right={<span style={{ fontSize: 11, color: "#8A9A96" }}>{prods.length}</span>}>
              <div style={styles.list}>
                {prods.map((p) => {
                  const open = openId === p.id;
                  return (
                  <div key={p.id} style={styles.card}>
                    <div style={styles.cardTop} onClick={() => setOpenId(open ? null : p.id)}>
                      <div style={{ flex: 1 }}>
                        <div style={styles.cardTitle}>{p.name}</div>
                        <div style={styles.cardMeta}>
                          {p.used || 0} used all-time{(p.variants || []).length > 0 ? ` · ${p.variants.length} size${p.variants.length > 1 ? "s" : ""}` : ""}
                        </div>
                      </div>
                      <div style={{ display: "flex", flexDirection: "column", alignItems: "flex-end", gap: 6 }}>
                        <span style={{ ...styles.badge, color: (p.available || 0) < LOW_STOCK_THRESHOLD ? "#E1483C" : "#D9720A", background: (p.available || 0) < LOW_STOCK_THRESHOLD ? "#FCE7E4" : "#FBEAD3" }}>{p.available || 0} available</span>
                        <span style={{ fontSize: 11, color: "#8A9A96" }}>{open ? "▲ hide" : "▼ details"}</span>
                      </div>
                    </div>
                    {open && (
                      <div style={{ padding: "0 14px 14px" }}>
                        <div style={styles.addPaymentRow}>
                          <span style={styles.mutedSmall}>Available qty</span>
                          <input type="number" style={styles.smallInput} defaultValue={p.available || 0} onBlur={(e) => updateAvailable(p.id, e.target.value)} />
                          <span style={{ ...styles.mutedSmall, color: "#D9720A" }}>Fix a wrong entry directly here</span>
                        </div>
                        <div style={styles.addPaymentRow}>
                          <span style={styles.mutedSmall}>Cost price ₹</span>
                          <input type="number" style={styles.smallInput} defaultValue={p.costPrice || 0} onBlur={(e) => updateCost(p.id, e.target.value)} />
                          <span style={styles.mutedSmall}>MRP ₹</span>
                          <input type="number" style={styles.smallInput} defaultValue={p.mrp || 0} onBlur={(e) => updateMrp(p.id, e.target.value)} />
                        </div>
                        <div style={styles.addPaymentRow}>
                          <input type="number" placeholder="Qty received" value={(receiveForm[p.id] || {}).qty || ""} onChange={(e) => setField(p.id, "qty", e.target.value)} style={styles.smallInput} />
                          <input type="text" placeholder="Company / supplier" value={(receiveForm[p.id] || {}).company || ""} onChange={(e) => setField(p.id, "company", e.target.value)} style={{ ...styles.smallInput, flex: 1 }} />
                          <button style={styles.smallBtn} onClick={() => doReceive(p.id)}>Receive Stock</button>
                        </div>

                        <div style={{ marginTop: 10 }}>
                          <span style={styles.mutedSmall}>Sizes / variants (e.g. 300ml, 500ml, 1000ml)</span>
                          <div style={{ display: "flex", gap: 6, flexWrap: "wrap", margin: "6px 0" }}>
                            {(p.variants || []).map((v) => (
                              <span key={v} style={{ ...styles.photoChip, ...styles.photoChipDone, cursor: "default", display: "flex", alignItems: "center", gap: 6 }}>
                                {v}
                                <span style={{ cursor: "pointer", color: "#E1483C", fontWeight: 700 }} onClick={() => removeVariant(p.id, v)}>✕</span>
                              </span>
                            ))}
                          </div>
                          <div style={styles.addPaymentRow}>
                            <input type="text" placeholder="Add size, e.g. 500ml" style={{ ...styles.smallInput, flex: 1 }}
                              value={variantInput[p.id] || ""} onChange={(e) => setVariantInput((prev) => ({ ...prev, [p.id]: e.target.value }))}
                              onKeyDown={(e) => { if (e.key === "Enter") addVariant(p.id); }} />
                            <button style={styles.smallBtn} onClick={() => addVariant(p.id)}>Add Size</button>
                          </div>
                        </div>

                        <button style={{ ...styles.linkBtn, color: "#E1483C", marginTop: 12 }} onClick={() => remove(p.id)}>Remove Product</button>
                      </div>
                    )}
                  </div>
                  );
                })}
              </div>
            </CollapsibleSection>
          ))}
        </div>
      )}
    </div>
  );
}

// ---------------- Dressers (Owner) ----------------
function DressersTab({ dressers, addDresser, removeDresser, dresserPins, setDresserPin, dresserStats, dresserProfiles, dresserStockAccess, setDresserStockAccess, dresserBusinessAccess, setDresserBusinessAccess, businesses, businessId }) {
  const [name, setName] = useState("");
  const [newPin, setNewPin] = useState("");
  const [pinEdits, setPinEdits] = useState({});
  const [openId, setOpenId] = useState(null);
  const countFor = (n) => (dresserStats.find((d) => d.name.toLowerCase() === n.toLowerCase()) || {}).count || 0;

  const submitAdd = () => {
    if (!name.trim()) return;
    addDresser(name, newPin.trim());
    setName(""); setNewPin("");
  };
  const savePinEdit = (d) => {
    const val = (pinEdits[d] || "").trim();
    if (val && val.length < 4) { alert("PIN should be at least 4 digits"); return; }
    setDresserPin(d, val || undefined);
    setPinEdits((prev) => ({ ...prev, [d]: "" }));
  };
  const businessesForDresser = (d) => {
    const list = (dresserBusinessAccess || {})[d.trim().toLowerCase()];
    return Array.isArray(list) && list.length > 0 ? list : [businessId];
  };
  const toggleBusinessAccess = (d, bId) => {
    const current = businessesForDresser(d);
    const next = current.includes(bId) ? current.filter((x) => x !== bId) : [...current, bId];
    if (next.length === 0) return; // must keep at least one
    setDresserBusinessAccess(d, next);
  };

  return (
    <div>
      <SectionTitle>Add Dresser</SectionTitle>
      <div style={styles.addPaymentRow}>
        <input
          style={{ ...styles.smallInput, flex: 1 }}
          placeholder="Dresser's name"
          value={name}
          onChange={(e) => setName(e.target.value)}
          onKeyDown={(e) => { if (e.key === "Enter") submitAdd(); }}
        />
        <input
          style={{ ...styles.smallInput, width: 90 }}
          placeholder="PIN (4+ digits)"
          inputMode="numeric"
          value={newPin}
          onChange={(e) => setNewPin(e.target.value)}
          onKeyDown={(e) => { if (e.key === "Enter") submitAdd(); }}
        />
        <button style={styles.smallBtn} onClick={submitAdd}>Add</button>
      </div>
      <div style={styles.emptyState2}>Only names added here can log in as a dresser. Give each dresser their own PIN so they can't log in under someone else's name.</div>

      <SectionTitle>Team</SectionTitle>
      {dressers.length === 0 ? (
        <EmptyState text="No dressers added yet." />
      ) : (
        <div style={styles.list}>
          {dressers.map((d) => {
            const open = openId === d;
            return (
            <div key={d} style={styles.card}>
              <div style={styles.cardTop} onClick={() => setOpenId(open ? null : d)}>
                {(dresserProfiles && dresserProfiles[d] && dresserProfiles[d].photo) ? (
                  <img src={dresserProfiles[d].photo} alt={d} style={{ width: 40, height: 40, borderRadius: 10, objectFit: "cover", marginRight: 10 }} />
                ) : (
                  <div style={{ width: 40, height: 40, borderRadius: 10, background: "#FBEAD3", color: "#D9720A", display: "flex", alignItems: "center", justifyContent: "center", fontWeight: 700, marginRight: 10, fontFamily: "'Space Grotesk', sans-serif" }}>
                    {d.charAt(0).toUpperCase()}
                  </div>
                )}
                <div style={{ flex: 1 }}>
                  <div style={styles.cardTitle}>{d}</div>
                  <div style={styles.cardMeta}>{countFor(d)} dressing{countFor(d) === 1 ? "" : "s"} logged{(dresserProfiles && dresserProfiles[d] && dresserProfiles[d].phone) ? ` · ${dresserProfiles[d].phone}` : ""}</div>
                </div>
                <div style={{ display: "flex", flexDirection: "column", alignItems: "flex-end", gap: 6 }}>
                  {dresserPins[d] ? (
                    <span style={{ ...styles.badge, color: "#D9720A", background: "#FBEAD3" }}>PIN protected</span>
                  ) : (
                    <span style={{ ...styles.badge, color: "#E1483C", background: "#FCE7E4" }}>No PIN</span>
                  )}
                  <span style={{ fontSize: 11, color: "#8A9A96" }}>{open ? "▲ hide" : "▼ details"}</span>
                </div>
              </div>
              {open && (
                <div style={{ padding: "0 14px 14px" }}>
                  {(dresserProfiles && dresserProfiles[d] && dresserProfiles[d].bio) && (
                    <div style={{ ...styles.notesText, marginBottom: 10 }}>{dresserProfiles[d].bio}</div>
                  )}
                  {!dresserPins[d] && (
                    <div style={{ ...styles.mutedSmall, color: "#E1483C", marginBottom: 6 }}>Anyone can log in as {d} until a PIN is set.</div>
                  )}
                  <div style={styles.addPaymentRow}>
                    <input type="text" inputMode="numeric" placeholder={dresserPins[d] ? "New PIN (4+ digits)" : "Set PIN (4+ digits)"}
                      style={styles.smallInput} value={pinEdits[d] || ""}
                      onChange={(e) => setPinEdits((prev) => ({ ...prev, [d]: e.target.value }))} />
                    <button style={styles.smallBtn} onClick={() => savePinEdit(d)}>Save PIN</button>
                    {dresserPins[d] && <button style={{ ...styles.linkBtn, color: "#E1483C" }} onClick={() => setDresserPin(d, undefined)}>Clear</button>}
                  </div>
                  <label style={{ display: "flex", alignItems: "center", gap: 8, marginTop: 12, fontSize: 13, cursor: "pointer" }}>
                    <input type="checkbox" checked={!!(dresserStockAccess && dresserStockAccess[d])} onChange={(e) => setDresserStockAccess(d, e.target.checked)} />
                    Can import &amp; manage stock
                  </label>
                  {businesses && businesses.length > 1 && (
                    <div style={{ marginTop: 12 }}>
                      <div style={styles.mutedSmall}>Can access these businesses</div>
                      <div style={{ display: "flex", gap: 6, flexWrap: "wrap", marginTop: 6 }}>
                        {businesses.map((b) => {
                          const has = businessesForDresser(d).includes(b.id);
                          return (
                            <button key={b.id} onClick={() => toggleBusinessAccess(d, b.id)}
                              style={{ ...styles.filterChip, ...(has ? styles.filterChipActive : {}) }}>
                              {b.name}{has ? " ✓" : ""}
                            </button>
                          );
                        })}
                      </div>
                    </div>
                  )}
                  <button style={{ ...styles.linkBtn, color: "#E1483C", marginTop: 12 }} onClick={() => removeDresser(d)}>Remove Dresser</button>
                </div>
              )}
            </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

// ---------------- Reports (Owner) ----------------
function CollapsibleSection({ title, defaultOpen, right, children }) {
  const [open, setOpen] = useState(!!defaultOpen);
  const [busy, setBusy] = useState(false);
  const contentRef = useRef(null);

  const download = async (e) => {
    e.stopPropagation();
    if (!contentRef.current) return;
    setBusy(true);
    try {
      const blob = await quotePdfBlob(contentRef.current);
      const filename = `${title.replace(/[^a-z0-9]+/gi, "-")}.pdf`;
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url; a.download = filename; a.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      alert("Couldn't generate PDF for this section.");
    } finally { setBusy(false); }
  };

  return (
    <div style={{ marginBottom: 4 }}>
      <div onClick={() => setOpen((o) => !o)}
        style={{ ...styles.sectionTitle, cursor: "pointer", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <span>{title}</span>
        <span style={{ display: "flex", alignItems: "center", gap: 10 }}>
          {right}
          {open && (
            <span onClick={download} title="Download this report as PDF"
              style={{ display: "flex", alignItems: "center", color: busy ? "#8A9A96" : "#D9720A", cursor: busy ? "default" : "pointer" }}>
              <Icon name="download" size={15} />
            </span>
          )}
          <span style={{ fontSize: 10 }}>{open ? "▲" : "▼"}</span>
        </span>
      </div>
      {open && <div ref={contentRef}>{children}</div>}
    </div>
  );
}

function weekStartLabel(dateStr) {
  const d = new Date(dateStr);
  const day = d.getDay(); // 0 = Sunday
  const diff = d.getDate() - day; // back to Sunday
  const start = new Date(d);
  start.setDate(diff);
  return start;
}
function pnlPeriodKey(dateStr, granularity) {
  const d = new Date(dateStr);
  if (granularity === "daily") return dateStr;
  if (granularity === "weekly") return weekStartLabel(dateStr).toISOString().slice(0, 10);
  if (granularity === "monthly") return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}`;
  return `${d.getFullYear()}`;
}
function pnlPeriodLabel(key, granularity) {
  if (granularity === "daily") return fmtDate(key);
  if (granularity === "weekly") {
    const start = new Date(key);
    const end = new Date(start); end.setDate(end.getDate() + 6);
    return `${fmtDate(start.toISOString().slice(0, 10))} – ${fmtDate(end.toISOString().slice(0, 10))}`;
  }
  if (granularity === "monthly") {
    const [y, m] = key.split("-");
    return new Date(Number(y), Number(m) - 1, 1).toLocaleDateString("en-IN", { month: "short", year: "numeric" });
  }
  return key;
}

function CollapsibleSubcard({ title, children }) {
  const [open, setOpen] = useState(false);
  return (
    <div style={styles.card}>
      <div style={styles.cardTop} onClick={() => setOpen((o) => !o)}>
        <div style={{ flex: 1 }}><div style={styles.cardTitle}>{title}</div></div>
        <span style={{ fontSize: 11, color: "#8A9A96" }}>{open ? "▲ hide" : "▼ details"}</span>
      </div>
      {open && <div style={{ padding: "0 14px 14px" }}>{children}</div>}
    </div>
  );
}

function SWOTGrid({ swot }) {
  const quadrants = [
    { key: "s", label: "Strengths", color: "#128577", bg: "#E3F3EF" },
    { key: "w", label: "Weaknesses", color: "#E1483C", bg: "#FCE7E4" },
    { key: "o", label: "Opportunities", color: "#3B5BA5", bg: "#E7ECF7" },
    { key: "t", label: "Threats", color: "#D98D2B", bg: "#FBF0DE" },
  ];
  return (
    <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10 }}>
      {quadrants.map((q) => (
        <div key={q.key} style={{ background: q.bg, borderRadius: 12, padding: 12 }}>
          <div style={{ fontWeight: 700, fontSize: 12, color: q.color, marginBottom: 6 }}>{q.label}</div>
          <ul style={{ margin: 0, paddingLeft: 16, fontSize: 12, color: "#182322", lineHeight: 1.5 }}>
            {swot[q.key].map((line, i) => <li key={i}>{line}</li>)}
          </ul>
        </div>
      ))}
    </div>
  );
}

function DoctorCommissionCard({ d, businessName = "Bhagirathi Agency" }) {
  const [open, setOpen] = useState(false);
  const [busy, setBusy] = useState(false);
  const sheetRef = useRef(null);
  const grandTotal = d.months.reduce((s, m) => s + m.total, 0);

  const downloadPdf = async (e) => {
    e.stopPropagation();
    if (!sheetRef.current) return;
    setBusy(true);
    try {
      const blob = await quotePdfBlob(sheetRef.current);
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url; a.download = `Commission-Statement-${d.doctor.replace(/[^a-z0-9]+/gi, "-")}.pdf`; a.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      alert("Couldn't generate PDF.");
    } finally { setBusy(false); }
  };

  return (
    <div style={styles.card}>
      <div style={styles.cardTop} onClick={() => setOpen((o) => !o)}>
        <div style={{ flex: 1 }}>
          <div style={styles.cardTitle}>{d.doctor}</div>
          <div style={styles.cardMeta}>{d.months.length} month{d.months.length > 1 ? "s" : ""} with commission</div>
        </div>
        <div style={{ display: "flex", flexDirection: "column", alignItems: "flex-end", gap: 6 }}>
          <span style={{ fontWeight: 700, color: "#D98D2B" }}>{fmtMoney(grandTotal)}</span>
          <span style={{ fontSize: 11, color: "#8A9A96" }}>{open ? "▲ hide" : "▼ details"}</span>
        </div>
      </div>
      {open && (
        <div style={{ padding: "0 14px 14px" }}>
          <button style={{ ...styles.smallBtn, width: "100%", marginBottom: 12 }} disabled={busy} onClick={downloadPdf}>
            {busy ? "Preparing…" : "Download Commission Statement PDF"}
          </button>
          <div ref={sheetRef} style={styles.quoteSheet}>
            <div style={styles.quoteHeader}>
              <img src="/bhagirathi-logo.png" alt={businessName} style={{ width: 40, height: 40, objectFit: "contain" }} />
              <div>
                <div style={{ fontFamily: "'Space Grotesk', sans-serif", fontWeight: 700, fontSize: 16 }}>{businessName}</div>
                <div style={{ fontSize: 11, color: "#5B6864" }}>Doctor Commission Statement</div>
              </div>
            </div>
            <div style={{ margin: "12px 0", fontSize: 13 }}>
              <strong>Doctor:</strong> {d.doctor}<br />
              <strong>Statement generated:</strong> {fmtDate(todayISO())}
            </div>
            {d.months.map((m) => (
              <div key={m.monthKey} style={{ marginBottom: 14 }}>
                <div style={{ fontWeight: 700, fontSize: 13, borderBottom: "1px solid #DCE4DF", paddingBottom: 4, marginBottom: 4 }}>{m.monthLabel}</div>
                <table style={styles.quoteTable}>
                  <thead><tr><th style={styles.quoteTh}>#</th><th style={styles.quoteTh}>Patient</th><th style={styles.quoteTh}>Date</th><th style={styles.quoteTh}>Amount</th></tr></thead>
                  <tbody>
                    {m.entries.map((e, i) => (
                      <tr key={i}>
                        <td style={styles.quoteTd}>{i + 1}</td>
                        <td style={styles.quoteTd}>{e.patientName}</td>
                        <td style={styles.quoteTd}>{fmtDate(e.date)}</td>
                        <td style={styles.quoteTd}>{fmtMoney(e.amount)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
                <div style={{ textAlign: "right", fontWeight: 700, fontSize: 12, marginTop: 4 }}>Month total: {fmtMoney(m.total)}</div>
              </div>
            ))}
            <div style={{ borderTop: "2px solid #6E0F1A", marginTop: 10, paddingTop: 8, textAlign: "right", fontWeight: 700 }}>
              Grand total payable: {fmtMoney(grandTotal)}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function ReportsTab({ cases, products, dresserStats, dressers, outstandingTotal, overdueCount, lowStock, resetTestData, clearAllOutstanding, doctorCalls, quotations, ownerLogins, businessId, businessName = "Bhagirathi Agency" }) {
  const [locations, setLocations] = useState({});
  const [expanded, setExpanded] = useState(null);

  const dresserNames = useMemo(() => {
    const set = new Set([...(dressers || []), ...dresserStats.map((d) => d.name)]);
    return Array.from(set);
  }, [dressers, dresserStats]);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      const entries = await Promise.all(dresserNames.map(async (name) => {
        const raw = await loadKey(locKey(businessId, name), []);
        const trail = Array.isArray(raw) ? raw : (raw ? [raw] : []); // migrate old single-object format
        return [name, trail];
      }));
      if (!cancelled) setLocations(Object.fromEntries(entries));
    })();
    return () => { cancelled = true; };
  }, [JSON.stringify(dresserNames), businessId]);

  const totalBilled = cases.reduce((s, c) => s + Number(c.totalAmount || 0), 0);
  const totalCollected = cases.reduce((s, c) => s + (c.payments || []).reduce((a, p) => a + Number(p.amount || 0), 0), 0);
  const collectedByMode = useMemo(() => {
    const tally = { Cash: 0, Online: 0, Credit: 0 };
    cases.forEach((c) => (c.payments || []).forEach((p) => { tally[p.mode || "Cash"] = (tally[p.mode || "Cash"] || 0) + Number(p.amount || 0); }));
    return tally;
  }, [cases]);
  const totalProfit = cases.reduce((s, c) => s + estimateProfit(c, products), 0);

  const [pnlGranularity, setPnlGranularity] = useState("monthly");
  const pnlRows = useMemo(() => {
    const tally = {};
    cases.forEach((c) => {
      if (!c.applicationDate) return;
      const key = pnlPeriodKey(c.applicationDate, pnlGranularity);
      if (!tally[key]) tally[key] = { key, revenue: 0, rental: 0, cost: 0, commission: 0, cases: 0 };
      const names = getCaseProducts(c);
      const cost = names.reduce((s, name) => {
        const prod = products.find((p) => p.name === name);
        return s + (prod ? Number(prod.costPrice || 0) : 0);
      }, 0);
      tally[key].revenue += Number(c.totalAmount || 0);
      tally[key].rental += Number(c.machineRentalAmount || 0);
      tally[key].cost += cost;
      tally[key].commission += Number(c.doctorCommission || 0);
      tally[key].cases += 1;
    });
    return Object.values(tally)
      .map((r) => ({ ...r, profit: r.revenue + r.rental - r.cost - r.commission }))
      .sort((a, b) => (a.key < b.key ? 1 : -1));
  }, [cases, products, pnlGranularity]);
  const pnlTotals = useMemo(() => pnlRows.reduce((acc, r) => ({
    revenue: acc.revenue + r.revenue, rental: acc.rental + r.rental, cost: acc.cost + r.cost, commission: acc.commission + r.commission, profit: acc.profit + r.profit,
  }), { revenue: 0, rental: 0, cost: 0, commission: 0, profit: 0 }), [pnlRows]);

  const allReceipts = useMemo(() => {
    const list = [];
    products.forEach((p) => (p.receipts || []).forEach((r) => list.push({ ...r, product: p.name })));
    return list.sort((a, b) => new Date(b.date) - new Date(a.date));
  }, [products]);
  const companyTotals = useMemo(() => {
    const tally = {};
    allReceipts.forEach((r) => { tally[r.company] = (tally[r.company] || 0) + Number(r.qty || 0); });
    return Object.entries(tally).map(([company, qty]) => ({ company, qty })).sort((a, b) => b.qty - a.qty);
  }, [allReceipts]);

  const companyStockSales = useMemo(() => {
    const map = {};
    products.forEach((p) => {
      (p.receipts || []).forEach((r) => {
        const co = (r.company || "Unspecified").trim() || "Unspecified";
        if (!map[co]) map[co] = { company: co, totalReceived: 0, products: {} };
        map[co].totalReceived += Number(r.qty || 0);
        if (!map[co].products[p.name]) {
          map[co].products[p.name] = { name: p.name, received: 0, available: p.available || 0, used: p.used || 0, mrp: p.mrp || 0 };
        }
        map[co].products[p.name].received += Number(r.qty || 0);
      });
    });
    return Object.values(map)
      .map((co) => ({
        ...co,
        estSales: Object.values(co.products).reduce((s, pr) => s + pr.used * pr.mrp, 0),
        productList: Object.values(co.products).sort((a, b) => b.received - a.received),
      }))
      .sort((a, b) => b.totalReceived - a.totalReceived);
  }, [products]);

  const doctorMonthlyStats = useMemo(() => {
    const tally = {};
    cases.forEach((c) => {
      const doctor = (c.doctorName || "Unknown").trim();
      const month = c.applicationDate ? new Date(c.applicationDate).toLocaleDateString("en-IN", { month: "short", year: "numeric" }) : "Unknown";
      const key = doctor + "||" + month;
      if (tally[key] === undefined) tally[key] = { doctor, month, count: 0, sortDate: c.applicationDate || "" };
      tally[key].count += 1;
    });
    return Object.values(tally).sort((a, b) => a.doctor.localeCompare(b.doctor) || new Date(b.sortDate) - new Date(a.sortDate));
  }, [cases]);

  const doctorCommissionStats = useMemo(() => {
    const tally = {};
    cases.forEach((c) => {
      const amt = Number(c.doctorCommission || 0);
      if (amt <= 0) return;
      const doctor = (c.doctorName || "Unknown").trim() || "Unknown";
      if (!tally[doctor]) tally[doctor] = { doctor, total: 0, cases: 0 };
      tally[doctor].total += amt;
      tally[doctor].cases += 1;
    });
    return Object.values(tally).sort((a, b) => b.total - a.total);
  }, [cases]);
  const doctorCommissionTotal = useMemo(() => doctorCommissionStats.reduce((s, d) => s + d.total, 0), [doctorCommissionStats]);

  const doctorCommissionMonthly = useMemo(() => {
    const byDoctor = {};
    cases.forEach((c) => {
      const amt = Number(c.doctorCommission || 0);
      if (amt <= 0) return;
      const doctor = (c.doctorName || "Unknown").trim() || "Unknown";
      const monthKey = c.applicationDate ? `${new Date(c.applicationDate).getFullYear()}-${String(new Date(c.applicationDate).getMonth() + 1).padStart(2, "0")}` : "Unknown";
      const monthLabel = c.applicationDate ? new Date(c.applicationDate).toLocaleDateString("en-IN", { month: "long", year: "numeric" }) : "Unknown";
      if (!byDoctor[doctor]) byDoctor[doctor] = {};
      if (!byDoctor[doctor][monthKey]) byDoctor[doctor][monthKey] = { monthKey, monthLabel, total: 0, entries: [] };
      byDoctor[doctor][monthKey].total += amt;
      byDoctor[doctor][monthKey].entries.push({ patientName: c.patientName, date: c.applicationDate, amount: amt });
    });
    return Object.entries(byDoctor).map(([doctor, months]) => ({
      doctor,
      months: Object.values(months).sort((a, b) => (a.monthKey < b.monthKey ? 1 : -1)),
    })).sort((a, b) => a.doctor.localeCompare(b.doctor));
  }, [cases]);

  const doctorCallsByDresser = useMemo(() => {
    const tally = {};
    (doctorCalls || []).forEach((c) => {
      const d = (c.dresserName || "Unassigned").trim() || "Unassigned";
      tally[d] = (tally[d] || 0) + 1;
    });
    return Object.entries(tally).map(([dresserName, calls]) => ({ dresserName, calls })).sort((a, b) => b.calls - a.calls);
  }, [doctorCalls]);
  const recentDoctorCalls = useMemo(
    () => [...(doctorCalls || [])].sort((a, b) => new Date(b.date) - new Date(a.date)).slice(0, 25),
    [doctorCalls]
  );

  const patientRevenue = useMemo(() => {
    const tally = {};
    cases.forEach((c) => {
      const patient = (c.patientName || "Unknown").trim() || "Unknown";
      const paid = (c.payments || []).reduce((s, p) => s + Number(p.amount || 0), 0);
      if (!tally[patient]) tally[patient] = { patient, revenue: 0, paid: 0, cases: 0 };
      tally[patient].revenue += Number(c.totalAmount || 0) + Number(c.machineRentalAmount || 0);
      tally[patient].paid += paid;
      tally[patient].cases += 1;
    });
    return Object.values(tally)
      .map((r) => ({ ...r, outstanding: Math.max(0, r.revenue - r.paid) }))
      .sort((a, b) => b.revenue - a.revenue);
  }, [cases]);

  const outstandingByPatient = useMemo(() => {
    return cases
      .map((c) => {
        const paid = (c.payments || []).reduce((s, p) => s + Number(p.amount || 0), 0);
        const balance = Math.max(0, Number(c.totalAmount || 0) - paid);
        return { ...c, balance };
      })
      .filter((c) => c.balance > 0)
      .sort((a, b) => b.balance - a.balance);
  }, [cases]);

  const outstandingByHospital = useMemo(() => {
    const tally = {};
    outstandingByPatient
      .filter((c) => c.billTo === "Hospital")
      .forEach((c) => {
        const hospital = (c.hospitalName || "Unnamed Hospital").trim() || "Unnamed Hospital";
        if (!tally[hospital]) tally[hospital] = { hospital, balance: 0, patients: 0 };
        tally[hospital].balance += c.balance;
        tally[hospital].patients += 1;
      });
    return Object.values(tally).sort((a, b) => b.balance - a.balance);
  }, [outstandingByPatient]);

  const rentedCases = useMemo(
    () => cases.filter((c) => Number(c.machineRentalAmount || 0) > 0),
    [cases]
  );
  const rentalTotal = useMemo(() => rentedCases.reduce((s, c) => s + Number(c.machineRentalAmount || 0), 0), [rentedCases]);
  const rentalByDresser = useMemo(() => {
    const tally = {};
    rentedCases.forEach((c) => {
      const d = (c.dresserName || "Unassigned").trim() || "Unassigned";
      tally[d] = (tally[d] || 0) + Number(c.machineRentalAmount || 0);
    });
    return Object.entries(tally).map(([dresserName, amount]) => ({ dresserName, amount })).sort((a, b) => b.amount - a.amount);
  }, [rentedCases]);
  const recentRentals = useMemo(
    () => [...rentedCases].sort((a, b) => new Date(b.applicationDate) - new Date(a.applicationDate)).slice(0, 20),
    [rentedCases]
  );

  const monthlyRevenueTrend = useMemo(() => {
    const tally = {};
    cases.forEach((c) => {
      const month = c.applicationDate ? new Date(c.applicationDate).toLocaleDateString("en-IN", { month: "short", year: "numeric" }) : "Unknown";
      if (!tally[month]) tally[month] = { month, billed: 0, collected: 0, sortDate: c.applicationDate || "" };
      tally[month].billed += Number(c.totalAmount || 0);
      tally[month].collected += (c.payments || []).reduce((s, p) => s + Number(p.amount || 0), 0);
    });
    return Object.values(tally).sort((a, b) => new Date(b.sortDate) - new Date(a.sortDate));
  }, [cases]);

  const overdueCasesList = useMemo(() => {
    return cases
      .filter((c) => c.status === "active" && overdueDays(c) > 0)
      .map((c) => ({ ...c, daysOverdue: overdueDays(c) }))
      .sort((a, b) => b.daysOverdue - a.daysOverdue);
  }, [cases]);

  const businessSWOT = useMemo(() => {
    const s = [], w = [], o = [], t = [];
    const activeCount = cases.filter((c) => c.status === "active").length;
    const totalCases = cases.length;
    const profit = pnlTotals.profit;

    if (totalCases > 0) {
      if (profit > 0) s.push(`Profitable so far: net profit of ${fmtMoney(profit)} across ${totalCases} case${totalCases > 1 ? "s" : ""}.`);
      if (activeCount > 0) s.push(`${activeCount} case${activeCount > 1 ? "s" : ""} currently on active VAC therapy.`);
    } else {
      w.push("No cases logged yet — too early to assess performance.");
    }
    if (dresserStats.length > 1) s.push(`Team of ${dresserStats.length} dressers actively logging dressing changes.`);
    if (lowStock.length === 0 && products.length > 0) s.push("No products currently below the low-stock threshold.");
    if ((doctorCalls || []).length > 0) s.push(`${doctorCalls.length} doctor call${doctorCalls.length > 1 ? "s" : ""} logged — active field outreach.`);
    if (companyStockSales.length > 1) s.push(`Sourcing spread across ${companyStockSales.length} supplier companies, reducing single-supplier dependency.`);

    if (outstandingTotal > 0) w.push(`${fmtMoney(outstandingTotal)} outstanding across patients — collection follow-up needed.`);
    if (lowStock.length > 0) w.push(`${lowStock.length} product${lowStock.length > 1 ? "s" : ""} below reorder level: ${lowStock.map((p) => p.name).join(", ")}.`);
    if (overdueCount > 0) w.push(`${overdueCount} dressing change${overdueCount > 1 ? "s" : ""} overdue right now — risk to continuity of care.`);
    if (profit < 0) w.push(`Operating at a net loss of ${fmtMoney(Math.abs(profit))} for the selected period.`);
    if (dresserStats.length === 1) w.push("Only one dresser logging changes — key-person dependency.");

    const pendingQuotes = (quotations || []).filter((q) => q.status === "sent" || q.status === "draft");
    if (pendingQuotes.length > 0) o.push(`${pendingQuotes.length} quotation${pendingQuotes.length > 1 ? "s" : ""} still pending — follow up to convert into cases.`);
    if (patientRevenue.length > 0) {
      const top = patientRevenue[0];
      if (patientRevenue.length > 1 && top.revenue > (patientRevenue.reduce((s, p) => s + p.revenue, 0) / patientRevenue.length) * 2) {
        o.push(`Revenue concentrated with top patient (${top.patient}) — cross-sell similar cases via referring doctors.`);
      }
    }
    if (doctorCommissionStats.length > 0) o.push(`${doctorCommissionStats[0].doctor} is the top commission-linked referrer — deepen this relationship for more volume.`);
    if (rentedCases.length > 0 && cases.length > rentedCases.length) o.push("Machine rental is being billed on some cases only — check if it can be extended to more.");

    const outstandingConcentration = outstandingByPatient => outstandingByPatient;
    if (outstandingTotal > 0 && cases.length > 0) {
      const outstandingCasesCount = cases.filter((c) => {
        const paid = (c.payments || []).reduce((s, p) => s + Number(p.amount || 0), 0);
        return Number(c.totalAmount || 0) - paid > 0;
      }).length;
      if (outstandingCasesCount / cases.length > 0.3) t.push("Over 30% of cases carry an outstanding balance — cash-flow risk if collections slip further.");
    }
    if (lowStock.some((p) => ["Canister", "Foam"].some((k) => p.name.toLowerCase().includes(k.toLowerCase())))) {
      t.push("Core VAC consumables (canister/foam) running low — risk of therapy disruption if not restocked soon.");
    }
    if (dresserStats.length > 0) {
      const top = dresserStats[0];
      const share = dresserStats.reduce((s, d) => s + d.count, 0);
      if (share > 0 && top.count / share > 0.6) t.push(`${top.name} handles over 60% of all dressing changes — losing them would significantly disrupt operations.`);
    }
    if (s.length === 0) s.push("Not enough data yet to identify clear strengths — keep logging cases.");
    if (o.length === 0) o.push("No standout growth opportunity detected yet from current data.");
    if (t.length === 0) t.push("No major threats detected from current data.");
    return { s, w, o, t };
  }, [cases, products, dresserStats, lowStock, outstandingTotal, overdueCount, doctorCalls, quotations, companyStockSales, patientRevenue, doctorCommissionStats, rentedCases, pnlTotals]);

  const dresserSWOT = useMemo(() => {
    return (dressers || []).map((name) => {
      const theirCases = cases.filter((c) => (c.dresserName || "").trim().toLowerCase() === name.trim().toLowerCase());
      const theirChanges = cases.reduce((sum, c) => sum + (c.dressingChanges || []).filter((e) => (e.dresserName || "").trim().toLowerCase() === name.trim().toLowerCase()).length, 0);
      const theirActive = theirCases.filter((c) => c.status === "active");
      const theirOverdue = theirActive.filter((c) => overdueDays(c) > 0).length;
      const theirOutstanding = theirCases.reduce((sum, c) => {
        const paid = (c.payments || []).reduce((s, p) => s + Number(p.amount || 0), 0);
        return sum + Math.max(0, Number(c.totalAmount || 0) - paid);
      }, 0);
      const theirCalls = (doctorCalls || []).filter((d) => (d.dresserName || "").trim().toLowerCase() === name.trim().toLowerCase()).length;
      const theirQuotes = (quotations || []).filter((q) => (q.createdBy || "").trim().toLowerCase() === name.trim().toLowerCase()).length;

      const s = [], w = [], o = [], t = [];
      if (theirChanges > 0) s.push(`${theirChanges} dressing change${theirChanges > 1 ? "s" : ""} logged.`);
      if (theirCases.length > 0) s.push(`${theirCases.length} case${theirCases.length > 1 ? "s" : ""} handled in total.`);
      if (theirCalls > 0) s.push(`${theirCalls} doctor call${theirCalls > 1 ? "s" : ""} logged — active in field outreach.`);
      if (theirQuotes > 0) s.push(`${theirQuotes} quotation${theirQuotes > 1 ? "s" : ""} created.`);

      if (theirOverdue > 0) w.push(`${theirOverdue} of their active case${theirOverdue > 1 ? "s" : ""} overdue for a dressing change.`);
      if (theirCalls === 0) w.push("No doctor calls logged yet.");
      if (theirCases.length === 0) w.push("No cases assigned/logged yet.");

      if (theirCalls > 0 && theirCases.length > 0) o.push("Existing doctor relationships could be leveraged for more referrals.");
      if (theirQuotes === 0) o.push("Hasn't created any quotations yet — could help with lead conversion.");

      if (theirOutstanding > 0) t.push(`${fmtMoney(theirOutstanding)} outstanding across their cases.`);
      if (theirOverdue > 0) t.push("Overdue changes risk patient complications if not addressed promptly.");

      if (s.length === 0) s.push("No activity logged yet.");
      if (o.length === 0) o.push("No specific opportunity identified from current data.");
      if (t.length === 0) t.push("No notable risk identified from current data.");
      return { name, s, w, o, t };
    });
  }, [dressers, cases, doctorCalls, quotations]);

  const sendSummary = () => {
    let msg = `${businessName} — Daily Summary\n`;
    msg += `Overdue changes: ${overdueCount}\nOutstanding: ${fmtMoney(outstandingTotal)}\n`;
    if (lowStock.length) msg += `Low stock: ${lowStock.map((p) => p.name).join(", ")}\n`;
    window.open(waLink(OWNER_WHATSAPP, msg), "_blank");
  };

  return (
    <div>
      <div style={{ display: "flex", justifyContent: "flex-end", marginBottom: 8 }}>
        <button style={{ ...styles.smallBtn, background: "#3B5BA5" }} onClick={() => window.print()}>Download as PDF</button>
      </div>

      <CollapsibleSection title="SWOT Analysis — Business">
        <SWOTGrid swot={businessSWOT} />
      </CollapsibleSection>

      <CollapsibleSection title="SWOT Analysis — Team (per Dresser)">
        {dresserSWOT.length === 0 ? <EmptyState text="No dressers added yet." /> : (
          <div style={styles.list}>
            {dresserSWOT.map((d) => (
              <CollapsibleSubcard key={d.name} title={d.name}>
                <SWOTGrid swot={d} />
              </CollapsibleSubcard>
            ))}
          </div>
        )}
      </CollapsibleSection>

      <SectionTitle>Revenue</SectionTitle>
      <div style={styles.cardGrid}>
        <div style={styles.reportCard}><div style={styles.statValue}>{fmtMoney(totalBilled)}</div><div style={styles.statLabel}>Total Billed</div></div>
        <div style={styles.reportCard}><div style={{ ...styles.statValue, color: "#D9720A" }}>{fmtMoney(totalCollected)}</div><div style={styles.statLabel}>Total Collected</div></div>
        <div style={styles.reportCard}><div style={{ ...styles.statValue, color: "#E1483C" }}>{fmtMoney(outstandingTotal)}</div><div style={styles.statLabel}>Outstanding</div></div>
        <div style={styles.reportCard}><div style={{ ...styles.statValue, color: "#3B5BA5" }}>{fmtMoney(totalProfit)}</div><div style={styles.statLabel}>Est. Profit</div></div>
      </div>

      <div style={styles.card}>
        {PAY_MODES.map((m) => (
          <div key={m} style={styles.dresserLine}><span style={{ flex: 1, fontWeight: 600 }}>{m}</span><span style={styles.mutedSmall}>{fmtMoney(collectedByMode[m] || 0)}</span></div>
        ))}
      </div>

      <button style={styles.primaryBtn} onClick={sendSummary}>Send Summary on WhatsApp</button>

      <CollapsibleSection title="Profit & Loss Statement" defaultOpen right={<span style={{ fontSize: 12, fontWeight: 700, color: pnlTotals.profit >= 0 ? "#D9720A" : "#E1483C" }}>{fmtMoney(pnlTotals.profit)}</span>}>
        <div style={styles.filterRow}>
          {[["daily", "Daily"], ["weekly", "Weekly"], ["monthly", "Monthly"], ["yearly", "Yearly"]].map(([key, label]) => (
            <button key={key} onClick={() => setPnlGranularity(key)}
              style={{ ...styles.filterChip, ...(pnlGranularity === key ? styles.filterChipActive : {}) }}>{label}</button>
          ))}
        </div>
        {pnlRows.length === 0 ? <EmptyState text="No cases yet to calculate profit & loss." /> : (
          <>
            <div style={styles.cardGrid}>
              <div style={styles.reportCard}><div style={styles.statValue}>{fmtMoney(pnlTotals.revenue + pnlTotals.rental)}</div><div style={styles.statLabel}>Total Revenue</div></div>
              <div style={styles.reportCard}><div style={{ ...styles.statValue, color: "#E1483C" }}>{fmtMoney(pnlTotals.cost + pnlTotals.commission)}</div><div style={styles.statLabel}>Total Cost + Commission</div></div>
              <div style={{ ...styles.reportCard, gridColumn: "1 / -1" }}>
                <div style={{ ...styles.statValue, color: pnlTotals.profit >= 0 ? "#D9720A" : "#E1483C" }}>{fmtMoney(pnlTotals.profit)}</div>
                <div style={styles.statLabel}>Net Profit / Loss</div>
              </div>
            </div>

            <div style={{ ...styles.card, padding: "16px 8px 8px", marginBottom: 12 }}>
              <ResponsiveContainer width="100%" height={200}>
                <LineChart data={[...pnlRows].reverse().map((r) => ({ label: pnlPeriodLabel(r.key, pnlGranularity), Revenue: r.revenue + r.rental, Cost: r.cost + r.commission, Profit: r.profit }))}>
                  <CartesianGrid stroke="#EEF1EC" vertical={false} />
                  <XAxis dataKey="label" tick={{ fontSize: 10, fill: "#8A9A96" }} interval="preserveStartEnd" />
                  <YAxis tick={{ fontSize: 10, fill: "#8A9A96" }} width={40} />
                  <Tooltip formatter={(v) => fmtMoney(v)} contentStyle={{ fontSize: 12, borderRadius: 10, border: "1px solid #E3E7E2" }} />
                  <Legend wrapperStyle={{ fontSize: 11 }} />
                  <Line type="monotone" dataKey="Revenue" stroke="#D9720A" strokeWidth={2} dot={false} />
                  <Line type="monotone" dataKey="Cost" stroke="#E1483C" strokeWidth={2} dot={false} />
                  <Line type="monotone" dataKey="Profit" stroke="#3B5BA5" strokeWidth={2} dot={false} />
                </LineChart>
              </ResponsiveContainer>
            </div>

            <div style={styles.card}>
              {pnlRows.map((r) => (
                <div key={r.key} style={styles.cardExpanded}>
                  <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 4 }}>
                    <span style={{ fontWeight: 700 }}>{pnlPeriodLabel(r.key, pnlGranularity)}</span>
                    <span style={{ fontWeight: 700, color: r.profit >= 0 ? "#D9720A" : "#E1483C" }}>{fmtMoney(r.profit)}</span>
                  </div>
                  <div style={{ display: "flex", gap: 14, fontSize: 12, color: "#5B6864", flexWrap: "wrap" }}>
                    <span>{r.cases} case{r.cases > 1 ? "s" : ""}</span>
                    <span>Revenue {fmtMoney(r.revenue + r.rental)}</span>
                    <span>Cost {fmtMoney(r.cost)}</span>
                    {r.commission > 0 && <span>Commission {fmtMoney(r.commission)}</span>}
                  </div>
                </div>
              ))}
            </div>
          </>
        )}
      </CollapsibleSection>

      <CollapsibleSection title="Stock Overview">
        <div style={styles.card}>
          {products.map((p) => (
            <div key={p.id} style={styles.dresserLine}>
              <span style={{ flex: 1, fontWeight: 600 }}>{p.name}</span>
              <span style={styles.mutedSmall}>{p.available || 0} avail · {p.used || 0} used</span>
            </div>
          ))}
        </div>
      </CollapsibleSection>

      <CollapsibleSection title="Stock Activity Log" right={allReceipts.length > 0 ? <span style={{ fontSize: 12, color: "#8A9A96" }}>{allReceipts.length}</span> : null}>
        <div style={{ ...styles.emptyState2, marginBottom: 8 }}>Every time stock is received or a product is added — by you or by a dresser with stock access — it's logged here with who did it.</div>
        {allReceipts.length === 0 ? <EmptyState text="No stock activity logged yet." /> : (
          <div style={styles.card}>
            {allReceipts.slice(0, 40).map((r) => (
              <div key={r.id} style={styles.dresserLine}>
                <span style={{ flex: 1, fontWeight: 600 }}>{r.product}</span>
                <span style={styles.mutedSmall}>+{r.qty} · {r.company}</span>
                <span style={{ ...styles.mutedSmall, color: "#D9720A", fontWeight: 600 }}>{r.receivedBy || "Owner"}</span>
                <span style={styles.mutedSmall}>{fmtDate(r.date)}{r.time ? ` ${r.time}` : ""}</span>
              </div>
            ))}
          </div>
        )}
      </CollapsibleSection>

      {companyTotals.length > 0 && (
        <CollapsibleSection title="Stock Received by Company">
          <div style={styles.card}>
            {companyTotals.map((c) => (
              <div key={c.company} style={styles.dresserLine}><span style={{ flex: 1, fontWeight: 600 }}>{c.company}</span><span style={styles.mutedSmall}>{c.qty} units</span></div>
            ))}
          </div>
        </CollapsibleSection>
      )}

      {companyStockSales.length > 0 && (
        <CollapsibleSection title="Company-wise Stock & Sales Statement">
          <div style={{ ...styles.emptyState2, marginBottom: 8 }}>Available &amp; used are current stock-wide figures (stock isn't tracked per supplier batch once received). Est. sales = units used × MRP.</div>
          {companyStockSales.map((co) => (
            <div key={co.company} style={{ ...styles.card, marginBottom: 10 }}>
              <div style={{ padding: "12px 14px", borderBottom: "1px solid #EEF1EC", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <span style={{ fontFamily: "'Space Grotesk', sans-serif", fontWeight: 700 }}>{co.company}</span>
                <span style={{ fontSize: 12, fontWeight: 700, color: "#D9720A" }}>Est. sales {fmtMoney(co.estSales)}</span>
              </div>
              {co.productList.map((p) => (
                <div key={p.name} style={styles.dresserLine}>
                  <span style={{ flex: 1, fontWeight: 600 }}>{p.name}</span>
                  <span style={styles.mutedSmall}>Recd {p.received}</span>
                  <span style={styles.mutedSmall}>Avail {p.available}</span>
                  <span style={styles.mutedSmall}>Used {p.used}</span>
                </div>
              ))}
            </div>
          ))}
        </CollapsibleSection>
      )}

      <CollapsibleSection title="Machine Rental Collections" right={rentalTotal > 0 ? <span style={{ fontSize: 12, fontWeight: 700, color: "#D9720A" }}>{fmtMoney(rentalTotal)}</span> : null}>
        {rentedCases.length === 0 ? <EmptyState text="No machine rental amounts logged on any case yet." /> : (
          <>
            <div style={styles.card}>
              {rentalByDresser.map((d) => (
                <div key={d.dresserName} style={styles.dresserLine}><span style={{ flex: 1, fontWeight: 600 }}>{d.dresserName}</span><span style={{ fontWeight: 700, color: "#D9720A" }}>{fmtMoney(d.amount)}</span></div>
              ))}
            </div>
            <div style={{ ...styles.mutedSmall, margin: "10px 0 4px" }}>Recent cases with rental</div>
            <div style={styles.card}>
              {recentRentals.map((c) => (
                <div key={c.id} style={styles.dresserLine}>
                  <span style={{ flex: 1, fontWeight: 600 }}>{c.patientName}</span>
                  <span style={styles.mutedSmall}>{c.machineSerial || "No machine"} · {c.dresserName || "Unassigned"}</span>
                  <span style={styles.mutedSmall}>{fmtDate(c.applicationDate)}</span>
                  <span style={{ fontWeight: 700 }}>{fmtMoney(c.machineRentalAmount)}</span>
                </div>
              ))}
            </div>
          </>
        )}
      </CollapsibleSection>

      <CollapsibleSection title="Dresser Workload">
        {dresserStats.length === 0 ? <EmptyState text="No dressing changes logged yet." /> : (
          <div style={styles.card}>
            {dresserStats.map((d, i) => (
              <div key={d.name} style={styles.dresserLine}><span style={styles.dresserRank}>{i + 1}</span><span style={{ flex: 1, fontWeight: 600 }}>{d.name}</span><span style={styles.mutedSmall}>{d.count} dressings</span></div>
            ))}
          </div>
        )}
      </CollapsibleSection>

      <CollapsibleSection title="Doctor-wise Monthly Cases">
        {doctorMonthlyStats.length === 0 ? <EmptyState text="No cases yet." /> : (
          <div style={styles.card}>
            {doctorMonthlyStats.map((d, i) => (
              <div key={i} style={styles.dresserLine}>
                <span style={{ flex: 1, fontWeight: 600 }}>{d.doctor}</span>
                <span style={styles.mutedSmall}>{d.month}</span>
                <span style={styles.mutedSmall}>{d.count} case{d.count > 1 ? "s" : ""}</span>
              </div>
            ))}
          </div>
        )}
      </CollapsibleSection>

      <CollapsibleSection title="Doctor Commission" defaultOpen={doctorCommissionStats.length > 0}
        right={doctorCommissionTotal > 0 ? <span style={{ fontSize: 12, fontWeight: 700, color: "#D98D2B" }}>{fmtMoney(doctorCommissionTotal)}</span> : null}>
        {doctorCommissionStats.length === 0 ? <EmptyState text="No commission entered on any case yet. Add it in the case form when applicable." /> : (
          <>
            <div style={{ ...styles.card, padding: "16px 8px 8px", marginBottom: 12 }}>
              <ResponsiveContainer width="100%" height={Math.max(160, doctorCommissionStats.length * 34)}>
                <BarChart data={doctorCommissionStats} layout="vertical" margin={{ left: 10, right: 20 }}>
                  <CartesianGrid stroke="#EEF1EC" horizontal={false} />
                  <XAxis type="number" tick={{ fontSize: 10, fill: "#8A9A96" }} />
                  <YAxis type="category" dataKey="doctor" width={90} tick={{ fontSize: 11, fill: "#182322" }} />
                  <Tooltip formatter={(v) => fmtMoney(v)} contentStyle={{ fontSize: 12, borderRadius: 10, border: "1px solid #E3E7E2" }} />
                  <Bar dataKey="total" name="Commission" fill="#D98D2B" radius={[0, 6, 6, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
            <div style={styles.list}>
              {doctorCommissionMonthly.map((d) => (
                <DoctorCommissionCard key={d.doctor} d={d} businessName={businessName} />
              ))}
            </div>
          </>
        )}
      </CollapsibleSection>

      <CollapsibleSection title="Doctor Call Report" defaultOpen={(doctorCalls || []).length > 0}
        right={(doctorCalls || []).length > 0 ? <span style={{ fontSize: 12, fontWeight: 700, color: "#3B5BA5" }}>{doctorCalls.length} calls</span> : null}>
        {(!doctorCalls || doctorCalls.length === 0) ? <EmptyState text="No doctor calls logged by any dresser yet." /> : (
          <>
            {doctorCallsByDresser.length > 1 && (
              <div style={{ ...styles.card, padding: "16px 8px 8px", marginBottom: 12 }}>
                <ResponsiveContainer width="100%" height={Math.max(140, doctorCallsByDresser.length * 34)}>
                  <BarChart data={doctorCallsByDresser} layout="vertical" margin={{ left: 10, right: 20 }}>
                    <CartesianGrid stroke="#EEF1EC" horizontal={false} />
                    <XAxis type="number" allowDecimals={false} tick={{ fontSize: 10, fill: "#8A9A96" }} />
                    <YAxis type="category" dataKey="dresserName" width={90} tick={{ fontSize: 11, fill: "#182322" }} />
                    <Tooltip contentStyle={{ fontSize: 12, borderRadius: 10, border: "1px solid #E3E7E2" }} />
                    <Bar dataKey="calls" name="Calls" fill="#3B5BA5" radius={[0, 6, 6, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            )}
            <div style={styles.list}>
              {recentDoctorCalls.map((c) => (
                <div key={c.id} style={styles.card}>
                  <div style={{ padding: 14 }}>
                    <div style={{ display: "flex", justifyContent: "space-between" }}>
                      <div style={styles.cardTitle}>{c.doctorName}</div>
                      <div style={styles.mutedSmall}>{fmtDate(c.date)}</div>
                    </div>
                    <div style={styles.cardMeta}>{c.speciality || "—"} · {c.doctorMobile || "no number"} · by {c.dresserName || "Unassigned"}</div>
                    {(c.products || []).length > 0 && <div style={{ ...styles.mutedSmall, marginTop: 6 }}>Discussed: {c.products.join(", ")}</div>}
                    {c.notes && <div style={{ ...styles.notesText, marginTop: 6 }}>{c.notes}</div>}
                  </div>
                </div>
              ))}
            </div>
          </>
        )}
      </CollapsibleSection>

      <CollapsibleSection title="Patient-wise Revenue Report">
        {patientRevenue.length === 0 ? <EmptyState text="No cases yet." /> : (
          <>
            <div style={{ ...styles.card, padding: "16px 8px 8px", marginBottom: 12 }}>
              <ResponsiveContainer width="100%" height={Math.max(160, Math.min(patientRevenue.length, 10) * 34)}>
                <BarChart data={patientRevenue.slice(0, 10)} layout="vertical" margin={{ left: 10, right: 20 }}>
                  <CartesianGrid stroke="#EEF1EC" horizontal={false} />
                  <XAxis type="number" tick={{ fontSize: 10, fill: "#8A9A96" }} />
                  <YAxis type="category" dataKey="patient" width={90} tick={{ fontSize: 11, fill: "#182322" }} />
                  <Tooltip formatter={(v) => fmtMoney(v)} contentStyle={{ fontSize: 12, borderRadius: 10, border: "1px solid #E3E7E2" }} />
                  <Bar dataKey="revenue" name="Revenue" fill="#D9720A" radius={[0, 6, 6, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
            <div style={styles.card}>
              {patientRevenue.map((p) => (
                <div key={p.patient} style={styles.cardExpanded}>
                  <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 4 }}>
                    <span style={{ fontWeight: 700 }}>{p.patient}</span>
                    <span style={{ fontWeight: 700, color: "#D9720A" }}>{fmtMoney(p.revenue)}</span>
                  </div>
                  <div style={{ display: "flex", gap: 14, fontSize: 12, color: "#5B6864", flexWrap: "wrap" }}>
                    <span>{p.cases} case{p.cases > 1 ? "s" : ""}</span>
                    <span>Paid {fmtMoney(p.paid)}</span>
                    {p.outstanding > 0 && <span style={{ color: "#E1483C", fontWeight: 600 }}>Outstanding {fmtMoney(p.outstanding)}</span>}
                  </div>
                </div>
              ))}
            </div>
          </>
        )}
      </CollapsibleSection>

      <CollapsibleSection title="Outstanding Payments by Patient" defaultOpen={outstandingByPatient.length > 0}>
        {outstandingByPatient.length === 0 ? <EmptyState text="No outstanding balances. All caught up!" /> : (
          <div style={styles.card}>
            {outstandingByPatient.map((c) => (
              <div key={c.id} style={styles.dresserLine}>
                <span style={{ flex: 1, fontWeight: 600 }}>{c.patientName}</span>
                <span style={styles.mutedSmall}>{fmtDate(c.applicationDate)}</span>
                <span style={{ ...styles.mutedSmall, color: "#E1483C", fontWeight: 600 }}>{fmtMoney(c.balance)}</span>
              </div>
            ))}
          </div>
        )}
      </CollapsibleSection>

      <CollapsibleSection title="Outstanding by Hospital" defaultOpen={outstandingByHospital.length > 0}>
        {outstandingByHospital.length === 0 ? <EmptyState text="No hospital-billed outstanding balances." /> : (
          <div style={styles.card}>
            {outstandingByHospital.map((h) => (
              <div key={h.hospital} style={styles.dresserLine}>
                <span style={{ flex: 1, fontWeight: 600 }}>{h.hospital}</span>
                <span style={styles.mutedSmall}>{h.patients} patient{h.patients > 1 ? "s" : ""}</span>
                <span style={{ ...styles.mutedSmall, color: "#E1483C", fontWeight: 600 }}>{fmtMoney(h.balance)}</span>
              </div>
            ))}
          </div>
        )}
      </CollapsibleSection>

      <CollapsibleSection title="Monthly Revenue Trend">
        {monthlyRevenueTrend.length === 0 ? <EmptyState text="No cases yet." /> : (
          <>
            <div style={{ ...styles.card, padding: "16px 8px 8px", marginBottom: 12 }}>
              <ResponsiveContainer width="100%" height={200}>
                <BarChart data={[...monthlyRevenueTrend].reverse()}>
                  <CartesianGrid stroke="#EEF1EC" vertical={false} />
                  <XAxis dataKey="month" tick={{ fontSize: 10, fill: "#8A9A96" }} />
                  <YAxis tick={{ fontSize: 10, fill: "#8A9A96" }} width={40} />
                  <Tooltip formatter={(v) => fmtMoney(v)} contentStyle={{ fontSize: 12, borderRadius: 10, border: "1px solid #E3E7E2" }} />
                  <Legend wrapperStyle={{ fontSize: 11 }} />
                  <Bar dataKey="billed" name="Billed" fill="#3B5BA5" radius={[4, 4, 0, 0]} />
                  <Bar dataKey="collected" name="Collected" fill="#D9720A" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
            <div style={styles.card}>
              {monthlyRevenueTrend.map((m) => (
                <div key={m.month} style={styles.dresserLine}>
                  <span style={{ flex: 1, fontWeight: 600 }}>{m.month}</span>
                  <span style={styles.mutedSmall}>Billed {fmtMoney(m.billed)}</span>
                  <span style={{ ...styles.mutedSmall, color: "#D9720A" }}>Collected {fmtMoney(m.collected)}</span>
                </div>
              ))}
            </div>
          </>
        )}
      </CollapsibleSection>

      <CollapsibleSection title="Overdue Dressing Changes" defaultOpen={overdueCasesList.length > 0}>
        {overdueCasesList.length === 0 ? <EmptyState text="No overdue cases right now." /> : (
          <div style={styles.card}>
            {overdueCasesList.map((c) => (
              <div key={c.id} style={styles.dresserLine}>
                <span style={{ flex: 1, fontWeight: 600 }}>{c.patientName}</span>
                <span style={styles.mutedSmall}>{c.dresserName || "Unassigned"}</span>
                <span style={{ ...styles.mutedSmall, color: "#E1483C", fontWeight: 600 }}>{c.daysOverdue}d overdue</span>
              </div>
            ))}
          </div>
        )}
      </CollapsibleSection>

      <CollapsibleSection title="Dresser Locations">
        <div style={styles.emptyState2}>Captured on login, on each dressing change, on safety alerts, and roughly every 5 minutes while a dresser has the app open. Stops updating once they close it or lock their phone.</div>
        {dresserNames.length === 0 ? <EmptyState text="No dressers added yet." /> : (
          <div style={styles.list}>
            {dresserNames.map((name) => {
              const trail = (locations[name] || []).slice().sort((a, b) => new Date(b.ts) - new Date(a.ts));
              const latest = trail[0];
              const isOpen = expanded === name;
              return (
                <div key={name} style={styles.card}>
                  <div style={styles.cardTop} onClick={() => setExpanded(isOpen ? null : name)}>
                    <div style={{ flex: 1 }}>
                      <div style={styles.cardTitle}>{name}</div>
                      <div style={styles.cardMeta}>{trail.length} check-in{trail.length === 1 ? "" : "s"} recorded</div>
                    </div>
                    {latest ? (
                      <div style={{ display: "flex", flexDirection: "column", alignItems: "flex-end", gap: 6 }}>
                        <span style={styles.mutedSmall}>{fmtRelative(latest.ts)}</span>
                        <a href={mapsLink(latest.lat, latest.lng)} target="_blank" rel="noreferrer" onClick={(e) => e.stopPropagation()} style={styles.linkBtn}>Map</a>
                    </div>
                  ) : <span style={styles.mutedSmall}>No location yet</span>}
                </div>
                {isOpen && trail.length > 0 && (
                  <div style={styles.cardExpanded}>
                    <div style={styles.detailLabel}>Recent check-ins</div>
                    {trail.slice(0, 15).map((p, i) => (
                      <div key={i} style={styles.paymentLine}>
                        <span>{new Date(p.ts).toLocaleString("en-IN")}</span>
                        <a href={mapsLink(p.lat, p.lng)} target="_blank" rel="noreferrer" style={styles.linkBtn}>Map</a>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
      </CollapsibleSection>

      <CollapsibleSection title="Owner Login Activity" right={ownerLogins && ownerLogins.length > 0 ? <span style={{ fontSize: 12, fontWeight: 700, color: "#5B6864" }}>{ownerLogins.length}</span> : null}>
        <div style={{ ...styles.emptyState2, marginBottom: 8 }}>Every time the owner PIN is entered successfully, it's logged here — date, time, and device/browser used — so you can spot any access you don't recognize.</div>
        {(!ownerLogins || ownerLogins.length === 0) ? <EmptyState text="No login activity recorded yet." /> : (
          <div style={styles.card}>
            {[...ownerLogins].reverse().map((l) => (
              <div key={l.id} style={styles.dresserLine}>
                <span style={{ flex: 1 }}>{fmtDate(l.date)} · {l.time}</span>
                <span style={styles.mutedSmall}>{l.device}</span>
              </div>
            ))}
          </div>
        )}
      </CollapsibleSection>

      <SectionTitle>Danger Zone</SectionTitle>
      <div style={{ ...styles.card, padding: 14, border: "1px solid #FCE7E4", marginBottom: 10 }}>
        <div style={{ fontSize: 13, color: "#5B6864", marginBottom: 10 }}>
          Marks every case's outstanding balance as paid (adds a settling payment entry to each). Case history stays intact — only outstanding drops to zero. Currently outstanding: {fmtMoney(outstandingTotal)}.
        </div>
        <button style={{ ...styles.smallBtn, background: "#E1483C" }} onClick={() => {
          const typed = window.prompt('This will mark ALL outstanding balances as paid. Type "CLEAR" to confirm:');
          if (typed === "CLEAR") clearAllOutstanding();
        }}>Zero Out All Outstanding</button>
      </div>
      <div style={{ ...styles.card, padding: 14, border: "1px solid #FCE7E4" }}>
        <div style={{ fontSize: 13, color: "#5B6864", marginBottom: 10 }}>
          Permanently clears all cases and all stock/products — use this to wipe out testing data before going live. This cannot be undone.
        </div>
        <button style={{ ...styles.smallBtn, background: "#E1483C" }} onClick={() => {
          const typed = window.prompt('This will permanently delete ALL cases and ALL stock/products. Type "RESET" to confirm:');
          if (typed === "RESET") resetTestData();
        }}>Clear All Cases &amp; Stock</button>
      </div>
    </div>
  );
}
// ---------------- styles ----------------
const printStyles = `
@media print {
  header, nav, .no-print { display: none !important; }
  body, .app-root { background: #fff !important; }
  main { max-width: 100% !important; padding: 0 !important; }
}
`;

const fontImport = `
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@500;600&display=swap');
`;

const styles = {
  app: { fontFamily: "'Inter', -apple-system, sans-serif", background: "#FBF6EC", minHeight: "100vh", color: "#182322", paddingBottom: 40 },
  loadingScreen: { minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center", background: "#FBF6EC" },
  loadingText: { fontFamily: "'Space Grotesk', sans-serif", color: "#5B6864", fontWeight: 600 },
  header: { background: "linear-gradient(135deg, #6E0F1A 0%, #D9720A 100%)", padding: "18px 16px", borderRadius: "0 0 20px 20px", boxShadow: "0 8px 24px rgba(14,36,34,0.18)" },
  headerInner: { display: "flex", alignItems: "center", gap: 12, maxWidth: 640, margin: "0 auto" },
  brandMark: { width: 40, height: 40, borderRadius: 12, background: "#fff", display: "flex", alignItems: "center", justifyContent: "center", overflow: "hidden" },
  brandMarkImg: { width: "82%", height: "82%", objectFit: "contain" },
  brandMarkLg: { width: 68, height: 68, borderRadius: 18, objectFit: "contain", margin: "60px auto 14px", cursor: "pointer", boxShadow: "0 8px 20px rgba(14,36,34,0.12)" },
  gateBrand: { textAlign: "center", color: "#6E0F1A", fontFamily: "'Space Grotesk', sans-serif", fontWeight: 700, fontSize: 19 },
  brandName: { color: "#FBF6EC", fontFamily: "'Space Grotesk', sans-serif", fontWeight: 700, fontSize: 16 },
  brandSub: { color: "#EBCB94", fontSize: 12, letterSpacing: 0.2, textAlign: "center" },
  logoutBtn: { display: "inline-flex", alignItems: "center", gap: 5, background: "rgba(255,255,255,0.1)", border: "1px solid rgba(255,255,255,0.22)", color: "#DCEFEA", borderRadius: 20, padding: "6px 12px", fontSize: 11, fontWeight: 600, cursor: "pointer" },
  pinPanel: { maxWidth: 640, margin: "12px auto 0", background: "#fff", borderRadius: 14, padding: 14 },
  gateWrap: { maxWidth: 360, margin: "0 auto", padding: "0 20px", textAlign: "center" },
  gateOptions: { display: "flex", flexDirection: "column", gap: 10, marginTop: 40 },
  gateBtn: { background: "#D9720A", color: "#fff", border: "none", borderRadius: 14, padding: "16px", fontSize: 15, fontWeight: 700, fontFamily: "'Space Grotesk', sans-serif", cursor: "pointer", boxShadow: "0 6px 16px rgba(18,133,119,0.28)" },
  gateBtnAlt: { background: "#fff", color: "#D9720A", border: "1px solid #CFE4DF", boxShadow: "none" },
  gateForm: { display: "flex", flexDirection: "column", gap: 10, marginTop: 30, textAlign: "left" },
  gateHint: { fontSize: 12, color: "#5B6864", textAlign: "center", marginBottom: 6 },
  gateInput: { border: "1px solid #DCE4DF", borderRadius: 12, padding: "12px 14px", fontSize: 15, fontFamily: "inherit", background: "#fff", textAlign: "center" },
  gateError: { color: "#E1483C", fontSize: 12, textAlign: "center" },
  nav: { display: "flex", gap: 6, padding: "10px 16px", maxWidth: 640, margin: "0 auto", overflowX: "auto" },
  navBtn: { display: "inline-flex", alignItems: "center", gap: 6, border: "1px solid #E3E7E2", background: "#fff", color: "#5B6864", padding: "8px 14px", borderRadius: 20, fontSize: 13, fontFamily: "'Space Grotesk', sans-serif", fontWeight: 600, cursor: "pointer", whiteSpace: "nowrap" },
  navBtnActive: { background: "#D9720A", color: "#fff", borderColor: "#D9720A", boxShadow: "0 4px 10px rgba(18,133,119,0.3)" },
  main: { maxWidth: 640, margin: "0 auto", padding: "8px 16px" },
  cardGrid: { display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12, margin: "10px 0 22px" },
  statCard: { textAlign: "left", border: "1px solid", background: "#fff", borderRadius: 16, padding: "16px 14px", cursor: "pointer", boxShadow: "0 1px 2px rgba(14,36,34,0.04), 0 8px 20px rgba(14,36,34,0.05)" },
  reportCard: { textAlign: "left", border: "1px solid #E3E7E2", background: "#fff", borderRadius: 16, padding: "16px 14px", boxShadow: "0 1px 2px rgba(14,36,34,0.04), 0 8px 20px rgba(14,36,34,0.05)" },
  statValue: { fontFamily: "'Space Grotesk', sans-serif", fontSize: 21, fontWeight: 700 },
  statLabel: { fontSize: 12, color: "#5B6864", marginTop: 4 },
  sectionTitle: { fontFamily: "'Space Grotesk', sans-serif", fontWeight: 700, fontSize: 15, color: "#182322", margin: "20px 0 8px" },
  emptyState: { color: "#8A9A96", fontSize: 13, padding: "24px 0", textAlign: "center", border: "1px dashed #DCE4DF", borderRadius: 14 },
  emptyState2: { color: "#8A9A96", fontSize: 11, marginBottom: 8 },
  list: { display: "flex", flexDirection: "column", gap: 10 },
  card: { background: "#fff", border: "1px solid #E3E7E2", borderRadius: 16, overflow: "hidden", boxShadow: "0 1px 2px rgba(14,36,34,0.03)" },
  cardTop: { display: "flex", padding: 14, gap: 10, cursor: "pointer", alignItems: "flex-start" },
  cardTitle: { fontFamily: "'Space Grotesk', sans-serif", fontWeight: 700, fontSize: 15 },
  cardMeta: { fontSize: 12, color: "#5B6864", marginTop: 2 },
  badge: { fontSize: 11, fontWeight: 700, padding: "4px 9px", borderRadius: 20 },
  dueTag: { fontSize: 11, color: "#E1483C", fontWeight: 700 },
  paidTag: { fontSize: 11, color: "#D9720A", fontWeight: 700 },
  overdueTag: { fontSize: 11, color: "#fff", background: "#E1483C", fontWeight: 700, padding: "3px 8px", borderRadius: 20 },
  cardExpanded: { borderTop: "1px solid #EEF1EC", padding: 14 },
  detailGrid: { display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12, marginBottom: 10 },
  detailLabel: { fontSize: 10, color: "#8A9A96", textTransform: "uppercase", letterSpacing: 0.5 },
  detailValue: { fontSize: 14, fontWeight: 600, marginTop: 2 },
  notesBox: { background: "#FBF6EC", borderRadius: 10, padding: 10, marginBottom: 10 },
  notesText: { fontSize: 13, marginTop: 4 },
  paymentsSection: { marginTop: 6 },
  paymentLine: { display: "flex", justifyContent: "space-between", gap: 8, fontSize: 12, padding: "6px 0", borderBottom: "1px solid #EEF1EC" },
  mutedSmall: { fontSize: 12, color: "#8A9A96" },
  addPaymentRow: { display: "flex", gap: 6, marginTop: 10, flexWrap: "wrap" },
  smallInput: { border: "1px solid #DCE4DF", borderRadius: 9, padding: "8px 10px", fontSize: 13, fontFamily: "inherit", minWidth: 90 },
  smallBtn: { background: "#D9720A", color: "#fff", border: "none", borderRadius: 9, padding: "8px 14px", fontSize: 13, fontWeight: 600, cursor: "pointer" },
  actionRow: { display: "flex", gap: 16, marginTop: 12 },
  linkBtn: { background: "none", border: "none", color: "#D9720A", fontSize: 12, fontWeight: 700, cursor: "pointer", padding: 0, textDecoration: "none" },
  filterRow: { display: "flex", gap: 6, flexWrap: "wrap", marginBottom: 10 },
  filterChip: { border: "1px solid #DCE4DF", background: "#fff", color: "#5B6864", padding: "6px 12px", borderRadius: 16, fontSize: 12, cursor: "pointer" },
  filterChipActive: { background: "#6E0F1A", color: "#fff", borderColor: "#6E0F1A" },
  primaryBtn: { background: "#D9720A", color: "#fff", border: "none", borderRadius: 12, padding: "12px 16px", fontSize: 14, fontWeight: 700, fontFamily: "'Space Grotesk', sans-serif", cursor: "pointer", width: "100%", margin: "6px 0 16px", boxShadow: "0 4px 12px rgba(18,133,119,0.25)" },
  secondaryBtn: { background: "#fff", color: "#5B6864", border: "1px solid #DCE4DF", borderRadius: 12, padding: "12px 16px", fontSize: 14, fontWeight: 600, cursor: "pointer", flex: 1 },
  safetyBtn: { background: "#E1483C", color: "#fff", border: "none", borderRadius: 14, padding: "16px", fontSize: 15, fontWeight: 700, fontFamily: "'Space Grotesk', sans-serif", cursor: "pointer", width: "100%", margin: "10px 0 20px", boxShadow: "0 6px 16px rgba(225,72,60,0.3)" },
  formGrid: { display: "flex", flexDirection: "column", gap: 12, marginBottom: 16 },
  field: { display: "flex", flexDirection: "column", gap: 4 },
  fieldLabel: { fontSize: 11, color: "#5B6864", fontWeight: 600, letterSpacing: 0.2 },
  input: { border: "1px solid #DCE4DF", borderRadius: 10, padding: "10px 12px", fontSize: 14, fontFamily: "inherit", background: "#fff" },
  formActions: { display: "flex", gap: 10 },
  dresserLine: { display: "flex", alignItems: "center", gap: 10, padding: "10px 14px", borderBottom: "1px solid #EEF1EC" },
  dresserRank: { fontFamily: "'Space Grotesk', sans-serif", fontWeight: 700, color: "#8A9A96", fontSize: 12, width: 16 },
  photoRow: { display: "flex", gap: 8, flexWrap: "wrap", marginTop: 8 },
  photoChip: { border: "1px solid #DCE4DF", borderRadius: 20, padding: "8px 12px", fontSize: 11, fontWeight: 600, color: "#5B6864", cursor: "pointer", background: "#fff" },
  photoChipDone: { background: "#FBEAD3", color: "#D9720A", borderColor: "#D9720A" },
  photoThumbWrap: { textAlign: "center", width: 90 },
  photoThumb: { width: 90, height: 90, objectFit: "cover", borderRadius: 10, cursor: "pointer", border: "1px solid #DCE4DF" },
  photoThumbEmpty: { width: 90, height: 90, borderRadius: 10, border: "1px dashed #DCE4DF", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 10, color: "#8A9A96", textAlign: "center" },
  quoteSheet: { background: "#fff", border: "1px solid #E3E7E2", borderRadius: 16, padding: 20 },
  quoteHeader: { display: "flex", alignItems: "center", gap: 12, borderBottom: "2px solid #6E0F1A", paddingBottom: 12 },
  quoteTable: { width: "100%", borderCollapse: "collapse", marginTop: 6, fontSize: 12 },
  quoteTh: { textAlign: "left", borderBottom: "1px solid #DCE4DF", padding: "6px 4px", color: "#5B6864", fontWeight: 700 },
  quoteTd: { borderBottom: "1px solid #EEF1EC", padding: "6px 4px", fontFamily: "'JetBrains Mono', monospace", fontSize: 11.5 },
};
