$(document).ready(function () {
    function search () {
        var btn = $(".search_btn");
        btn.click( function (event) {
            $.post('/card');
        });
    }
    function lucky () {
        var btn = $(".lucky_btn");
        btn.click( function (event) {
            $.post('/lucky');
        })
    }
    search();
});
//lucky_btn