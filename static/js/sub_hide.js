// Скрываем пустые сабменю.
function hideEmptySubmenus() {
    var submenusContainers = document.querySelectorAll(".submenu-container");
    submenusContainers.forEach(function(container) {
        var submenu = container.querySelector(".submenu");
        if (submenu && submenu.children.length === 0) {
            container.style.display = 'none'; // Скрываем контейнер, если сабменю пустое.
        }
    });
}

// Запускаем функцию после загрузки страницы
document.addEventListener("DOMContentLoaded", function() {
    hideEmptySubmenus();
});

