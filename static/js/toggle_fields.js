document.addEventListener('DOMContentLoaded', function() {
    // Находим все элементы, которые начинаются с класса 'type-select-'
    var typeFieldElements = document.querySelectorAll('[class^="type-select-"]');

    // Функция для переключения полей в зависимости от значения "Тип".
    function toggleFields(typeFieldElement, selectedTypeAtr) {
        var value = typeFieldElement.type === "checkbox" ? typeFieldElement.checked : typeFieldElement.value;
        console.log("value", value);

        // Проходим по всем элементам с классом 'toggle-field'
        document.querySelectorAll('.toggle-field').forEach(function(field) {
            var selectedTypeAttr = field.getAttribute(selectedTypeAtr);
            if (!selectedTypeAttr) return;  // Если атрибут не найден, пропускаем

            console.log("selectedTypeAttr", selectedTypeAttr);

            // Преобразуем атрибут в массив, если это необходимо
            var selectedType = [];
            try {
                selectedType = JSON.parse(selectedTypeAttr);
            } catch (e) {
                selectedType = [selectedTypeAttr];  // Если не удалось, обрабатываем как строку
            }
            console.log("selectedType", selectedType);

            var parentElement = field.closest('p') || field.closest('.form-group');
            if (parentElement) {
                parentElement.style.display = selectedType.includes(value) ? 'block' : 'none';
                console.log(selectedType.includes(value) ? "Показан" : "Скрыт", "для поля:", field);
            }
        });
    }

    // Настроим обработку изменений
    typeFieldElements.forEach(function(element, index) {
        var selectedTypeAtr = 'data-show-if-type-' + (index + 1);
        element.addEventListener('change', function() {
            toggleFields(element, selectedTypeAtr);
        });
        toggleFields(element, selectedTypeAtr);  // При загрузке страницы тоже вызываем
    });
});
