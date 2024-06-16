// Функция для получения уникального ключа для текущей страницы с табами.
function getPageKey() {
    return 'activeTab_' + window.location.pathname;
}

function openTab(evt, tabName) {
    if (!tabName) {
        console.error('tabName is undefined');
        return;
    }

    console.log('openTab вызвана с tabName:', tabName); // Логирование

    var clickedTab = document.getElementById(tabName);
    var clickedTabLink = evt.currentTarget;

    // Снятие фокуса с текущей ссылки.
    clickedTabLink.blur();

    // Получаем текущее состояние табов для текущей страницы.
    var storedActiveTab = sessionStorage.getItem(getPageKey());

    // Проверяем, активен ли таб, на который кликнули
    if (clickedTab.classList.contains('active')) {
        // Если активен, закрываем его
        clickedTab.classList.remove('active');
        clickedTabLink.classList.remove('active');
        sessionStorage.removeItem(getPageKey()); // Удаляем активный таб из sessionStorage
        console.log('Таб закрыт и удален из sessionStorage для страницы', window.location.pathname, ':', tabName); // Логирование
    } else {
        // Проверяем, активен ли уже другой таб
        if (storedActiveTab && storedActiveTab !== tabName) {
            // Получаем элемент активного таба
            var storedTab = document.getElementById(storedActiveTab);
            // Проверяем, активен ли уже другой таб
            if (storedTab && storedTab.classList.contains('active')) {
                // Если активен, закрываем его
                storedTab.classList.remove('active');
                var storedTabLink = document.querySelector('.tab-menu-link[href="#' + storedActiveTab + '"]');
                if (storedTabLink) {
                    storedTabLink.classList.remove('active');
                }
            }
        }

        // Отображаем выбранный таб и добавляем ему класс "active".
        clickedTab.classList.add("active");
        clickedTabLink.classList.add("active");
        console.log('Добавлен класс active для таба и ссылки:', tabName); // Логирование

        // Сохраняем активный таб в sessionStorage для текущей страницы с табами.
        sessionStorage.setItem(getPageKey(), tabName);
        console.log('Сохранен активный таб в sessionStorage для страницы', window.location.pathname, ':', tabName); // Логирование
    }
}

function loadActiveTab() {
    var storedActiveTab = sessionStorage.getItem(getPageKey());
    console.log('loadActiveTab вызвана. Активный таб из sessionStorage:', storedActiveTab); // Логирование

    if (storedActiveTab) {
        var activeTab = document.getElementById(storedActiveTab);
        var activeTabLink = document.querySelector('.tab-menu-link[href="#' + storedActiveTab + '"]');
        if (activeTab && activeTabLink && !activeTab.classList.contains('active')) {
            // Только открывать таб, если он не активен
            activeTab.classList.add("active");
            activeTabLink.classList.add("active");
            console.log('Добавлен класс active для таба и ссылки:', storedActiveTab); // Логирование
        }
    }
}

// Добавляем обработчик события для загрузки активного таба при загрузке страницы.
document.addEventListener('DOMContentLoaded', loadActiveTab);

// Здесь вы также можете добавить другие обработчики событий, если это необходимо.
