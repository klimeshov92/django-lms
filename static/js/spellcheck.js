// Функция для настройки CKEditor.
function setupCKEditor() {
    console.log("Настройка CKEditor...");
    // Подписываемся на событие 'instanceReady' CKEditor, которое срабатывает, когда редактор полностью инициализирован.
    CKEDITOR.on('instanceReady', function(ev) {
        console.log("Редактор CKEditor готов к использованию.");
        // Получаем экземпляр редактора из объекта события.
        var editor = ev.editor;
        // Снимаем режим только для чтения, чтобы сделать редактор интерактивным.
        editor.setReadOnly(false);
        console.log("Редактор теперь интерактивный.");
        // Устанавливаем атрибут 'spellcheck' в 'true' для тела документа в редакторе, чтобы включить проверку орфографии.
        editor.document.getBody().setAttribute('spellcheck', 'true');
        console.log("Проверка орфографии включена для тела редактора.");
    });
}

// Делаем функцию глобальной, присваивая ее глобальному объекту 'window'.
window.setupCKEditor = setupCKEditor;

// Ждем, пока документ полностью загрузится, и затем вызываем функцию для настройки CKEditor.
document.addEventListener('DOMContentLoaded', setupCKEditor);