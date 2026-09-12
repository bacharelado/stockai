(() => {
    const $ = (selector) => document.querySelector(selector);

    function updateInsights() {
        const products = Number($("#total-products")?.textContent || 0);
        const low = Number($("#low-products")?.textContent || 0);
        const units = $("#total-units")?.textContent?.trim() || "0";
        const value = $("#total-value")?.textContent?.trim() || "R$ 0,00";
        const lowNames = [...document.querySelectorAll("#attention-list .attention-name")].map((item) => item.textContent.trim());
        const dataElement = $("#initial-products");
        let productData = [];
        try { productData = dataElement ? JSON.parse(dataElement.textContent) : []; } catch (_) { productData = []; }

        const health = $("#insight-health");
        const healthNote = $("#insight-health-note");
        const priority = $("#insight-priority");
        const priorityNote = $("#insight-priority-note");
        const valueTarget = $("#insight-value");
        const valueNote = $("#insight-value-note");
        const replenishment = $("#insight-replenishment");
        const replenishmentNote = $("#insight-replenishment-note");
        if (!health || !healthNote || !priority || !priorityNote || !valueTarget || !valueNote || !replenishment || !replenishmentNote) return;

        const suggestedUnits = productData.reduce((total, product) => {
            const current = Number(product.estoque_atual) || 0;
            const minimum = Number(product.estoque_minimo) || 0;
            return total + Math.max(0, minimum - current);
        }, 0);
        const urgent = [...productData]
            .filter((product) => Number(product.estoque_atual) <= Number(product.estoque_minimo))
            .sort((a, b) => {
                const deficitA = Math.max(0, Number(a.estoque_minimo) - Number(a.estoque_atual));
                const deficitB = Math.max(0, Number(b.estoque_minimo) - Number(b.estoque_atual));
                return deficitB - deficitA;
            });

        replenishment.textContent = `${suggestedUnits.toLocaleString("pt-BR")} ${suggestedUnits === 1 ? "unidade" : "unidades"}`;
        if (!suggestedUnits) {
            replenishmentNote.textContent = "Nenhuma reposição sugerida no momento.";
        } else {
            const main = urgent[0]?.nome || "itens em alerta";
            replenishmentNote.textContent = `${main}${urgent.length > 1 ? ` e mais ${urgent.length - 1}` : ""}. Sugestão baseada no estoque mínimo.`;
        }

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
        healthNote.textContent = low === 0
            ? `${products} ${products === 1 ? "produto está" : "produtos estão"} dentro do mínimo.`
            : `${low} de ${products} ${products === 1 ? "produto está" : "produtos estão"} no mínimo ou abaixo.`;

        if (lowNames.length) {
            priority.textContent = lowNames[0];
            priorityNote.textContent = lowNames.length === 1 ? "É o item que merece conferência primeiro." : `Mais ${lowNames.length - 1} ${lowNames.length - 1 === 1 ? "item precisa" : "itens precisam"} de atenção.`;
        } else {
            priority.textContent = "Tudo em dia";
            priorityNote.textContent = "Nenhum produto atingiu o estoque mínimo.";
        }

        valueTarget.textContent = value;
        valueNote.textContent = `${units} ${units === "1" ? "unidade disponível" : "unidades disponíveis"}.`;
    }

    document.addEventListener("DOMContentLoaded", () => {
        updateInsights();
        const observed = ["#total-products", "#low-products", "#total-units", "#total-value", "#attention-list"];
        const observer = new MutationObserver(updateInsights);
        observed.forEach((selector) => {
            const element = $(selector);
            if (element) observer.observe(element, { childList: true, characterData: true, subtree: true });
        });
    });
})();
