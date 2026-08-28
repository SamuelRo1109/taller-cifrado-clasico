function mostrarParametros(tipo) {
    document.getElementById('params-cesar').style.display = tipo === 'cesar' ? 'block' : 'none';
    document.getElementById('params-afin').style.display = tipo === 'afin' ? 'block' : 'none';
    document.getElementById('params-vigenere').style.display = tipo === 'vigenere' ? 'block' : 'none';
}

document.addEventListener('DOMContentLoaded', () => {
    const tabButtons = document.querySelectorAll('.tab-btn');
    tabButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            btn.classList.add('active');
            document.getElementById('tab-' + btn.dataset.tab).classList.add('active');
        });
    });

    const tipoSelect = document.getElementById('tipo_cifrado');
    if (tipoSelect) mostrarParametros(tipoSelect.value);
});