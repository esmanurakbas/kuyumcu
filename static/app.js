const state = {
  view: "dashboard",
  search: "",
  cariFilter: "tedarikci",
  filters: {
    tarihBaslangic: "",
    tarihBitis: "",
    kisi: "",
    cinsi: "",
    ayar: "",
  },
  suggestions: {
    products: ["Çeyrek Altın", "Yarım Altın", "Tam Altın", "Gram Altın", "Bilezik", "Hurda Altın"],
    customers: [],
    suppliers: [],
    people: [],
  },
};

const views = {
  dashboard: { title: "Dashboard", subtitle: "Güncel stok, cari ve satış özeti" },
  alis: { title: "Alış", subtitle: "Stok artıran tedarikçi işlemleri" },
  satis: { title: "Satış", subtitle: "Stok düşen müşteri satışları" },
  hurda: { title: "Hurda", subtitle: "Hurda alış ve satış işlemleri" },
  stok: { title: "Stok", subtitle: "Cinsi + ayar bazında canlı hesap" },
  cari: { title: "Cari", subtitle: "Müşteri ve tedarikçi bakiyeleri" },
};

const forms = {
  alis: [
    ["tarih", "Tarih", "date", "main"],
    ["tedarikci", "Tedarikçi", "autocomplete", "main", "suppliers"],
    ["cinsi", "Ürün", "autocomplete", "main", "products"],
    ["ayar", "Ayar", "text", "main"],
    ["adet", "Adet", "number", "amount"],
    ["gram", "Gram", "text", "amount"],
    ["milyem", "Milyem", "text", "amount"],
    ["notlar", "Not", "textarea", "note"],
  ],
  satis: [
    ["tarih", "Tarih", "date", "main"],
    ["musteri", "Müşteri", "autocomplete", "main", "customers"],
    ["cinsi", "Ürün", "autocomplete", "main", "products"],
    ["ayar", "Ayar", "text", "main"],
    ["adet", "Adet", "number", "amount"],
    ["gram", "Gram", "text", "amount"],
    ["milyem", "Milyem", "text", "amount"],
    ["notlar", "Not", "textarea", "note"],
  ],
  hurda: [
    ["tarih", "Tarih", "date", "main"],
    ["islem_turu", "İşlem", "select", "main", ["ALIŞ", "SATIŞ"]],
    ["kisi", "Kişi", "autocomplete", "main", "people"],
    ["cinsi", "Ürün", "autocomplete", "main", "products"],
    ["ayar", "Ayar", "text", "main"],
    ["adet", "Adet", "number", "amount"],
    ["gram", "Gram", "text", "amount"],
    ["milyem", "Milyem", "text", "amount"],
    ["notlar", "Not", "textarea", "note"],
  ],
};

const columns = {
  alis: ["tarih", "tedarikci", "cinsi", "ayar", "adet", "gram", "milyem", "has", "not"],
  satis: ["tarih", "musteri", "cinsi", "ayar", "adet", "gram", "milyem", "has", "kar", "not"],
  hurda: ["tarih", "islem_turu", "kisi", "cinsi", "ayar", "adet", "gram", "milyem", "has", "not"],
  stok: ["cinsi", "ayar", "alis_has", "satis_has", "kalan_has", "kalan_adet", "kalan_gram", "ortalama_has_maliyeti", "stok_degeri", "hurda_kalan_has", "uyari"],
  cari: ["isim", "tip", "alis_has", "satis_has", "kalan_has", "toplam_islem", "toplam_odeme_alma", "bakiye", "son_islem_tarihi"],
};

const labels = {
  tarih: "Tarih",
  tedarikci: "Tedarikçi",
  musteri: "Müşteri",
  kisi: "Kişi",
  cinsi: "Ürün",
  ayar: "Ayar",
  adet: "Adet",
  gram: "Gram",
  milyem: "Milyem",
  has: "Has",
  has_fiyati: "Has Fiyatı",
  iscilik: "İşçilik",
  ek_masraf: "Ek Masraf",
  ek_ucret: "Ek Ücret",
  indirim: "İndirim",
  odenen: "Ödenen",
  alinan: "Alınan",
  odenen_veya_alinan: "Ödenen / Alınan",
  toplam_tutar: "Toplam",
  kar: "Kâr",
  uyari: "Uyarı",
  not: "Not",
  islem_turu: "İşlem",
  alis_has: "Alış Has",
  satis_has: "Satış Has",
  kalan_has: "Kalan Has",
  kalan_adet: "Kalan Adet",
  kalan_gram: "Kalan Gram",
  ortalama_has_maliyeti: "Ort. Has Maliyet",
  stok_degeri: "Stok Değeri",
  hurda_kalan_has: "Hurda Kalan Has",
  isim: "İsim",
  tip: "Tip",
  toplam_islem: "Toplam İşlem",
  toplam_odeme_alma: "Ödeme / Alma",
  bakiye: "Bakiye",
  son_islem_tarihi: "Son İşlem",
};

const moneyFields = new Set(["has_fiyati", "iscilik", "ek_masraf", "ek_ucret", "indirim", "odenen", "alinan", "toplam_tutar", "kar", "ortalama_has_maliyeti", "stok_degeri", "toplam_islem", "toplam_odeme_alma", "bakiye", "odenen_veya_alinan"]);
const numberFields = new Set(["adet", "gram", "milyem", "has", "alis_has", "satis_has", "kalan_has", "kalan_adet", "kalan_gram", "hurda_kalan_has"]);

const content = document.querySelector("#content");
const search = document.querySelector("#search");

let editingId = null;

function today() {
  return new Date().toISOString().slice(0, 10);
}

function normalize(value) {
  return String(value || "")
    .toLocaleLowerCase("tr-TR")
    .replaceAll("ı", "i")
    .normalize("NFD")
    .replace(/[\u0300-\u036f]/g, "");
}

function safe(value) {
  return value === null || value === undefined || Number.isNaN(value) ? "" : value;
}

function formatValue(key, value) {
  value = safe(value);
  if (value === "") return "";
  if (moneyFields.has(key)) {
    return Number(value).toLocaleString("tr-TR", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  }
  if (numberFields.has(key)) {
    return Number(value).toLocaleString("tr-TR", { maximumFractionDigits: 3 });
  }
  return String(value);
}

function parseNumber(value) {
  const number = Number(String(value || "").trim().replace(",", "."));
  return Number.isFinite(number) ? number : 0;
}

function calcHasFromForm(form) {
  const adet = parseNumber(form.elements.adet?.value);
  const gram = parseNumber(form.elements.gram?.value);
  const milyem = parseNumber(form.elements.milyem?.value);
  return (adet * gram * milyem) / 1000;
}

function showMessage(text, isError = false) {
  const toast = document.createElement("div");
  toast.className = `toast ${isError ? "toast-error" : "toast-info"}`;
  toast.textContent = text;
  document.body.appendChild(toast);
  
  setTimeout(() => toast.classList.add("toast-show"), 10);
  
  setTimeout(() => {
    toast.classList.remove("toast-show");
    setTimeout(() => toast.remove(), 300);
  }, 3500);
}

function showConfirm(message, confirmText = "Evet", cancelText = "Hayır") {
  return new Promise((resolve) => {
    const overlay = document.createElement("div");
    overlay.className = "confirm-overlay";
    
    const dialog = document.createElement("div");
    dialog.className = "confirm-dialog";
    
    const messageEl = document.createElement("p");
    messageEl.className = "confirm-message";
    messageEl.textContent = message;
    dialog.appendChild(messageEl);
    
    const actions = document.createElement("div");
    actions.className = "confirm-actions";
    
    const cancelBtn = document.createElement("button");
    cancelBtn.className = "confirm-btn confirm-cancel";
    cancelBtn.textContent = cancelText;
    cancelBtn.addEventListener("click", () => {
      overlay.remove();
      resolve(false);
    });
    
    const confirmBtn = document.createElement("button");
    confirmBtn.className = "confirm-btn confirm-ok";
    confirmBtn.textContent = confirmText;
    confirmBtn.addEventListener("click", () => {
      overlay.remove();
      resolve(true);
    });
    
    actions.appendChild(cancelBtn);
    actions.appendChild(confirmBtn);
    dialog.appendChild(actions);
    
    overlay.appendChild(dialog);
    document.body.appendChild(overlay);
    
    setTimeout(() => overlay.classList.add("confirm-show"), 10);
  });
}

async function api(path, options = {}) {
  const response = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  const body = await response.json().catch(() => ({ status: "error", message: "İşlem yapılamadı.", data: null }));
  if (!response.ok || body.status === "error") {
    throw new Error(body.message || "İşlem yapılamadı.");
  }
  return body.data;
}

function filtered(rows) {
  let result = rows;
  
  // Cari filtresi
  if (state.view === "cari" && state.cariFilter !== "all") {
    result = result.filter((row) => {
      if (state.cariFilter === "musteri") {
        return row.tip === "MÜŞTERİ";
      } else if (state.cariFilter === "tedarikci") {
        return row.tip === "TEDARİKÇİ";
      }
      return true;
    });
  }
  
  // Genel arama
  const needle = normalize(state.search);
  if (needle) {
    result = result.filter((row) => normalize(Object.values(row).join(" ")).includes(needle));
  }
  
  // Tarih filtresi
  if (state.filters.tarihBaslangic) {
    result = result.filter((row) => row.tarih >= state.filters.tarihBaslangic);
  }
  if (state.filters.tarihBitis) {
    result = result.filter((row) => row.tarih <= state.filters.tarihBitis);
  }
  
  // Kişi filtresi (tedarikçi, müşteri, kişi)
  if (state.filters.kisi) {
    const kisiNorm = normalize(state.filters.kisi);
    result = result.filter((row) => {
      const tedarikci = normalize(row.tedarikci || "");
      const musteri = normalize(row.musteri || "");
      const kisi = normalize(row.kisi || "");
      const isim = normalize(row.isim || "");
      return tedarikci.includes(kisiNorm) || musteri.includes(kisiNorm) || kisi.includes(kisiNorm) || isim.includes(kisiNorm);
    });
  }
  
  // Cins filtresi
  if (state.filters.cinsi) {
    const cinsiNorm = normalize(state.filters.cinsi);
    result = result.filter((row) => normalize(row.cinsi || "").includes(cinsiNorm));
  }
  
  // Ayar filtresi
  if (state.filters.ayar) {
    result = result.filter((row) => normalize(row.ayar || "").includes(normalize(state.filters.ayar)));
  }
  
  return result;
}

async function refreshSuggestions() {
  try {
    state.suggestions = await api("/api/suggestions");
  } catch {
    // Hata durumunda varsayılan suggestions kullanılır
  }
}

function fieldElement(name, inputType, source) {
  if (inputType === "textarea") {
    const input = document.createElement("textarea");
    input.rows = 2;
    input.maxLength = 300;
    return input;
  }

  if (inputType === "select") {
    const input = document.createElement("select");
    source.forEach((option) => {
      const opt = document.createElement("option");
      opt.value = option;
      opt.textContent = option;
      input.appendChild(opt);
    });
    return input;
  }

  const input = document.createElement("input");
  if (inputType === "autocomplete") {
    input.type = "text";
    input.autocomplete = "off";
  } else if (inputType === "money") {
    input.type = "text";
    input.inputMode = "decimal";
  } else {
    input.type = inputType;
  }
  if (inputType === "number") input.min = "0";
  if (["adet", "gram", "milyem"].includes(name)) input.required = true;
  return input;
}

function attachAutocomplete(input, source) {
  const box = document.createElement("div");
  box.className = "suggest-box hidden";
  input.parentElement.appendChild(box);

  const close = () => box.classList.add("hidden");
  const open = () => {
    const needle = normalize(input.value);
    const values = state.suggestions[source] || [];
    const matches = values.filter((value) => !needle || normalize(value).includes(needle)).slice(0, 8);
    if (!matches.length) {
      close();
      return;
    }
    box.innerHTML = "";
    matches.forEach((value) => {
      const option = document.createElement("button");
      option.type = "button";
      option.textContent = value;
      option.addEventListener("mousedown", (event) => {
        event.preventDefault();
        input.value = value;
        close();
      });
      box.appendChild(option);
    });
    box.classList.remove("hidden");
  };

  input.addEventListener("input", open);
  input.addEventListener("focus", open);
  input.addEventListener("blur", () => setTimeout(close, 120));
}

function renderForm(type) {
  const panel = document.createElement("section");
  panel.className = "panel form-panel";
  const form = document.createElement("form");
  form.className = "entry-form";

  forms[type].forEach(([name, label, inputType, group, source]) => {
    const wrap = document.createElement("label");
    wrap.className = `field field-${group}`;
    wrap.appendChild(document.createTextNode(label));

    const input = fieldElement(name, inputType, source);
    input.name = name;
    if (name === "tarih") input.value = today();
    if (["cinsi", "ayar", "tedarikci", "musteri", "kisi"].includes(name)) input.required = true;
    wrap.appendChild(input);
    form.appendChild(wrap);
    if (inputType === "autocomplete") attachAutocomplete(input, source);
  });

  const hasPreview = document.createElement("div");
  hasPreview.className = "has-preview";
  hasPreview.innerHTML = "<span>Hesaplanan Has</span><strong>0</strong>";
  form.appendChild(hasPreview);
  
  // Kaydet butonu EN ALTTA EN BAŞTA
  const bottomActions = document.createElement("div");
  bottomActions.className = "form-bottom-actions";
  const saveBtn = document.createElement("button");
  saveBtn.type = "submit";
  saveBtn.textContent = editingId ? "Güncelle" : "Kaydet";
  bottomActions.appendChild(saveBtn);
  form.appendChild(bottomActions);

  const updateHasPreview = () => {
    hasPreview.querySelector("strong").textContent = formatValue("has", calcHasFromForm(form));
  };
  ["adet", "gram", "milyem"].forEach((name) => {
    form.elements[name]?.addEventListener("input", updateHasPreview);
  });
  updateHasPreview();

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const data = Object.fromEntries(new FormData(form).entries());
    try {
      if (editingId) {
        await api(`/api/${type}/${editingId}`, { method: "PUT", body: JSON.stringify(data) });
        showMessage(`${views[type].title} güncellendi.`);
        editingId = null;
      } else {
        const saved = await api(`/api/${type}`, { method: "POST", body: JSON.stringify(data) });
        showMessage(`${views[type].title} kaydedildi. Has: ${formatValue("has", saved.has)}`);
      }
      form.reset();
      form.querySelector("[name=tarih]").value = today();
      await refreshSuggestions();
      render();
    } catch (error) {
      showMessage(error.message, true);
      editingId = null;
    }
  });

  panel.appendChild(form);
  return panel;
}

function renderTable(type, rows, title = "") {
  const cols = columns[type];
  
  const section = document.createElement("section");
  section.className = "table-section";
  if (title) {
    const heading = document.createElement("h2");
    heading.textContent = title;
    section.appendChild(heading);
  }

  // Filtre paneli
  if (["alis", "satis", "hurda", "cari", "stok"].includes(type)) {
    const filterGrid = document.createElement("div");
    filterGrid.className = "filter-grid";
    filterGrid.id = "filter-grid";
    
    // Tarih başlangıç (cari ve stok hariç)
    if (!["cari", "stok"].includes(type)) {
      const dateStartWrap = document.createElement("label");
      dateStartWrap.className = "filter-field";
      dateStartWrap.textContent = "Başlangıç Tarihi";
      const dateStart = document.createElement("input");
      dateStart.type = "date";
      dateStart.value = state.filters.tarihBaslangic;
      dateStart.addEventListener("change", (e) => {
        state.filters.tarihBaslangic = e.target.value;
        render();
      });
      dateStartWrap.appendChild(dateStart);
      filterGrid.appendChild(dateStartWrap);
    }
    
    // Tarih bitiş (cari ve stok hariç)
    if (!["cari", "stok"].includes(type)) {
      const dateEndWrap = document.createElement("label");
      dateEndWrap.className = "filter-field";
      dateEndWrap.textContent = "Bitiş Tarihi";
      const dateEnd = document.createElement("input");
      dateEnd.type = "date";
      dateEnd.value = state.filters.tarihBitis;
      dateEnd.addEventListener("change", (e) => {
        state.filters.tarihBitis = e.target.value;
        render();
      });
      dateEndWrap.appendChild(dateEnd);
      filterGrid.appendChild(dateEndWrap);
    }
    
    // Kişi filtresi (stok hariç)
    if (type !== "stok") {
      const personWrap = document.createElement("label");
      personWrap.className = "filter-field";
      personWrap.textContent = type === "alis" ? "Tedarikçi" : type === "satis" ? "Müşteri" : type === "cari" ? "İsim" : "Kişi";
      const personInput = document.createElement("input");
      personInput.type = "text";
      personInput.placeholder = "Ara...";
      personInput.value = state.filters.kisi;
      personInput.addEventListener("input", (e) => {
        state.filters.kisi = e.target.value;
        render();
      });
      personWrap.appendChild(personInput);
      filterGrid.appendChild(personWrap);
    }
    
    // Cins filtresi
    if (["alis", "satis", "hurda", "stok"].includes(type)) {
      const productWrap = document.createElement("label");
      productWrap.className = "filter-field";
      productWrap.textContent = "Ürün";
      const productInput = document.createElement("input");
      productInput.type = "text";
      productInput.placeholder = "Ara...";
      productInput.value = state.filters.cinsi;
      productInput.addEventListener("input", (e) => {
        state.filters.cinsi = e.target.value;
        render();
      });
      productWrap.appendChild(productInput);
      filterGrid.appendChild(productWrap);
      
      // Ayar filtresi
      const ayarWrap = document.createElement("label");
      ayarWrap.className = "filter-field";
      ayarWrap.textContent = "Ayar";
      const ayarInput = document.createElement("input");
      ayarInput.type = "text";
      ayarInput.placeholder = "Ara...";
      ayarInput.value = state.filters.ayar;
      ayarInput.addEventListener("input", (e) => {
        state.filters.ayar = e.target.value;
        render();
      });
      ayarWrap.appendChild(ayarInput);
      filterGrid.appendChild(ayarWrap);
    }
    
    // Temizle butonu
    const clearBtn = document.createElement("button");
    clearBtn.type = "button";
    clearBtn.className = "filter-clear";
    clearBtn.textContent = "Temizle";
    clearBtn.addEventListener("click", () => {
      state.filters = {
        tarihBaslangic: "",
        tarihBitis: "",
        kisi: "",
        cinsi: "",
        ayar: "",
      };
      render();
    });
    filterGrid.appendChild(clearBtn);
    
    section.appendChild(filterGrid);
    
    // Filter butonunu topbar'a ekle
    const topbarControls = document.querySelector(".topbar-controls");
    let existingFilterBtn = document.getElementById("filter-toggle-btn");
    if (existingFilterBtn) existingFilterBtn.remove();
    
    const filterToggle = document.createElement("button");
    filterToggle.type = "button";
    filterToggle.className = "filter-toggle";
    filterToggle.id = "filter-toggle-btn";
    filterToggle.innerHTML = '<svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor"><path d="M6 10.5a.5.5 0 0 1 .5-.5h3a.5.5 0 0 1 0 1h-3a.5.5 0 0 1-.5-.5zm-2-3a.5.5 0 0 1 .5-.5h7a.5.5 0 0 1 0 1h-7a.5.5 0 0 1-.5-.5zm-2-3a.5.5 0 0 1 .5-.5h11a.5.5 0 0 1 0 1h-11a.5.5 0 0 1-.5-.5z"/></svg> Filtreler';
    filterToggle.addEventListener("click", () => {
      filterGrid.classList.toggle("filter-grid-open");
      filterToggle.classList.toggle("filter-toggle-active");
    });
    topbarControls.appendChild(filterToggle);
  } else {
    // Filter butonunu kaldır
    const existingFilterBtn = document.getElementById("filter-toggle-btn");
    if (existingFilterBtn) existingFilterBtn.remove();
  }

  rows = filtered(rows);

  const wrap = document.createElement("div");
  wrap.className = "table-wrap";
  if (!rows.length) {
    wrap.innerHTML = '<div class="empty">Kayıt yok.</div>';
    section.appendChild(wrap);
    return section;
  }

  const table = document.createElement("table");
  const thead = document.createElement("thead");
  thead.innerHTML = `<tr>${cols.map((col) => `<th class="${tableCellClass(col)}">${labels[col] || col}</th>`).join("")}${["alis", "satis", "hurda"].includes(type) ? "<th></th>" : ""}</tr>`;
  table.appendChild(thead);

  const tbody = document.createElement("tbody");
  rows.forEach((row) => {
    const tr = document.createElement("tr");
    cols.forEach((col) => {
      const td = document.createElement("td");
      const value = row[col];
      td.className = tableCellClass(col);
      td.dataset.col = col;
      if (col === "uyari" && value) {
        td.innerHTML = `<span class="pill warn">${formatValue(col, value)}</span>`;
      } else if (["tip", "islem_turu"].includes(col)) {
        td.innerHTML = `<span class="pill">${formatValue(col, value)}</span>`;
      } else {
        td.textContent = formatValue(col, value);
      }
      tr.appendChild(td);
    });

    if (["alis", "satis", "hurda"].includes(type)) {
      const td = document.createElement("td");
      const actionsCell = document.createElement("div");
      actionsCell.className = "actions-cell";
      
      // Edit button
      const editBtn = document.createElement("button");
      editBtn.className = "edit";
      editBtn.type = "button";
      editBtn.innerHTML = '<svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor"><path d="M12.146.146a.5.5 0 0 1 .708 0l3 3a.5.5 0 0 1 0 .708l-10 10a.5.5 0 0 1-.168.11l-5 2a.5.5 0 0 1-.65-.65l2-5a.5.5 0 0 1 .11-.168l10-10zM11.207 2.5 13.5 4.793 14.793 3.5 12.5 1.207 11.207 2.5zm1.586 3L10.5 3.207 4 9.707V10h.5a.5.5 0 0 1 .5.5v.5h.5a.5.5 0 0 1 .5.5v.5h.293l6.5-6.5zm-9.761 5.175-.106.106-1.528 3.821 3.821-1.528.106-.106A.5.5 0 0 1 5 12.5V12h-.5a.5.5 0 0 1-.5-.5V11h-.5a.5.5 0 0 1-.468-.325z"/></svg>';
      editBtn.title = "Düzenle";
      editBtn.addEventListener("click", () => {
        editingId = row.id;
        const formElement = document.querySelector(".entry-form");
        if (!formElement) return;
        
        // Form alanlarını doldur
        Object.keys(row).forEach((key) => {
          const input = formElement.querySelector(`[name="${key}"]`);
          if (input && key !== "id" && key !== "has" && key !== "toplam_tutar" && key !== "kar" && key !== "uyari") {
            input.value = row[key] || "";
          }
        });
        
        // Forma scroll
        formElement.scrollIntoView({ behavior: "smooth", block: "start" });
        showMessage("Kayıt düzenleme modunda. Güncellemek için Kaydet butonuna basın.");
      });
      
      // Delete button
      const deleteBtn = document.createElement("button");
      deleteBtn.className = "delete";
      deleteBtn.type = "button";
      deleteBtn.innerHTML = '<svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor"><path d="M5.5 5.5A.5.5 0 0 1 6 6v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5zm2.5 0a.5.5 0 0 1 .5.5v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5zm3 .5a.5.5 0 0 0-1 0v6a.5.5 0 0 0 1 0V6z"/><path fill-rule="evenodd" d="M14.5 3a1 1 0 0 1-1 1H13v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V4h-.5a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1H6a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1h3.5a1 1 0 0 1 1 1v1zM4.118 4 4 4.059V13a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1V4.059L11.882 4H4.118zM2.5 3V2h11v1h-11z"/></svg>';
      deleteBtn.title = "Sil";
      deleteBtn.addEventListener("click", async () => {
        const confirmDelete = await showConfirm("Bu kaydı silmek istediğinize emin misiniz?", "Sil", "İptal");
        if (!confirmDelete) return;
        try {
          await api(`/api/${type}/${row.id}`, { method: "DELETE" });
          showMessage("Kayıt başarıyla silindi.");
          await refreshSuggestions();
          render();
        } catch (error) {
          showMessage(error.message, true);
        }
      });
      
      actionsCell.appendChild(editBtn);
      actionsCell.appendChild(deleteBtn);
      td.appendChild(actionsCell);
      tr.appendChild(td);
    }
    tbody.appendChild(tr);
  });
  table.appendChild(tbody);
  wrap.appendChild(table);
  section.appendChild(wrap);
  return section;
}

function tableCellClass(col) {
  const classes = [`col-${col}`];
  if (moneyFields.has(col) || numberFields.has(col)) classes.push("num");
  if (["has", "has_fiyati", "kalan_has", "alis_has", "satis_has", "hurda_kalan_has"].includes(col)) classes.push("important-num");
  return classes.join(" ");
}

function renderCards(data) {
  const cards = [
    ["Toplam Stok Has", data.toplam_stok_has, "has", "primary"],
    ["Stok Değeri", data.stok_degeri, "money", "neutral"],
    ["Günlük Satış", data.gunluk_satis, "money", "accent"],
    ["Toplam Kâr", data.toplam_kar, "money", "good"],
  ];
  const section = document.createElement("section");
  section.className = "cards";
  
  cards.forEach(([label, value, kind, tone]) => {
    const key = kind === "has" ? "has" : kind === "plain" ? "" : "toplam_tutar";
    const card = document.createElement("article");
    card.className = `card tone-${tone}`;
    card.innerHTML = `<span>${label}</span><strong>${formatValue(key, value)}</strong>`;
    section.appendChild(card);
  });
  
  return section;
}


async function render() {
  const meta = views[state.view];
  document.querySelector("#pageTitle").textContent = meta.title;
  document.querySelector("#pageSubtitle").textContent = meta.subtitle;
  content.innerHTML = "";
  
  // Cari slider göster/gizle
  const cariSlider = document.getElementById("cari-slider");
  if (state.view === "cari") {
    cariSlider.style.display = "flex";
  } else {
    cariSlider.style.display = "none";
  }

  try {
    if (state.view === "dashboard") {
      const [dashboard, stock] = await Promise.all([api("/api/dashboard"), api("/api/stok")]);
      content.appendChild(renderCards(dashboard));
      content.appendChild(renderTable("stok", stock.slice(0, 10), "Stok Özeti"));
      return;
    }

    if (forms[state.view]) {
      content.appendChild(renderForm(state.view));
    }
    const rows = await api(`/api/${state.view}`);
    content.appendChild(renderTable(state.view, rows));
  } catch (error) {
    showMessage(error.message, true);
  }
}

document.querySelectorAll(".nav").forEach((button) => {
  button.addEventListener("click", () => {
    document.querySelectorAll(".nav").forEach((item) => item.classList.remove("active"));
    button.classList.add("active");
    state.view = button.dataset.view;
    search.value = "";
    state.search = "";
    // Filtreleri temizle
    state.filters = {
      tarihBaslangic: "",
      tarihBitis: "",
      kisi: "",
      cinsi: "",
      ayar: "",
    };
    render();
  });
});

search.addEventListener("input", () => {
  state.search = search.value;
  render();
});

// Cari slider event listeners
document.querySelectorAll(".slider-btn").forEach((btn) => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".slider-btn").forEach((b) => b.classList.remove("active"));
    btn.classList.add("active");
    state.cariFilter = btn.dataset.value;
    render();
  });
});

refreshSuggestions().then(render);
