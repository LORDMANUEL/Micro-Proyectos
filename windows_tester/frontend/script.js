document.addEventListener('DOMContentLoaded', () => {
    const apiUrl = 'http://127.0.0.1:5009/api';

    const diagnoseForm = document.getElementById('diagnose-form');
    const problemDescription = document.getElementById('problem-description');
    const resultContainer = document.getElementById('result-container');
    const diagnosticGuide = document.getElementById('diagnostic-guide');

    diagnoseForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        const problem = problemDescription.value;
        if (!problem) return;

        // Show loading state
        resultContainer.style.display = 'block';
        diagnosticGuide.innerHTML = '<p>Generando guía de diagnóstico, por favor espera...</p>';

        try {
            const response = await fetch(`${apiUrl}/diagnose`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ problem }),
            });

            if (!response.ok) {
                throw new Error('La respuesta del servidor no fue exitosa.');
            }

            const data = await response.json();
            diagnosticGuide.textContent = data.diagnostic_guide;

        } catch (error) {
            console.error('Error al generar la guía:', error);
            diagnosticGuide.innerHTML = '<p>Ocurrió un error al contactar al servicio de IA. Por favor, inténtalo de nuevo más tarde.</p>';
        }
    });
});
