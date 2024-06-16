document.addEventListener('DOMContentLoaded', function () {
    // Находим элемент выбора типа.
    var typeSelect = document.querySelector('.type-select-1');
    // Если элемент выбора типа не найден, прекращаем выполнение.
    if (!typeSelect) {
        return;
    }
    // Находим элемент инструкции.
    var instructionField = document.querySelector('.instruction');

    // Функция для обновления поля инструкции.
    function updateInstruction() {
        var selectedType = typeSelect.value;
        switch(selectedType) {
            case 'single_selection':
                instructionField.value = 'Выберите один верный ответ';
                break;
            case 'multiple_choice':
                instructionField.value = 'Выберите один или несколько верных ответов';
                break;
            case 'sorting':
                instructionField.value = 'Выберите верный порядок ответов';
                break;
            case 'compliance':
                instructionField.value = 'Соотнесите ответы с предложенными пунктами';
                break;
            case 'text_input':
                instructionField.value = 'Введите верное значение текстом';
                break;
            case 'numeric_input':
                instructionField.value = 'Введите верное значение числом';
                break;
            default:
                instructionField.value = ''; // Очистить инструкцию, если тип не выбран.
        }
    }

    // Добавляем обработчик события изменения для поля выбора типа.
    typeSelect.addEventListener('change', updateInstruction);

    // Вызываем функцию обновления инструкции при первоначальной загрузке страницы.
    updateInstruction();
});
