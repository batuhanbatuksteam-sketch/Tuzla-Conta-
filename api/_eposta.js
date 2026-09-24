/**
 * Teklif maili şablonu. "_" ile başladığı için Vercel bunu uç nokta yapmaz.
 *
 * E-posta HTML'i web sayfası gibi yazılamaz: Outlook masaüstü Word motoruyla
 * çizer, flex/grid/harici CSS/SVG/webp tanımaz. Bu yüzden her şey tablo +
 * satır içi stil, görseller jpg/png ve maile gömülü (CID) — "görselleri indir"
 * uyarısına takılmadan ilk açılışta görünür.
 */
const fs = require("fs");
const path = require("path");
const KAT = require("./_katalog.json");

const SITE = "https://www.tuzlaconta.com";
const C = {
  navy: "#162D63", navyLo: "#0E1E45", ink: "#101A2C", mute: "#5B677B", line: "#E3E8F0",
  paper: "#F3F6FA", seal: "#4E9C7F", sealLo: "#2F6B55", steel: "#A6A6A6", studio: "#14171C",
};
const FONT = "font-family:Arial,Helvetica,sans-serif;";

const esc = (s) => String(s == null ? "" : s)
  .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");

const ACIL = {
  "Bugün lazım": { renk: "#D2472F", yazi: "ACİL · BUGÜN LAZIM" },
  "Bu hafta": { renk: "#C98A1B", yazi: "BU HAFTA" },
  "Planlı iş": { renk: C.seal, yazi: "PLANLI İŞ" },
};

function urunBul(slug) {
  return slug && Object.prototype.hasOwnProperty.call(KAT.urunler, slug) ? KAT.urunler[slug] : null;
}

function dnBul(urun, dn) {
  if (!urun || urun.olcu !== "din2576" || !dn) return null;
  const r = KAT.din2576.find((x) => String(x[0]) === String(dn));
  return r ? { dn: r[0], ic: r[1], dis: r[2], merkez: r[3], delik: r[4], adet: r[5] } : null;
}

function gorsel(dosya) {
  const p = path.join(__dirname, "_mail", dosya);
  try { return fs.readFileSync(p); } catch (e) { return null; }
}

// Outlook'ta da dolu renkli çıkan "kurşun geçirmez" buton
function buton(href, yazi, bg, renk) {
  return `<table role="presentation" cellpadding="0" cellspacing="0" border="0" style="display:inline-table;margin:0 8px 8px 0">
<tr><td bgcolor="${bg}" style="background:${bg};border-radius:6px;mso-padding-alt:12px 20px">
<a href="${esc(href)}" style="${FONT}display:inline-block;padding:12px 20px;font-size:14px;font-weight:bold;color:${renk};text-decoration:none;border-radius:6px">${yazi}</a>
</td></tr></table>`;
}

function satir(k, v) {
  if (!v) return "";
  return `<tr><td style="${FONT}padding:9px 0;border-bottom:1px solid ${C.line};font-size:13px;color:${C.mute};width:38%;vertical-align:top">${esc(k)}</td>
<td style="${FONT}padding:9px 0;border-bottom:1px solid ${C.line};font-size:14px;color:${C.ink};font-weight:bold;vertical-align:top">${esc(v)}</td></tr>`;
}

/**
 * a: { ad, firma, tel, urun (slug), dn, adet, olcu, aciliyet, not, tarih }
 * Döner: { subject, html, text, importance, inline: [{cid, ad, tur, veri}] }
 */
function olustur(a) {
  const urun = urunBul(a.urun);
  const olcu = dnBul(urun, a.dn);
  const acil = ACIL[a.aciliyet] || ACIL["Planlı iş"];
  const inline = [];

  const logo = gorsel("_logo.png");
  if (logo) inline.push({ cid: "tc-logo", ad: "tuzla-conta.png", tur: "image/png", veri: logo });
  const foto = urun ? gorsel(a.urun + ".jpg") : null;
  if (foto) inline.push({ cid: "urun-foto", ad: a.urun + ".jpg", tur: "image/jpeg", veri: foto });

  const urunAd = urun ? urun.ad : (a.urun === "emin-degilim" ? "Ürün seçilmedi — yardım istiyor" : "Ürün seçilmedi");
  const telHref = "tel:" + a.tel.replace(/[^\d+]/g, "");
  const waNo = a.tel.replace(/\D/g, "").replace(/^0/, "90");
  const waMetin = `Merhaba ${a.ad}, Tuzla Conta'dan yazıyoruz. ${urun ? urun.ad + " için " : ""}teklif talebinizi aldık.`;
  const waHref = `https://wa.me/${waNo}?text=${encodeURIComponent(waMetin)}`;
  const urunHref = urun ? `${SITE}/urun/${a.urun}.html` : `${SITE}/urunler.html`;
  // "12" -> "12 adet"; "120 metre" olduğu gibi kalır
  const miktar = a.adet ? (/^\d+([.,]\d+)?$/.test(a.adet.trim()) ? a.adet.trim() + " adet" : a.adet.trim()) : "";

  const onbaslik = `${urunAd}${olcu ? " · DN " + olcu.dn : ""} · ${a.ad}${a.firma ? " (" + a.firma + ")" : ""} · ${a.aciliyet}`;

  // --- ürün kartı
  const fotoBlok = foto
    ? `<tr><td bgcolor="${C.studio}" style="background:${C.studio};padding:0;line-height:0;font-size:0">
<img src="cid:urun-foto" width="560" alt="${esc(urunAd)}" style="display:block;width:100%;max-width:560px;height:auto;border:0"></td></tr>`
    : "";
  const urunBlok = `<tr><td style="padding:0 20px">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="border-radius:10px;overflow:hidden;border:1px solid ${C.line}">
${fotoBlok}
<tr><td bgcolor="#FFFFFF" style="background:#FFFFFF;padding:20px 22px 22px">
<div style="${FONT}font-size:11px;letter-spacing:1.4px;text-transform:uppercase;color:${C.seal};font-weight:bold">${esc(urun ? urun.kat : "Teklif")}</div>
<div style="${FONT}font-size:24px;line-height:1.2;color:${C.ink};font-weight:bold;margin-top:6px">${esc(urunAd)}</div>
${urun ? `<div style="${FONT}font-size:14px;line-height:1.5;color:${C.mute};margin-top:8px">${esc(urun.ozet)}</div>` : ""}
</td></tr></table></td></tr>`;

  // --- ölçü
  let olcuBlok = "";
  if (olcu || a.adet) {
    const hucre = (k, v, vurgu) => `<td width="20%" align="center" style="${FONT}padding:14px 4px;border-right:1px solid ${C.line}">
<div style="font-size:20px;font-weight:bold;color:${vurgu ? C.navy : C.ink}">${esc(v)}</div>
<div style="font-size:11px;color:${C.mute};margin-top:4px">${esc(k)}</div></td>`;
    olcuBlok = `<tr><td style="padding:22px 20px 0">
<div style="${FONT}font-size:11px;letter-spacing:1.4px;text-transform:uppercase;color:${C.mute};font-weight:bold;margin-bottom:10px">
${olcu ? `Standart ölçü · DIN 2576 PN16 · <span style="color:${C.navy}">DN ${esc(olcu.dn)}</span>` : "Miktar"}${miktar ? ` · <span style="color:${C.navy}">${esc(miktar)}</span>` : ""}</div>
${olcu ? `<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" style="background:${C.paper};border-radius:10px;border:1px solid ${C.line}">
<tr>${hucre("İç çap", olcu.ic, true)}${hucre("Dış çap", olcu.dis, true)}${hucre("Delik merkezi", olcu.merkez)}${hucre("Delik çapı", olcu.delik)}
<td width="20%" align="center" style="${FONT}padding:14px 4px"><div style="font-size:20px;font-weight:bold;color:${C.ink}">${esc(olcu.adet)}</div><div style="font-size:11px;color:${C.mute};margin-top:4px">Delik adedi</div></td></tr>
</table>
<div style="${FONT}font-size:11px;color:${C.mute};margin-top:6px">Ölçüler milimetredir.</div>` : ""}
</td></tr>`;
  }

  // --- müşteri notu
  const notBlok = (a.olcu || a.not) ? `<tr><td style="padding:22px 20px 0">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"><tr>
<td width="4" bgcolor="${C.seal}" style="background:${C.seal};border-radius:2px"></td>
<td style="${FONT}padding:4px 0 4px 16px">
<div style="font-size:11px;letter-spacing:1.4px;text-transform:uppercase;color:${C.mute};font-weight:bold">Müşterinin yazdığı</div>
${a.olcu ? `<div style="font-size:15px;line-height:1.55;color:${C.ink};margin-top:6px;white-space:pre-line">${esc(a.olcu)}</div>` : ""}
${a.not ? `<div style="font-size:14px;line-height:1.5;color:${C.mute};margin-top:8px"><b style="color:${C.ink}">Not:</b> ${esc(a.not)}</div>` : ""}
</td></tr></table></td></tr>` : "";

  // --- teknik
  const teknikBlok = urun && urun.teknik && urun.teknik.length ? `<tr><td style="padding:26px 20px 0">
<div style="${FONT}font-size:11px;letter-spacing:1.4px;text-transform:uppercase;color:${C.mute};font-weight:bold;margin-bottom:4px">Ürünün teknik bilgileri</div>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">${urun.teknik.map(([k, v]) => satir(k, v)).join("")}</table>
</td></tr>` : "";

  const html = `<!doctype html>
<html lang="tr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="color-scheme" content="light only"><meta name="supported-color-schemes" content="light">
<title>${esc(onbaslik)}</title></head>
<body style="margin:0;padding:0;background:${C.paper}">
<div style="display:none;max-height:0;overflow:hidden;opacity:0;color:${C.paper}">${esc(onbaslik)}</div>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" bgcolor="${C.paper}" style="background:${C.paper}">
<tr><td align="center" style="padding:24px 12px">
<table role="presentation" width="600" cellpadding="0" cellspacing="0" border="0" style="width:100%;max-width:600px;background:#FFFFFF;border-radius:14px;overflow:hidden">

<tr><td bgcolor="${C.navy}" style="background:${C.navy};padding:22px 24px">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"><tr>
<td valign="middle" style="line-height:0">${logo ? `<img src="cid:tc-logo" width="60" height="32" alt="TC" style="display:inline-block;vertical-align:middle;border:0">` : ""}
<span style="${FONT}display:inline-block;vertical-align:middle;margin-left:12px;line-height:1.2">
<span style="font-size:13px;letter-spacing:3px;color:#FFFFFF;font-weight:bold">TUZLA CONTA</span><br>
<span style="font-size:9px;letter-spacing:3.4px;color:${C.steel};font-weight:bold">SIZDIRMAZLIK</span></span></td>
<td align="right" valign="middle" style="${FONT}font-size:12px;color:#C9D2E3">${esc(a.tarih)}</td>
</tr></table></td></tr>

<tr><td style="padding:26px 24px 18px">
<table role="presentation" cellpadding="0" cellspacing="0" border="0"><tr>
<td bgcolor="${acil.renk}" style="background:${acil.renk};border-radius:99px;${FONT}font-size:11px;font-weight:bold;letter-spacing:1.2px;color:#FFFFFF;padding:6px 12px">${acil.yazi}</td>
</tr></table>
<div style="${FONT}font-size:28px;line-height:1.15;color:${C.ink};font-weight:bold;margin-top:14px">Yeni teklif talebi</div>
<div style="${FONT}font-size:15px;line-height:1.5;color:${C.mute};margin-top:6px"><b style="color:${C.ink}">${esc(a.ad)}</b>${a.firma ? ` · ${esc(a.firma)}` : ""} web sitesinden teklif istedi.</div>
</td></tr>

${urunBlok}
${olcuBlok}
${notBlok}

<tr><td style="padding:26px 20px 0">
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" bgcolor="${C.navy}" style="background:${C.navy};border-radius:12px">
<tr><td style="padding:20px 22px">
<div style="${FONT}font-size:11px;letter-spacing:1.4px;text-transform:uppercase;color:#9FB0CF;font-weight:bold">Müşteri</div>
<div style="${FONT}font-size:20px;color:#FFFFFF;font-weight:bold;margin-top:6px">${esc(a.ad)}</div>
${a.firma ? `<div style="${FONT}font-size:14px;color:#C9D2E3;margin-top:2px">${esc(a.firma)}</div>` : ""}
<div style="${FONT}font-size:18px;color:#FFFFFF;margin-top:10px;letter-spacing:.5px"><a href="${esc(telHref)}" style="color:#FFFFFF;text-decoration:none">${esc(a.tel)}</a></div>
<div style="margin-top:16px">${buton(telHref, "Hemen ara", "#FFFFFF", C.navy)}${buton(waHref, "WhatsApp'tan yaz", "#25D366", "#FFFFFF")}${buton(urunHref, urun ? "Ürün sayfası" : "Ürünler", C.navyLo, "#FFFFFF")}</div>
</td></tr></table></td></tr>

${teknikBlok}

<tr><td style="padding:28px 24px 26px">
<div style="${FONT}font-size:12px;line-height:1.6;color:${C.mute};border-top:1px solid ${C.line};padding-top:16px">
Bu talep <a href="${SITE}" style="color:${C.navy};text-decoration:none;font-weight:bold">tuzlaconta.com</a> teklif formundan geldi.
Müşteriye dönüş için telefon veya WhatsApp kullanın; formda e-posta adresi istenmiyor.</div>
</td></tr>

</table></td></tr></table></body></html>`;

  const text = [
    "Yeni teklif talebi — tuzlaconta.com",
    "",
    "Aciliyet: " + a.aciliyet,
    "Ürün: " + urunAd + (urun ? " (" + urun.kat + ")" : ""),
    olcu ? `Standart ölçü: DN ${olcu.dn} — iç ${olcu.ic}, dış ${olcu.dis}, delik merkezi ${olcu.merkez}, delik çapı ${olcu.delik}, delik adedi ${olcu.adet} (mm)` : "",
    miktar ? "Miktar: " + miktar : "",
    a.olcu ? "Ölçü / açıklama: " + a.olcu : "",
    a.not ? "Not: " + a.not : "",
    "",
    "Ad soyad: " + a.ad,
    a.firma ? "Firma: " + a.firma : "",
    "Telefon: " + a.tel,
    "Tarih: " + a.tarih,
  ].filter((x) => x !== "").join("\n");

  const subject = `Teklif talebi · ${urunAd}${olcu ? " DN " + olcu.dn : ""} · ${a.ad}`;
  return { subject, html, text, importance: a.aciliyet === "Bugün lazım" ? "high" : "normal", inline };
}

module.exports = { olustur, urunBul };
