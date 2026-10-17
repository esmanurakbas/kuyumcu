
const state = {
  view: "dashboard",
  search: "",
  cariFilter: "all",
  cariData: null,
  hurdaKayitFilter: "all",
  hurdaScrollToRecords: false,
  stokFilter: "normal",
  selectedPurchase: null,
  selectedHurdaPurchase: null,
  suggestions: { products: ["B\u0130LEZ\u0130K", "Y\u00dcZ\u00dcK", "KOLYE", "K\u00dcPE", "SET", "\u00c7EYREK", "YARIM", "TAM", "GRAM ALTIN", "RE\u015eAT", "RE\u015eAT \u00c7EYREK", "RE\u015eAT YARIM", "RE\u015eAT TAM", "RE\u015eAT GREMSE", "RE\u015eAT BE\u015eL\u0130", "ATA L\u0130RA", "CUMHUR\u0130YET", "GREMSE", "BE\u015eL\u0130", "D\u0130\u011eER"], customers: [], suppliers: [], people: [] },
};

const views = {
  giderler: { title: "Giderler", subtitle: "Ki\u015fisel ve i\u015fletme giderleri" },
  dashboard: { title: "Dashboard", subtitle: "G\u00fcncel stok, cari ve sat\u0131\u015f \u00f6zeti" },
  alis: { title: "Al\u0131\u015f", subtitle: "Normal \u00fcr\u00fcn al\u0131\u015f kay\u0131tlar\u0131" },
  satis: { title: "Sat\u0131\u015f", subtitle: "Al\u0131\u015ftan se\u00e7erek sat\u0131\u015f" },
  hurda_alis: { title: "Hurda Al\u0131\u015f", subtitle: "Sadece hurda al\u0131\u015f kay\u0131tlar\u0131" },
  hurda_satis: { title: "Hurda Sat\u0131\u015f", subtitle: "Hurda al\u0131\u015ftan se\u00e7erek sat\u0131\u015f" },
  stok: { title: "Stok", subtitle: "Normal stok ve hurda stok ayr\u0131" },
  cari: { title: "Cari", subtitle: "M\u00fc\u015fteri ve tedarik\u00e7i bakiyeleri" },
};

const forms = {
  giderler: [["tarih", "Tarih", "date"], ["tutar", "Gider (has)", "decimal"], ["kategori", "Kategori", "text"], ["notlar", "A\u00e7\u0131klama / not", "textarea"]],
  alis: [
    ["tarih", "Tarih", "date"], ["tedarikci", "Tedarik\u00e7i", "autocomplete", "suppliers"],
    ["cinsi", "Cinsi", "autocomplete", "products"], ["ayar", "Ayar", "text"],
    ["gram", "Gram", "decimal"], ["milyem", "Al\u0131\u015f Milyem", "decimal"],
    ["notlar", "Not", "textarea"],
  ],
  satis: [
    ["purchase_id", "", "hidden"], ["alis_id", "", "hidden"],
    ["tarih", "Tarih", "date"], ["musteri", "M\u00fc\u015fteri", "autocomplete", "customers"],
    ["cinsi", "Cinsi", "text", null, true], ["ayar", "Ayar", "text", null, true],
    ["alis_milyem", "Al\u0131\u015f Milyem", "decimal", null, true],
    ["gram", "Sat\u0131\u015f Gram", "decimal"], ["satis_milyem", "Sat\u0131\u015f Milyem", "decimal"],
    ["notlar", "Not", "textarea"],
  ],
  hurda: [
    ["hurda_alis_id", "", "hidden"], ["tarih", "Tarih", "date"], ["islem_turu", "", "hidden"],
    ["kisi", "Ki\u015fi / Firma", "autocomplete", "people"], ["cinsi", "Cinsi", "text"], ["ayar", "Ayar", "text"],
    ["gram", "Gram", "decimal"], ["milyem", "Al\u0131\u015f Milyem", "decimal"],
    ["notlar", "Not", "textarea"],
  ],
};

const columns = {
  giderler: ["tarih", "tutar", "kategori", "notlar"],
  alis: ["tarih", "tedarikci", "cinsi", "ayar", "gram", "milyem", "has", "not"],
  satis: ["tarih", "musteri", "cinsi", "ayar", "gram", "alis_milyem", "satis_milyem", "milyem_farki", "milyem_kari", "not"],
  hurdaAlis: ["tarih", "kisi", "cinsi", "ayar", "gram", "milyem", "has", "not"],
  hurdaSatis: ["tarih", "kisi", "cinsi", "ayar", "gram", "alis_milyem", "satis_milyem", "milyem_farki", "milyem_kari", "kalan_gram", "not"],
  stok: ["cinsi", "ayar", "alis_gram", "alis_has", "satis_gram", "satis_has", "kalan_gram", "kalan_has"],
  hurdaStok: ["cinsi", "ayar", "hurda_alis_gram", "hurda_alis_has", "hurda_satis_gram", "hurda_satis_has", "kalan_gram", "kalan_has"],
  musteriCari: ["musteri_adi", "net_bakiye_has", "toplam_satis_has", "tahsil_edilen_has", "son_islem_tarihi"],
  tedarikciCari: ["tedarikci_adi", "net_bakiye_has", "toplam_alis_has", "odedigimiz_has", "odeyecegimiz_has", "son_islem_tarihi"],
  kisiCari: ["isim", "net_bakiye_has", "toplam_satis_has", "toplam_alis_has", "tahsil_edilen_has", "odedigimiz_has", "son_islem_tarihi"],
  cariHistory: ["tarih", "hareket", "kaynak", "gram", "has", "not"],
  cariOdeme: ["tarih", "isim", "yon", "odeme_tipi", "odenen_has", "not"],
};

const labels = {
  hareket: "\u0130\u015flem", kaynak: "Kaynak",
  tutar: "Gider (has)", kategori: "Kategori", notlar: "A\u00e7\u0131klama / not",
  tarih: "Tarih", tedarikci: "Tedarik\u00e7i", musteri: "M\u00fc\u015fteri", kisi: "Ki\u015fi / Firma", cinsi: "Cinsi", ayar: "Ayar",
  gram: "Gram", milyem: "Milyem", has: "Has", has_fiyati: "Has Fiyat\u0131", toplam_tutar: "Toplam",
  odenen: "\u00d6denen", alinan: "Al\u0131nan", odenen_veya_alinan: "\u00d6denen / Al\u0131nan", kalan_borc: "Kalan Bor\u00e7", not: "Not",
  islem_turu: "\u0130\u015flem", alis_gram: "Al\u0131\u015f Gram", alis_has: "Al\u0131\u015f Has",
  satis_gram: "Sat\u0131\u015f Gram", satis_has: "Sat\u0131\u015f Has", kalan_gram: "Kalan Gram", kalan_has: "Kalan Has",
  alis_milyem: "Al\u0131\u015f Milyem", satis_milyem: "Sat\u0131\u015f Milyem", milyem_farki: "Milyem Fark\u0131",
  tahmini_kar: "Milyem K\u00e2r\u0131", has_kari: "Milyem K\u00e2r\u0131", milyem_kari: "Milyem K\u00e2r\u0131", musteri_adi: "Ad", tedarikci_adi: "Ad", toplam_satis: "Toplam Sat\u0131\u015f", toplam_alis: "Toplam Al\u0131\u015f",
  alis_borcu: "Al\u0131\u015f Borcu", satis_borcu: "Sat\u0131\u015f Borcu", net_bakiye: "Net Bakiye", net_bakiye_has: "Net Has Bakiyesi", son_islem_tarihi: "Son \u0130\u015flem", odeme_tipi: "\u00d6deme Tipi", yon: "\u0130\u015flem Y\u00f6n\u00fc", odenen_has: "\u0130\u015flem Has\u0131", odenen_gram: "\u00d6denen Gram", odenen_milyem: "\u00d6denen Milyem", hesaplanan_has: "Hesaplanan Has", toplam_has: "Toplam Has", odeme_has: "\u00d6deme Has", odedigimiz_has: "\u00d6dedi\u011fimiz Has", tahsil_edilen_has: "Tahsil Etti\u011fimiz Has", odeyecegimiz_has: "\u00d6deyece\u011fimiz Has", tahsil_edilecek_has: "Tahsil Edilecek Has", normal_alis_has: "Normal Al\u0131\u015f Has", normal_satis_has: "Normal Sat\u0131\u015f Has", hurda_alis_has: "Hurda Al\u0131\u015f Has", hurda_satis_has: "Hurda Sat\u0131\u015f Has", toplam_alis_has: "Toplam Al\u0131\u015f Has", toplam_satis_has: "Toplam Sat\u0131\u015f Has", hurda_alis_gram: "Hurda Al\u0131\u015f Gram", hurda_satis_gram: "Hurda Sat\u0131\u015f Gram",
};

const moneyFields = new Set(["has_fiyati", "iscilik", "ek_masraf", "ek_ucret", "indirim", "odenen", "alinan", "toplam_tutar", "kalan_borc", "toplam_satis", "toplam_alis", "alis_borcu", "satis_borcu", "net_bakiye", "odenen_veya_alinan"]);
const numberFields = new Set(["gram", "milyem", "has", "alis_gram", "alis_has", "satis_gram", "satis_has", "kalan_gram", "kalan_has", "alis_milyem", "satis_milyem", "milyem_farki", "has_kari", "milyem_kari", "tahmini_kar", "hurda_alis_gram", "hurda_alis_has", "hurda_satis_gram", "hurda_satis_has", "normal_alis_has", "normal_satis_has", "toplam_alis_has", "toplam_satis_has", "tutar", "toplam_has", "odeme_has", "odedigimiz_has", "tahsil_edilen_has", "odeyecegimiz_has", "tahsil_edilecek_has", "net_bakiye_has", "odenen_has", "odenen_gram", "odenen_milyem", "hesaplanan_has"]);

const content = document.querySelector("#content");
const search = document.querySelector("#search");
let editing = null;

const today = () => new Date().toISOString().slice(0, 10);
const normalize = (value) => String(value || "").toLocaleLowerCase("tr-TR").replaceAll("\u0131", "i").normalize("NFD").replace(/[\u0300-\u036f]/g, "");
const parseNum = (value) => Number(String(value || "0").replace(",", ".")) || 0;
const paymentDisplayValue = (value) => parseNum(value) > 0 ? String(value).replace(".", ",") : "";

function cleanDecimalInput(input) {
  const before = input.value;
  if (before.includes("-")) {
    input.value = "";
    return;
  }
  input.value = before.replace(/[^0-9.,]/g, "");
}

function positiveValue(input, label, allowEmpty = false) {
  const raw = String(input.value || "").trim();
  if (!raw) {
    if (allowEmpty) return null;
    throw new Error(`${label} girin.`);
  }
  if (raw.includes("-")) throw new Error(`${label} negatif olamaz.`);
  const value = Number(raw.replace(",", "."));
  if (!Number.isFinite(value) || value <= 0) throw new Error(`${label} 0'dan b\u00fcy\u00fck olmal\u0131.`);
  return value;
}

function attachDecimalGuard(input) {
  input.addEventListener("input", () => cleanDecimalInput(input));
  input.addEventListener("focus", () => { if (parseNum(input.value) === 0) input.value = ""; });
}

function formatValue(key, value) {
  if (value === null || value === undefined || value === "") return "";
  if (key === "odeme_tipi") return paymentLabel(value);
  if (key === "yon") return value === "ODEME" ? "Tedarik\u00e7iye \u00d6deme" : "M\u00fc\u015fteriden Tahsilat";
  if (key === "net_bakiye_has") return `${Number(value) > 0 ? "+" : ""}${Number(value).toLocaleString("tr-TR", { maximumFractionDigits: 3 })}`;
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
    ok.className = `confirm-btn confirm-ok ${normalize(okText) === "sil" ? "confirm-danger" : ""}`;
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
  if (input._autocompleteAttached) return;
  input._autocompleteAttached = true;
  // A single custom list owns suggestions; no native datalist is mounted.
  input.removeAttribute("list");
  const box = document.createElement("div");
  box.className = "suggest-box hidden";
  box.id = `suggest-${source}-${input.name}`;
  box.setAttribute("role", "listbox");
  input.parentElement.appendChild(box);
  input.setAttribute("role", "combobox");
  input.setAttribute("aria-autocomplete", "list");
  input.setAttribute("aria-controls", box.id);
  input.setAttribute("aria-expanded", "false");
  let active = -1;
  const close = () => {
    box.classList.add("hidden"); active = -1;
    input.setAttribute("aria-expanded", "false");
    input.removeAttribute("aria-activedescendant");
  };
  const select = value => {
    input.value = value;
    input.dispatchEvent(new Event("input", { bubbles: true }));
    input.dispatchEvent(new Event("change", { bubbles: true }));
    close();
  };
  const open = () => {
    const values = [...new Map((state.suggestions[source] || []).map(value => [normalize(value), value])).values()];
    const needle = normalize(input.value);
    const matches = values.filter(item => !needle || normalize(item).includes(needle));
    box.replaceChildren(); active = -1;
    input.removeAttribute("aria-activedescendant");
    if (!matches.length) { close(); return; }
    matches.forEach((item, index) => {
      const btn = document.createElement("button");
      btn.type = "button"; btn.textContent = item; btn.tabIndex = -1;
      btn.id = `${box.id}-${index}`; btn.setAttribute("role", "option");
      btn.setAttribute("aria-selected", "false");
      btn.addEventListener("pointerdown", event => event.preventDefault());
      btn.addEventListener("click", () => select(item));
      box.appendChild(btn);
    });
    box.scrollTop = 0;
    box.classList.remove("hidden");
    input.setAttribute("aria-expanded", "true");
  };
  input.addEventListener("input", open);
  input.addEventListener("focus", open);
  input.addEventListener("click", () => { if (box.classList.contains("hidden")) open(); });
  input.addEventListener("blur", close);
  input.addEventListener("keydown", event => {
    if (event.key === "Escape" || event.key === "Tab") { close(); return; }
    if (event.key === "Enter" && !box.classList.contains("hidden")) {
      event.preventDefault();
      if (active >= 0) select(box.children[active].textContent);
      return;
    }
    if (!["ArrowDown", "ArrowUp"].includes(event.key)) return;
    event.preventDefault();
    if (box.classList.contains("hidden")) open();
    if (!box.children.length) return;
    active = (active + (event.key === "ArrowDown" ? 1 : (active < 0 ? 0 : -1)) + box.children.length) % box.children.length;
    [...box.children].forEach((option, index) => option.setAttribute("aria-selected", String(index === active)));
    input.setAttribute("aria-activedescendant", box.children[active].id);
    box.children[active].scrollIntoView({ block: "nearest" });
  });
}
function fieldElement(name, type, source, readonly) {
  if (type === "hidden") { const input = document.createElement("input"); input.type = "hidden"; return input; }
  if (type === "textarea") { const input = document.createElement("textarea"); input.rows = 1; input.maxLength = 200; return input; }
  if (type === "select") {
    const input = document.createElement("select");
    const values = Array.isArray(source) ? source : (state.suggestions[source] || []); values.forEach((value) => { const opt = document.createElement("option"); opt.value = value; opt.textContent = value; input.appendChild(opt); });
    return input;
  }
  const input = document.createElement("input");
  input.type = type === "decimal" || type === "autocomplete" ? "text" : type;
  if (type === "decimal") input.inputMode = "decimal";
  if (type === "autocomplete") input.autocomplete = "off";
  if (type === "number") input.min = "0";
  if (readonly) input.readOnly = true;
  if (["gram", "milyem", "satis_milyem"].includes(name)) input.required = true;
  return input;
}

function calcHas(form) {
  const milyem = form.elements.satis_milyem ? parseNum(form.elements.satis_milyem.value) : parseNum(form.elements.milyem?.value);
  return parseNum(form.elements.gram.value) * milyem / 1000;
}

function ensureTransactionPaymentFields(form) {
  const defaults = { odeme_tipi: "ODEME_YOK", odenen_has: "0", odenen_gram: "0", odenen_milyem: "0" };
  Object.entries(defaults).forEach(([name, value]) => {
    if (!form.elements[name]) {
      const input = document.createElement("input");
      input.type = "hidden";
      input.name = name;
      input.value = value;
      form.appendChild(input);
    }
  });
}

function paymentLabel(value) {
  return ({ ODEME_YOK: "Ödeme Yok", HAS: "Has ile Ödeme", ADET_GRAM_MILYEM: "Gram + Milyem", TAM_KAPAT: "Borcu Tam Kapat" })[value] || "deme Yok";
}

function calculatedTransactionPayment(form) {
  const tip = form.elements.odeme_tipi.value || "ODEME_YOK";
  if (tip === "HAS") return parseNum(form.elements.odenen_has.value);
  if (tip === "ADET_GRAM_MILYEM") return parseNum(form.elements.odenen_gram.value) * parseNum(form.elements.odenen_milyem.value) / 1000;
  if (tip === "TAM_KAPAT") return calcHas(form);
  return 0;
}

function syncTransactionPayment(form) {
  const tip = form.elements.odeme_tipi.value || "ODEME_YOK";
  if (tip === "ADET_GRAM_MILYEM" || tip === "TAM_KAPAT") form.elements.odenen_has.value = String(calculatedTransactionPayment(form));
  if (tip === "ODEME_YOK") {
    form.elements.odenen_has.value = "0";
    form.elements.odenen_gram.value = "0";
    form.elements.odenen_milyem.value = "0";
  }
  form._refreshPaymentSummary?.();
}

function attachPaymentButton(form) {
  ensureTransactionPaymentFields(form);
  const box = document.createElement("div");
  box.className = "payment-action-box";
  box.innerHTML = `
    <div><span>\u00d6deme Bilgisi</span><strong data-payment-summary>\u00d6deme Yok</strong></div>
    <button type="button" class="secondary payment-open-btn">\u00d6deme Ekle / D\u00fczenle</button>
  `;
  form._refreshPaymentSummary = () => {
    const paidHas = calculatedTransactionPayment(form);
    const text = `${paymentLabel(form.elements.odeme_tipi.value)}${paidHas ? ` - ${formatValue("has", paidHas)} has` : ""}`;
    box.querySelector("[data-payment-summary]").textContent = text;
  };
  box.querySelector("button").addEventListener("click", () => openTransactionPaymentModal(form));
  [form.elements.gram, form.elements.milyem, form.elements.satis_milyem].filter(Boolean).forEach((input) => input.addEventListener("input", () => syncTransactionPayment(form)));
  form._refreshPaymentSummary();
  return box;
}

function modalField(label, input) {
  const wrap = document.createElement("label");
  wrap.className = "field field-main";
  wrap.append(label, input);
  return wrap;
}

function paymentInput(name, placeholder = "") {
  const input = document.createElement("input");
  input.type = "text";
  input.inputMode = "decimal";
  input.value = "";
  input.placeholder = placeholder;
  return input;
}

function openTransactionPaymentModal(form) {
  const overlay = document.createElement("div");
  overlay.className = "modal";
  const box = document.createElement("div");
  box.className = "modal-box payment-modal transaction-payment-modal";
  const title = document.createElement("h3");
  title.className = "modal-title";
  title.textContent = "\u00d6deme Bilgisi";

  let selectedPaymentType = form.elements.odeme_tipi.value || "ODEME_YOK";
  const paymentTabs = document.createElement("div");
  paymentTabs.className = "payment-type-tabs";
  const paymentOptions = [
    ["ODEME_YOK", "\u00d6deme Yok"],
    ["HAS", "Has ile \u00d6deme"],
    ["ADET_GRAM_MILYEM", "Gram + Milyem"],
    ["TAM_KAPAT", "Borcu Tam Kapat"],
  ];
  paymentOptions.forEach(([value, label]) => {
    const tab = document.createElement("button");
    tab.type = "button";
    tab.className = "payment-type-tab";
    tab.dataset.value = value;
    tab.textContent = label;
    tab.onclick = () => {
      selectedPaymentType = value;
      update();
    };
    paymentTabs.appendChild(tab);
  });

  const paidInput = document.createElement("input");
  paidInput.type = "text";
  paidInput.inputMode = "decimal";
  paidInput.value = paymentDisplayValue(form.elements.odenen_has.value);
  paidInput.placeholder = "\u00d6denen has";

  const gramInput = document.createElement("input");
  gramInput.type = "text";
  gramInput.inputMode = "decimal";
  gramInput.value = paymentDisplayValue(form.elements.odenen_gram.value);

  const milyemInput = document.createElement("input");
  milyemInput.type = "text";
  milyemInput.inputMode = "decimal";
  milyemInput.value = paymentDisplayValue(form.elements.odenen_milyem.value);

  const calculated = document.createElement("div");
  calculated.className = "has-preview payment-preview";
  calculated.innerHTML = `<span>Hesaplanan \u00d6denen Has</span><strong data-calculated-payment>0</strong>`;

  const paidField = modalField("\u00d6denen Has", paidInput);
  const gramField = modalField("Gram", gramInput);
  const milyemField = modalField("Milyem", milyemInput);
  paidField.classList.add("payment-fill-field", "transaction-paid-field");
  gramField.classList.add("payment-fill-field", "transaction-product-payment-field", "payment-gram-field");
  milyemField.classList.add("payment-fill-field", "transaction-product-payment-field", "payment-milyem-field");
  const closeBtn = document.createElement("button");
  closeBtn.type = "button";
  closeBtn.className = "secondary";
  closeBtn.textContent = "\u0130ptal";
  closeBtn.onclick = () => overlay.remove();
  const saveBtn = document.createElement("button");
  saveBtn.type = "button";
  saveBtn.textContent = "\u00d6demeyi Uygula";

  const update = () => {
    const tip = selectedPaymentType;
    paymentTabs.querySelectorAll(".payment-type-tab").forEach((tab) => tab.classList.toggle("active", tab.dataset.value === tip));
    paidField.classList.toggle("payment-inactive", tip !== "HAS");
    paidInput.disabled = tip !== "HAS";
    [gramField, milyemField].forEach((field) => field.classList.toggle("payment-inactive", tip !== "ADET_GRAM_MILYEM"));
    [gramInput, milyemInput].forEach((input) => input.disabled = tip !== "ADET_GRAM_MILYEM");
    calculated.classList.toggle("payment-inactive", tip === "HAS" || tip === "ODEME_YOK");
    let value = 0;
    if (tip === "HAS") value = parseNum(paidInput.value);
    if (tip === "ADET_GRAM_MILYEM") value = parseNum(gramInput.value) * parseNum(milyemInput.value) / 1000;
    if (tip === "TAM_KAPAT") value = calcHas(form);
    calculated.querySelector("[data-calculated-payment]").textContent = formatValue("has", value);
  };

  [paidInput, gramInput, milyemInput].forEach((input) => {
    attachDecimalGuard(input);
    input.addEventListener("input", update);
    input.addEventListener("change", update);
  });
  saveBtn.onclick = () => {
    try {
      if (selectedPaymentType === "HAS") positiveValue(paidInput, "\u00d6denen has");
      if (selectedPaymentType === "ADET_GRAM_MILYEM") {
        positiveValue(gramInput, "Gram");
        positiveValue(milyemInput, "Milyem");
      }
      if (selectedPaymentType === "TAM_KAPAT" && calcHas(form) <= 0) throw new Error("Kapat\u0131lacak has bulunamad\u0131.");
      form.elements.odeme_tipi.value = selectedPaymentType;
        form.elements.odenen_gram.value = gramInput.value || "0";
      form.elements.odenen_milyem.value = milyemInput.value || "0";
      form.elements.odenen_has.value = selectedPaymentType === "HAS" ? paidInput.value : String(selectedPaymentType === "ODEME_YOK" ? 0 : (selectedPaymentType === "TAM_KAPAT" ? calcHas(form) : parseNum(gramInput.value) * parseNum(milyemInput.value) / 1000));
      syncTransactionPayment(form);
      form._refreshPaymentSummary?.();
      overlay.remove();
    } catch (error) {
      showMessage(error.message, true);
    }
  };

  const actions = document.createElement("div");
  actions.className = "form-bottom-actions";
  actions.append(closeBtn, saveBtn);
  box.append(title, paymentTabs, paidField, gramField, milyemField, calculated, actions);
  overlay.appendChild(box);
  document.body.appendChild(overlay);
  update();
}function renderForm(type, hurdaMode = null) {
  const isEditing = editing?.type === type;
  const panel = document.createElement("section");
  panel.className = "panel form-panel";
  const form = document.createElement("form");
  form.className = "entry-form";
  ensureTransactionPaymentFields(form);

  if (type === "satis") form.appendChild(renderSelectAction("ALI\u015eTAN \u00dcR\u00dcN SE\u00c7", "Sat\u0131\u015f i\u00e7in \u00f6nce al\u0131\u015ftan \u00fcr\u00fcn se\u00e7in.", (label) => openPurchaseModal(form, label)));
  if (type === "hurda" && hurdaMode === "SATIS") form.appendChild(renderSelectAction("HURDA ALI\u015eTAN SE\u00c7", "Hurda sat\u0131\u015f i\u00e7in al\u0131\u015ftan se\u00e7im yap\u0131n.", (label) => openHurdaPurchaseModal(form, label)));

  // Both sale screens share the same visible fields; keep the scrap API names.
  const formFields = type === "hurda" && hurdaMode === "SATIS" ? [
    ...forms.hurda.filter(([, , inputType]) => inputType === "hidden"),
    ...forms.satis.filter(([, , inputType]) => inputType !== "hidden").map(field => {
      if (field[0] === "musteri") return ["kisi", field[1], field[2], "people"];
      if (field[0] === "satis_milyem") return ["milyem", ...field.slice(1)];
      return field;
    }),
  ] : forms[type];
  formFields.forEach(([name, label, inputType, source, readonly]) => {
    const input = fieldElement(name, inputType, source, readonly);
    input.name = name;
    if (inputType === "hidden") { form.appendChild(input); return; }
    const wrap = document.createElement("label");
    wrap.className = "field field-main";
    wrap.dataset.field = name;
    wrap.append(label, input);
    if (type === "hurda" && hurdaMode && name === "islem_turu") wrap.classList.add("hidden");
    if (name === "tarih") input.value = today();
    if (type === "hurda" && name === "cinsi") input.value = "HURDA";
    if (["cinsi", "ayar", "tedarikci", "musteri", "kisi"].includes(name)) input.required = true;
    form.appendChild(wrap);
    if (inputType === "autocomplete") attachAutocomplete(input, source);
  });

  if (type === "hurda" && hurdaMode && form.elements.islem_turu) form.elements.islem_turu.value = hurdaMode;

  if (type === "hurda") {
    const modeSelect = form.elements.islem_turu;
    const purchaseActions = form.querySelector(".purchase-actions");
    const updateHurdaMode = () => {
      const isSale = normalize(modeSelect.value).startsWith("satis");
      if (purchaseActions) purchaseActions.classList.toggle("hidden", !isSale);
      const milyemField = form.querySelector('[data-field="milyem"]');
      if (milyemField.firstChild) milyemField.firstChild.textContent = isSale ? "Sat\u0131\u015f Milyem" : "Al\u0131\u015f Milyem";
      if (form.elements.milyem) form.elements.milyem.placeholder = isSale ? "Sat\u0131\u015f milyem girin" : "Al\u0131\u015f milyem girin";
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
    modeSelect.addEventListener("change", updateHurdaMode);
    updateHurdaMode();
  }
  const preview = document.createElement("div");
  preview.className = "has-preview";
  preview.innerHTML = "<span>Hesaplanan Has</span><strong data-has>0</strong><span>Gram</span><strong data-gram>0</strong>";
  form.appendChild(preview);
  form.appendChild(attachPaymentButton(form));
  const updatePreview = () => {
    preview.querySelector("[data-has]").textContent = formatValue("has", calcHas(form));
    preview.querySelector("[data-gram]").textContent = formatValue("gram", parseNum(form.elements.gram.value));
  };
  ["gram", "milyem", "satis_milyem"].map((name) => form.elements[name]).filter(Boolean).forEach((input) => input.addEventListener("input", updatePreview));
  updatePreview();

  const actions = document.createElement("div");
  actions.className = "form-bottom-actions";
  const save = document.createElement("button");
  save.type = "submit";
  save.textContent = isEditing ? "G\u00fcncelle" : "Kaydet";
  actions.appendChild(save);
  form.appendChild(actions);

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    syncTransactionPayment(form);
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
      if (hurdaMode) data.islem_turu = hurdaMode;
      delete data.alis_milyem; // Display only; the linked purchase remains the source of cost.
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
    const actionText = isEditing ? "g\u00fcncellemek" : "kaydetmek";
    const messages = { alis: `Bu al\u0131\u015f kayd\u0131n\u0131 ${actionText} istiyor musunuz`, satis: `Bu sat\u0131\u015f kayd\u0131n\u0131 ${actionText} istiyor musunuz`, hurda: `Bu hurda kayd\u0131n\u0131 ${actionText} istiyor musunuz` };
    if (!(await showConfirm(messages[type], isEditing ? "G\u00fcncelle" : "Kaydet", "\u0130ptal"))) return;
    try {
      if (isEditing) {
        await api(`/api/${type}/${editing.id}`, { method: "PUT", body: JSON.stringify(data) });
        showMessage(`${formViewMeta(type, hurdaMode).title} g\u00fcncellendi.`);
      } else {
        const saved = await api(`/api/${type}`, { method: "POST", body: JSON.stringify(data) });
        showMessage(`${formViewMeta(type, hurdaMode).title} kaydedildi. Has: ${formatValue("has", saved.has)}`);
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

function formViewMeta(type, hurdaMode = null) {
  if (type === "hurda") return hurdaMode === "SATIS" ? views.hurda_satis : views.hurda_alis;
  return views[type] || { title: "Kay\u0131t" };
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

function showSelectedPurchase(label, row, includeMilyem = false) {
  const remaining = document.createElement("strong");
  remaining.className = "purchase-remaining";
  remaining.textContent = `${row.kalan_gram} gr`;
  const prefix = `Se\u00e7ilen: ${row.cinsi} ${row.ayar} | ${includeMilyem ? `Al\u0131\u015f milyem ${row.milyem} | ` : ""}`;
  label.replaceChildren(document.createTextNode(`${prefix}Kalan `), remaining, document.createTextNode(` / ${row.kalan_has} has`));
}

async function openPurchaseModal(form, chosenLabel) {
  try {
    const rows = await api("/api/satis/urun-secenekleri");
    if (!rows.length) { showMessage("Se\u00e7ilebilir al\u0131\u015f kayd\u0131 yok.", true); return; }
    openSelectableModal("Al\u0131\u015ftan \u00dcr\u00fcn Se\u00e7", ["tarih", "tedarikci", "cinsi", "ayar", "kalan_gram", "alis_milyem"], rows, (row) => {
      state.selectedPurchase = row;
      form.elements.purchase_id.value = row.id;
      form.elements.alis_id.value = row.id;
      form.elements.cinsi.value = row.cinsi;
      form.elements.ayar.value = row.ayar;
      form.elements.alis_milyem.value = row.alis_milyem;
      if (form.elements.alis_has_maliyeti) form.elements.alis_has_maliyeti.value = row.alis_has_maliyeti || "";
      form.elements.satis_milyem.value = "";
      form.elements.satis_milyem.placeholder = "Sat\u0131\u015f milyem girin";
      showSelectedPurchase(chosenLabel, row);
    });
  } catch (error) { showMessage(error.message, true); }
}

async function openHurdaPurchaseModal(form, chosenLabel) {
  try {
    if (form.elements.islem_turu) { form.elements.islem_turu.value = "SATIS"; form.elements.islem_turu.dispatchEvent(new Event("change")); }
    const rows = await api("/api/hurda/urun-secenekleri");
    if (!rows.length) { showMessage("Se\u00e7ilebilir hurda al\u0131\u015f kayd\u0131 yok.", true); return; }
    openSelectableModal("Hurda Al\u0131\u015ftan Se\u00e7", ["tarih", "kisi", "cinsi", "ayar", "kalan_gram", "milyem", "has", "kalan_has"], rows, (row) => {
      state.selectedHurdaPurchase = row;
      form.elements.hurda_alis_id.value = row.id;
      form.elements.cinsi.value = row.cinsi;
      form.elements.ayar.value = row.ayar;
      if (form.elements.alis_milyem) form.elements.alis_milyem.value = row.milyem;
      form.elements.milyem.value = "";
      form.elements.milyem.placeholder = "Sat\u0131\u015f milyem girin";
      showSelectedPurchase(chosenLabel, row);
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
    td.dataset.label = "Se\u00e7";
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

function valueOrFallback(value, fallback) {
  return value === null || value === undefined || value === "" ? fallback : value;
}

function enrichHurdaRows(rows) {
  const allRows = rows || [];
  const purchases = new Map(allRows.filter((row) => normalize(row.islem_turu).startsWith("alis")).map((row) => [Number(row.id), row]));
  const saleTotalsByPurchase = new Map();
  allRows.forEach((row) => {
    if (!normalize(row.islem_turu).startsWith("satis")) return;
    const purchaseId = Number(row.hurda_alis_id || 0);
    if (!purchaseId) return;
    const current = saleTotalsByPurchase.get(purchaseId) || { gram: 0, has: 0 };
    current.gram += parseNum(row.gram);
    current.has += parseNum(row.has);
    saleTotalsByPurchase.set(purchaseId, current);
  });

  return allRows.map((row) => {
    if (!normalize(row.islem_turu).startsWith("satis")) return row;
    const purchase = purchases.get(Number(row.hurda_alis_id));
    const totals = saleTotalsByPurchase.get(Number(row.hurda_alis_id)) || { gram: 0, has: 0 };
    const alisMilyem = Number(valueOrFallback(row.alis_milyem, purchase.milyem || 0));
    const satisMilyem = Number(valueOrFallback(row.satis_milyem, row.milyem || 0));
    const milyemFarki = Number(valueOrFallback(row.milyem_farki, satisMilyem - alisMilyem));
    const milyemKari = Number(valueOrFallback(row.milyem_kari, parseNum(row.gram) * milyemFarki / 1000));
    const kalanGram = valueOrFallback(row.kalan_gram, purchase ? parseNum(purchase.gram) - totals.gram : "");
    const kalanHas = valueOrFallback(row.kalan_has, purchase ? parseNum(purchase.has) - totals.has : "");
    return {
      ...row,
      alis_milyem: alisMilyem,
      satis_milyem: satisMilyem,
      milyem_farki: milyemFarki,
      milyem_kari: milyemKari,
      has_kari: valueOrFallback(row.has_kari, milyemKari),
      kalan_gram: kalanGram,
      kalan_has: kalanHas,
    };
  });
}function filteredRows(rows) {
  const needle = normalize(state.search);
  if (!needle) return rows;
  return rows.filter((row) => normalize(Object.values(row).join(" ")).includes(needle));
}

function iconSvg(kind) {
  if (kind === "view") return '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7S2 12 2 12Z"></path><circle cx="12" cy="12" r="3"></circle></svg>';
  if (kind === "close") return '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="m6 6 12 12M18 6 6 18"></path></svg>';
  if (kind === "edit") return '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 20h4l10.5-10.5a2.1 2.1 0 0 0 0-3L17.5 5.5a2.1 2.1 0 0 0-3 0L4 16v4Z"></path><path d="M13.5 7.5l3 3"></path></svg>';
  return '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 7h16"></path><path d="M10 11v6"></path><path d="M14 11v6"></path><path d="M6 7l1 14h10l1-14"></path><path d="M9 7V4h6v3"></path></svg>';
}

function columnLabel(type, col) {
  return labels[col] || col;
}

function renderTable(type, rows, title = "", applySearch = true) {
  const section = document.createElement("section");
  section.className = "table-section";
  if (title) {
    const h = document.createElement("h2"); h.textContent = title;
    if (["stok", "hurdaStok"].includes(type)) {
      const header = document.createElement("div"); header.className = "stock-table-heading";
      const summary = document.createElement("div"); summary.className = "stock-heading-summary";
      [["gram", "Toplam gram", "gr"], ["has", "Toplam has", "has"]].forEach(([key, label, unit]) => {
        const metric = document.createElement("span");
        const amount = document.createElement("strong"); amount.dataset.stockTotal = key;
        const total = (rows || []).reduce((sum, row) => sum + Number(row[`kalan_${key}`] || 0), 0);
        amount.textContent = `${formatValue(key, total)} ${unit}`;
        const caption = document.createElement("span"); caption.className = "stock-summary-label"; caption.textContent = label;
        metric.append(caption, amount); summary.appendChild(metric);
      });
      header.append(h, summary); section.appendChild(header);
    } else section.appendChild(h);
  }
  if (["stok", "hurdaStok"].includes(type)) rows = (rows || []).filter(row => Number(row.kalan_gram) !== 0);
  rows = applySearch ? filteredRows(rows || []) : (rows || []);
  section.dataset.tableType = type;
  if (["kisiCari", "musteriCari", "tedarikciCari", "cariOdeme"].includes(type)) section.classList.add("cari-table");
  const wrap = document.createElement("div");
  wrap.className = "table-wrap";
  if (!rows.length) { wrap.innerHTML = '<div class="empty">Kay\u0131t yok.</div>'; section.appendChild(wrap); return section; }
  const cols = columns[type];
  const actionType = type === "hurdaAlis" || type === "hurdaSatis" ? "hurda" : type;
  const table = document.createElement("table");
  table.innerHTML = `<thead><tr>${cols.map((col) => `<th>${columnLabel(type, col)}</th>`).join("")}${["giderler", "alis", "satis", "hurda", "hurdaAlis", "hurdaSatis", "kisiCari", "musteriCari", "tedarikciCari", "cariOdeme"].includes(type) ? "<th>\u0130\u015flemler</th>" : ""}</tr></thead>`;
  const tbody = document.createElement("tbody");
  rows.forEach((row) => {
    const tr = document.createElement("tr");
    cols.forEach((col) => {
      const td = document.createElement("td");
      td.dataset.label = columnLabel(type, col);
      td.dataset.col = col;
      td.textContent = formatValue(col, row[col]);
      if (moneyFields.has(col) || numberFields.has(col)) td.className = "num";
      if (["stok", "hurdaStok"].includes(type) && ["kalan_gram", "kalan_has"].includes(col)) td.classList.add("stock-priority");
      if (col === "net_bakiye_has") {
        td.classList.add("cari-net-balance", Number(row[col]) > 0 ? "pos" : Number(row[col]) < 0 ? "neg" : "balance-zero");
      } else if (["milyem_farki", "has_kari", "milyem_kari"].includes(col)) td.classList.add(Number(row[col]) >= 0 ? "pos" : "neg");
      tr.appendChild(td);
    });
    if (["kisiCari", "musteriCari", "tedarikciCari"].includes(type)) {
      const td = document.createElement("td");
      td.className = "actions-cell";
      td.dataset.label = "\u0130\u015flemler";
      const menu = document.createElement("button");
      menu.type = "button";
      menu.className = "icon-btn icon-edit kebab-btn";
      menu.title = "Cari i\u015flemleri";
      menu.setAttribute("aria-label", "Cari i\u015flemleri");
      menu.textContent = "\u22ee";
      menu.onclick = () => openCariActions(row, state.cariData || { kisiler: [] });
      const detail = document.createElement("button"); detail.type = "button";
      detail.className = "icon-btn icon-detail cari-detail-btn"; detail.innerHTML = iconSvg("view");
      detail.title = "Cari detay\u0131n\u0131 g\u00f6ster"; detail.setAttribute("aria-label", detail.title);
      detail.onclick = () => openCariDetail(row.isim || row.musteri_adi || row.tedarikci_adi);
      td.append(detail, menu);
      tr.appendChild(td);
    }
    if (type === "cariOdeme") {
      const td = document.createElement("td");
      td.className = "actions-cell";
      td.dataset.label = "\u0130\u015flemler";
      const edit = document.createElement("button");
      edit.type = "button";
      edit.className = "icon-btn icon-edit";
      edit.title = "\u00d6demeyi d\u00fczenle";
      edit.innerHTML = iconSvg("edit");
      edit.onclick = () => openCariPaymentModal(state.cariData || { kisiler: [] }, row.isim, row);
      const del = document.createElement("button");
      del.type = "button";
      del.className = "icon-btn icon-delete";
      del.title = "\u00d6demeyi sil";
      del.innerHTML = iconSvg("delete");
      del.onclick = async () => { if (await showConfirm("Bu cari \u00f6deme kayd\u0131 silinsin mi", "Sil", "\u0130ptal")) { try { await api(`/api/cari/odeme/${row.id}`, { method: "DELETE" }); render(); } catch (error) { showMessage(error.message, true); } } };
      const detail = document.createElement("button"); detail.type = "button";
      detail.className = "icon-btn icon-detail cari-detail-btn"; detail.innerHTML = iconSvg("view");
      detail.title = "Cari detay\u0131n\u0131 g\u00f6ster"; detail.setAttribute("aria-label", detail.title);
      detail.onclick = () => openCariDetail(row.isim);
      td.append(detail, edit, del);
      tr.appendChild(td);
    }
    if (["giderler", "alis", "satis", "hurda", "hurdaAlis", "hurdaSatis"].includes(type)) {
      const td = document.createElement("td");
      td.className = "actions-cell";
      td.dataset.label = "\u0130\u015flemler";
      const edit = document.createElement("button");
      edit.type = "button";
      edit.className = "icon-btn icon-edit";
      edit.title = "D\u00fczenle";
      edit.setAttribute("aria-label", "D\u00fczenle");
      edit.innerHTML = iconSvg("edit");
      edit.onclick = () => startEdit(actionType, row);
      const del = document.createElement("button");
      del.type = "button";
      del.className = "icon-btn icon-delete";
      del.title = "Sil";
      del.setAttribute("aria-label", "Sil");
      del.innerHTML = iconSvg("delete");
      del.onclick = async () => { if (await showConfirm("Bu kayd\u0131 silmek istedi\u011finize emin misiniz", "Sil", "\u0130ptal")) { try { await api(`/api/${actionType}/${row.id}`, { method: "DELETE" }); render(); } catch (error) { showMessage(error.message, true); } } };
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

async function startEdit(type, row) {
  editing = { type, id: row.id };
  state.selectedPurchase = null;
  state.selectedHurdaPurchase = null;
  await render();
  setTimeout(() => {
    const form = document.querySelector(".entry-form");
    if (!form) return;
    Object.entries(row).forEach(([key, value]) => { if (form.elements[key]) form.elements[key].value = value ?? ""; });
    form.elements.islem_turu?.dispatchEvent(new Event("change"));
    if (form.elements.notlar) form.elements.notlar.value = row.notlar ?? row.not ?? "";
    if (type === "satis") {
      const selectedId = row.purchase_id || row.alis_id;
      state.selectedPurchase = selectedId ? { id: selectedId, has_fiyati: row.has_fiyati || 0 } : null;
      form.elements.purchase_id.value = selectedId || "";
      form.elements.alis_id.value = selectedId || "";
      form.elements.satis_milyem.value = row.satis_milyem || row.milyem || "";
    }
    if (type !== "giderler") syncTransactionPayment(form);
    if (type === "hurda") {
      const selectedHurdaId = row.hurda_alis_id || "";
      state.selectedHurdaPurchase = selectedHurdaId ? { id: selectedHurdaId } : null;
      if (form.elements.hurda_alis_id) form.elements.hurda_alis_id.value = selectedHurdaId;
    }
    form._refreshPaymentSummary?.();
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
  if (!(await showConfirm("T\u00fcm verileri JSON olarak indirmek istiyor musunuz", "D\u0131\u015fa Aktar", "\u0130ptal"))) return;
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

async function createDatabaseBackup() {
  try {
    const result = await api("/api/backup", { method: "POST" });
    showMessage(`Yedek oluşturuldu: ${result.file}`);
  } catch (error) {
    showMessage(error.message || "Yedek oluşturulamadı.", true);
  }
}

async function restoreLatestDatabaseBackup() {
  const confirmed = await showConfirm(
    "En son veritabanı yedeği geri yüklenecek. Mevcut veriler önce ayrıca yedeklenecek. Devam edilsin mi",
    "Geri Yükle",
    "İptal",
  );
  if (!confirmed) return;
  try {
    const result = await api("/api/restore-latest", { method: "POST" });
    showMessage(`Yedek geri yüklendi: ${result.restored_from}`);
    await refreshSuggestions();
    await render();
  } catch (error) {
    showMessage(error.message || "Yedek geri yüklenemedi.", true);
  }
}

function renderCariPaymentForm(data) {
  const panel = document.createElement("section");
  panel.className = "panel form-panel cari-payment-panel";
  const form = document.createElement("form");
  form.className = "entry-form cari-payment-form";
  const people = data.kisiler || [];
  let selectedPaymentType = "HAS";

  const makeField = (labelText, input) => {
    const label = document.createElement("label");
    label.className = "field field-main";
    label.append(labelText, input);
    return label;
  };

  const dateInput = document.createElement("input");
  dateInput.type = "date";
  dateInput.name = "tarih";
  dateInput.value = today();

  const personSelect = document.createElement("select");
  personSelect.name = "isim";
  personSelect.required = true;
  personSelect.innerHTML = `<option value="">Cari ki\u015fi/firma se\u00e7</option>${people.map((row) => `<option value="${row.isim}">${row.isim} | Kalan ${formatValue("has", row.kalan_has)} has</option>`).join("")}`;

  const directionSelect = document.createElement("select");
  directionSelect.name = "yon";
  directionSelect.innerHTML = '<option value="TAHSILAT">M\u00fc\u015fteriden Tahsilat</option><option value="ODEME">Tedarik\u00e7iye \u00d6deme</option>';

  const typeInput = document.createElement("input");
  typeInput.type = "hidden";
  typeInput.name = "odeme_tipi";
  typeInput.value = selectedPaymentType;

  const paymentTabs = document.createElement("div");
  paymentTabs.className = "payment-type-tabs cari-payment-tabs";
  [
    ["HAS", "Has ile \u00d6deme"],
    ["ADET_GRAM_MILYEM", "Gram + Milyem"],
    ["TAM_KAPAT", "Borcu Tam Kapat"],
  ].forEach(([value, label]) => {
    const tab = document.createElement("button");
    tab.type = "button";
    tab.className = "payment-type-tab";
    tab.dataset.value = value;
    tab.textContent = label;
    tab.onclick = () => {
      selectedPaymentType = value;
      typeInput.value = value;
      updateMode();
    };
    paymentTabs.appendChild(tab);
  });

  const paidInput = document.createElement("input");
  paidInput.name = "odenen_has";
  paidInput.inputMode = "decimal";
  paidInput.placeholder = "\u00d6denen has";

  const gramInput = document.createElement("input");
  gramInput.name = "gram";
  gramInput.inputMode = "decimal";
  gramInput.placeholder = "Gram";

  const milyemInput = document.createElement("input");
  milyemInput.name = "milyem";
  milyemInput.inputMode = "decimal";
  milyemInput.placeholder = "Milyem";

  const calcBox = document.createElement("div");
  calcBox.className = "has-preview cari-payment-preview field-note";
  calcBox.innerHTML = `<div class="cari-has-card"><span>Hesaplanan Has</span><strong data-calc-has>0</strong></div><div class="cari-has-card"><span>Kalan Has</span><strong data-kalan-has>0</strong></div>`;

  const noteInput = document.createElement("textarea");
  noteInput.name = "notlar";
  noteInput.rows = 1;
  noteInput.maxLength = 200;

  const paidField = makeField("\u00d6denen Has", paidInput);
  const gramField = makeField("Gram", gramInput);
  const milyemField = makeField("Milyem", milyemInput);
  paidField.classList.add("payment-fill-field", "cari-paid-field");
  gramField.classList.add("payment-fill-field", "cari-product-payment-field", "payment-gram-field");
  milyemField.classList.add("payment-fill-field", "cari-product-payment-field", "payment-milyem-field");
  const noteField = makeField("Not", noteInput);
  noteField.classList.add("field-note", "cari-note-field");

  form.append(
    (() => { const field = makeField("Tarih", dateInput); field.classList.add("cari-date-field"); return field; })(),
    (() => { const field = makeField("Cari Ki\u015fi / Firma", personSelect); field.classList.add("cari-person-field"); return field; })(),
    makeField("\u0130\u015flem Y\u00f6n\u00fc", directionSelect),
    typeInput,
    paymentTabs,
    paidField,
    gramField,
    milyemField,
    calcBox,
    noteField,
  );

  const actions = document.createElement("div");
  actions.className = "form-bottom-actions";
  const save = document.createElement("button");
  save.type = "submit";
  save.textContent = "\u00d6deme Ekle";
  actions.appendChild(save);
  form.appendChild(actions);

  const selectedCari = () => people.find((row) => normalize(row.isim) === normalize(personSelect.value));
  const selectedCariKalanHas = () => parseNum(selectedCari()?.kalan_has);
  const calculatedHas = () => {
    if (selectedPaymentType === "ADET_GRAM_MILYEM") return parseNum(gramInput.value) * parseNum(milyemInput.value) / 1000;
    if (selectedPaymentType === "TAM_KAPAT") return Math.abs(selectedCariKalanHas());
    return parseNum(paidInput.value);
  };
  function updateMode() {
    paymentTabs.querySelectorAll(".payment-type-tab").forEach((tab) => tab.classList.toggle("active", tab.dataset.value === selectedPaymentType));
    paidField.classList.toggle("payment-inactive", selectedPaymentType !== "HAS");
    paidInput.disabled = selectedPaymentType !== "HAS";
    [gramField, milyemField].forEach((field) => field.classList.toggle("payment-inactive", selectedPaymentType !== "ADET_GRAM_MILYEM"));
    [gramInput, milyemInput].forEach((input) => input.disabled = selectedPaymentType !== "ADET_GRAM_MILYEM");
    calcBox.classList.toggle("payment-inactive", selectedPaymentType === "HAS");
    if (selectedPaymentType === "TAM_KAPAT") paidInput.value = formatValue("has", Math.abs(selectedCariKalanHas())).replaceAll(".", "").replace(",", ".");
    calcBox.querySelector("[data-calc-has]").textContent = formatValue("has", calculatedHas());
    const projected = selectedCariKalanHas() + (directionSelect.value === "ODEME" ? calculatedHas() : -calculatedHas());
    calcBox.querySelector("[data-kalan-has]").textContent = formatValue("net_bakiye_has", projected);
  }

  [paidInput, gramInput, milyemInput].forEach(attachDecimalGuard);
  [personSelect, directionSelect, paidInput, gramInput, milyemInput].forEach((input) => input.addEventListener("input", updateMode));
  personSelect.addEventListener("change", () => {
    directionSelect.value = selectedCariKalanHas() < 0 ? "ODEME" : "TAHSILAT";
    updateMode();
  });
  updateMode();

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    if (!personSelect.value) { showMessage("Cari ki\u015fi/firma se\u00e7in.", true); return; }
    try {
      if (selectedPaymentType === "HAS") positiveValue(paidInput, "\u00d6denen has");
      if (selectedPaymentType === "ADET_GRAM_MILYEM") {
        positiveValue(gramInput, "Gram");
        positiveValue(milyemInput, "Milyem");
      }
      if (selectedPaymentType === "TAM_KAPAT" && calculatedHas() <= 0) throw new Error("Kapat\u0131lacak has bulunamad\u0131.");
    } catch (error) {
      showMessage(error.message, true);
      return;
    }
    typeInput.value = selectedPaymentType;
    const payload = Object.fromEntries(new FormData(form).entries());
    if (payload.odeme_tipi === "ADET_GRAM_MILYEM") payload.odenen_has = String(calculatedHas());
    if (payload.odeme_tipi === "TAM_KAPAT") payload.odenen_has = String(calculatedHas());
    if (!(await showConfirm("Cari \u00f6deme kaydedilsin mi", "Kaydet", "\u0130ptal"))) return;
    try {
      const editId = form.dataset.editPaymentId;
      await api(editId ? `/api/cari/odeme/${editId}` : "/api/cari/odeme", { method: editId ? "PUT" : "POST", body: JSON.stringify(payload) });
      showMessage(editId ? "Cari \u00f6deme g\u00fcncellendi." : "Cari \u00f6deme kaydedildi.");
      render();
    } catch (error) { showMessage(error.message, true); }
  });

  panel.appendChild(form);
  return panel;
}
function openCariPaymentModal(data, personName = "", payment = null) {
  const overlay = document.createElement("div");
  overlay.className = "modal";
  const box = document.createElement("div");
  box.className = "modal-box payment-modal cari-person-modal";
  const title = document.createElement("div");
  title.className = "modal-title";
  title.innerHTML = `<h2>${payment ? "\u00d6deme Bilgisini D\u00fczenle" : "\u00d6deme Bilgisi"}</h2>`;
  const close = document.createElement("button");
  close.type = "button";
  close.className = "icon-btn cari-dialog-close";
  close.innerHTML = iconSvg("close");
  close.title = "Kapat"; close.setAttribute("aria-label", "Kapat");
  close.onclick = () => overlay.remove();
  title.appendChild(close);
  const panel = renderCariPaymentForm(data);
  const form = panel.querySelector("form");
  box.append(title, panel);
  overlay.appendChild(box);
  document.body.appendChild(overlay);

  if (personName && form.elements.isim) {
    form.elements.isim.value = personName;
    form.elements.isim.dispatchEvent(new Event("change"));
  }
  if (payment) {
    form.elements.tarih.value = payment.tarih || today();
    form.elements.isim.value = payment.isim || personName;
    form.elements.notlar.value = payment.not || payment.notlar || "";
    form.elements.odenen_has.value = paymentDisplayValue(payment.odenen_has);
    form.elements.gram.value = paymentDisplayValue(payment.gram);
    form.elements.milyem.value = paymentDisplayValue(payment.milyem);
    form.elements.yon.value = payment.yon || "TAHSILAT";
    const tab = form.querySelector(`.payment-type-tab[data-value="${payment.odeme_tipi || "HAS"}"]`);
    tab.click();
    const save = form.querySelector('button[type="submit"]');
    if (save) save.textContent = "\u00d6demeyi G\u00fcncelle";
    form.dataset.editPaymentId = payment.id;
  }

  form.addEventListener("submit", () => setTimeout(() => overlay.remove(), 150), true);
}

function renameCariPerson(oldName) {
  const overlay = document.createElement("div");
  overlay.className = "modal";
  const box = document.createElement("div");
  box.className = "modal-box cari-rename-modal";
  const title = document.createElement("div");
  title.className = "modal-title";
  title.innerHTML = `<h2>\u0130sim De\u011fi\u015ftir</h2><p>${oldName}</p>`;
  const input = document.createElement("input");
  input.type = "text";
  input.value = oldName;
  input.className = "rename-input";
  input.placeholder = "Yeni cari ad\u0131";
  const actions = document.createElement("div");
  actions.className = "form-bottom-actions";
  const cancel = document.createElement("button");
  cancel.type = "button";
  cancel.className = "secondary";
  cancel.textContent = "\u0130ptal";
  cancel.onclick = () => overlay.remove();
  const save = document.createElement("button");
  save.type = "button";
  save.textContent = "G\u00fcncelle";
  save.onclick = async () => {
    const yeni = input.value.trim();
    if (!yeni) { showMessage("Yeni cari ad\u0131 girin.", true); return; }
    if (normalize(yeni) === normalize(oldName)) { overlay.remove(); return; }
    if (!(await showConfirm("Cari ad\u0131 g\u00fcncellensin mi", "G\u00fcncelle", "\u0130ptal"))) return;
    try {
      await api("/api/cari/kisi", { method: "PUT", body: JSON.stringify({ eski_isim: oldName, yeni_isim: yeni }) });
      showMessage("Cari ad\u0131 g\u00fcncellendi.");
      overlay.remove();
      render();
    } catch (error) { showMessage(error.message, true); }
  };
  input.addEventListener("keydown", (event) => { if (event.key === "Enter") save.click(); });
  actions.append(cancel, save);
  box.append(title, input, actions);
  overlay.appendChild(box);
  document.body.appendChild(overlay);
  input.focus();
  input.select();
}

async function deleteCariPerson(name) {
  if (!(await showConfirm(`${name} carisini ve ba\u011fl\u0131 kay\u0131tlar\u0131 silmek istiyor musunuz`, "Sil", "\u0130ptal"))) return;
  try {
    await api("/api/cari/kisi/sil", { method: "POST", body: JSON.stringify({ isim: name }) });
    showMessage("Cari silindi.");
    render();
  } catch (error) { showMessage(error.message, true); }
}

async function openCariDetail(name) {
  if (document.querySelector(".cari-detail-modal")) return;
  const opener = document.activeElement;
  const overlay = document.createElement("div"); overlay.className = "modal cari-detail-modal";
  const box = document.createElement("div"); box.className = "modal-box cari-detail-box";
  box.setAttribute("role", "dialog"); box.setAttribute("aria-modal", "true");
  box.setAttribute("aria-label", `${name} cari detay\u0131`); box.tabIndex = -1;
  const head = document.createElement("div"); head.className = "modal-title";
  const title = document.createElement("h2"); title.textContent = name;
  const close = document.createElement("button"); close.type = "button"; close.className = "icon-btn cari-detail-close"; close.innerHTML = iconSvg("close");
  close.title = "Kapat"; close.setAttribute("aria-label", "Cari detay\u0131n\u0131 kapat");
  const dismiss = () => { overlay.remove(); if (opener?.isConnected) opener.focus(); };
  close.onclick = dismiss; head.append(title, close);
  const body = document.createElement("div"); body.className = "cari-detail-body"; body.textContent = "\u0130\u015flemler y\u00fckleniyor...";
  box.append(head, body); overlay.appendChild(box); document.body.appendChild(overlay); close.focus();
  overlay.addEventListener("click", event => { if (event.target === overlay) dismiss(); });
  overlay.addEventListener("keydown", event => {
    if (event.key === "Escape") { event.preventDefault(); dismiss(); }
    if (event.key === "Tab") {
      const focusable = [...box.querySelectorAll("button, [href], input, select, textarea, [tabindex='0']")];
      const first = focusable[0], last = focusable[focusable.length - 1];
      if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last.focus(); }
      else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus(); }
    }
  });
  try {
    const [purchases, sales, scrap, accounts] = await Promise.all([api("/api/alis"), api("/api/satis"), api("/api/hurda"), api("/api/cari")]);
    if (!overlay.isConnected) return;
    const person = (accounts.kisiler || []).find(row => normalize(row.isim) === normalize(name));
    if (!person) throw new Error("Cari bulunamad\u0131.");
    const history = [];
    const addTransactions = (rows, nameKey, isSale, source) => rows.filter(row => normalize(row[nameKey]) === normalize(name)).forEach(row => {
      history.push({ tarih: row.tarih, hareket: isSale ? "Sat\u0131\u015f" : "Al\u0131\u015f", kaynak: source, gram: row.gram, has: row.has, not: row.not ?? row.notlar ?? "", id: row.id });
      if (Number(row.odenen_has) > 0) history.push({ tarih: row.tarih, hareket: isSale ? "Tahsilat" : "\u00d6deme", kaynak: `${source} #${row.id}`, gram: null, has: row.odenen_has, not: "\u0130\u015flem s\u0131ras\u0131nda", id: row.id });
    });
    addTransactions(purchases || [], "tedarikci", false, "Normal");
    addTransactions(sales || [], "musteri", true, "Normal");
    addTransactions((scrap.kayitlar || []).filter(row => normalize(row.islem_turu) === "alis"), "kisi", false, "Hurda");
    addTransactions((scrap.kayitlar || []).filter(row => normalize(row.islem_turu) === "satis"), "kisi", true, "Hurda");
    (accounts.odemeler || []).filter(row => normalize(row.isim) === normalize(name)).forEach(row => history.push({ tarih: row.tarih, hareket: row.yon === "ODEME" ? "\u00d6deme" : "Tahsilat", kaynak: "Cari", gram: null, has: row.odenen_has, not: row.not ?? row.notlar ?? "", id: row.id }));
    history.sort((a, b) => String(b.tarih).localeCompare(String(a.tarih)) || Number(b.id) - Number(a.id));
    const balance = document.createElement("p"); balance.className = `cari-detail-balance ${person.net_bakiye_has > 0 ? "pos" : person.net_bakiye_has < 0 ? "neg" : "balance-zero"}`;
    balance.textContent = `Net Has Bakiyesi: ${formatValue("net_bakiye_has", person.net_bakiye_has)} has`;
    const totals = renderCards([["Sat\u0131\u015f Has", person.toplam_satis_has, "has"], ["Al\u0131\u015f Has", person.toplam_alis_has, "has"], ["Tahsilat Has", person.tahsil_edilen_has, "has"], ["\u00d6deme Has", person.odedigimiz_has, "has"]]);
    body.replaceChildren(balance, totals, renderTable("cariHistory", history, "\u0130\u015flem Ge\u00e7mi\u015fi", false));
  } catch (error) { if (overlay.isConnected) body.textContent = error.message; }
}

function openCariActions(row, data) {
  const overlay = document.createElement("div");
  overlay.className = "modal";
  const box = document.createElement("div");
  box.className = "modal-box cari-actions-modal";
  const title = document.createElement("div");
  title.className = "modal-title cari-actions-title";
  title.innerHTML = `<h2>${row.isim}</h2><p>Sat\u0131\u015f ${formatValue("has", row.toplam_satis_has)} | Al\u0131\u015f ${formatValue("has", row.toplam_alis_has)} | Net ${formatValue("net_bakiye_has", row.net_bakiye_has)} has</p>`;
  const actions = document.createElement("div");
  actions.className = "cari-action-list";
  const items = [
    ["\u00d6deme Bilgilerini De\u011fi\u015ftir", () => openCariPaymentModal(data, row.isim)],
    ["\u0130sim De\u011fi\u015ftir", () => renameCariPerson(row.isim)],
    ["Ki\u015fiyi Sil", () => deleteCariPerson(row.isim), "danger"],
  ];
  items.forEach(([label, fn, tone]) => {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = `cari-action-btn ${tone || ""}`;
    btn.textContent = label;
    btn.onclick = () => { overlay.remove(); fn(); };
    actions.appendChild(btn);
    if (tone === "danger") {
      const note = document.createElement("small");
      note.className = "cari-danger-note";
      note.textContent = "Dikkat: Bu ki\u015fiye ba\u011fl\u0131 al\u0131\u015f, sat\u0131\u015f, hurda ve \u00f6deme kay\u0131tlar\u0131 da silinir.";
      actions.appendChild(note);
    }
  });
  const close = document.createElement("button");
  close.type = "button";
  close.className = "icon-btn cari-dialog-close";
  close.innerHTML = iconSvg("close");
  close.title = "Kapat"; close.setAttribute("aria-label", "Kapat");
  close.onclick = () => overlay.remove();
  title.appendChild(close);
  box.append(title, actions);
  overlay.appendChild(box);
  document.body.appendChild(overlay);
}
function renderProfitSummary(data) {
  const panel = document.createElement("aside"); panel.className = "expense-profit-summary";
  const title = document.createElement("h2"); title.textContent = "Milyem K\u00e2r\u0131 \u00d6zeti";
  const note = document.createElement("p"); note.textContent = "T\u00fcm zamanlar \u00b7 Normal + hurda \u00b7 Has";
  panel.append(title, note);
  [["Toplam Milyem K\u00e2r\u0131", data.genel_milyem_kari, "neutral"],
   ["Toplam Gider", data.toplam_gider, "warn"],
   ["Kalan Net K\u00e2r", data.net_kar, data.net_kar < 0 ? "warn" : "good"]].forEach(([label, value, tone]) => {
    const card = renderMetricCard(label, value, "has", tone);
    card.classList.add("expense-summary-card"); panel.appendChild(card);
  });
  const formula = document.createElement("small"); formula.textContent = "Net k\u00e2r = toplam milyem k\u00e2r\u0131 \u2212 giderler"; panel.appendChild(formula);
  return panel;
}

function renderExpenseForm() {
  const panel = document.createElement("section"); panel.className = "panel form-panel expense-form-panel";
  const heading = document.createElement("h2"); heading.textContent = editing?.type === "giderler" ? "Gideri d\u00fczenle" : "Yeni gider";
  const note = document.createElement("p"); note.className = "hint"; note.textContent = "Giderleri has olarak girin. Stok de\u011fi\u015fmez; giderler toplam milyem k\u00e2r\u0131ndan d\u00fc\u015f\u00fcl\u00fcr.";
  panel.append(heading, note);
  const form = document.createElement("form"); form.className = "entry-form expense-form";
  forms.giderler.forEach(([name, label, type]) => {
    const wrap = document.createElement("label"); wrap.className = "field field-main";
    wrap.dataset.field = name;
    const input = fieldElement(name, type); input.name = name; input.required = name !== "notlar";
    if (name === "tutar") input.placeholder = "0,000";
    if (name === "notlar") { input.rows = 2; input.maxLength = 1000; input.placeholder = "Giderle ilgili k\u0131sa bir not..."; }
    if (name === "tarih") input.value = today();
    if (name === "kategori") {
      input.setAttribute("list", "expenseCategories");
      const list = document.createElement("datalist"); list.id = "expenseCategories";
      ["Ara\xe7 / yak\u0131t", "U\xe7ak bileti", "\xc7al\u0131\u015fan \xf6demesi", "Kargo / ula\u015f\u0131m", "Yemek", "Konaklama", "Ki\u015fisel", "Di\u011fer i\u015fletme giderleri"].forEach(value => {
        const option = document.createElement("option"); option.value = value; list.appendChild(option);
      }); wrap.appendChild(list);
    }
    wrap.append(label, input); form.appendChild(wrap);
  });
  const save = document.createElement("button"); save.type = "submit";
  save.textContent = editing?.type === "giderler" ? "G\xfcncelle" : "Kaydet";
  const cancel = document.createElement("button"); cancel.type = "button"; cancel.textContent = "Vazge\xe7";
  cancel.onclick = () => { editing = null; render(); };
  const actions = document.createElement("div"); actions.className = "form-bottom-actions"; actions.append(save, cancel); cancel.className = "secondary";
  form.appendChild(actions);
  form.onsubmit = async event => {
    event.preventDefault();
    const data = Object.fromEntries(new FormData(form).entries()); data.tutar = String(data.tutar).replace(",", ".");
    const id = editing?.type === "giderler" ? editing.id : null;
    try {
      await api(`/api/giderler${id ? `/${id}` : ""}`, { method: id ? "PUT" : "POST", body: JSON.stringify(data) });
      editing = null; await render(); showMessage("Gider kaydedildi.");
    } catch (error) { showMessage(error.message, true); }
  };
  panel.appendChild(form); return panel;
}

function renderDashboard(data) {
  const root = document.createElement("div");
  root.className = "dashboard-root dashboard-restored";

  const hero = document.createElement("section");
  hero.className = "dashboard-hero";
  const heroMetrics = document.createElement("div");
  heroMetrics.className = "dashboard-hero-metrics";
  [
    ["Genel Milyem K\u00e2r\u0131", data.genel_urun_kari, "has", "good", "Normal sat\u0131\u015flardan"],
    ["G\u00fcnl\u00fck Milyem K\u00e2r\u0131", data.gunluk_urun_kari, "has", "good", data.gunluk_tarih ? `Tarih: ${data.gunluk_tarih}` : "G\u00fcnl\u00fck hareket"],
    ["Normal Stok Has", data.normal_stok_has, "has", "neutral", "\u00dcr\u00fcn sto\u011fu"],
    ["Hurda Kalan Has", data.hurda_kalan_has, "has", "accent", "Hurda sto\u011fu"],
  ].forEach((card) => heroMetrics.appendChild(renderMetricCard(...card)));
  hero.appendChild(heroMetrics);

  const topGroups = document.createElement("div");
  topGroups.className = "dashboard-groups dashboard-groups-polished dashboard-groups-top";
  const bottomGroups = document.createElement("div");
  bottomGroups.className = "dashboard-groups dashboard-groups-polished dashboard-groups-bottom";
  const stock = renderDashboardPanel("Stok \u00d6zeti", "", []);
  stock.classList.add("dashboard-stock-summary");
  const stockGrid = stock.querySelector(".dashboard-panel-grid");
  stockGrid.className = "dashboard-stock-sections";
  [
    ["Normal stok", [
      ["Normal Stok Gram", data.normal_stok_gram, "gram", "neutral"],
      ["Normal Stok Has", data.normal_stok_has, "has", "accent"],
    ]],
    ["Hurda", [
      ["Hurda Stok Gram", data.hurda_kalan_gram, "gram", "neutral"],
      ["Hurda Kalan Has", data.hurda_kalan_has, "has", "accent"],
      ["Hurda Milyem K\u00e2r\u0131", data.hurda_milyem_kari, "has", "good"],
      ["Hurda Al\u0131\u015f Has", data.hurda_alis_has_toplami, "has", "neutral"],
      ["Hurda Sat\u0131\u015f Has", data.hurda_satis_has_toplami, "has", "accent"],
      ["Hurda Kayd\u0131", data.hurda_adedi, "", "neutral"],
    ]],
  ].forEach(([title, cards]) => {
    const section = document.createElement("section");
    const heading = document.createElement("h3"); heading.textContent = title;
    const metrics = document.createElement("div"); metrics.className = "dashboard-stock-metrics";
    cards.forEach(card => metrics.appendChild(renderMetricCard(...card)));
    section.append(heading, metrics); stockGrid.appendChild(section);
  });
  const totalStock = document.createElement("p"); totalStock.className = "dashboard-stock-footnote";
  const totalLabel = document.createElement("span"); totalLabel.textContent = "Toplam Stok Has";
  const totalValue = document.createElement("strong"); totalValue.textContent = formatValue("has", data.toplam_stok_has);
  totalStock.append(totalLabel, totalValue); stock.appendChild(totalStock);
  const cari = renderDashboardPanel("Cari \u00d6zeti", "", [
    ["Kar\u015f\u0131 Taraftan Alaca\u011f\u0131m\u0131z Has", data.net_cari_alacak_has, "has", "good"],
    ["Bizim \u00d6deyece\u011fimiz Has", data.net_cari_borc_has, "has", data.net_cari_borc_has ? "warn" : "neutral"],
    ["Bize Bor\u00e7lu Cari", data.alacakli_cari_sayisi, "", "neutral"],
    ["Bizim Bor\u00e7lu Oldu\u011fumuz Cari", data.borclu_cari_sayisi, "", "neutral"],
  ]);
  cari.classList.add("dashboard-cari-summary");
  topGroups.append(stock, cari);
  bottomGroups.append(
    renderDashboardPanel("Gider \u00d6zeti", "", [
      ["Toplam Milyem K\u00e2r\u0131", data.genel_milyem_kari, "has", "neutral", "Normal + hurda"],
      ["Toplam Gider", data.toplam_gider, "has", "warn"],
      ["Kalan Net K\u00e2r", data.net_kar, "has", data.net_kar < 0 ? "warn" : "good", "Giderler d\u00fc\u015f\u00fcld\u00fckten sonra"],
    ]),
    renderDashboardPanel("Uyar\u0131lar", "", [
      ["Stok Yetersiz Uyar\u0131s\u0131", data.uyari_sayisi, "", data.uyari_sayisi ? "warn" : "good", data.uyari_sayisi ? "Kontrol edin" : "Sorun yok"],
    ])
  );

  root.append(hero, topGroups, bottomGroups);
  return root;
}
let renderVersion = 0;
async function render() {
  const version = ++renderVersion;
  const view = state.view;
  document.querySelector(".app").dataset.view = view;
  const rendered = document.createDocumentFragment();
  const meta = views[view];
  document.querySelector("#pageTitle").textContent = meta.title;
  document.querySelector("#pageSubtitle").textContent = meta.subtitle;
  content.replaceChildren();
  try {
    if (view === "dashboard") {
      const dashboard = await api("/api/dashboard");
      rendered.appendChild(renderDashboard(dashboard));
      return;
    }
    if (view === "giderler") {
      const [rows, summary] = await Promise.all([api("/api/giderler"), api("/api/dashboard")]);
      const layout = document.createElement("div"); layout.className = "expenses-layout form-summary-layout";
      const main = document.createElement("div"); main.className = "expenses-main";
      main.appendChild(renderExpenseForm());
      layout.append(main, renderProfitSummary(summary), renderTable("giderler", rows, "Gider Kay\u0131tlar\u0131")); rendered.appendChild(layout);
      return;
    }
    if (view === "cari") {
      const data = await api("/api/cari");
      state.cariData = data;
      const filters = [["all", "T\u00dcM\u00dc"], ["musteri", "M\u00dc\u015eTER\u0130LER"], ["tedarikci", "TEDAR\u0130K\u00c7\u0130LER"], ["odeme", "\u00d6DEMELER"]];
      if (!filters.some(([key]) => key === state.cariFilter)) state.cariFilter = "all";
      const tabs = renderTabs(filters, state.cariFilter, value => { state.cariFilter = value; render(); });
      tabs.setAttribute("role", "tablist"); tabs.setAttribute("aria-label", "Cari filtreleri");
      [...tabs.children].forEach((button, index) => {
        button.dataset.filter = filters[index][0]; button.setAttribute("role", "tab");
        button.setAttribute("aria-selected", String(filters[index][0] === state.cariFilter));
      });
      rendered.appendChild(tabs);
      const selected = {
        all: ["kisiCari", data.kisiler, "Genel Cari \u00d6zeti"],
        musteri: ["musteriCari", data.musteriler, "M\u00fc\u015fteriler"],
        tedarikci: ["tedarikciCari", data.tedarikciler, "Tedarik\u00e7iler"],
        odeme: ["cariOdeme", data.odemeler, "Cari \u00d6demeleri"],
      }[state.cariFilter];
      rendered.appendChild(renderTable(selected[0], selected[1] || [], selected[2]));
      return;
    }
    if (view === "stok") {
      const [normal, hurda] = await Promise.all([api("/api/stok/normal"), api("/api/stok/hurda")]);
      rendered.appendChild(renderTabs([["normal", "NORMAL STOK"], ["hurda", "HURDA STOK"]], state.stokFilter, (value) => { state.stokFilter = value; render(); }));
      rendered.appendChild(state.stokFilter === "hurda" ? renderTable("hurdaStok", hurda || [], "Hurda Stok") : renderTable("stok", normal || [], "Normal Stok"));
      return;
    }
    if (["alis", "satis"].includes(view)) {
      rendered.appendChild(renderForm(view));
      rendered.appendChild(renderTable(view, await api(`/api/${view}`)));
      return;
    }
    if (["hurda_alis", "hurda_satis"].includes(view)) {
      const isSale = view === "hurda_satis";
      rendered.appendChild(renderForm("hurda", isSale ? "SATIS" : "ALIS"));
      const data = await api("/api/hurda");
      const allHurdaRows = enrichHurdaRows(data.kayitlar || []);
      const hurdaRows = allHurdaRows.filter((row) => normalize(row.islem_turu).startsWith(isSale ? "satis" : "alis"));
      rendered.appendChild(renderTable(isSale ? "hurdaSatis" : "hurdaAlis", hurdaRows, isSale ? "Hurda Sat\u0131\u015f Kay\u0131tlar\u0131" : "Hurda Al\u0131\u015f Kay\u0131tlar\u0131"));
      return;
    }
    rendered.appendChild(renderTable(view, await api(`/api/${view}`)));
  } catch (error) { if (version === renderVersion) showMessage(error.message, true); }
  finally { if (version === renderVersion) content.replaceChildren(rendered); }
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


document.querySelector("#exportBtn").addEventListener("click", downloadAllData);
document.querySelector("#backupBtn").addEventListener("click", createDatabaseBackup);
document.querySelector("#restoreBtn").addEventListener("click", restoreLatestDatabaseBackup);

const dataMenu = document.querySelector("#dataMenu");
document.addEventListener("click", event => {
  if (!dataMenu.contains(event.target) || event.target.closest(".toolbar-menu-panel button")) dataMenu.open = false;
});
document.addEventListener("keydown", event => {
  if (event.key === "Escape" && dataMenu.open) {
    dataMenu.open = false; dataMenu.querySelector("summary").focus();
  }
});

api("/api/session").then((session) => { if (!session?.authenticated) window.location.href = "/login"; else refreshSuggestions().then(render); }).catch((error) => showMessage(error.message, true));
