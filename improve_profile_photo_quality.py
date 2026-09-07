edits = []

def apply(label, old, new):
    edits.append((label, old, new))

apply("Add compressProfilePhoto function",
'''function compressImage(file) {
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
}''',
'''function compressImage(file) {
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
// Only ever one photo per dresser, so we can afford much higher quality than case photos.
function compressProfilePhoto(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = (e) => {
      const img = new Image();
      img.onload = () => {
        const maxW = 1000;
        const scale = Math.min(1, maxW / img.width);
        const canvas = document.createElement("canvas");
        canvas.width = Math.round(img.width * scale);
        canvas.height = Math.round(img.height * scale);
        const ctx = canvas.getContext("2d");
        ctx.imageSmoothingQuality = "high";
        ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
        resolve(canvas.toDataURL("image/jpeg", 0.92));
      };
      img.onerror = reject;
      img.src = e.target.result;
    };
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });
}''')

apply("Use compressProfilePhoto for profile photo upload",
'''  const handlePhoto = async (file) => {
    if (!file) return;
    setUploading(true);
    try {
      const dataURL = await compressImage(file);
      setDresserProfile(name, { photo: dataURL });
    } catch (e) { console.error(e); }
    setUploading(false);
  };''',
'''  const handlePhoto = async (file) => {
    if (!file) return;
    setUploading(true);
    try {
      const dataURL = await compressProfilePhoto(file);
      setDresserProfile(name, { photo: dataURL });
    } catch (e) { console.error(e); }
    setUploading(false);
  };''')

apply("Add polish filter to profile card image",
'''            <img src={photo} alt={name} style={{ width: 120, height: 120, borderRadius: 24, objectFit: "cover", border: "4px solid #FFFFFF", boxShadow: "0 6px 18px rgba(27,107,99,0.25)" }} />''',
'''            <img src={photo} alt={name} style={{ width: 120, height: 120, borderRadius: 24, objectFit: "cover", border: "4px solid #FFFFFF", boxShadow: "0 6px 18px rgba(27,107,99,0.25)", filter: "contrast(1.08) saturate(1.12) brightness(1.03)" }} />''')

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
