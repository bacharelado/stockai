(() => {
    const money = (value) => Number(value).toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
    const safe = (value) => { const el = document.createElement("span"); el.textContent = value ?? ""; return el.innerHTML; };
    const api = async (url) => {
        const response = await fetch(url, { headers: { "Accept": "application/json" } });
        const payload = await response.json();
        if (!response.ok) throw new Error(payload?.data?.detail || payload?.detail || "Não foi possível carregar o relatório.");
        return payload?.data ?? payload;
    };
    const csvCell = (value) => `"${String(value ?? "").replaceAll('"', '""')}"`;

    async function load() {
        document.querySelector("#app").classList.add("loading");
        try {
            const [products, movements] = await Promise.all([api("/produtos"), api("/movimentacoes")]);
            const low = products.filter((item) => item.status === "baixo");
            const units = products.reduce((sum, item) => sum + Number(item.estoque_atual || 0), 0);
            const totalValue = products.reduce((sum, item) => sum + Number(item.preco || 0) * Number(item.estoque_atual || 0), 0);
            document.querySelector("#products").textContent = products.length.toLocaleString("pt-BR");
            document.querySelector("#low").textContent = low.length.toLocaleString("pt-BR");
            document.querySelector("#units").textContent = units.toLocaleString("pt-BR");
            document.querySelector("#value").textContent = money(totalValue);

            document.querySelector("#attention").innerHTML = low.length
                ? `<table><thead><tr><th>Produto</th><th>Atual</th><th>Mínimo</th></tr></thead><tbody>${low.map((item) => `<tr><td>${safe(item.nome)}</td><td class="status-low">${item.estoque_atual}</td><td>${item.estoque_minimo}</td></tr>`).join("")}</tbody></table>`
                : '<div class="empty">Nenhum produto precisa de atenção.</div>';

            const byCategory = {};
            products.forEach((item) => {
                const category = item.categoria || "Sem categoria";
                byCategory[category] = (byCategory[category] || 0) + Number(item.preco || 0) * Number(item.estoque_atual || 0);
            });
            const categories = Object.entries(byCategory).sort((a, b) => b[1] - a[1]);
            document.querySelector("#categories").innerHTML = categories.length
                ? `<table><thead><tr><th>Categoria</th><th>Valor</th></tr></thead><tbody>${categories.map(([name, amount]) => `<tr><td>${safe(name)}</td><td>${money(amount)}</td></tr>`).join("")}</tbody></table>`
                : '<div class="empty">Cadastre produtos para ver este relatório.</div>';

            const recent = movements.slice(0, 10);
            document.querySelector("#movements").innerHTML = recent.length
                ? `<table><thead><tr><th>Data</th><th>Produto</th><th>Tipo</th><th>Quantidade</th></tr></thead><tbody>${recent.map((item) => `<tr><td>${safe(new Date(item.data).toLocaleString("pt-BR"))}</td><td>${safe(item.produto)}</td><td class="${item.tipo === "entrada" ? "status-ok" : "status-low"}">${item.tipo === "entrada" ? "Entrada" : "Saída"}</td><td>${item.quantidade}</td></tr>`).join("")}</tbody></table>`
                : '<div class="empty">Ainda não há movimentações.</div>';

            document.querySelector("#download").onclick = () => {
                const rows = [["Produto", "Categoria", "Preço", "Estoque atual", "Estoque mínimo", "Valor no estoque", "Status"], ...products.map((item) => [item.nome, item.categoria || "Sem categoria", item.preco, item.estoque_atual, item.estoque_minimo, Number(item.preco) * Number(item.estoque_atual), item.status])];
                const csv = rows.map((row) => row.map(csvCell).join(",")).join("\n");
                const blob = new Blob(["\ufeff" + csv], { type: "text/csv;charset=utf-8" });
                const url = URL.createObjectURL(blob);
                const link = document.createElement("a"); link.href = url; link.download = "stockai-relatorio.csv"; link.click(); URL.revokeObjectURL(url);
            };
        } catch (error) {
            document.querySelector("#app").innerHTML += `<div class="card"><strong>Não foi possível carregar os relatórios.</strong><p class="muted">${safe(error.message)}</p><p class="muted"><a href="/login">Entrar novamente</a></p></div>`;
        } finally {
            document.querySelector("#app").classList.remove("loading");
        }
    }
    load();
})();
