// Функция для загрузки SCORM контента.
function loadScormContent(scorm_package_id) {
    console.log("Загрузка SCORM контента для пакета:", scorm_package_id);

    var contentUrl;
    if (type === 'ispring') {
        contentUrl = `/media/scorm_packages/${scorm_package_id}/res/index.html`;
    } else if (type === 'articulate') {
        contentUrl = `/media/scorm_packages/${scorm_package_id}/index_lms.html`;
    } else if (type === 'scroll') {
        contentUrl = `/media/scorm_packages/${scorm_package_id}/index.html`;
    } else {
        console.error("Неизвестный тип SCORM пакета:", type);
        return;
    }
    console.log("contentUrl:", contentUrl);

    var scormPlayerIframe = document.getElementById('scorm-player-iframe');
    scormPlayerIframe.src = contentUrl;

    scormPlayerIframe.onload = function() {
        console.log("Iframe загружен успешно");
    };

    scormPlayerIframe.onerror = function() {
        console.error("Произошла ошибка при загрузке Iframe.");
    };

    scormPlayerIframe.onabort = function() {
        console.error("Загрузка Iframe была прервана.");
    };
}

// Запрос на полноэкранный режим.
function requestFullscreen(element) {
    console.log("Запрос на полноэкранный режим для элемента:", element);
    if (element.requestFullscreen) {
        element.requestFullscreen().then(() => {
            console.log("Полноэкранный режим активирован");
        }).catch((err) => {
            console.error("Ошибка при активации полноэкранного режима:", err);
        });
    } else if (element.mozRequestFullScreen) { // Firefox
        element.mozRequestFullScreen().then(() => {
            console.log("Полноэкранный режим активирован (Firefox)");
        }).catch((err) => {
            console.error("Ошибка при активации полноэкранного режима (Firefox):", err);
        });
    } else if (element.webkitRequestFullscreen) { // Chrome, Safari and Opera
        element.webkitRequestFullscreen().then(() => {
            console.log("Полноэкранный режим активирован (Webkit)");
        }).catch((err) => {
            console.error("Ошибка при активации полноэкранного режима (Webkit):", err);
        });
    } else if (element.msRequestFullscreen) { // IE/Edge
        element.msRequestFullscreen().then(() => {
            console.log("Полноэкранный режим активирован (IE/Edge)");
        }).catch((err) => {
            console.error("Ошибка при активации полноэкранного режима (IE/Edge):", err);
        });
    } else {
        console.error("Полноэкранный режим не поддерживается этим браузером");
    }
}

// Загрузка SCORM контента при открытии окна.
window.addEventListener('load', function() {
    console.log("Окно загружено, начинаем загрузку SCORM контента");
    loadScormContent(scorm_package_id);
    console.log("SCORM контент загружен");
});

// Переход в полноэкранный режим при нажатии кнопки.
document.getElementById('fullscreen-btn').addEventListener('click', function(event) {
    event.preventDefault();
    console.log("Попытка перехода в полноэкранный режим по нажатию кнопки");
    requestFullscreen(document.documentElement);
    console.log("Скрытие/показ меню выполнено");
});

// Обработчик события изменения состояния полноэкранного режима.
document.addEventListener('fullscreenchange', function(event) {
    // Проверяем, активен ли в данный момент полноэкранный режим.
    var fullscreenElement = document.fullscreenElement || document.mozFullScreenElement || document.webkitFullscreenElement || document.msFullscreenElement;
    if (fullscreenElement) {
        console.log("Полноэкранный режим активирован");
        // Изменяем видимость меню.
        const submenu = document.querySelector('.submenu');
        submenu.classList.add('hidden'); // Скрываем меню.
    } else {
        console.log("Полноэкранный режим не активен");
        // Изменяем видимость меню.
        const submenu = document.querySelector('.submenu');
        submenu.classList.remove('hidden'); // Показываем меню.
    }
});


