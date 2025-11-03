document.addEventListener('DOMContentLoaded', () => {
    const apiUrl = 'http://127.0.0.1:5006/api';
    const computerList = document.getElementById('computer-list');
    const addComputerBtn = document.getElementById('add-computer-btn');
    const formModal = document.getElementById('form-modal');
    const detailsModal = document.getElementById('details-modal');
    const closeBtns = document.querySelectorAll('.close-btn');
    const computerForm = document.getElementById('computer-form');
    const formTitle = document.getElementById('form-title');

    let currentComputerId = null;

    // Fetch and display all computers
    async function fetchComputers() {
        try {
            const response = await fetch(`${apiUrl}/computers`);
            const computers = await response.json();
            computerList.innerHTML = '';
            computers.forEach(computer => {
                const item = document.createElement('div');
                item.className = 'computer-item';
                item.innerHTML = `
                    <span>${computer.brand} ${computer.model} (${computer.serial_number})</span>
                    <div>
                        <button class="btn view-btn" data-id="${computer.id}">Ver</button>
                        <button class="btn edit-btn" data-id="${computer.id}">Editar</button>
                        <button class="btn delete-btn" data-id="${computer.id}">Eliminar</button>
                    </div>
                `;
                computerList.appendChild(item);
            });
        } catch (error) {
            console.error('Error fetching computers:', error);
        }
    }

    // Show modal
    function showModal(modal) {
        modal.style.display = 'block';
    }

    // Hide modal
    function hideModal(modal) {
        modal.style.display = 'none';
    }

    // Open "add computer" form
    addComputerBtn.addEventListener('click', () => {
        formTitle.textContent = 'Agregar Computadora';
        computerForm.reset();
        currentComputerId = null;
        showModal(formModal);
    });

    // Close modals
    closeBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            hideModal(e.target.closest('.modal'));
        });
    });

    // Handle form submission (add/edit)
    computerForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const formData = {
            serial_number: document.getElementById('serial_number').value,
            brand: document.getElementById('brand').value,
            model: document.getElementById('model').value,
            purchase_date: document.getElementById('purchase_date').value,
            purchase_price: document.getElementById('purchase_price').value,
            status: document.getElementById('status').value,
            location: document.getElementById('location').value,
            assigned_to: document.getElementById('assigned_to').value,
        };

        const method = currentComputerId ? 'PUT' : 'POST';
        const url = currentComputerId ? `${apiUrl}/computers/${currentComputerId}` : `${apiUrl}/computers`;

        try {
            const response = await fetch(url, {
                method: method,
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formData),
            });
            if (response.ok) {
                hideModal(formModal);
                fetchComputers();
            }
        } catch (error) {
            console.error('Error saving computer:', error);
        }
    });

    // Handle clicks on computer list (view, edit, delete)
    computerList.addEventListener('click', async (e) => {
        const id = e.target.dataset.id;
        if (!id) return;

        if (e.target.classList.contains('delete-btn')) {
            if (confirm('¿Estás seguro de que quieres eliminar este equipo?')) {
                try {
                    await fetch(`${apiUrl}/computers/${id}`, { method: 'DELETE' });
                    fetchComputers();
                } catch (error) {
                    console.error('Error deleting computer:', error);
                }
            }
        } else if (e.target.classList.contains('edit-btn')) {
            // Fetch computer data and populate form
            try {
                const response = await fetch(`${apiUrl}/computers/${id}`);
                const computer = await response.json();
                formTitle.textContent = 'Editar Computadora';
                document.getElementById('computer-id').value = computer.id;
                document.getElementById('serial_number').value = computer.serial_number;
                document.getElementById('brand').value = computer.brand;
                document.getElementById('model').value = computer.model;
                document.getElementById('purchase_date').value = computer.purchase_date;
                document.getElementById('purchase_price').value = computer.purchase_price;
                document.getElementById('status').value = computer.status;
                document.getElementById('location').value = computer.location;
                document.getElementById('assigned_to').value = computer.assigned_to;
                currentComputerId = id;
                showModal(formModal);
            } catch (error) {
                console.error('Error fetching computer for edit:', error);
            }
        } else if (e.target.classList.contains('view-btn')) {
            // Fetch all details and show details modal
            showDetails(id);
        }
    });

    async function showDetails(id) {
        try {
            // Fetch computer details
            const compRes = await fetch(`${apiUrl}/computers/${id}`);
            const computer = await compRes.json();
            document.getElementById('details-title').textContent = `${computer.brand} ${computer.model}`;
            document.getElementById('computer-details').innerHTML = `
                <p><strong>Número de Serie:</strong> ${computer.serial_number}</p>
                <p><strong>Ubicación:</strong> ${computer.location}</p>
                <p><strong>Asignado a:</strong> ${computer.assigned_to}</p>
                <p><strong>Estado:</strong> ${computer.status}</p>
            `;

            // Fetch and display QR code
            document.getElementById('qr-code-container').innerHTML = `<img src="${apiUrl}/computers/${id}/qr" alt="QR Code">`;

            // Fetch and display depreciation
            const depRes = await fetch(`${apiUrl}/computers/${id}/depreciation`);
            const depreciation = await depRes.json();
            document.getElementById('depreciation-info').innerHTML = `
                <h4>Depreciación</h4>
                <p>Valor Contable Actual: $${depreciation.current_book_value}</p>
                <p>Depreciación Anual: $${depreciation.annual_depreciation}</p>
            `;

            // Fetch and display software
            const swRes = await fetch(`${apiUrl}/computers/${id}/software`);
            const software = await swRes.json();
            const swList = document.getElementById('software-list');
            swList.innerHTML = software.map(s => `<li>${s.name}</li>`).join('');

            // Fetch and display policies
            const polRes = await fetch(`${apiUrl}/policies`);
            const policies = await polRes.json();
            const polList = document.getElementById('policy-list');
            polList.innerHTML = policies.map(p => `<div><h4>${p.title}</h4><p>${p.content}</p></div>`).join('');


            showModal(detailsModal);
        } catch (error) {
            console.error('Error fetching details:', error);
        }
    }

    // Initial fetch
    fetchComputers();
});
