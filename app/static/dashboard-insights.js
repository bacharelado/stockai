(() => {
    const $ = (selector) => document.querySelector(selector);
    function updateInsights() {
        const summary = window.stockaiSummary || {};
        const products = Number(summary.total_products || 0);
        const low = Number(summary.low_products || 0);
        const units = Number(summary.total_units || 0).toLocaleString("pt-BR");
        const value = Number(summary.total_value || 0).toLocaleString("pt-BR", { style: "currency", currency: "BRL" });
        const lowItems = Array.isArray(summary.low_items) ? summary.low_items : [];
        const health = $("#insight-health");
        const healthNote = $("#insight-health-note");
        const priority = $("#insight-priority");
        const priorityNote = $("#insight-priority-note");
        const valueTarget = $("#insight-value");
        const valueNote = $("#insight-value-note");
        const replenishment = $("#insight-replenishment");
        const replenishmentNote = $("#insight-replenishment-note");
        if (!health || !healthNote || !priority || !priorityNote || !valueTarget || !valueNote || !replenishment || !replenishmentNote) return;
        const suggestedUnits = Number(summary.replenishment_units || 0);
        replenishment.textContent = `${suggestedUnits.toLocaleString("pt-BR")} ${suggestedUnits === 1 ? "unidade" : "unidades"}`;
        replenishmentNote.textContent = suggestedUnits ? `${lowItems[0]?.nome || "Itens em alerta"}${lowItems.length > 1 ? ` e mais ${lowItems.length - 1}` : ""}. Sugestão baseada no estoque mínimo.` : "Nenhuma reposição sugerida no momento.";
        if (!products) {
            health.textContent = "Pronto para começar";
            healthNote.textContent = "Cadastre seu primeiro produto para liberar os insights.";
            priority.textContent = "Nenhuma prioridade";
            priorityNote.textContent = "Seu estoque ainda não tem itens cadastrados.";
            valueTarget.textContent = value;
            valueNote.textContent = "Valor atual do estoque";
            return;
        }
        const lowRate = low / products;
        health.textContent = low === 0 ? "Estoque saudável" : lowRate <= 0.2 ? "Atenção moderada" : "Atenção alta";
        healthNote.textContent = low === 0 ? `${products} ${products === 1 ? "produto está" : "produtos estão"} dentro do mínimo.` : `${low} de ${products} ${products === 1 ? "produto está" : "produtos estão"} no mínimo ou abaixo.`;
        if (lowItems.length) {
            priority.textContent = lowItems[0].nome;
            priorityNote.textContent = lowItems.length === 1 ? "É o item que merece conferência primeiro." : `Mais ${lowItems.length - 1} ${lowItems.length - 1 === 1 ? "item precisa" : "itens precisam"} de atenção.`;
        } else {
            priority.textContent = "Tudo em dia";
            priorityNote.textContent = "Nenhum produto atingiu o estoque mínimo.";
        }
        valueTarget.textContent = value;
        valueNote.textContent = `${units} ${units === "1" ? "unidade disponível" : "unidades disponíveis"}.`;
    }
    document.addEventListener("DOMContentLoaded", () => {
        updateInsights();
        window.addEventListener("stockai:summary-updated", updateInsights);
        const observed = ["#total-products", "#low-products", "#total-units", "#total-value", "#attention-list"];
        const observer = new MutationObserver(updateInsights);
        observed.forEach((selector) => { const element = $(selector); if (element) observer.observe(element, { childList: true, characterData: true, subtree: true }); });
    });
})();
