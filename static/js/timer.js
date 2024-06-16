// Функция запуска таймера.
function startTimer(duration, display) {
    // Вывод в консоль сообщения о запуске таймера с указанием его продолжительности.
    console.log("Таймер запущен с продолжительностью: " + duration);

    // Объявление переменных: timer для отслеживания оставшегося времени, minutes и seconds для минут и секунд.
    var timer = duration, minutes, seconds;

    // Настройка повторяющегося интервала (каждую секунду) для функции обратного отсчета.
    var interval = setInterval(function () {
        // Расчет количества минут и секунд, оставшихся до конца таймера.
        minutes = parseInt(timer / 60, 10);
        seconds = parseInt(timer % 60, 10);

        // Добавление ведущего нуля к минутам и секундам, если они меньше 10.
        minutes = minutes < 10 ? "0" + minutes : minutes;
        seconds = seconds < 10 ? "0" + seconds : seconds;

        // Установка текста элемента display для показа оставшегося времени.
        display.textContent = minutes + ":" + seconds;

        // Вывод в консоль оставшегося времени.
        console.log("Оставшееся время: " + minutes + ":" + seconds);

        // Уменьшение таймера на 1 каждую секунду и проверка, не истекло ли время.
        if (--timer < 0) {
            // Если время истекло, остановка интервала.
            clearInterval(interval);
            // Вывод в консоль сообщения о завершении работы таймера.
            console.log("Таймер завершил свою работу.");
            // Перенаправление пользователя на другую страницу.
            window.location.href = "/tests/attempt_end_timeout/" + window.testsResultId + "/";
        }
    }, 1000);
}

// Функция настройки таймера.
function setupTimer() {
    // Поиск элемента с идентификатором 'timer' и сохранение его в переменную display.
    var display = document.querySelector('#timer');

    // Проверка, найден ли элемент для отображения таймера.
    if (!display) {
        // Вывод в консоль сообщения, если элемент не найден.
        console.log("Элемент таймера не найден.");
        return;
    }

    // Проверка, определена ли глобальная переменная timerDuration.
    if (typeof window.timerDuration === 'undefined') {
        // Вывод в консоль сообщения, если продолжительность таймера не определена.
        console.log("Продолжительность таймера не определена.");
        return;
    }

    // Запуск таймера с заданной продолжительностью и элементом для отображения.
    startTimer(window.timerDuration, display);
}

// Обработчик события DOMContentLoaded для запуска таймера после загрузки содержимого страницы.
document.addEventListener('DOMContentLoaded', setupTimer);
