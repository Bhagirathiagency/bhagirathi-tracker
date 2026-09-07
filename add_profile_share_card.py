edits = []

def apply(label, old, new):
    edits.append((label, old, new))

apply("Pass businessName to DresserProfileForm",
'''          <DresserProfileForm name={name} profile={profile} setDresserProfile={setDresserProfile} />''',
'''          <DresserProfileForm name={name} profile={profile} setDresserProfile={setDresserProfile} businessName={business.name} />''')

apply("Add shareable profile card and share logic",
'''function DresserProfileForm({ name, profile, setDresserProfile }) {
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
    <div>''',
'''function DresserProfileForm({ name, profile, setDresserProfile, businessName = "Bhagirathi Agency" }) {
  const [phone, setPhone] = useState((profile && profile.phone) || "");
  const [bio, setBio] = useState((profile && profile.bio) || "");
  const [uploading, setUploading] = useState(false);
  const [sharing, setSharing] = useState(false);
  const cardRef = useRef(null);
  const photo = profile && profile.photo;
  const profileComplete = photo && phone.trim();

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

  const shareProfileCard = async () => {
    if (!cardRef.current) return;
    setSharing(true);
    try {
      const canvas = await html2canvas(cardRef.current, { scale: 2, backgroundColor: "#ffffff", useCORS: true });
      const blob = await new Promise((resolve) => canvas.toBlob(resolve, "image/png"));
      const file = new File([blob], `${name.replace(/\\s+/g, "_")}_Profile.png`, { type: "image/png" });
      const shareText = `${name} — ${businessName}\\nWound Care Field Dresser`;
      if (navigator.canShare && navigator.canShare({ files: [file] })) {
        await navigator.share({ files: [file], title: `${name}'s Profile`, text: shareText });
      } else {
        const url = URL.createObjectURL(file);
        const a = document.createElement("a");
        a.href = url; a.download = file.name; a.click();
        URL.revokeObjectURL(url);
        alert("Profile card image downloaded — attach it manually in WhatsApp.");
      }
    } catch (e) { console.error(e); }
    setSharing(false);
  };

  return (
    <div>
      {profileComplete && (
        <div style={{ position: "fixed", left: -9999, top: 0 }}>
          <div ref={cardRef} style={{ width: 360, padding: 28, background: "linear-gradient(160deg, #E7F1EF 0%, #FFFFFF 60%)", fontFamily: "'Space Grotesk', sans-serif" }}>
            <div style={{ fontSize: 12, fontWeight: 700, letterSpacing: 1, color: "#3B5BA5", textTransform: "uppercase", marginBottom: 4 }}>{businessName}</div>
            <div style={{ fontSize: 11, color: "#8A9A96", marginBottom: 18 }}>Wound Care Field Dresser</div>
            <div style={{ display: "flex", justifyContent: "center", marginBottom: 16 }}>
              <img src={photo} alt={name} style={{ width: 120, height: 120, borderRadius: 24, objectFit: "cover", border: "4px solid #FFFFFF", boxShadow: "0 6px 18px rgba(27,107,99,0.25)" }} />
            </div>
            <div style={{ textAlign: "center", fontSize: 22, fontWeight: 700, color: "#0E2422", marginBottom: 4 }}>{name}</div>
            {phone && <div style={{ textAlign: "center", fontSize: 13, color: "#3B5BA5", fontWeight: 600, marginBottom: 10 }}>📞 {phone}</div>}
            {bio && <div style={{ textAlign: "center", fontSize: 12, color: "#5B6864", lineHeight: 1.5, padding: "0 8px" }}>{bio}</div>}
            <div style={{ marginTop: 22, paddingTop: 14, borderTop: "1px solid #D9E4E0", textAlign: "center", fontSize: 10, color: "#8A9A96" }}>Verified team member — {businessName}</div>
          </div>
        </div>
      )}''')

apply("Add Share Profile Card button",
'''      <button style={styles.smallBtn} onClick={save}>Save Profile</button>''',
'''      <button style={styles.smallBtn} onClick={save}>Save Profile</button>
      {profileComplete && (
        <button style={{ ...styles.smallBtn, marginTop: 8, background: "#3B5BA5" }} onClick={shareProfileCard} disabled={sharing}>
          {sharing ? "Preparing…" : "📇 Share My Profile Card"}
        </button>
      )}''')

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
