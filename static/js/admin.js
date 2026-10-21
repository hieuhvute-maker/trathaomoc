document.addEventListener('click', function (e) {
    const addBtn = e.target.closest('[data-add-row]');
    if (addBtn) {
        const id = addBtn.dataset.addRow;
        const tpl = document.getElementById('tpl-' + id);
        const list = document.querySelector('[data-list="' + id + '"]');
        const uid = 'n' + Date.now() + Math.floor(Math.random() * 1000);
        list.insertAdjacentHTML('beforeend', tpl.innerHTML.split('__IDX__').join(uid));
        return;
    }
    const removeBtn = e.target.closest('[data-remove-row]');
    if (removeBtn) {
        removeBtn.closest('.row-card').remove();
    }
});
