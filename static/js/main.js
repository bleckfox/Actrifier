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
            var form = $('form');
            //$.post('/card');
            form.attr('action', '/card');
            form.attr('method', 'post');

        });
    }
    function lucky () {
        var btn = $(".lucky_btn");
        btn.click( function (event) {
            $.post('/card');
        })
    }
    search();
    lucky();
    //$('input').keyup(get_json_info);
});