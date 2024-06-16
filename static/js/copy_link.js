document.addEventListener("DOMContentLoaded", function() {
    // Пытаемся найти элемент с id "copy_link"
    var copyLinkElement = document.getElementById("copy_link");

    // Проверяем, существует ли элемент
    if (copyLinkElement) {
        // Если элемент существует, добавляем к нему обработчик события клика
        copyLinkElement.addEventListener("click", function(event) {
            event.preventDefault(); // Отменяем стандартное действие перехода по ссылке

            // Создаем временное текстовое поле и устанавливаем его значение равным URL из атрибута href ссылки
            var urlField = document.createElement("input");
            urlField.value = event.target.getAttribute("href");

            // Добавляем временное текстовое поле в тело документа
            document.body.appendChild(urlField);

            // Выделяем содержимое текстового поля
            urlField.select();

            // Копируем выделенный текст в буфер обмена
            document.execCommand("copy");

            // Удаляем временное текстовое поле из документа
            document.body.removeChild(urlField);

            // Выводим сообщение об успешном копировании
            alert("Ссылка скопирована в буфер обмена");
        });
    }
    // Если элемент не найден, ничего не делаем.
});
