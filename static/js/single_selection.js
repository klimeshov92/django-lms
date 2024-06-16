// Получаем все поля выбора с классом "selected_answer".
var singleSelectionFields = document.querySelectorAll('.single_selection');

// Проходимся по каждому полю и добавляем обработчик события.
singleSelectionFields.forEach(function(singleSelectionField) {
    // Добавляем обработчик события при изменении значения.
    singleSelectionField.addEventListener('change', function(event) {
        // Снимаем галочку со всех полей.
        singleSelectionFields.forEach(function(field) {
            field.checked = false;
        });

        // Устанавливаем галочку только на выбранном поле.
        event.target.checked = true;
    });
});
