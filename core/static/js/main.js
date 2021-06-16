$(document).ready(function () {

    function get_json_info () {
        var field = $('input');
        var value = field.val();
        if (value !== '') {
            $.post( "/actor", {
                javascript_data: value
            });
            console.log(value);
        }
    }
    function search () {

        var btn = $(".search_btn");
        btn.click( function (event) {
            console.log('search');
            var form = $('form');
            var value = $('input').val();
            if (value !== ''){
                form.attr('action', '/card');
                form.attr('method', 'post');
            }
            else {
                alert('Введите имя актера или нажмите "I\'m Feeling Lucky"')
            }
        });
    }
    function lucky () {

        var btn = $(".lucky_btn");
        btn.click( function (event) {
            console.log('lucky');
            var form = $('form');
            //$.post('/card');
            form.attr('action', '/card');
            form.attr('method', 'post');
        })
    }
    search();
    lucky();
    //$('input').keyup(get_json_info);
});