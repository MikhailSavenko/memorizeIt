let deletedWordIds = [];

function toggleSoftDelete(button, wordId) {

    const saveContainer = document.getElementById('save-changes-container');

    // Приводим к числу, чтобы в массиве были строго Integer
    const numericId = parseInt(wordId, 10);
    const row = document.getElementById(`word-${numericId}`);
    if (!row.classList.contains('is-deleted-blur')) {
        row.classList.add('is-deleted-blur');
        deletedWordIds.push(numericId);
        button.innerHTML = '<i class="fa-solid fa-rotate-left"></i>';
    } else {
        row.classList.remove('is-deleted-blur');
        deletedWordIds = deletedWordIds.filter(id => id !== numericId);
        button.innerHTML = '<i class="fa-solid fa-trash-can"></i>';
    }

    // --- А ВОТ СЮДА ДОБАВЛЯЕМ ТОЛЬКО ПРОВЕРКУ ДЛЯ КНОПКИ ---
    if (deletedWordIds.length > 0) {
        saveContainer.style.display = 'flex'; // Показываем кнопку сохранения
    } else {
        saveContainer.style.display = 'none';  // Прячем кнопку, если все слова вернули назад
    }
}

// Обработчик клика по самой кнопке "Сохранить изменения"
const saveBtn = document.getElementById('save-deletes-btn');

if (saveBtn) {
    saveBtn.addEventListener('click', async function() {
        saveBtn.disabled = true;
        saveBtn.innerText = 'Сохранение...';

        const formData = new FormData();
        formData.append('delete_ids', JSON.stringify(deletedWordIds));
        formData.append('csrfmiddlewaretoken', document.querySelector('[name=csrfmiddlewaretoken]').value);

        try {
            await fetch('/word/bulk_destroy/', {
                method: 'POST',
                body: formData
            });
            deletedWordIds = [];
            window.location.reload(); 
        } catch (error) {
            console.error('Error in save:', error);
            alert('No save. Bad Internet connect.');
            saveBtn.disabled = false;
            saveBtn.innerText = 'Save changes';
        }
    });
}



