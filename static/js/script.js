 const number_lines = 1000;

 // Удалить комутационный центр
 function delete_centers(data) {
    try{
        $.ajax({
            url: "/api/v1/switching-center/delete/"+data+"",
            type: "GET",
            data: {},
            success: function(response) {
                if(response == 'yes'){
                    $('tr#centers-'+data+'').css({'display':'none'});
                    UIkit.notification("<span uk-icon='icon: trash'></span> Видалено успішно", {status: 'success', pos: 'top-right'});
                } else {
                    UIkit.notification("<span uk-icon='icon: close'></span> Помилка", {status: 'warning', pos: 'top-right'});
                }
            }
        });
    } catch(e){
        alert(e);
    }
}

//Функция вывода комутационных центров
function listcenters(page_number) {
    var search = $('input.search_input_filters').val();
    
    if(page_number == null || page_number == '' || page_number == ' '){
        page_number = '1';
    } else {}

    $.ajax({
        url: "/api/v1/switching-centers",
        type: "GET",
        data: { search:search, number_lines: number_lines, page_number:page_number},
        beforeSend: function() {
            // Покажите индикатор загрузки или текст "Загрузка..."
            $("#list-centers").html("<tr><td colspan='100' class='uk-text-center'>Loading...</td></tr>");
        },
        success: function(response) {
            // Assuming response contains an array of centers
            var centers = response;
            
            // Format the centers data as HTML
            var htmlContent = '';
            for (var i = 0; i < centers.length; i++) {
                htmlContent += '<tr id="centers-' + centers[i].id + '">' +
                    '<td class="uk-text-center">' + centers[i].id + '</td>' +
                    '<td>' +
                        '<a class="ViewCenter dashed" id-center="' + centers[i].id + '" href="#modal-center" uk-toggle>'+
                        '' + centers[i].name + '' +
                        '</a>'+
                    '</td>' +
                    '<td>' + centers[i].room + '</td>' +
                    '<td class="uk-text-center">' +
                        '<a id="ViewCenter" id-center="' + centers[i].id + '" href="#modal-center" uk-toggle class="uk-margin-right ViewCenter" uk-tooltip="Редагувати">' +
                            '<span uk-icon="pencil"></span>'+
                        '</a>'+
                        '<a id="" uk-tooltip="Видалити" onclick="if (confirm(\'\Справді видалити?\'\)) {delete_centers('+ centers[i].id +')}">'+
                            '<span uk-icon="trash"></span>'+
                        '</a>' +
                        '</td>' +
                    '</tr>';
            }
            htmlContent += '';

            // Set the HTML content of the #list div
            $("#list-centers").html(htmlContent);
        }
    });
}

function dateformattext(date){
    var rawDateStart = new Date(date);
    var options = {
        weekday: 'short',
        day: 'numeric',
        month: 'short',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: false,
        timeZone: 'UTC'
    };
    if(date){
        return formattedDateStart = rawDateStart.toLocaleString('uk-UA', options);
    } else {
        return ''
    }
    
}

// Функция вывода журнала заявок
function listjournal() {
    if(active == 'None'){
        active = '';
    }
    $.ajax({
        url: "/api/v1/journal-order",
        type: "GET",
        data: { active: active },
        beforeSend: function() {
            // Покажите индикатор загрузки или текст "Загрузка..."
            $("#list-journal").html("<tr><td colspan='100' class='uk-text-center'>Loading...</td></tr>");
        },
        success: function(response) {
            var journal = response;
            var htmlContent = '';
            for (var i = 0; i < journal.length; i++) {

                if(active == '-1'){
                htmlContent += '<tr id="centers-' + journal[i].id + '">' +
                        '<td class="uk-text-center">' + journal[i].id + '</td>' +
                        '<td class="uk-text-">' + dateformattext(journal[i].datestart) + '</td>' +
                        '<td class="uk-text-">' + journal[i].name_center + '</td>' +
                        '<td class="uk-text-">' + journal[i].pib + '</td>' +
                        '<td class="uk-text-">' + dateformattext(journal[i].dateend) + '</td>' +
                        '<td class="uk-text-center">' + 
                        '</td>' +
                    '</tr>';
                } else {
                    htmlContent += '<tr id="centers-' + journal[i].id + '">' +
                    '<td class="uk-text-center">' + journal[i].id + '</td>' +
                    '<td class="uk-text-">' + dateformattext(journal[i].datestart) + '</td>' +
                    '<td class="uk-text-">' + journal[i].name_center + '</td>' +
                    '<td class="uk-text-">' + journal[i].pib + '</td>' +
                    '<td class="uk-text-"> <span class="uk-badge uk-badge-danger">Не повернено</span> </td>' +
                    '<td class="uk-text-center">' + 
                        '<a id="ViewJournal" id-journal="' + journal[i].id + '" href="#modal-edit-journal" uk-toggle class="" uk-tooltip="Закрити заявку">'+
                            '<span uk-icon="icon: pencil"></span>' +
                        '</a>' +
                    '</td>' +
                '</tr>';
                }
            }
            htmlContent += '';
            $("#list-journal").html(htmlContent);
        }
    });
}
 
// Просмотр информации о комутационном центре (информация в модальное окно)
$(document).on('click', 'a.ViewCenter', function(){
    var id = $(this).attr('id-center');
    try{
        $.ajax({
            url: "/api/v1/switching-centers/view/"+id+"",
            type: "GET",
            data: {},
            success: function(response) {
                if(response){
                    $("h2#ModalH1Name").html(response[0]['name']);
                    $("input#ModalInputId").val(response[0]['id']);
                    $("input#ModalInputName").val(response[0]['name']);
                    $("input#ModalInputRoom").val(response[0]['room']);
                } else {

                }
            }
        });
    } catch(e){
        alert(e);
    }
});

// Редагувати комутаційний центр
$(document).on('click', 'button#SaveDataModal', function(){
    var id = $('input#ModalInputId').val();
    var name = $('input#ModalInputName').val();
    var room = $('input#ModalInputRoom').val();
    if(name === ''){
        $('input#ModalInputName').css({'border':'1px solid red'});
        UIkit.notification("<span uk-icon='icon: warning'></span> Введіть назву", {status: 'warning', pos: 'top-right'});
    } else if(room === ''){
        $('input#ModalInputRoom').css({'border':'1px solid red'});
        UIkit.notification("<span uk-icon='icon: warning'></span> Введіть приміщення ", {status: 'warning', pos: 'top-right'});
    } else {
        try{
            $.ajax({
                url: "/api/v1/switching-centers/update",
                type: "GET",
                data: {
                    id:id,  
                    name:name, 
                    room:room 
                },
                success: function(response) {
                    if(response){
                        $('input#ModalInputName, input#ModalInputRoom').val('').html('');
                        UIkit.modal('#modal-center').hide();
                        listcenters();
                        UIkit.notification("<span uk-icon='icon: check'></span> Дані збережено", {status: 'success', pos: 'top-right'});
                    } else {
                        UIkit.notification("<span uk-icon='icon: close'></span> Помилка", {status: 'warning', pos: 'top-right'});
                    }
                }
            });
        } catch(e){
            //alert(e);
        }
    }
});

//Додати комутаційний центр
$(document).on('keyup', 'input#AddModalInputName', function(){
    $('input#AddModalInputName').css({'border':''});
});
$(document).on('keyup', 'input#AddModalInputRoom', function(){
    $('input#AddModalInputRoom').css({'border':''});
});

$(document).on('click', 'button#AddDataModal', function(){
    var name = $('input#AddModalInputName').val();
    var room = $('input#AddModalInputRoom').val();
    if(name === ''){
        $('input#AddModalInputName').css({'border':'1px solid red'});
        UIkit.notification("<span uk-icon='icon: warning'></span> Введіть назву", {status: 'warning', pos: 'top-right'});
    } else if(room === ''){
        $('input#AddModalInputRoom').css({'border':'1px solid red'});
        UIkit.notification("<span uk-icon='icon: warning'></span> Введіть приміщення ", {status: 'warning', pos: 'top-right'});
    } else {
        try{
            $.ajax({
                url: "/api/v1/switching-centers/add",
                type: "GET",
                data: {
                    name:name, 
                    room:room 
                },
                success: function(response) {
                    if(response){
                        //alert(response);
                        $('input#AddModalInputName, input#AddModalInputRoom').val('').html('');
                        UIkit.modal('#modal-add-centers').hide();
                        listcenters();
                        UIkit.notification("<span uk-icon='icon: check'></span> Додано успішно", {status: 'success', pos: 'top-right'});
                    } else {
                        //alert('error - add');
                        UIkit.notification("<span uk-icon='icon: close'></span> Помилка", {status: 'warning', pos: 'top-right'});
                    }
                }
            });
        } catch(e){
            //alert(e);
        }
    }
});

// Відкриття модального вікна для додавання заявки
$(document).on('click', 'a#OpenModalZayavka', function(){
    // Список Комутаційних центрів
    var page_number = ''
    if(page_number == null || page_number == '' || page_number == ' '){
        page_number = '1';
    } else {}
    $.ajax({
        url: "/api/v1/switching-centers",
        type: "GET",
        data: { },
        beforeSend: function() {
            // Покажите индикатор загрузки или текст "Загрузка..."
            $("#JuornalListCenters").html("<option>Loading...</option>");
        },
        success: function(response) {
            var centers = response;
            var htmlContent = '';
            for (var i = 0; i < centers.length; i++) {
                htmlContent += '<option value="' + centers[i].id + '">' + centers[i].name + '</option>';
            }
            htmlContent += '';
            $("#JuornalListCenters").html(htmlContent);
        }
    });

    // Список персоналу кому дозволено брати ключі
    $.ajax({
        url: "/api/v1/staff-allowed-keys",
        type: "GET",
        data: { },
        beforeSend: function() {
            // Покажите индикатор загрузки или текст "Загрузка..."
            $("#JuornalListPersonal").html("Loading...");
        },
        success: function(response) {
            var centers = response;
            var htmlContent = '';
            for (var i = 0; i < centers.length; i++) {
                htmlContent += '<option value="' + centers[i].tab_no + '">' + centers[i].pib + '</option>';
            }
            htmlContent += '';
            $("#JuornalListPersonal").html(htmlContent);
        }
    });

    //Час отримання - по замовчуванням
    const dateControl = document.querySelector('input[type="datetime-local"]');
    const formattedDate = new Date();
    const padZero = (number) => (number < 10 ? '0' + number : number);
    const formattedDateString = `${formattedDate.getFullYear()}-${padZero(formattedDate.getMonth() + 1)}-${padZero(formattedDate.getDate())}T${padZero(formattedDate.getHours())}:${padZero(formattedDate.getMinutes())}`;
    dateControl.value = formattedDateString;
});

// Додавання заявки
$(document).on('click', 'button#AddDataJournal', function(){
    var centers = $("select#JuornalAddCenters option:selected").val();
    var personal = $("select#JuornalAddPersonal option:selected").val();
    var date_start = $("input#JuornalAddDatetime").val();
    
    if(centers == ''){
        $('select#JuornalAddCenters').css({'border':'1px solid red'});
        UIkit.notification("<span uk-icon='icon: warning'></span> Виберіть комутаційний центр ", {status: 'warning', pos: 'top-right'});
    } else if(personal == ''){
        $('select#JuornalAddPersonal').css({'border':'1px solid red'});
        UIkit.notification("<span uk-icon='icon: warning'></span> Виберіть особу яка отримала ключ ", {status: 'warning', pos: 'top-right'});
    } else if(date_start == ''){
        $('input#JuornalAddDatetime').css({'border':'1px solid red'});
        UIkit.notification("<span uk-icon='icon: warning'></span> Виберіть дату ", {status: 'warning', pos: 'top-right'});
    } else {
        $.ajax({
            url: "/api/v1/journal-order/add",
            type: "GET",
            data: {centers: centers, date_start: date_start, personal_received: personal},
            success: function(response) {
                UIkit.modal('#modal-zayavka').hide();
                listjournal();
                UIkit.notification("<span uk-icon='icon: check'></span> Заявку додано", {status: 'success', pos: 'top-right'});
            }
        });
    }

    // Исходная строка даты
    var dateString = date_start;
    // Создаем объект Date из исходной строки
    var dateObject = new Date(dateString);
    // Получаем компоненты даты и времени
    var day = dateObject.getDate();
    var month = dateObject.getMonth() + 1; // Месяцы в JavaScript начинаются с 0
    var year = dateObject.getFullYear();
    var hours = dateObject.getHours();
    var minutes = dateObject.getMinutes();

    // Форматируем компоненты даты и времени
    var formattedDate = (day < 10 ? "0" : "") + day + "-" + (month < 10 ? "0" : "") + month + "-" + year;
    var formattedTime = (hours < 10 ? "0" : "") + hours + ":" + (minutes < 10 ? "0" : "") + minutes;

    // Получаем окончательную строку в нужном формате
    var result = formattedDate + " " + formattedTime;

}); 

//Відкрити картку заявки для закриття
$(document).on('click', 'a#ViewJournal', function(){
    var id = $(this).attr('id-journal');
    $("span#JournalModalH1Name").html(id);
    $("input#JournalModalInputId").val(id);

    //Час повернення - по замовчуванням
    const dateControl = document.querySelector('input#JournalModalInputDateEnd');
    const formattedDate = new Date();
    const padZero = (number) => (number < 10 ? '0' + number : number);
    const formattedDateString = `${formattedDate.getFullYear()}-${padZero(formattedDate.getMonth() + 1)}-${padZero(formattedDate.getDate())}T${padZero(formattedDate.getHours())}:${padZero(formattedDate.getMinutes())}`;
    dateControl.value = formattedDateString;
});

//Закрити заявку
$(document).on('click', 'button#JournalEditModal', function(){
    var id = $("input#JournalModalInputId").val();
    var date_end = $("input#JournalModalInputDateEnd").val().trim();

    if(id == ''){
        UIkit.notification("<span uk-icon='icon: warning'></span> Помилка ID ", {status: 'warning', pos: 'top-right'});
    } else if(date_end == ''){
        $('input#JournalModalInputDateEnd').css({'border':'1px solid red'});
        UIkit.notification("<span uk-icon='icon: warning'></span> Виберіть Час повернення", {status: 'warning', pos: 'top-right'});
    } else {
        $.ajax({
            url: "/api/v1/journal-order/edit",
            type: "GET",
            data: { id:id, date_end:date_end },
            success: function(response) {
                console.log(response);
                UIkit.modal('#modal-edit-journal').hide();
                listjournal();
                UIkit.notification("<span uk-icon='icon: check'></span> Заявку закрито", {status: 'success', pos: 'top-right'});
            }
        });
    }
}); 

//Запуск скрипта при открытии страницы
$(document).ready(function() {
    if (document.getElementById('list-centers')) {listcenters();} else {}
    if (document.getElementById('list-journal')) {listjournal();} else {}
});
