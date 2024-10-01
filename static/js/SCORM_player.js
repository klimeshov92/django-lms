// Функция для загрузки SCORM контента.
function loadScormContent(course_id) {
    console.log("Загрузка SCORM контента для пакета:", course_id);

    var contentUrl;
    if (type === 'ispring') {
        contentUrl = `/media/scorm_packages/${course_id}/res/index.html`;
    } else if (type === 'articulate') {
        contentUrl = `/media/scorm_packages/${course_id}/index_lms.html`;
    } else if (type === 'scroll') {
        contentUrl = `/media/scorm_packages/${course_id}/index.html`;
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

// Функция для скрытия меню.
function hideMenu() {
    const submenu = document.querySelector('.submenu');
    submenu.classList.add('hidden');
}

// Запрос на полноэкранный режим.
function requestFullscreen(element) {
    console.log("Запрос на полноэкранный режим для элемента:", element);

    // Стандартные методы для других браузеров.
    if (element.requestFullscreen) {
        element.requestFullscreen().then(() => {
            console.log("Полноэкранный режим активирован");
        }).catch((err) => {
            console.error("Ошибка при активации полноэкранного режима:", err);
            hideMenu(); // Скрываем меню, если активация не удалась.
        });
    } else if (element.mozRequestFullScreen) { // Firefox
        element.mozRequestFullScreen().then(() => {
            console.log("Полноэкранный режим активирован (Firefox)");
        }).catch((err) => {
            console.error("Ошибка при активации полноэкранного режима (Firefox):", err);
            hideMenu(); // Скрываем меню, если активация не удалась.
        });
    } else if (element.webkitRequestFullscreen) { // Chrome, Safari, Opera
        element.webkitRequestFullscreen().then(() => {
            console.log("Полноэкранный режим активирован (Webkit)");
        }).catch((err) => {
            console.error("Ошибка при активации полноэкранного режима (Webkit):", err);
            hideMenu(); // Скрываем меню, если активация не удалась.
        });
    } else if (element.msRequestFullscreen) { // IE/Edge
        element.msRequestFullscreen().then(() => {
            console.log("Полноэкранный режим активирован (IE/Edge)");
        }).catch((err) => {
            console.error("Ошибка при активации полноэкранного режима (IE/Edge):", err);
            hideMenu(); // Скрываем меню, если активация не удалась.
        });
    } else {
        console.error("Полноэкранный режим не поддерживается этим браузером");
        hideMenu(); // Скрываем меню, если активация не удалась.
    }
}

// Обработчик нажатия кнопки полноэкранного режима.
document.getElementById('fullscreen-btn').addEventListener('click', function(event) {
    event.preventDefault();
    var iframe = document.getElementById('scorm-player-iframe');
    requestFullscreen(iframe);
});

// Загрузка SCORM контента при открытии окна.
window.addEventListener('load', function() {
    console.log("Окно загружено, начинаем загрузку SCORM контента");
    loadScormContent(course_id);
    console.log("SCORM контент загружен");
});

// Обработчик события изменения состояния полноэкранного режима.
document.addEventListener('fullscreenchange', function() {
    var fullscreenElement = document.fullscreenElement || document.mozFullScreenElement || document.webkitFullscreenElement || document.msFullscreenElement;
    const submenu = document.querySelector('.submenu');
    if (fullscreenElement) {
        console.log("Полноэкранный режим активирован");
        hideMenu(); // Скрываем меню при активации полноэкранного режима.
    } else {
        console.log("Полноэкранный режим не активен");
        submenu.classList.remove('hidden'); // Показываем меню, если полноэкранный режим отключен.
    }
});
