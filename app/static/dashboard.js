(() => {
    const productsData = document.querySelector("#initial-products");
    const permissionsData = document.querySelector("#user-permissions");
    let products = productsData ? JSON.parse(productsData.textContent) : [];
    const permissions = permissionsData ? JSON.parse(permissionsData.textContent) : { canManage: false };
    let movement = { id: null, type: "entrada" };
    let editingId = null;
    let deletingProduct = null;
    let sort = { field: "nome", direction: "asc" };
    let page = 1;
    const pageSize = 8;
    const $ = (selector) => document.querySelector(selector);
    const money = (value) => Number(value).toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
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
            const asString = typeof value === "string" ? value.trim() : value;
            normalized[key] = asString;
        });
        if (!normalized.nome || !String(normalized.nome).trim()) {
            throw new Error("Nome do produto é obrigatório.");
        }
        return normalized;
    }

    function openModal(id) {
        const modal = $(`#${id}`);
        modal.classList.add("open");
        const firstInput = modal.querySelector("input");
        if (firstInput) window.setTimeout(() => firstInput.focus(), 30);
    }

    function closeModal(id) {
        $(`#${id}`).classList.remove("open");
    }

    function updateCategories() {
        const select = $("#category-filter");
        const current = select.value;
        const categories = [...new Set(products.map((product) => product.categoria).filter(Boolean))].sort((a, b) => a.localeCompare(b, "pt-BR"));
        select.innerHTML = '<option value="todas">Todas as categorias</option>' + categories.map((category) => `<option value="${safe(category)}">${safe(category)}</option>`).join("");
        select.value = categories.includes(current) ? current : "todas";
    }

    function filteredProducts() {
        const query = $("#product-search").value.toLocaleLowerCase("pt-BR").trim();
        const status = $("#status-filter").value;
        const category = $("#category-filter").value;
        return products.filter((product) => {
            const searchable = `${product.nome} ${product.categoria || ""}`.toLocaleLowerCase("pt-BR");
            return (!query || searchable.includes(query)) && (status === "todos" || product.status === status) && (category === "todas" || product.categoria === category);
        }).sort((left, right) => {
            const first = left[sort.field];
            const second = right[sort.field];
            const comparison = typeof first === "string" ? first.localeCompare(second, "pt-BR") : first - second;
            return sort.direction === "asc" ? comparison : -comparison;
        });
    }

    function renderPagination(total) {
        const pages = Math.ceil(total / pageSize);
        const pagination = $("#pagination");
        if (pages <= 1) { pagination.innerHTML = ""; return; }
        const buttons = [];
        buttons.push(`<button class="page-button" type="button" data-page="${page - 1}" ${page === 1 ? "disabled" : ""} aria-label="Página anterior">‹</button>`);
        for (let number = 1; number <= pages; number += 1) {
            buttons.push(`<button class="page-button${number === page ? " active" : ""}" type="button" data-page="${number}" aria-label="Página ${number}">${number}</button>`);
        }
        buttons.push(`<button class="page-button" type="button" data-page="${page + 1}" ${page === pages ? "disabled" : ""} aria-label="Próxima página">›</button>`);
        pagination.innerHTML = `<span>Página ${page} de ${pages}</span><div class="page-buttons">${buttons.join("")}</div>`;
    }

    function drawChart(data) {
        const canvas = $("#stock-chart");
        const context = canvas.getContext("2d");
        const width = canvas.clientWidth || 240;
        const height = canvas.clientHeight || 210;
        const ratio = window.devicePixelRatio || 1;
        canvas.width = width * ratio;
        canvas.height = height * ratio;
        context.setTransform(ratio, 0, 0, ratio, 0, 0);
        context.clearRect(0, 0, width, height);
        const ok = data.filter((product) => product.status === "ok").length;
        const low = data.length - ok;
        const total = ok + low;
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

    function render() {
        const low = products.filter((product) => product.status === "baixo");
        $("#total-products").textContent = products.length;
        $("#low-products").textContent = low.length;
        $("#total-units").textContent = products.reduce((total, product) => total + product.estoque_atual, 0).toLocaleString("pt-BR");
        $("#total-value").textContent = money(products.reduce((total, product) => total + product.preco * product.estoque_atual, 0));
        $("#attention-list").innerHTML = low.length ? low.map((product) => `<div class="attention-item"><div><div class="attention-name">${safe(product.nome)}</div><div class="attention-meta">Atual: ${safe(product.estoque_atual)} · mínimo: ${safe(product.estoque_minimo)}</div></div><span class="low-number">Atenção</span></div>`).join("") : '<div class="empty-mini">Tudo certo por aqui.</div>';
        updateCategories();
        const visible = filteredProducts();
        const pages = Math.max(1, Math.ceil(visible.length / pageSize));
        if (page > pages) page = pages;
        const pageItems = visible.slice((page - 1) * pageSize, page * pageSize);
        $("#visible-count").textContent = visible.length;
        $("#empty-state").classList.toggle("visible", !visible.length);
        $("#product-list").innerHTML = pageItems.map((product) => `<tr tabindex="0"><td class="product-name">${safe(product.nome)}</td><td class="category">${safe(product.categoria || "Sem categoria")}</td><td class="price">${money(product.preco)}</td><td class="stock">${safe(product.estoque_atual)}</td><td class="muted">${safe(product.estoque_minimo)}</td><td><span class="status status-${product.status}">${product.status === "ok" ? "Em dia" : "No mínimo ou abaixo"}</span></td><td><div class="row-actions"><button class="icon-btn" type="button" data-movement="entrada" data-id="${product.id}"><span aria-hidden="true">+</span> Entrada</button><button class="icon-btn out" type="button" data-movement="saida" data-id="${product.id}"><span aria-hidden="true">−</span> Saída</button>${permissions.canManage ? `<button class="icon-btn" type="button" data-edit="${product.id}">Editar</button><button class="icon-btn out" type="button" data-delete="${product.id}">Excluir</button>` : ""}</div></td></tr>`).join("");
        renderPagination(visible.length);
        drawChart(products);
    }

    async function api(url, options = {}) {
        const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content;
        const response = await fetch(url, {
            headers: { "Content-Type": "application/json", ...(csrfToken ? { "X-CSRF-Token": csrfToken } : {}), ...options.headers },
            ...options,
        });

        const contentType = response.headers.get("content-type") || "";
        const data = contentType.includes("application/json") ? await response.json() : null;

        if (!response.ok) {
            throw new Error(extractErrorMessage(data));
        }

        if (data && Object.prototype.hasOwnProperty.call(data, "success") && Object.prototype.hasOwnProperty.call(data, "data")) {
            return data.data;
        }

        return data;
    }

    async function loadHistory() {
        const history = await api("/movimentacoes");
        $("#history-list").innerHTML = history.length ? history.map((item) => `<div class="history-row"><div><strong>${safe(item.produto)}</strong><div class="history-date">${safe(new Date(item.data).toLocaleString("pt-BR"))}</div></div><span class="history-type ${item.tipo}">${item.tipo === "entrada" ? "Entrada" : "Saída"}</span><strong>${item.tipo === "entrada" ? "+" : "−"}${safe(item.quantidade)}</strong></div>`).join("") : '<div class="empty-mini">Ainda não há movimentações registradas.</div>';
    }

    function setLoading(form, loading) {
        const submit = form.querySelector("button[type=submit]");
        form.classList.toggle("loading", loading);
        if (submit) {
            setLoadingState(submit, loading, loading ? "Salvando..." : "");
        }
    }

    document.querySelectorAll("button[type=submit]").forEach((button) => {
        button.dataset.defaultText = button.textContent.trim();
    });

    $("#create-form").addEventListener("submit", async (event) => {
        event.preventDefault();
        const form = event.target;
        try {
            const data = normalizeFormData(form);
            data.preco = Number(data.preco); data.custo = Number(data.custo); data.estoque_atual = Number(data.estoque_atual); data.estoque_minimo = Number(data.estoque_minimo);
            setLoading(form, true);
            products.push(await api("/produtos", { method: "POST", body: JSON.stringify(data) }));
            form.reset(); closeModal("create-modal"); page = 1; render(); showToast("Produto cadastrado.");
        }
        catch (error) { showToast(error.message, true); }
        finally { setLoading(form, false); }
    });

    $("#movement-form").addEventListener("submit", async (event) => {
        event.preventDefault();
        const form = event.target;
        const quantity = Number(new FormData(form).get("quantidade"));
        setLoading(form, true);
        try { const product = await api(`/produtos/${movement.id}/${movement.type}`, { method: "POST", body: JSON.stringify({ quantidade: quantity }) }); products = products.map((item) => item.id === product.id ? product : item); closeModal("movement-modal"); render(); showToast("Estoque atualizado."); }
        catch (error) { showToast(error.message, true); } finally { setLoading(form, false); }
    });

    $("#edit-form").addEventListener("submit", async (event) => {
        event.preventDefault();
        const form = event.target;
        try {
            const data = normalizeFormData(form);
            data.preco = Number(data.preco); data.custo = Number(data.custo); data.estoque_minimo = Number(data.estoque_minimo);
            setLoading(form, true);
            const product = await api(`/produtos/${editingId}`, { method: "PUT", body: JSON.stringify(data) });
            products = products.map((item) => item.id === product.id ? product : item);
            closeModal("edit-modal"); render(); showToast("Produto atualizado.");
        }
        catch (error) { showToast(error.message, true); }
        finally { setLoading(form, false); }
    });

    $("#open-create").addEventListener("click", () => openModal("create-modal"));
    $("#confirm-delete").addEventListener("click", async () => {
        if (!deletingProduct) return;
        const button = $("#confirm-delete");
        setLoadingState(button, true, "Excluindo...");
        try {
            await api(`/produtos/${deletingProduct.id}`, { method: "DELETE" });
            products = products.filter((item) => item.id !== deletingProduct.id);
            closeModal("delete-modal");
            showToast("Produto e histórico excluídos.");
            deletingProduct = null;
            render();
        } catch (error) {
            showToast(error.message, true);
        } finally {
            setLoadingState(button, false);
        }
    });
    $("#open-history").addEventListener("click", async () => { try { await loadHistory(); openModal("history-modal"); } catch (error) { showToast(error.message, true); } });
    $("#history-link")?.addEventListener("click", async (event) => {
        event.preventDefault();
        try { await loadHistory(); openModal("history-modal"); } catch (error) { showToast(error.message, true); }
    });
    $("#product-search").addEventListener("input", () => { page = 1; render(); });
    $("#status-filter").addEventListener("change", () => { page = 1; render(); });
    $("#category-filter").addEventListener("change", () => { page = 1; render(); });
    $("#pagination").addEventListener("click", (event) => { const button = event.target.closest("[data-page]"); if (button && !button.disabled) { page = Number(button.dataset.page); render(); } });
    document.querySelectorAll("[data-sort]").forEach((button) => button.addEventListener("click", () => { const field = button.dataset.sort; sort = { field, direction: sort.field === field && sort.direction === "asc" ? "desc" : "asc" }; page = 1; render(); }));

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
            Object.entries({ nome: product.nome, categoria: product.categoria || "", preco: product.preco, custo: product.custo, codigo_barras: product.codigo_barras || "", estoque_minimo: product.estoque_minimo }).forEach(([name, value]) => {
                form.elements[name].value = value;
            });
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

        const pageButton = event.target.closest("[data-page]");
        if (!pageButton) {
            const close = event.target.closest("[data-close]");
            if (close) closeModal(close.dataset.close);
        }
    });

    $("#theme-toggle").addEventListener("click", () => {
        const dark = document.documentElement.dataset.theme !== "dark";
        document.documentElement.dataset.theme = dark ? "dark" : "light";
        localStorage.setItem("stockai-theme", dark ? "dark" : "light");
        $("#theme-toggle").textContent = dark ? "☀ Tema" : "☾ Tema";
        drawChart(products);
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
    window.addEventListener("resize", () => drawChart(products));
    $("#today").textContent = new Intl.DateTimeFormat("pt-BR", { dateStyle: "medium" }).format(new Date());
    updateCategories();
    render();
})();