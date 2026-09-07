edits = []

def apply(label, old, new):
    edits.append((label, old, new))

apply("Make saveKey queue failed writes for offline retry",
'''async function saveKey(key, value) {
  try {
    await supabase
      .from("app_kv")
      .upsert({ key, value, updated_at: new Date().toISOString() });
  } catch (e) {
    console.error("save failed", key, e);
  }
}''',
'''function getOfflineQueue() {
  try { return JSON.parse(localStorage.getItem("wca-offline-queue") || "{}"); } catch (e) { return {}; }
}
function setOfflineQueue(q) {
  try { localStorage.setItem("wca-offline-queue", JSON.stringify(q)); } catch (e) {}
}
async function saveKey(key, value) {
  try {
    await supabase
      .from("app_kv")
      .upsert({ key, value, updated_at: new Date().toISOString() });
    const q = getOfflineQueue();
    if (q[key]) { delete q[key]; setOfflineQueue(q); }
  } catch (e) {
    console.error("save failed — queued for retry when back online", key, e);
    const q = getOfflineQueue();
    q[key] = { value, ts: Date.now() };
    setOfflineQueue(q);
  }
}
async function flushOfflineQueue() {
  const q = getOfflineQueue();
  const keys = Object.keys(q);
  if (keys.length === 0) return { synced: 0, remaining: 0 };
  let synced = 0;
  for (const key of keys) {
    try {
      await supabase.from("app_kv").upsert({ key, value: q[key].value, updated_at: new Date().toISOString() });
      delete q[key];
      synced++;
    } catch (e) { /* still failing — leave queued, will retry again later */ }
  }
  setOfflineQueue(q);
  return { synced, remaining: Object.keys(q).length };
}''')

apply("Add online/offline detection state and auto-sync effect",
'''  const [loaded, setLoaded] = useState(false);
  const [dresserBusinessAccess, setDresserBusinessAccessState] = useState({});
  const [businessAccessLoaded, setBusinessAccessLoaded] = useState(false);''',
'''  const [loaded, setLoaded] = useState(false);
  const [dresserBusinessAccess, setDresserBusinessAccessState] = useState({});
  const [businessAccessLoaded, setBusinessAccessLoaded] = useState(false);

  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [pendingSyncCount, setPendingSyncCount] = useState(() => Object.keys(getOfflineQueue()).length);
  const [justSynced, setJustSynced] = useState(false);

  useEffect(() => {
    const trySync = async () => {
      if (!navigator.onLine) { setIsOnline(false); return; }
      setIsOnline(true);
      const { synced, remaining } = await flushOfflineQueue();
      setPendingSyncCount(remaining);
      if (synced > 0) { setJustSynced(true); setTimeout(() => setJustSynced(false), 3000); }
    };
    const onOnline = () => trySync();
    const onOffline = () => setIsOnline(false);
    window.addEventListener("online", onOnline);
    window.addEventListener("offline", onOffline);
    trySync();
    const syncInterval = setInterval(trySync, 20000); // retry periodically in case the offline event doesn't fire
    const badgeInterval = setInterval(() => setPendingSyncCount(Object.keys(getOfflineQueue()).length), 4000); // keep the count badge fresh
    return () => {
      window.removeEventListener("online", onOnline);
      window.removeEventListener("offline", onOffline);
      clearInterval(syncInterval);
      clearInterval(badgeInterval);
    };
  }, []);''')

apply("Add offline/sync status banner",
'''  return (
    <div style={styles.app}>
      <style>{fontImport}</style>
      <style>{`@keyframes wca-spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } } .wca-spinning { animation: wca-spin 0.7s linear infinite; display: inline-flex; }`}</style>
      <style>{printStyles}</style>
      {activityToast && (''',
'''  return (
    <div style={styles.app}>
      <style>{fontImport}</style>
      <style>{`@keyframes wca-spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } } .wca-spinning { animation: wca-spin 0.7s linear infinite; display: inline-flex; }`}</style>
      <style>{printStyles}</style>
      {(!isOnline || pendingSyncCount > 0 || justSynced) && (
        <div style={{
          position: "fixed", top: 0, left: 0, right: 0, zIndex: 1000,
          padding: "8px 16px", textAlign: "center", fontSize: 12, fontWeight: 700,
          background: justSynced ? "#128577" : !isOnline ? "#E1483C" : "#D98D2B",
          color: "#FFFFFF",
        }}>
          {justSynced
            ? "✓ Back online — your saved changes have synced"
            : !isOnline
              ? `📴 Offline — your work is being saved on this device${pendingSyncCount > 0 ? ` (${pendingSyncCount} waiting to sync)` : ""}, will sync automatically once you're back online`
              : `⏳ Syncing ${pendingSyncCount} saved change${pendingSyncCount > 1 ? "s" : ""}…`}
        </div>
      )}
      {activityToast && (''')

with open('src/App.jsx', 'r') as f:
    content = f.read()

all_ok = True
for label, old, new in edits:
    c = content.count(old)
    print(label, "matches:", c)
    if c != 1:
        all_ok = False
    else:
        content = content.replace(old, new, 1)

if all_ok:
    with open('src/App.jsx', 'w') as f:
        f.write(content)
    print("ALL_APPLIED_OK")
else:
    print("SOME_MISMATCHES_FILE_NOT_CHANGED")
