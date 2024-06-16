document.addEventListener("DOMContentLoaded", function() {
    // Пытаемся найти элемент с id "copy_link"
    var copyLinkElement = document.getElementById("copy_link");

    // Проверяем, существует ли элемент
    if (copyLinkElement) {
        console.log("Элемент с id 'copy_link' найден");

        // Если элемент существует, добавляем к нему обработчик события клика
        copyLinkElement.addEventListener("click", function(event) {
            event.preventDefault(); // Отменяем стандартное действие перехода по ссылке

            console.log("Клик по элементу с id 'copy_link' произведен");

            // Получаем URL из атрибута href ссылки
            var urlToCopy = event.target.getAttribute("href");
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
    } else {
        console.log("Элемент с id 'copy_link' не найден");
    }
});
