function SCORM_API() {
    var course_id = window.course_id;
    var user_id = window.user_id;

    this.Initialize = function() {
        console.log("Initialize вызван для пользователя:", user_id, "и пакета:", course_id);
        const data = {
            user_id: user_id,
            course_id: course_id
        };

        const xhr = new XMLHttpRequest();
        xhr.open('POST', '/courses/api/scorm_initialize/', false); // Синхронный запрос
        xhr.setRequestHeader('Content-Type', 'application/json');
        xhr.send(JSON.stringify(data));

        if (xhr.status === 200) {
            try {
                const response = JSON.parse(xhr.responseText);
                return response.status === 'initialize_success' ? "true" : "false";
            } catch (error) {
                console.error('Ошибка в Initialize:', error);
                return "false";
            }
        } else {
            console.error('Ошибка в Initialize:', xhr.status);
            return "false";
        }
    };


    this.Terminate = function() {
        console.log("Terminate вызван");
        const data = {}; // Пустой объект данных для POST-запроса

        const xhr = new XMLHttpRequest();
        xhr.open('POST', '/courses/api/scorm_finish/', false); // Синхронный запрос
        xhr.setRequestHeader('Content-Type', 'application/json');
        xhr.send(JSON.stringify(data)); // Отправляем пустые данные

        function exitFullscreen() {
            if (document.exitFullscreen) {
                document.exitFullscreen();
            } else if (document.mozCancelFullScreen) {
                document.mozCancelFullScreen();
            } else if (document.webkitExitFullscreen) {
                document.webkitExitFullscreen();
            } else if (document.msExitFullscreen) {
                document.msExitFullscreen();
            }
        }

        if (document.fullscreenElement || document.webkitFullscreenElement || document.mozFullScreenElement || document.msFullscreenElement) {
            exitFullscreen();
        } else {
            const submenu = document.querySelector('.submenu');
            if (submenu && submenu.classList.contains('hidden')) {
                submenu.classList.remove('hidden');
            }
        }

        if (xhr.status === 200) {
            try {
                const response = JSON.parse(xhr.responseText);
                return response.status === 'finish_success' ? "true" : "false";
            } catch (error) {
                console.error('Ошибка в Terminate:', error);
                return "false";
            }
        } else {
            console.error('Ошибка в Terminate:', xhr.status);
            return "false";
        }
    };


    this.GetValue = function(element) {
        console.log("GetValue вызван с элементом:", element);
        const url = `/courses/api/get_value/?element=${encodeURIComponent(element)}`;
        const xhr = new XMLHttpRequest();
        xhr.open('GET', url, false); // Устанавливаем третий параметр как false для синхронного запроса
        xhr.send();

        if (xhr.status === 200) {
            try {
                const response = JSON.parse(xhr.responseText);
                return response[element] || "";
            } catch (error) {
                console.error('Ошибка в GetValue:', error);
                return "";
            }
        } else {
            console.error('Ошибка в GetValue:', xhr.status);
            return "";
        }
    };


    this.SetValue = function(element, value) {
        console.log("SetValue вызван с элементом:", element, "и значением:", value);
        const data = {[element]: value};

        const xhr = new XMLHttpRequest();
        xhr.open('POST', '/courses/api/set_value/', false); // Синхронный запрос
        xhr.setRequestHeader('Content-Type', 'application/json');
        xhr.send(JSON.stringify(data));

        if (xhr.status === 200) {
            try {
                const response = JSON.parse(xhr.responseText);
                return response.status === 'set_value_success' ? "true" : "false";
            } catch (error) {
                console.error('Ошибка в SetValue:', error);
                return "false";
            }
        } else {
            console.error('Ошибка в SetValue:', xhr.status);
            return "false";
        }
    };

    this.Commit = function() {
        console.log("Commit вызван");

        const data = {}; // Нет необходимости передавать данные

        const xhr = new XMLHttpRequest();
        xhr.open('POST', '/courses/api/scorm_commit/', false); // Синхронный запрос
        xhr.setRequestHeader('Content-Type', 'application/json');
        xhr.send(JSON.stringify(data)); // Отправка данных

        if (xhr.status === 200) {
            try {
                const response = JSON.parse(xhr.responseText);
                const isCommitSuccess = response.status === 'commit_success';
                console.log("Статус commit_success:", isCommitSuccess);
                return isCommitSuccess ? "true" : "false";
            } catch (error) {
                console.error('Ошибка в Commit:', error);
                return "false";
            }
        } else {
            console.error('Ошибка в Commit:', xhr.status);
            return "false";
        }
    };

    this.GetLastError = function() {
        console.log("GetLastError вызван");

        const xhr = new XMLHttpRequest();
        xhr.open('GET', '/courses/api/get_last_error/', false); // Синхронный запрос
        xhr.send();

        if (xhr.status === 200) {
            try {
                const response = JSON.parse(xhr.responseText);
                return response.error_code || "0";
            } catch (error) {
                console.error('Ошибка в GetLastError:', error);
                return "0";
            }
        } else {
            console.error('Ошибка в GetLastError:', xhr.status);
            return "0";
        }
    };


    this.GetErrorString = function(errorCode) {
        console.log("GetErrorString вызван с кодом ошибки:", errorCode);

        const xhr = new XMLHttpRequest();
        xhr.open('GET', '/courses/api/get_error_string/?error_code=' + encodeURIComponent(errorCode), false); // Синхронный запрос
        xhr.send();

        if (xhr.status === 200) {
            try {
                const response = JSON.parse(xhr.responseText);
                return response.error_string || "No error";
            } catch (error) {
                console.error('Ошибка в GetErrorString:', error);
                return "No error";
            }
        } else {
            console.error('Ошибка в GetErrorString:', xhr.status);
            return "No error";
        }
    };


    this.GetDiagnostic = function(errorCode) {
        console.log("GetDiagnostic вызван с кодом ошибки:", errorCode);

        const xhr = new XMLHttpRequest();
        xhr.open('GET', '/courses/api/get_diagnostic/?error_code=' + encodeURIComponent(errorCode), false); // Синхронный запрос
        xhr.send();

        if (xhr.status === 200) {
            try {
                const response = JSON.parse(xhr.responseText);
                return response.diagnostic_info || "No diagnostic information";
            } catch (error) {
                console.error('Ошибка в GetDiagnostic:', error);
                return "No diagnostic information";
            }
        } else {
            console.error('Ошибка в GetDiagnostic:', xhr.status);
            return "No diagnostic information";
        }
    };

}
// Создание экземпляра API и присвоение его к window.API_1484_11
window.API_1484_11 = new SCORM_API();
