document.addEventListener('DOMContentLoaded', function() {
    // Находим все элементы, которые начинаются с класса 'type-select-'
    var typeFieldElements = document.querySelectorAll('[class^="type-select-"]');

    // Создаем массив для хранения конфигурации каждого поля
    var typeConfigs = [];

    // Проходимся по каждому найденному элементу и создаем конфигурацию
    typeFieldElements.forEach(function(element, index) {
        var selectedTypeAtr = 'data-show-if-type-' + (index + 1);
        typeConfigs.push({
            element: element,
            selectedTypeAtr: selectedTypeAtr
        });
    });

    // Функция для переключения полей в зависимости от значения "Тип".
    function toggleFields(typeFieldElement, selectedTypeAtr) {
        var typeField = typeFieldElement;
        var allToggleFields = document.querySelectorAll('.toggle-field');

        allToggleFields.forEach(function(field) {
            var selectedTypeAttr = field.getAttribute(selectedTypeAtr);
            if (!selectedTypeAttr) {
                console.log("У поля нет атрибута", selectedTypeAtr + ":", field);
                return;
            }
            var selectedType = JSON.parse(selectedTypeAttr);

            var selectedTypeParentElement = field.closest('p') || field.closest('.form-group');
            if (!selectedTypeParentElement) {
                console.log("Не удалось найти родительский элемент для поля:", field);
                return;
            }

            if (selectedType.includes(typeField.value)) {
                selectedTypeParentElement.style.display = 'block';
                console.log("Родительский элемент показан для поля:", field);
            } else {
                selectedTypeParentElement.style.display = 'none';
                console.log("Родительский элемент скрыт для поля:", field);
            }
        });
    }

    // Для каждой конфигурации вызываем функцию toggleFields при загрузке страницы и при изменении значения
    typeConfigs.forEach(function(config) {
        var typeFieldElement = config.element;
        var selectedTypeAtr = config.selectedTypeAtr;

        if (typeFieldElement) {
            typeFieldElement.addEventListener('change', function() {
                toggleFields(typeFieldElement, selectedTypeAtr);
            });

            toggleFields(typeFieldElement, selectedTypeAtr);
        } else {
            console.log("Элемент не найден на странице.");
        }
    });
});
