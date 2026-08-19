import re

path = "src/App.jsx"
with open(path, "r") as f:
    content = f.read()

old = '''async function loadKey(key, fallback) {
  try {
    const res = await window.storage.get(key, true);
    return res ? JSON.parse(res.value) : fallback;
  } catch (e) {
    return fallback;
  }
}
async function saveKey(key, value) {
  try {
    await window.storage.set(key, JSON.stringify(value), true);
  } catch (e) {
    console.error("save failed", key, e);
  }
}'''

new = '''async function loadKey(key, fallback) {
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

if old not in content:
    print("OLD BLOCK NOT FOUND — no changes made. Paste me your loadKey/saveKey lines again.")
else:
    content = content.replace(old, new)
    with open(path, "w") as f:
python3 fix_pin.py
npm run build
git add -A
git commit -m "Fix owner PIN not persisting - was using artifact-only window.storage API"
