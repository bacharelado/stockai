(() => {
    const $ = (selector) => document.querySelector(selector);

    function updateInsights() {
        const products = Number($("#total-products")?.textContent || 0);
        const low = Number($("#low-products")?.textContent || 0);
        const units = $("#total-units")?.textContent?.trim() || "0";
        const value = $("#total-value")?.textContent?.trim() || "R$ 0,00";
        const lowNames = [...document.querySelectorAll("#attention-list .attention-name")].map((item) => item.textContent.trim());

        const health = $("#insight-health");
        const healthNote = $("#insight-health-note");
        const priority = $("#insight-priority");
        const priorityNote = $("#insight-priority-note");
        const valueTarget = $("#insight-value");
        const valueNote = $("#insight-value-note");
        if (!health || !healthNote || !priority || !priorityNote || !valueTarget || !valueNote) return;

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
