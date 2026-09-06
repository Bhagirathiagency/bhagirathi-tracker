import nodemailer from "nodemailer";

// Sends the quotation PDF from bhagirathiagency@gmail.com using a Gmail App Password.
// Required Vercel env vars (Project Settings -> Environment Variables):
//   GMAIL_USER            = bhagirathiagency@gmail.com
//   GMAIL_APP_PASSWORD    = 16-character Google App Password (not the normal Gmail password)

export const config = {
  api: {
    bodyParser: { sizeLimit: "10mb" },
  },
};

export default async function handler(req, res) {
  if (req.method !== "POST") {
    res.status(405).json({ error: "Method not allowed" });
    return;
  }

  const { to, subject, text, pdfBase64, filename } = req.body || {};

  if (!to || !pdfBase64) {
    res.status(400).json({ error: "Missing 'to' or 'pdfBase64'" });
    return;
  }

  const user = process.env.GMAIL_USER;
  const pass = process.env.GMAIL_APP_PASSWORD;

  if (!user || !pass) {
    res.status(500).json({ error: "Email sending is not configured yet (missing GMAIL_USER / GMAIL_APP_PASSWORD env vars in Vercel)." });
    return;
  }

  try {
    const transporter = nodemailer.createTransport({
      service: "gmail",
      auth: { user, pass },
    });

    await transporter.sendMail({
      from: `"Bhagirathi Agency" <${user}>`,
      to,
      subject: subject || "Quotation from Bhagirathi Agency",
      text: text || "",
      attachments: [
        {
          filename: filename || "quotation.pdf",
          content: Buffer.from(pdfBase64, "base64"),
          contentType: "application/pdf",
        },
      ],
    });

    res.status(200).json({ ok: true });
  } catch (err) {
    console.error("send-quote-email error:", err);
    res.status(500).json({ error: err.message || "Failed to send email" });
  }
}
