let deletedWordIds = [];

function toggleSoftDelete(button, wordId) {
    const row = document.getElementById(`word-${wordId}`);
    if (!row.classList.contains('is-deleted-blur')) {
        row.classList.add('is-deleted-blur');
        deletedWordIds.push(wordId);
        button.innerHTML = '<i class="fa-solid fa-rotate-left"></i>';
    } else {
        row.classList.remove('is-deleted-blur');
        deletedWordIds = deletedWordIds.filter(id => id !== wordId);
        button.innerHTML = '<i class="fa-solid fa-trash-can"></i>';
    }
}

// ГЛОБАЛЬНЫЙ ПЕРЕХВАТЧИК: Срабатывает всегда, когда пользователь покидает страницу!
window.addEventListener('pagehide', function () {
    if (deletedWordIds.length > 0) {
        // Подготавливаем данные в безопасном формате FormData
        const formData = new FormData();
        formData.append('delete_ids', deletedWordIds.join(','));
        // Берем CSRF-токен прямо из куки или мета-тега
        formData.append('csrfmiddlewaretoken', document.querySelector('[name=csrfmiddlewaretoken]').value);

        // Магия sendBeacon: браузер ГАРАНТИРОВАННО доставит этот POST-запрос на бэк,
        // даже если вкладку закрыли крестиком!
        navigator.sendBeacon('/word/bulk-destroy/', formData);
    }
});
