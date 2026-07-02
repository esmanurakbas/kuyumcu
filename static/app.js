
const state = {
  view: "dashboard",
  search: "",
  cariFilter: "all",
  hurdaKayitFilter: "all",
  hurdaScrollToRecords: false,
  stokFilter: "normal",
  selectedPurchase: null,
  selectedHurdaPurchase: null,
  suggestions: { products: ["B\u0130LEZ\u0130K", "Y\u00dcZ\u00dcK", "KOLYE", "K\u00dcPE", "SET", "\u00c7EYREK", "YARIM", "TAM", "GRAM ALTIN", "D\u0130\u011eER"], customers: [], suppliers: [], people: [] },
};

const views = {
  dashboard: { title: "Dashboard", subtitle: "G\u00fcncel stok, cari ve sat\u0131\u015f \u00f6zeti" },
  alis: { title: "Al\u0131\u015f", subtitle: "Normal \u00fcr\u00fcn al\u0131\u015f kay\u0131tlar\u0131" },
  satis: { title: "Sat\u0131\u015f", subtitle: "Al\u0131\u015ftan se\u00e7erek sat\u0131\u015f" },
  hurda: { title: "Hurda", subtitle: "Ayr\u0131 hurda al\u0131\u015f ve sat\u0131\u015f sistemi" },
  stok: { title: "Stok", subtitle: "Normal stok ve hurda stok ayr\u0131" },
  cari: { title: "Cari", subtitle: "M\u00fc\u015fteri ve tedarik\u00e7i bakiyeleri" },
};

const forms = {
  alis: [
    ["tarih", "Tarih", "date"], ["tedarikci", "Tedarik\u00e7i", "autocomplete", "suppliers"],
    ["cinsi", "Cinsi", "autocomplete", "products"], ["ayar", "Ayar", "text"],
    ["adet", "Adet", "number"], ["gram", "Gram", "decimal"], ["milyem", "Al\u0131\u015f Milyem", "decimal"],
    ["notlar", "Not", "textarea"],
  ],
  satis: [
    ["purchase_id", "", "hidden"], ["alis_id", "", "hidden"],
    ["tarih", "Tarih", "date"], ["musteri", "M\u00fc\u015fteri", "autocomplete", "customers"],
    ["cinsi", "Cinsi", "text", null, true], ["ayar", "Ayar", "text", null, true],
    ["alis_milyem", "Al\u0131\u015f Milyem", "decimal", null, true],
    ["adet", "Sat\u0131\u015f Adet", "number"], ["gram", "Sat\u0131\u015f Gram", "decimal"], ["satis_milyem", "Sat\u0131\u015f Milyem", "decimal"],
    ["notlar", "Not", "textarea"],
  ],
  hurda: [
    ["hurda_alis_id", "", "hidden"], ["tarih", "Tarih", "date"], ["islem_turu", "\u0130\u015flem T\u00fcr\u00fc", "select", ["ALI\u015e", "SATI\u015e"]],
    ["kisi", "Ki\u015fi / Firma", "autocomplete", "people"], ["cinsi", "Cinsi", "text"], ["ayar", "Ayar", "text"],
    ["adet", "Adet", "number"], ["gram", "Gram", "decimal"], ["milyem", "Milyem", "decimal"],
    ["notlar", "Not", "textarea"],
  ],
};

const columns = {
  alis: ["tarih", "tedarikci", "cinsi", "ayar", "adet", "gram", "milyem", "has", "not"],
  satis: ["tarih", "musteri", "cinsi", "ayar", "adet", "gram", "alis_milyem", "satis_milyem", "milyem_farki", "milyem_kari", "not"],
  hurda: ["tarih", "islem_turu", "kisi", "cinsi", "ayar", "gram", "milyem", "has", "not"],
  stok: ["cinsi", "ayar", "alis_adet", "alis_gram", "alis_has", "satis_adet", "satis_gram", "satis_has", "kalan_adet", "kalan_gram", "kalan_has", "stok_degeri"],
  hurdaStok: ["cinsi", "ayar", "hurda_alis_adet", "hurda_alis_gram", "hurda_alis_has", "hurda_satis_adet", "hurda_satis_gram", "hurda_satis_has", "kalan_adet", "kalan_gram", "kalan_has"],
  musteriCari: ["musteri_adi", "toplam_satis", "alinan", "kalan_borc", "son_islem_tarihi"],
  tedarikciCari: ["tedarikci_adi", "toplam_alis", "odenen", "kalan_borc", "son_islem_tarihi"],
  kisiCari: ["isim", "normal_alis_has", "normal_satis_has", "hurda_alis_has", "hurda_satis_has", "toplam_alis_has", "toplam_satis_has", "kalan_has", "son_islem_tarihi"],
};

const labels = {
  tarih: "Tarih", tedarikci: "Tedarik\u00e7i", musteri: "M\u00fc\u015fteri", kisi: "Ki\u015fi / Firma", cinsi: "Cinsi", ayar: "Ayar",
  adet: "Adet", gram: "Gram", milyem: "Milyem", has: "Has", has_fiyati: "Has Fiyat\u0131", toplam_tutar: "Toplam",
  odenen: "\u00d6denen", alinan: "Al\u0131nan", odenen_veya_alinan: "\u00d6denen / Al\u0131nan", kalan_borc: "Kalan Bor\u00e7", not: "Not",
  islem_turu: "\u0130\u015flem", alis_adet: "Al\u0131\u015f Adet", alis_gram: "Al\u0131\u015f Gram", alis_has: "Al\u0131\u015f Has",
  satis_adet: "Sat\u0131\u015f Adet", satis_gram: "Sat\u0131\u015f Gram", satis_has: "Sat\u0131\u015f Has", kalan_adet: "Kalan Adet", kalan_gram: "Kalan Gram", kalan_has: "Kalan Has",
  stok_degeri: "Stok De\u011feri", alis_milyem: "Al\u0131\u015f Milyem", satis_milyem: "Sat\u0131\u015f Milyem", milyem_farki: "Milyem Fark\u0131",
  tahmini_kar: "Milyem K\u00e2r\u0131", has_kari: "Milyem K\u00e2r\u0131", milyem_kari: "Milyem K\u00e2r\u0131", musteri_adi: "Ad", tedarikci_adi: "Ad", toplam_satis: "Toplam Sat\u0131\u015f", toplam_alis: "Toplam Al\u0131\u015f",
  alis_borcu: "Al\u0131\u015f Borcu", satis_borcu: "Sat\u0131\u015f Borcu", net_bakiye: "Net Bakiye", son_islem_tarihi: "Son \u0130\u015flem", normal_alis_has: "Normal Alış Has", normal_satis_has: "Normal Satış Has", hurda_alis_has: "Hurda Alış Has", hurda_satis_has: "Hurda Satış Has", toplam_alis_has: "Toplam Alış Has", toplam_satis_has: "Toplam Satış Has", hurda_alis_adet: "Hurda Al\u0131\u015f Adet", hurda_alis_gram: "Hurda Al\u0131\u015f Gram", hurda_alis_has: "Hurda Al\u0131\u015f Has", hurda_satis_adet: "Hurda Sat\u0131\u015f Adet", hurda_satis_gram: "Hurda Sat\u0131\u015f Gram", hurda_satis_has: "Hurda Sat\u0131\u015f Has",
};

const moneyFields = new Set(["has_fiyati", "iscilik", "ek_masraf", "ek_ucret", "indirim", "odenen", "alinan", "toplam_tutar", "kalan_borc", "stok_degeri", "toplam_satis", "toplam_alis", "alis_borcu", "satis_borcu", "net_bakiye", "odenen_veya_alinan"]);
const numberFields = new Set(["adet", "gram", "milyem", "has", "alis_adet", "alis_gram", "alis_has", "satis_adet", "satis_gram", "satis_has", "kalan_adet", "kalan_gram", "kalan_has", "alis_milyem", "satis_milyem", "milyem_farki", "has_kari", "milyem_kari", "tahmini_kar", "hurda_alis_adet", "hurda_alis_gram", "hurda_alis_has", "hurda_satis_adet", "hurda_satis_gram", "hurda_satis_has", "normal_alis_has", "normal_satis_has", "hurda_alis_has", "hurda_satis_has", "toplam_alis_has", "toplam_satis_has"]);

const content = document.querySelector("#content");
const search = document.querySelector("#search");
let editing = null;

const today = () => new Date().toISOString().slice(0, 10);
const normalize = (value) => String(value || "").toLocaleLowerCase("tr-TR").replaceAll("\u0131", "i").normalize("NFD").replace(/[\u0300-\u036f]/g, "");
const parseNum = (value) => Number(String(value || "0").replace(",", ".")) || 0;

function formatValue(key, value) {
  if (value === null || value === undefined || value === "") return "";
  if (moneyFields.has(key)) return Number(value).toLocaleString("tr-TR", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  if (numberFields.has(key)) return Number(value).toLocaleString("tr-TR", { maximumFractionDigits: 3 });
  return String(value);
}

async function api(path, options = {}) {
  let response;
  try {
    response = await fetch(path, { headers: { "Content-Type": "application/json" }, ...options });
  } catch {
    throw new Error("Sunucuya ula\u015f\u0131lamad\u0131.");
  }
  const body = await response.json().catch(() => ({ status: "error", message: "", detail: "", data: null }));
  if (response.status === 401) { window.location.href = "/login"; return null; }
  const serverMessage = body.message || body.detail;
  const statusMessages = {
    404: "Sunucu endpointi bulunamad\u0131.",
    405: "Sunucu bu i\u015flem metodunu desteklemiyor. Uygulamay\u0131 yeniden ba\u015flat\u0131n ve endpointleri kontrol edin.",
  };
  if (!response.ok || body.status === "error") throw new Error(statusMessages[response.status] || serverMessage || "\u0130\u015flem yap\u0131lamad\u0131.");
  return body.data;
}

function showMessage(text, isError = false) {
  const toast = document.createElement("div");
  toast.className = `toast ${isError ? "toast-error" : "toast-info"}`;
  toast.textContent = text;
  document.body.appendChild(toast);
  setTimeout(() => toast.classList.add("toast-show"), 10);
  setTimeout(() => { toast.classList.remove("toast-show"); setTimeout(() => toast.remove(), 250); }, 3200);
}

function showConfirm(message, okText = "Tamam", cancelText = "\u0130ptal") {
  return new Promise((resolve) => {
    const overlay = document.createElement("div");
    overlay.className = "confirm-overlay confirm-show";
    const dialog = document.createElement("div");
    dialog.className = "confirm-dialog";
    dialog.innerHTML = `<p class="confirm-message">${message}</p>`;
    const actions = document.createElement("div");
    actions.className = "confirm-actions";
    const cancel = document.createElement("button");
    cancel.className = "confirm-btn confirm-cancel";
    cancel.type = "button";
    cancel.textContent = cancelText;
    cancel.onclick = () => { overlay.remove(); resolve(false); };
    const ok = document.createElement("button");
    ok.className = "confirm-btn confirm-ok";
    ok.type = "button";
    ok.textContent = okText;
    ok.onclick = () => { overlay.remove(); resolve(true); };
    actions.append(cancel, ok);
    dialog.appendChild(actions);
    overlay.appendChild(dialog);
    document.body.appendChild(overlay);
  });
}

async function refreshSuggestions() {
  try {
    const data = await api("/api/suggestions");
    data.products = (data.products || []).filter((item) => !normalize(item).includes("hurda"));
    state.suggestions = data;
  } catch { /* keep defaults */ }
}

function attachAutocomplete(input, source) {
  const box = document.createElement("div");
  box.className = "suggest-box hidden";
  input.parentElement.appendChild(box);
  const close = () => box.classList.add("hidden");
  const open = () => {
    const needle = normalize(input.value);
    const values = state.suggestions[source] || [];
    const matches = values.filter((item) => !needle || normalize(item).includes(needle)).slice(0, 8);
    if (!matches.length) { close(); return; }
    box.innerHTML = "";
    matches.forEach((item) => {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.textContent = item;
      btn.onmousedown = (event) => { event.preventDefault(); input.value = item; close(); };
      box.appendChild(btn);
    });
    box.classList.remove("hidden");
  };
  input.addEventListener("input", open);
  input.addEventListener("focus", open);
  input.addEventListener("blur", () => setTimeout(close, 120));
}

function fieldElement(name, type, source, readonly) {
  if (type === "hidden") { const input = document.createElement("input"); input.type = "hidden"; return input; }
  if (type === "textarea") { const input = document.createElement("textarea"); input.rows = 2; return input; }
  if (type === "select") {
    const input = document.createElement("select");
    source.forEach((value) => { const opt = document.createElement("option"); opt.value = value; opt.textContent = value; input.appendChild(opt); });
    return input;
  }
  const input = document.createElement("input");
  input.type = type === "decimal" || type === "autocomplete" ? "text" : type;
  if (type === "decimal") input.inputMode = "decimal";
  if (type === "autocomplete") input.autocomplete = "off";
  if (type === "number") input.min = "0";
  if (readonly) input.readOnly = true;
  if (["adet", "gram", "milyem", "satis_milyem"].includes(name)) input.required = true;
  return input;
}

function calcHas(form) {
  const milyem = form.elements.satis_milyem ? parseNum(form.elements.satis_milyem.value) : parseNum(form.elements.milyem?.value);
  return parseNum(form.elements.adet?.value) * parseNum(form.elements.gram?.value) * milyem / 1000;
}

function renderForm(type) {
  const panel = document.createElement("section");
  panel.className = "panel form-panel";
  const form = document.createElement("form");
  form.className = "entry-form";

  if (type === "satis") form.appendChild(renderSelectAction("ALI\u015eTAN \u00dcR\u00dcN SE\u00c7", "Sat\u0131\u015f i\u00e7in \u00f6nce al\u0131\u015ftan \u00fcr\u00fcn se\u00e7in.", (label) => openPurchaseModal(form, label)));
  if (type === "hurda") form.appendChild(renderSelectAction("HURDA ALI\u015eTAN SE\u00c7", "Hurda sat\u0131\u015f i\u00e7in al\u0131\u015ftan se\u00e7im yap\u0131n.", (label) => openHurdaPurchaseModal(form, label)));

  forms[type].forEach(([name, label, inputType, source, readonly]) => {
    const input = fieldElement(name, inputType, source, readonly);
    input.name = name;
    if (inputType === "hidden") { form.appendChild(input); return; }
    const wrap = document.createElement("label");
    wrap.className = "field field-main";
    wrap.append(label, input);
    if (name === "tarih") input.value = today();
    if (type === "hurda" && name === "cinsi") input.value = "HURDA";
    if (["cinsi", "ayar", "tedarikci", "musteri", "kisi"].includes(name)) input.required = true;
    form.appendChild(wrap);
    if (inputType === "autocomplete") attachAutocomplete(input, source);
  });

  if (type === "hurda") {
    const modeSelect = form.elements.islem_turu;
    const purchaseActions = form.querySelector(".purchase-actions");
    const updateHurdaMode = () => {
      const isSale = normalize(modeSelect?.value).startsWith("satis");
      if (purchaseActions) purchaseActions.classList.toggle("hidden", !isSale);
      if (!isSale) {
        state.selectedHurdaPurchase = null;
        if (form.elements.hurda_alis_id) form.elements.hurda_alis_id.value = "";
        if (form.elements.cinsi) form.elements.cinsi.readOnly = false;
        if (form.elements.ayar) form.elements.ayar.readOnly = false;
      } else {
        if (form.elements.cinsi) form.elements.cinsi.readOnly = true;
        if (form.elements.ayar) form.elements.ayar.readOnly = true;
      }
    };
    modeSelect?.addEventListener("change", updateHurdaMode);
    updateHurdaMode();
  }
  const preview = document.createElement("div");
  preview.className = "has-preview";
  preview.innerHTML = "<span>Hesaplanan Has</span><strong data-has>0</strong><span>Toplam Gram</span><strong data-gram>0</strong>";
  form.appendChild(preview);
  const updatePreview = () => {
    preview.querySelector("[data-has]").textContent = formatValue("has", calcHas(form));
    preview.querySelector("[data-gram]").textContent = formatValue("gram", parseNum(form.elements.adet?.value) * parseNum(form.elements.gram?.value));
  };
  ["adet", "gram", "milyem", "satis_milyem"].forEach((name) => form.elements[name]?.addEventListener("input", updatePreview));
  updatePreview();

  const actions = document.createElement("div");
  actions.className = "form-bottom-actions";
  const save = document.createElement("button");
  save.type = "submit";
  save.textContent = editing?.type === type ? "G\u00fcncelle" : "Kaydet";
  actions.appendChild(save);
  form.appendChild(actions);

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const data = Object.fromEntries(new FormData(form).entries());
    if (type === "alis") { data.has_fiyati = 0; data.iscilik = 0; data.ek_masraf = 0; data.odenen = 0; }
    if (type === "satis") {
      const selectedId = state.selectedPurchase?.id || data.purchase_id || data.alis_id;
      if (!selectedId) { showMessage("Sat\u0131\u015f i\u00e7in al\u0131\u015ftan \u00fcr\u00fcn se\u00e7in.", true); return; }
      data.purchase_id = selectedId;
      data.alis_id = selectedId;
      data.milyem = data.satis_milyem;
      data.has_fiyati = 0;
      data.iscilik = 0;
      data.ek_ucret = 0;
      data.indirim = 0;
      data.alinan = 0;
    }
    if (type === "hurda") {
      data.has_fiyati = 0;
      data.iscilik = 0;
      data.odenen_veya_alinan = 0;
      if (normalize(data.islem_turu).startsWith("satis")) {
        const selectedId = state.selectedHurdaPurchase?.id || data.hurda_alis_id;
        if (!selectedId) { showMessage("Hurda sat\u0131\u015f i\u00e7in hurda al\u0131\u015ftan \u00fcr\u00fcn se\u00e7in.", true); return; }
        data.hurda_alis_id = selectedId;
      } else {
        delete data.hurda_alis_id;
      }
    }
    const actionText = editing?.type === type ? "g\u00fcncellemek" : "kaydetmek";
    const messages = { alis: `Bu al\u0131\u015f kayd\u0131n\u0131 ${actionText} istiyor musunuz?`, satis: `Bu sat\u0131\u015f kayd\u0131n\u0131 ${actionText} istiyor musunuz?`, hurda: `Bu hurda kayd\u0131n\u0131 ${actionText} istiyor musunuz?` };
    if (!(await showConfirm(messages[type], editing?.type === type ? "G\u00fcncelle" : "Kaydet", "\u0130ptal"))) return;
    try {
      if (editing?.type === type) {
        await api(`/api/${type}/${editing.id}`, { method: "PUT", body: JSON.stringify(data) });
        showMessage(`${views[type].title} g\u00fcncellendi.`);
      } else {
        const saved = await api(`/api/${type}`, { method: "POST", body: JSON.stringify(data) });
        showMessage(`${views[type].title} kaydedildi. Has: ${formatValue("has", saved.has)}`);
      }
      editing = null;
      state.selectedPurchase = null;
      state.selectedHurdaPurchase = null;
      await refreshSuggestions();
      render();
    } catch (error) { showMessage(error.message, true); }
  });

  panel.appendChild(form);
  return panel;
}

function renderSelectAction(text, note, onClick) {
  const wrap = document.createElement("div");
  wrap.className = "purchase-actions";
  const btn = document.createElement("button");
  btn.type = "button";
  btn.className = "filter-toggle filter-toggle-active";
  btn.textContent = text;
  const label = document.createElement("span");
  label.className = "purchase-note";
  label.textContent = note;
  btn.addEventListener("click", () => onClick(label));
  wrap.append(btn, label);
  return wrap;
}

async function openPurchaseModal(form, chosenLabel) {
  try {
    const rows = await api("/api/satis/urun-secenekleri");
    if (!rows.length) { showMessage("Se\u00e7ilebilir al\u0131\u015f kayd\u0131 yok.", true); return; }
    openSelectableModal("Al\u0131\u015ftan \u00dcr\u00fcn Se\u00e7", ["tarih", "tedarikci", "cinsi", "ayar", "kalan_adet", "kalan_gram", "alis_milyem"], rows, (row) => {
      state.selectedPurchase = row;
      form.elements.purchase_id.value = row.id;
      form.elements.alis_id.value = row.id;
      form.elements.cinsi.value = row.cinsi;
      form.elements.ayar.value = row.ayar;
      form.elements.alis_milyem.value = row.alis_milyem;
      if (form.elements.alis_has_maliyeti) form.elements.alis_has_maliyeti.value = row.alis_has_maliyeti || "";
      form.elements.satis_milyem.value = "";
      form.elements.satis_milyem.placeholder = "Sat\u0131\u015f milyem girin";
      chosenLabel.textContent = `Se\u00e7ilen: ${row.cinsi} ${row.ayar} | Kalan ${row.kalan_adet} adet / ${row.kalan_gram} gr / ${row.kalan_has} has`;
    });
  } catch (error) { showMessage(error.message, true); }
}

async function openHurdaPurchaseModal(form, chosenLabel) {
  try {
    if (form.elements.islem_turu) { form.elements.islem_turu.value = "SATI\u015e"; form.elements.islem_turu.dispatchEvent(new Event("change")); }
    const rows = await api("/api/hurda/urun-secenekleri");
    if (!rows.length) { showMessage("Se\u00e7ilebilir hurda al\u0131\u015f kayd\u0131 yok.", true); return; }
    openSelectableModal("Hurda Al\u0131\u015ftan Se\u00e7", ["tarih", "kisi", "cinsi", "ayar", "kalan_adet", "kalan_gram", "milyem", "has", "kalan_has"], rows, (row) => {
      state.selectedHurdaPurchase = row;
      form.elements.hurda_alis_id.value = row.id;
      form.elements.cinsi.value = row.cinsi;
      form.elements.ayar.value = row.ayar;
      form.elements.milyem.value = row.milyem;
      chosenLabel.textContent = `Se\u00e7ilen: ${row.cinsi} ${row.ayar} | Kalan ${row.kalan_adet} adet / ${row.kalan_gram} gr / ${row.kalan_has} has`;
    });
  } catch (error) { showMessage(error.message, true); }
}

function openSelectableModal(titleText, cols, rows, onSelect) {
  const overlay = document.createElement("div");
  overlay.className = "modal";
  const box = document.createElement("div");
  box.className = "modal-box modal-box-wide";
  const title = document.createElement("div");
  title.className = "modal-title";
  title.innerHTML = `<h2>${titleText}</h2>`;
  const close = document.createElement("button");
  close.type = "button";
  close.className = "filter-clear";
  close.textContent = "Kapat";
  close.onclick = () => overlay.remove();
  title.appendChild(close);
  box.append(title, renderSelectableTable(cols, rows, (row) => { onSelect(row); overlay.remove(); }));
  overlay.appendChild(box);
  document.body.appendChild(overlay);
}

function renderSelectableTable(cols, rows, onSelect) {
  const wrap = document.createElement("div");
  wrap.className = "table-wrap";
  if (!rows.length) { wrap.innerHTML = '<div class="empty">Kay\u0131t yok.</div>'; return wrap; }
  const table = document.createElement("table");
  table.innerHTML = `<thead><tr>${cols.map((col) => `<th>${labels[col] || col}</th>`).join("")}<th>Se\u00e7</th></tr></thead>`;
  const tbody = document.createElement("tbody");
  rows.forEach((row) => {
    const tr = document.createElement("tr");
    cols.forEach((col) => {
      const td = document.createElement("td");
      td.dataset.label = labels[col] || col;
      td.textContent = formatValue(col, row[col]);
      if (moneyFields.has(col) || numberFields.has(col)) td.className = "num";
      tr.appendChild(td);
    });
    const td = document.createElement("td");
    td.dataset.label = "Seç";
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "filter-toggle filter-toggle-active";
    btn.textContent = "Se\u00e7";
    btn.onclick = () => onSelect(row);
    td.appendChild(btn);
    tr.appendChild(td);
    tbody.appendChild(tr);
  });
  table.appendChild(tbody);
  wrap.appendChild(table);
  return wrap;
}

function filteredRows(rows) {
  const needle = normalize(state.search);
  if (!needle) return rows;
  return rows.filter((row) => normalize(Object.values(row).join(" ")).includes(needle));
}

function iconSvg(kind) {
  if (kind === "edit") return '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 20h4l10.5-10.5a2.1 2.1 0 0 0 0-3L17.5 5.5a2.1 2.1 0 0 0-3 0L4 16v4Z"></path><path d="M13.5 7.5l3 3"></path></svg>';
  return '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 7h16"></path><path d="M10 11v6"></path><path d="M14 11v6"></path><path d="M6 7l1 14h10l1-14"></path><path d="M9 7V4h6v3"></path></svg>';
}

function renderTable(type, rows, title = "") {
  const section = document.createElement("section");
  section.className = "table-section";
  if (title) { const h = document.createElement("h2"); h.textContent = title; section.appendChild(h); }
  rows = filteredRows(rows || []);
  const wrap = document.createElement("div");
  wrap.className = "table-wrap";
  if (!rows.length) { wrap.innerHTML = '<div class="empty">Kay\u0131t yok.</div>'; section.appendChild(wrap); return section; }
  const cols = columns[type];
  const table = document.createElement("table");
  table.innerHTML = `<thead><tr>${cols.map((col) => `<th>${labels[col] || col}</th>`).join("")}${["alis", "satis", "hurda"].includes(type) ? "<th>\u0130\u015flemler</th>" : ""}</tr></thead>`;
  const tbody = document.createElement("tbody");
  rows.forEach((row) => {
    const tr = document.createElement("tr");
    cols.forEach((col) => {
      const td = document.createElement("td");
      td.dataset.label = labels[col] || col;
      td.textContent = formatValue(col, row[col]);
      if (moneyFields.has(col) || numberFields.has(col)) td.className = "num";
      if (["milyem_farki", "has_kari", "milyem_kari"].includes(col)) td.classList.add(Number(row[col]) >= 0 ? "pos" : "neg");
      tr.appendChild(td);
    });
    if (["alis", "satis", "hurda"].includes(type)) {
      const td = document.createElement("td");
      td.className = "actions-cell";
      td.dataset.label = "İşlemler";
      const edit = document.createElement("button");
      edit.type = "button";
      edit.className = "icon-btn icon-edit";
      edit.title = "D\u00fczenle";
      edit.setAttribute("aria-label", "D\u00fczenle");
      edit.innerHTML = iconSvg("edit");
      edit.onclick = () => startEdit(type, row);
      const del = document.createElement("button");
      del.type = "button";
      del.className = "icon-btn icon-delete";
      del.title = "Sil";
      del.setAttribute("aria-label", "Sil");
      del.innerHTML = iconSvg("delete");
      del.onclick = async () => { if (await showConfirm("Bu kayd\u0131 silmek istedi\u011finize emin misiniz?", "Sil", "\u0130ptal")) { try { await api(`/api/${type}/${row.id}`, { method: "DELETE" }); render(); } catch (error) { showMessage(error.message, true); } } };
      td.append(edit, del);
      tr.appendChild(td);
    }
    tbody.appendChild(tr);
  });
  table.appendChild(tbody);
  wrap.appendChild(table);
  section.appendChild(wrap);
  return section;
}

function startEdit(type, row) {
  editing = { type, id: row.id };
  state.selectedPurchase = null;
  state.selectedHurdaPurchase = null;
  render();
  setTimeout(() => {
    const form = document.querySelector(".entry-form");
    if (!form) return;
    Object.entries(row).forEach(([key, value]) => { if (form.elements[key]) form.elements[key].value = value ?? ""; });
    form.elements.islem_turu?.dispatchEvent(new Event("change"));
    if (form.elements.notlar && row.not !== undefined) form.elements.notlar.value = row.not || "";
    if (type === "satis") {
      const selectedId = row.purchase_id || row.alis_id;
      state.selectedPurchase = selectedId ? { id: selectedId, has_fiyati: row.has_fiyati || 0 } : null;
      form.elements.purchase_id.value = selectedId || "";
      form.elements.alis_id.value = selectedId || "";
      form.elements.satis_milyem.value = row.satis_milyem || row.milyem || "";
    }
    if (type === "hurda") {
      const selectedHurdaId = row.hurda_alis_id || "";
      state.selectedHurdaPurchase = selectedHurdaId ? { id: selectedHurdaId } : null;
      if (form.elements.hurda_alis_id) form.elements.hurda_alis_id.value = selectedHurdaId;
    }
    form.scrollIntoView({ behavior: "smooth", block: "start" });
  }, 0);
}

function renderTabs(options, active, onChange) {
  const tabs = document.createElement("div");
  tabs.className = "page-tabs";
  options.forEach(([value, label]) => {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = `page-tab ${active === value ? "active" : ""}`;
    btn.textContent = label;
    btn.onclick = () => onChange(value);
    tabs.appendChild(btn);
  });
  return tabs;
}

function renderCards(cards) {
  const wrap = document.createElement("div");
  wrap.className = "cards";
  cards.forEach(([label, value, key, tone]) => {
    const card = document.createElement("article");
    card.className = `card tone-${tone || "neutral"}`;
    card.innerHTML = `<span>${label}</span><strong>${formatValue(key, value)}</strong>`;
    wrap.appendChild(card);
  });
  return wrap;
}

function renderMetricCard(label, value, key, tone = "neutral", note = "") {
  const card = document.createElement("article");
  card.className = `metric-card tone-${tone}`;
  card.innerHTML = `<span>${label}</span><strong>${formatValue(key, value)}</strong>${note ? `<small>${note}</small>` : ""}`;
  return card;
}

function renderDashboardPanel(title, subtitle, cards) {
  const group = document.createElement("section");
  group.className = "dashboard-panel";
  const head = document.createElement("div");
  head.className = "dashboard-panel-head";
  head.innerHTML = `<h2>${title}</h2>${subtitle ? `<p>${subtitle}</p>` : ""}`;
  const grid = document.createElement("div");
  grid.className = "dashboard-panel-grid";
  cards.forEach((card) => grid.appendChild(renderMetricCard(...card)));
  group.append(head, grid);
  return group;
}

async function downloadAllData() {
  if (!(await showConfirm("T\u00fcm verileri JSON olarak indirmek istiyor musunuz?", "D\u0131\u015fa Aktar", "\u0130ptal"))) return;
  try {
    const data = await api("/api/export");
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `kuyumcu_backup_${today()}.json`;
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
    showMessage("T\u00fcm veriler JSON olarak indirildi.");
  } catch (error) {
    showMessage(error.message || "D\u0131\u015fa aktarma yap\u0131lamad\u0131.", true);
  }
}

function renderDashboard(data) {
  const root = document.createElement("div");
  root.className = "dashboard-root";

  const hero = document.createElement("section");
  hero.className = "dashboard-hero";
  const heroText = document.createElement("div");
  heroText.className = "dashboard-hero-text";
  heroText.innerHTML = `<span>Genel Durum</span><h2>\u0130\u015fletme \u00d6zeti</h2><p>Normal \u00fcr\u00fcn, hurda, stok ve cari hareketleri tek ekranda d\u00fczenli takip edilir.</p>`;
  const heroMetrics = document.createElement("div");
  heroMetrics.className = "dashboard-hero-metrics";
  [
    ["Genel Milyem K\u00e2r\u0131", data.genel_urun_kari, "has", "good", "Normal sat\u0131\u015flardan"],
    ["G\u00fcnl\u00fck Milyem K\u00e2r\u0131", data.gunluk_urun_kari, "has", "good", "Bug\u00fcnk\u00fc hareket"],
    ["Normal Stok Has", data.normal_stok_has, "has", "neutral", "\u00dcr\u00fcn sto\u011fu"],
    ["Hurda Kalan Has", data.hurda_kalan_has, "has", "accent", "Hurda sto\u011fu"],
  ].forEach((card) => heroMetrics.appendChild(renderMetricCard(...card)));
  hero.append(heroText, heroMetrics);

  const groups = document.createElement("div");
  groups.className = "dashboard-groups dashboard-groups-polished";
  [
    ["Genel \u00d6zet", "Al\u0131\u015f, sat\u0131\u015f ve k\u00e2rl\u0131l\u0131k", [
      ["Toplam Normal Al\u0131\u015f", data.toplam_normal_alis, "toplam_tutar", "neutral"],
      ["Toplam Normal Sat\u0131\u015f", data.toplam_normal_satis, "toplam_tutar", "accent"],
      ["Al\u0131\u015f Kay\u0131t", data.alis_adedi, "", "neutral"],
      ["Sat\u0131\u015f Kay\u0131t", data.satis_adedi, "", "neutral"],
    ]],
    ["Stok \u00d6zeti", "Normal \u00fcr\u00fcn ve hurda ayr\u0131 izlenir", [
      ["Normal Stok Gram", data.normal_stok_gram, "gram", "neutral"],
      ["Normal Stok De\u011feri", data.normal_stok_degeri, "toplam_tutar", "accent"],
      ["Hurda Stok Gram", data.hurda_kalan_gram, "gram", "neutral"],
      ["Stok De\u011feri", data.stok_degeri, "toplam_tutar", "neutral"],
    ]],
    ["Cari \u00d6zeti", "M\u00fc\u015fteri ve tedarik\u00e7i bor\u00e7lar\u0131", [
      ["M\u00fc\u015fteri Borcu", data.toplam_musteri_borcu, "toplam_tutar", "warn"],
      ["Tedarik\u00e7i Borcu", data.toplam_tedarikci_borcu, "toplam_tutar", "warn"],
    ]],
    ["Hurda \u00d6zeti", "Hurda al\u0131\u015f/sat\u0131\u015f ayr\u0131 hesaplan\u0131r", [
      ["Hurda Al\u0131\u015f", data.hurda_alis_toplami, "toplam_tutar", "neutral"],
      ["Hurda Sat\u0131\u015f", data.hurda_satis_toplami, "toplam_tutar", "accent"],
      ["Hurda K\u00e2r\u0131", data.hurda_kar, "toplam_tutar", "good"],
      ["Hurda Kay\u0131t", data.hurda_adedi, "", "neutral"],
    ]],
    ["Uyar\u0131lar", "Kontrol gerektiren durumlar", [
      ["Stok Yetersiz Uyar\u0131s\u0131", data.uyari_sayisi, "", data.uyari_sayisi ? "warn" : "good", data.uyari_sayisi ? "Kontrol edin" : "Sorun yok"],
    ]],
  ].forEach(([title, subtitle, cards]) => groups.appendChild(renderDashboardPanel(title, subtitle, cards)));

  root.append(hero, groups);
  return root;
}
async function render() {
  const meta = views[state.view];
  document.querySelector("#pageTitle").textContent = meta.title;
  document.querySelector("#pageSubtitle").textContent = meta.subtitle;
  content.innerHTML = "";
  try {
    if (state.view === "dashboard") {
      const [dashboard, stock] = await Promise.all([api("/api/dashboard"), api("/api/stok")]);
      content.append(renderDashboard(dashboard), renderTable("stok", stock.slice(0, 10), "Normal Stok \u00d6zeti"));
      return;
    }
    if (state.view === "cari") {
      const data = await api("/api/cari");
      content.appendChild(renderTabs([["all", "T\u00dcM\u00dc"], ["kisi", "K\u0130\u015e\u0130 / F\u0130RMA"], ["musteri", "M\u00dc\u015eTER\u0130LER"], ["tedarikci", "TEDAR\u0130K\u00c7\u0130LER"]], state.cariFilter, (value) => { state.cariFilter = value; render(); }));
      const note = document.createElement("p"); note.className = "hint danger"; note.textContent = "Ayn\u0131 isim farkl\u0131 yaz\u0131l\u0131rsa farkl\u0131 cari say\u0131l\u0131r."; content.appendChild(note);
      if (["all", "kisi"].includes(state.cariFilter)) content.appendChild(renderTable("kisiCari", data.kisiler || [], "Ki\u015fi / Firma Cari"));
      if (["all", "musteri"].includes(state.cariFilter)) content.appendChild(renderTable("musteriCari", data.musteriler || [], "M\u00fc\u015fteriler"));
      if (["all", "tedarikci"].includes(state.cariFilter)) content.appendChild(renderTable("tedarikciCari", data.tedarikciler || [], "Tedarik\u00e7iler"));
      return;
    }
    if (state.view === "stok") {
      const [normal, hurda] = await Promise.all([api("/api/stok/normal"), api("/api/stok/hurda")]);
      content.appendChild(renderTabs([["normal", "NORMAL STOK"], ["hurda", "HURDA STOK"]], state.stokFilter, (value) => { state.stokFilter = value; render(); }));
      content.appendChild(state.stokFilter === "hurda" ? renderTable("hurdaStok", hurda || [], "Hurda Stok") : renderTable("stok", normal || [], "Normal Stok"));
      return;
    }
    if (["alis", "satis", "hurda"].includes(state.view)) content.appendChild(renderForm(state.view));
    if (state.view === "hurda") {
      const data = await api("/api/hurda");
      content.appendChild(renderTable("hurdaStok", data.stok || [], "Hurda Stok"));
      content.appendChild(renderTabs([["all", "T\u00dcM\u00dc"], ["alis", "HURDA ALI\u015e"], ["satis", "HURDA SATI\u015e"]], state.hurdaKayitFilter, (value) => { state.hurdaKayitFilter = value; state.hurdaScrollToRecords = true; render(); }));
      const hurdaRows = (data.kayitlar || []).filter((row) => state.hurdaKayitFilter === "all" || normalize(row.islem_turu).startsWith(state.hurdaKayitFilter));
      const recordsSection = renderTable("hurda", hurdaRows, "Hurda Kay\u0131tlar\u0131");
      content.appendChild(recordsSection);
      if (state.hurdaScrollToRecords) {
        state.hurdaScrollToRecords = false;
        requestAnimationFrame(() => recordsSection.scrollIntoView({ block: "start" }));
      }
    } else {
      content.appendChild(renderTable(state.view, await api(`/api/${state.view}`)));
    }
  } catch (error) { showMessage(error.message, true); }
}

document.querySelectorAll(".nav").forEach((button) => button.addEventListener("click", () => {
  document.querySelectorAll(".nav").forEach((item) => item.classList.remove("active"));
  button.classList.add("active");
  state.view = button.dataset.view;
  editing = null;
  search.value = "";
  state.search = "";
  render();
}));

search.addEventListener("input", () => { state.search = search.value; render(); });


document.querySelector("#exportBtn")?.addEventListener("click", downloadAllData);

document.querySelector("#logoutBtn")?.addEventListener("click", async () => {
  if (!(await showConfirm("\u00c7\u0131k\u0131\u015f yapmak istedi\u011finize emin misiniz?", "\u00c7\u0131k\u0131\u015f", "\u0130ptal"))) return;
  await api("/api/logout", { method: "POST" });
  window.location.href = "/login";
});

api("/api/session").then((session) => { if (!session?.authenticated) window.location.href = "/login"; else refreshSuggestions().then(render); }).catch((error) => showMessage(error.message, true));
