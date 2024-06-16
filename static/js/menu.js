document.addEventListener('DOMContentLoaded', function() {

    // Получаем элемент кнопки гамбургер-меню по классу.
    const hamburgerMenu = document.querySelector('.hamburger-menu');

    // Получаем элемент меню по классу.
    const menu = document.querySelector('.menu');

    // Вешаем обработчик события клика на кнопку гамбургер-меню.
    hamburgerMenu.addEventListener('click', function() {
        // Переключаем класс 'active' для меню при клике (показываем или скрываем меню).
        menu.classList.toggle('active');
    });
});
