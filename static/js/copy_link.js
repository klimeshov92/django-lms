document.addEventListener("DOMContentLoaded", function() {
    // Находим все элементы с классом "copy_link"
    var copyLinkElements = document.querySelectorAll(".copy_link");

    // Перебираем все найденные элементы и добавляем обработчик события клика
    copyLinkElements.forEach(function(copyLinkElement) {
        copyLinkElement.addEventListener("click", function(event) {
            event.preventDefault();

            console.log("Клик по элементу с классом 'copy_link' произведен");

            // Получаем URL из атрибута href ссылки
            var urlToCopy = copyLinkElement.getAttribute("href");
            console.log("URL для копирования:", urlToCopy);

            // Создаем временное текстовое поле и устанавливаем его значение равным URL
            var urlField = document.createElement("input");
            urlField.value = urlToCopy;

            // Добавляем временное текстовое поле в тело документа
            document.body.appendChild(urlField);

            // Выделяем содержимое текстового поля
            urlField.select();

            // Копируем выделенный текст в буфер обмена
            var successful = document.execCommand("copy");
            if (successful) {
                console.log("Текст успешно скопирован в буфер обмена");
                alert("Ссылка скопирована в буфер обмена");
            } else {
                console.log("Не удалось скопировать текст в буфер обмена");
                alert("Не удалось скопировать ссылку в буфер обмена");
            }

            // Удаляем временное текстовое поле из документа
            document.body.removeChild(urlField);
        });
    });
});
