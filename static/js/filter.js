document.addEventListener('DOMContentLoaded', function() {
    const filtersButtons = document.querySelectorAll('.filters-button');
    const filtersAreas = document.querySelectorAll('.filters-area');

    // Проверяем, существуют ли элементы на странице.
    if (!filtersButtons.length || !filtersAreas.length) {
        return; // Прерываем выполнение, если элементы не найдены.
    }

    // Добавляем обработчик события клика на каждую кнопку фильтра.
    filtersButtons.forEach(function(filtersButton, index) {
        // Получаем соответствующую область фильтра по индексу.
        const filtersArea = filtersAreas[index];

        // Проверяем, сохранено ли состояние показа фильтров в localStorage.
        const filtersVisible = localStorage.getItem(`filtersVisible_${index}`);

        // Если состояние сохранено и равно 'true', показываем фильтры.
        if (filtersVisible === 'true') {
            filtersArea.classList.add('active');
        }

        // Вешаем обработчик события клика на кнопку фильтра.
        filtersButton.addEventListener('click', function(event) {
            // Предотвращаем стандартное действие кнопки (перезагрузку страницы).
            event.preventDefault();

            // Переключаем класс 'active' для соответствующей области фильтра.
            filtersArea.classList.toggle('active');

            // Сохраняем текущее состояние показа фильтров в localStorage.
            const filtersVisible = filtersArea.classList.contains('active');
            localStorage.setItem(`filtersVisible_${index}`, filtersVisible);
        });
    });
});
