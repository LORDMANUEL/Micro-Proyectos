document.addEventListener('DOMContentLoaded', () => {
    const apiUrl = 'http://127.0.0.1:5007/api';

    // Main elements
    const printerList = document.getElementById('printer-list');
    const addPrinterBtn = document.getElementById('add-printer-btn');
    const manageTonerBtn = document.getElementById('manage-toner-btn');

    // Modals
    const printerFormModal = document.getElementById('printer-form-modal');
    const tonerModal = document.getElementById('toner-modal');
    const detailsModal = document.getElementById('details-modal');
    const closeBtns = document.querySelectorAll('.close-btn');

    // Forms
    const printerForm = document.getElementById('printer-form');
    const tonerCartridgeForm = document.getElementById('toner-cartridge-form');
    const tonerInventoryForm = document.getElementById('toner-inventory-form');
    const logTonerChangeForm = document.getElementById('log-toner-change-form');

    let currentPrinterId = null;

    // --- Core Functions ---
    async function fetchData(endpoint) {
        try {
            const response = await fetch(`${apiUrl}${endpoint}`);
            if (!response.ok) throw new Error(`Error fetching ${endpoint}`);
            return await response.json();
        } catch (error) {
            console.error(error);
        }
    }

    async function postData(endpoint, data) {
        try {
            const response = await fetch(`${apiUrl}${endpoint}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data),
            });
            if (!response.ok) throw new Error(`Error posting to ${endpoint}`);
            return await response.json();
        } catch (error) {
            console.error(error);
        }
    }

    // --- Render Functions ---
    async function renderPrinters() {
        const printers = await fetchData('/printers');
        printerList.innerHTML = '';
        if (!printers) return;
        printers.forEach(printer => {
            const item = document.createElement('div');
            item.className = 'printer-item';
            item.innerHTML = `
                <span>${printer.name} (${printer.model}) - ${printer.location}</span>
                <div>
                    <button class="btn view-btn" data-id="${printer.id}">Ver Detalles</button>
                    <button class="btn delete-btn" data-id="${printer.id}">Eliminar</button>
                </div>
            `;
            printerList.appendChild(item);
        });
    }

    async function renderTonerInventory() {
        const inventory = await fetchData('/toner_inventory');
        const list = document.getElementById('toner-inventory-list');
        list.innerHTML = '<h4>Stock Actual</h4>';
        if (!inventory) return;
        inventory.forEach(item => {
            list.innerHTML += `<p>${item.model} (${item.color}): ${item.quantity} unidades</p>`;
        });
    }

    async function populateTonerSelects() {
        const cartridges = await fetchData('/toner_cartridges');
        const inventorySelect = document.getElementById('inventory-toner-select');
        const logSelect = document.getElementById('log-toner-select');
        inventorySelect.innerHTML = '';
        logSelect.innerHTML = '';
        if (!cartridges) return;
        cartridges.forEach(c => {
            const option = `<option value="${c.id}">${c.model} (${c.color})</option>`;
            inventorySelect.innerHTML += option;
            logSelect.innerHTML += option;
        });
    }

    // --- Event Listeners ---
    addPrinterBtn.addEventListener('click', () => printerFormModal.style.display = 'block');
    manageTonerBtn.addEventListener('click', async () => {
        await renderTonerInventory();
        await populateTonerSelects();
        tonerModal.style.display = 'block';
    });

    closeBtns.forEach(btn => btn.addEventListener('click', () => {
        [printerFormModal, tonerModal, detailsModal].forEach(m => m.style.display = 'none');
    }));

    printerForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const data = {
            name: document.getElementById('name').value,
            model: document.getElementById('model').value,
            ip_address: document.getElementById('ip_address').value,
            location: document.getElementById('location').value,
            purchase_date: document.getElementById('purchase_date').value,
            purchase_price: document.getElementById('purchase_price').value,
            driver_url: document.getElementById('driver_url').value,
            notes: document.getElementById('notes').value,
        };
        await postData('/printers', data);
        printerForm.reset();
        printerFormModal.style.display = 'none';
        renderPrinters();
    });

    tonerCartridgeForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const data = {
            model: document.getElementById('toner-model').value,
            color: document.getElementById('toner-color').value,
            yield: document.getElementById('toner-yield').value,
        };
        await postData('/toner_cartridges', data);
        tonerCartridgeForm.reset();
        populateTonerSelects();
    });

    tonerInventoryForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const data = {
            cartridge_id: document.getElementById('inventory-toner-select').value,
            quantity: parseInt(document.getElementById('inventory-quantity').value, 10),
        };
        await postData('/toner_inventory', data);
        tonerInventoryForm.reset();
        renderTonerInventory();
    });

    printerList.addEventListener('click', async (e) => {
        currentPrinterId = e.target.dataset.id;
        if (!currentPrinterId) return;

        if (e.target.classList.contains('view-btn')) {
            await showDetails(currentPrinterId);
        } else if (e.target.classList.contains('delete-btn')) {
            if (confirm('¿Seguro que quieres eliminar esta impresora?')) {
                await fetch(`${apiUrl}/printers/${currentPrinterId}`, { method: 'DELETE' });
                renderPrinters();
            }
        }
    });

    logTonerChangeForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const data = {
            cartridge_id: document.getElementById('log-toner-select').value,
            change_date: document.getElementById('log-change-date').value,
        };
        await postData(`/printers/${currentPrinterId}/toner_logs`, data);
        logTonerChangeForm.reset();
        alert('Cambio de tóner registrado.');
    });

    async function showDetails(id) {
        const printer = await fetchData(`/printers/${id}`);
        document.getElementById('details-title').textContent = `Detalles de ${printer.name}`;
        document.getElementById('printer-details').innerHTML = `
            <p><strong>Modelo:</strong> ${printer.model}</p>
            <p><strong>Ubicación:</strong> ${printer.location}</p>
            <p><strong>IP:</strong> ${printer.ip_address}</p>
        `;

        // Populate toner log select
        await populateTonerSelects();

        // Reset AI fields and fetch them
        document.getElementById('toner-prediction').textContent = 'Cargando...';
        document.getElementById('profitability-analysis').textContent = 'Cargando...';
        document.getElementById('repairability-analysis').textContent = 'Cargando...';
        detailsModal.style.display = 'block';

        const prediction = await fetchData(`/printers/${id}/predict_toner`);
        document.getElementById('toner-prediction').textContent = prediction.prediction;

        const profitability = await fetchData(`/printers/${id}/profitability`);
        document.getElementById('profitability-analysis').textContent = profitability.analysis;

        const repairability = await fetchData(`/printers/${id}/repairability`);
        document.getElementById('repairability-analysis').textContent = repairability.analysis;
    }

    // --- Initial Load ---
    renderPrinters();
});
