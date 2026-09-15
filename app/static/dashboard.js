(() => {
    const permissionsData = document.querySelector("#user-permissions");
    const permissions = permissionsData ? JSON.parse(permissionsData.textContent) : { canManage: false };
    let products = [];
    let pagination = { page: 1, page_size: 8, total: 0, total_pages: 1 };
    let summary = null;
    let movement = { id: null, type: "entrada" };
    let editingId = null;
    let deletingProduct = null;
    let sort = { field: "nome", direction: "asc" };
    let page = 1;
    const pageSize = 8;
    let searchTimer = null;
    const $ = (selector) => document.querySelector(selector);
    const money = (value) => Number(value || 0).toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
    const safe = (value) => { const element = document.createElement("span"); element.textContent = value ?? ""; return element.innerHTML; };

    function showToast(message, error = false) {
        const toast = $("#toast");
        toast.textContent = message;
        toast.className = `toast show${error ? " error" : ""}`;
        window.setTimeout(() => { toast.className = "toast"; }, 3200);
    }

    function setLoadingState(button, isLoading, label = "") {
        if (!button) return;
        const original = button.dataset.defaultText || button.textContent.trim();
        button.disabled = isLoading;
        button.textContent = isLoading ? (label || "Carregando...") : original;
    }

    function extractErrorMessage(payload) {
        if (!payload) return "Não foi possível concluir a operação.";
        if (typeof payload.detail === "string") return payload.detail;
        if (Array.isArray(payload.detail)) {
            const first = payload.detail[0];
            if (first && typeof first.msg === "string") return first.msg;
        }
        if (payload.errors && Array.isArray(payload.errors)) {
            const first = payload.errors[0];
            if (first && typeof first.msg === "string") return first.msg;
        }
        return payload.message || "Não foi possível concluir a operação.";
    }

    function normalizeFormData(form) {
        const data = Object.fromEntries(new FormData(form));
        const normalized = {};
        Object.entries(data).forEach(([key, value]) => {
            normalized[key] = typeof value === "string" ? value.trim() : value;
        });
        if (!normalized.nome) throw new Error("Nome do produto é obrigatório.");
        return normalized;
    }

    function openModal(id) {
        const modal = $(`#${id}`);
        if (!modal) return;
        modal.classList.add("open");
        const firstInput = modal.querySelector("input");
        if (firstInput) window.setTimeout(() => firstInput.focus(), 30);
    }

    function closeModal(id) {
        const modal = $(`#${id}`);
        if (modal) modal.classList.remove("open");
    }

    function updateCategories() {
        const select = $("#category-filter");
        if (!select) return;
        const current = select.value;
        const categories = Array.isArray(summary?.categories) ? summary.categories : [];
        select.innerHTML = '<option value="todas">Todas as categorias</option>' + categories.map((category) => `<option value="${safe(category)}">${safe(category)}</option>`).join("");
        select.value = categories.includes(current) ? current : "todas";
    }

    function renderPagination() {
        const paginationElement = $("#pagination");
        const pages = Math.max(1, Number(pagination.total_pages) || 1);
        page = Math.min(Math.max(1, page), pages);
        if (pages <= 1) { paginationElement.innerHTML = ""; return; }
        const buttons = [];
        const start = Math.max(1, page - 2);
        const end = Math.min(pages, page + 2);
        buttons.push(`<button class="page-button" type="button" data-page="${page - 1}" ${page === 1 ? "disabled" : ""} aria-label="Página anterior">‹</button>`);
        if (start > 1) buttons.push('<button class="page-button" type="button" data-page="1">1</button>');
        if (start > 2) buttons.push('<span class="page-button" aria-hidden="true">…</span>');
        for (let number = start; number <= end; number += 1) {
            buttons.push(`<button class="page-button${number === page ? " active" : ""}" type="button" data-page="${number}" aria-label="Página ${number}">${number}</button>`);
        }
        if (end < pages - 1) buttons.push('<span class="page-button" aria-hidden="true">…</span>');
        if (end < pages) buttons.push(`<button class="page-button" type="button" data-page="${pages}">${pages}</button>`);
        buttons.push(`<button class="page-button" type="button" data-page="${page + 1}" ${page === pages ? "disabled" : ""} aria-label="Próxima página">›</button>`);
        paginationElement.innerHTML = `<span>Página ${page} de ${pages}</span><div class="page-buttons">${buttons.join("")}</div>`;
    }

    function drawChart() {
        const canvas = $("#stock-chart");
        if (!canvas) return;
        const context = canvas.getContext("2d");
        const width = canvas.clientWidth || 240;
        const height = canvas.clientHeight || 210;
        const ratio = window.devicePixelRatio || 1;
        canvas.width = width * ratio;
        canvas.height = height * ratio;
        context.setTransform(ratio, 0, 0, ratio, 0, 0);
        context.clearRect(0, 0, width, height);
        const ok = Number(summary?.normal_products || 0);
        const low = Number(summary?.low_products || 0);
        const total = Number(summary?.total_products || ok + low);
        const centerX = width / 2;
        const centerY = height / 2;
        const radius = Math.min(78, height * .34);
        const lineWidth = 22;
        let start = -Math.PI / 2;
        [[ok, "#087f78"], [low, "#d95f4d"]].forEach(([amount, color]) => {
            const slice = total ? (amount / total) * Math.PI * 2 : 0;
            context.beginPath();
            context.strokeStyle = color;
            context.lineWidth = lineWidth;
            context.lineCap = "round";
            context.arc(centerX, centerY, radius, start, start + slice);
            context.stroke();
            start += slice;
        });
        context.fillStyle = getComputedStyle(document.body).getPropertyValue("--ink");
        context.textAlign = "center";
        context.font = "700 24px Space Grotesk, sans-serif";
        context.fillText(total, centerX, centerY + 5);
        context.font = "11px DM Sans, sans-serif";
        context.fillStyle = getComputedStyle(document.body).getPropertyValue("--muted");
        context.fillText("produtos", centerX, centerY + 22);
        $("#chart-ok").textContent = ok;
        $("#chart-low").textContent = low;
        $("#chart-summary-note").textContent = low ? `${low} ${low === 1 ? "produto precisa" : "produtos precisam"} de atenção.` : "Tudo certo: nenhum produto em alerta.";
    }

    function renderSummary() {
        const total = Number(summary?.total_products || 0);
        const low = Number(summary?.low_products || 0);
        const units = Number(summary?.total_units || 0);
        const value = Number(summary?.total_value || 0);
        $("#total-products").textContent = total;
        $("#low-products").textContent = low;
        $("#total-units").textContent = units.toLocaleString("pt-BR");
        $("#total-value").textContent = money(value);
        const lowItems = Array.isArray(summary?.low_items) ? summary.low_items : [];
        $("#attention-list").innerHTML = lowItems.length ? lowItems.map((product) => `<div class="attention-item"><div><div class="attention-name">${safe(product.nome)}</div><div class="attention-meta">Atual: ${safe(product.estoque_atual)} · mínimo: ${safe(product.estoque_minimo)}</div></div><span class="low-number">Atenção</span></div>`).join("") : '<div class="empty-mini">Tudo certo por aqui.</div>';
        $("#visible-count").textContent = Number(pagination.total || 0).toLocaleString("pt-BR");
        const gettingStarted = document.querySelector(".getting-started");
        if (gettingStarted) gettingStarted.hidden = total > 0;
        window.stockaiSummary = summary || {};
        updateCategories();
        drawChart();
    }

    function renderProducts() {
        const items = Array.isArray(products) ? products : [];
        $("#empty-state").classList.toggle("visible", !items.length);
        $("#product-list").innerHTML = items.map((product) => `<tr tabindex="0"><td class="product-name">${safe(product.nome)}</td><td class="category">${safe(product.categoria || "Sem categoria")}</td><td class="price">${money(product.preco)}</td><td class="stock">${safe(product.estoque_atual)}</td><td class="muted">${safe(product.estoque_minimo)}</td><td><span class="status status-${product.status}">${product.status === "ok" ? "Em dia" : "No mínimo ou abaixo"}</span></td><td><div class="row-actions"><button class="icon-btn" type="button" data-movement="entrada" data-id="${product.id}"><span aria-hidden="true">+</span> Entrada</button><button class="icon-btn out" type="button" data-movement="saida" data-id="${product.id}"><span aria-hidden="true">−</span> Saída</button>${permissions.canManage ? `<button class="icon-btn" type="button" data-edit="${product.id}">Editar</button><button class="icon-btn out" type="button" data-delete="${product.id}">Excluir</button>` : ""}</div></td></tr>`).join("");
        renderPagination();
    }

    function render() {
        renderSummary();
        renderProducts();
    }

    async function api(url, options = {}) {
        const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content;
        const response = await fetch(url, {
            headers: { "Content-Type": "application/json", ...(csrfToken ? { "X-CSRF-Token": csrfToken } : {}), ...options.headers },
            ...options,
        });
        const contentType = response.headers.get("content-type") || "";
        const data = contentType.includes("application/json") ? await response.json() : null;
        if (!response.ok) throw new Error(extractErrorMessage(data));
        if (data && Object.prototype.hasOwnProperty.call(data, "success") && Object.prototype.hasOwnProperty.call(data, "data")) return data.data;
        return data;
    }

    function buildProductsUrl() {
        const params = new URLSearchParams({
            page: String(page),
            page_size: String(pageSize),
            status: $("#status-filter").value,
            ordenar_por: sort.field,
            ordem: sort.direction,
        });
        const busca = $("#product-search").value.trim();
        const categoria = $("#category-filter").value;
        if (busca) params.set("busca", busca);
        if (categoria && categoria !== "todas") params.set("categoria", categoria);
        return `/produtos?${params.toString()}`;
    }

    async function loadProducts({ showLoading = false } = {}) {
        if (showLoading) $("#product-list").innerHTML = '<tr><td colspan="7" class="muted">Carregando produtos...</td></tr>';
        try {
            const data = await api(buildProductsUrl());
            products = Array.isArray(data?.items) ? data.items : [];
            pagination = data?.pagination || { page, page_size: pageSize, total: products.length, total_pages: 1 };
            summary = data?.summary || { total_products: pagination.total, low_products: 0, normal_products: pagination.total, total_units: 0, total_value: 0, low_items: [], categories: [] };
            page = Number(pagination.page) || page;
            render();
        } catch (error) {
            showToast(error.message, true);
        }
    }

    async function refreshAfterMutation(preferredPage = page) {
        page = preferredPage;
        await loadProducts();
        if (!products.length && page > 1) {
            page -= 1;
            await loadProducts();
        }
    }

    async function loadHistory() {
        const history = await api("/movimentacoes");
        $("#history-list").innerHTML = history.length ? history.map((item) => `<div class="history-row"><div><strong>${safe(item.produto)}</strong><div class="history-date">${safe(new Date(item.data).toLocaleString("pt-BR"))}</div></div><span class="history-type ${item.tipo}">${item.tipo === "entrada" ? "Entrada" : "Saída"}</span><strong>${item.tipo === "entrada" ? "+" : "−"}${safe(item.quantidade)}</strong></div>`).join("") : '<div class="empty-mini">Ainda não há movimentações registradas.</div>';
    }

    function setLoading(form, loading) {
        const submit = form.querySelector("button[type=submit]");
        form.classList.toggle("loading", loading);
        if (submit) setLoadingState(submit, loading, loading ? "Salvando..." : "");
    }

    document.querySelectorAll("button[type=submit]").forEach((button) => { button.dataset.defaultText = button.textContent.trim(); });

    $("#create-form").addEventListener("submit", async (event) => {
        event.preventDefault();
        const form = event.target;
        try {
            const data = normalizeFormData(form);
            data.preco = Number(data.preco); data.estoque_atual = Number(data.estoque_atual); data.estoque_minimo = Number(data.estoque_minimo);
            setLoading(form, true);
            await api("/produtos", { method: "POST", body: JSON.stringify(data) });
            form.reset(); closeModal("create-modal"); page = 1; await loadProducts(); showToast("Produto cadastrado.");
        } catch (error) { showToast(error.message, true); }
        finally { setLoading(form, false); }
    });

    $("#movement-form").addEventListener("submit", async (event) => {
        event.preventDefault();
        const form = event.target;
        const quantity = Number(new FormData(form).get("quantidade"));
        setLoading(form, true);
        try {
            await api(`/produtos/${movement.id}/${movement.type}`, { method: "POST", body: JSON.stringify({ quantidade: quantity }) });
            closeModal("movement-modal"); await refreshAfterMutation(); showToast("Estoque atualizado.");
        } catch (error) { showToast(error.message, true); }
        finally { setLoading(form, false); }
    });

    $("#edit-form").addEventListener("submit", async (event) => {
        event.preventDefault();
        const form = event.target;
        try {
            const data = normalizeFormData(form);
            data.preco = Number(data.preco); data.estoque_minimo = Number(data.estoque_minimo);
            setLoading(form, true);
            await api(`/produtos/${editingId}`, { method: "PUT", body: JSON.stringify(data) });
            closeModal("edit-modal"); await refreshAfterMutation(); showToast("Produto atualizado.");
        } catch (error) { showToast(error.message, true); }
        finally { setLoading(form, false); }
    });

    $("#open-create").addEventListener("click", () => openModal("create-modal"));
    $("#confirm-delete").addEventListener("click", async () => {
        if (!deletingProduct) return;
        const button = $("#confirm-delete");
        setLoadingState(button, true, "Excluindo...");
        try {
            await api(`/produtos/${deletingProduct.id}`, { method: "DELETE" });
            closeModal("delete-modal");
            const targetPage = page;
            deletingProduct = null;
            await refreshAfterMutation(targetPage);
            showToast("Produto arquivado com sucesso.");
        } catch (error) { showToast(error.message, true); }
        finally { setLoadingState(button, false); }
    });

    $("#open-history").addEventListener("click", async () => { try { await loadHistory(); openModal("history-modal"); } catch (error) { showToast(error.message, true); } });
    $("#history-link")?.addEventListener("click", async (event) => { event.preventDefault(); try { await loadHistory(); openModal("history-modal"); } catch (error) { showToast(error.message, true); } });

    $("#product-search").addEventListener("input", () => {
        window.clearTimeout(searchTimer);
        page = 1;
        searchTimer = window.setTimeout(() => loadProducts(), 250);
    });
    $("#status-filter").addEventListener("change", () => { page = 1; loadProducts(); });
    $("#category-filter").addEventListener("change", () => { page = 1; loadProducts(); });
    $("#pagination").addEventListener("click", (event) => {
        const button = event.target.closest("[data-page]");
        if (button && !button.disabled) { page = Number(button.dataset.page); loadProducts({ showLoading: true }); }
    });
    document.querySelectorAll("[data-sort]").forEach((button) => button.addEventListener("click", () => {
        const field = button.dataset.sort;
        sort = { field, direction: sort.field === field && sort.direction === "asc" ? "desc" : "asc" };
        page = 1;
        loadProducts({ showLoading: true });
    }));

    document.addEventListener("click", async (event) => {
        const movementButton = event.target.closest("[data-movement]");
        if (movementButton) {
            const product = products.find((item) => item.id === Number(movementButton.dataset.id));
            if (!product) return;
            movement = { id: product.id, type: movementButton.dataset.movement };
            $("#movement-title").textContent = movement.type === "entrada" ? "Adicionar estoque" : "Retirar estoque";
            $("#movement-eyebrow").textContent = movement.type === "entrada" ? "Entrada" : "Saída";
            $("#movement-product").textContent = `${product.nome} · estoque atual: ${product.estoque_atual}`;
            openModal("movement-modal");
            return;
        }
        const edit = event.target.closest("[data-edit]");
        if (edit) {
            const product = products.find((item) => item.id === Number(edit.dataset.edit));
            if (!product) return;
            editingId = product.id;
            const form = $("#edit-form");
            Object.entries({ nome: product.nome, categoria: product.categoria || "", preco: product.preco, estoque_minimo: product.estoque_minimo }).forEach(([name, value]) => { form.elements[name].value = value; });
            openModal("edit-modal");
            return;
        }
        const remove = event.target.closest("[data-delete]");
        if (remove) {
            const product = products.find((item) => item.id === Number(remove.dataset.delete));
            if (!product) return;
            deletingProduct = product;
            $("#delete-product-name").textContent = product.nome;
            openModal("delete-modal");
            return;
        }
        if (!event.target.closest("[data-page]")) {
            const close = event.target.closest("[data-close]");
            if (close) closeModal(close.dataset.close);
        }
    });

    $("#theme-toggle").addEventListener("click", () => {
        const dark = document.documentElement.dataset.theme !== "dark";
        document.documentElement.dataset.theme = dark ? "dark" : "light";
        localStorage.setItem("stockai-theme", dark ? "dark" : "light");
        $("#theme-toggle").textContent = dark ? "☀ Tema" : "☾ Tema";
        drawChart();
    });
    $("#logout").addEventListener("click", async () => {
        const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content;
        const response = await fetch("/logout", { method: "POST", headers: { "X-CSRF-Token": csrfToken } });
        if (response.ok) window.location.href = "/login";
    });
    const savedTheme = localStorage.getItem("stockai-theme");
    if (savedTheme === "dark") { document.documentElement.dataset.theme = "dark"; $("#theme-toggle").textContent = "☀ Tema"; }
    $("#mobile-menu").addEventListener("click", () => { const open = $("#sidebar").classList.toggle("open"); $("#mobile-overlay").classList.toggle("open", open); $("#mobile-menu").setAttribute("aria-expanded", String(open)); });
    $("#mobile-overlay").addEventListener("click", () => { $("#sidebar").classList.remove("open"); $("#mobile-overlay").classList.remove("open"); $("#mobile-menu").setAttribute("aria-expanded", "false"); });
    document.addEventListener("keydown", (event) => { if (event.key === "Escape") document.querySelectorAll(".modal-backdrop.open").forEach((modal) => modal.classList.remove("open")); });
    window.addEventListener("resize", drawChart);
    $("#today").textContent = new Intl.DateTimeFormat("pt-BR", { dateStyle: "medium" }).format(new Date());
    loadProducts({ showLoading: true });
})();
