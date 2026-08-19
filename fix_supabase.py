path = "src/App.jsx"
with open(path, "r") as f:
    content = f.read()

old = '''async function loadKey(key, fallback) {
  try {
    const raw = window.localStorage.getItem(key);
    return raw !== null ? JSON.parse(raw) : fallback;
  } catch (e) {
    return fallback;
  }
}
async function saveKey(key, value) {
  try {
    window.localStorage.setItem(key, JSON.stringify(value));
  } catch (e) {
    console.error("save failed", key, e);
  }
}'''

new = '''import { createClient } from "@supabase/supabase-js";

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
}'''

if old not in content:
    print("OLD BLOCK NOT FOUND")
else:
    content = content.replace(old, new)
    with open(path, "w") as f:
        f.write(content)
    print("FIXED")
