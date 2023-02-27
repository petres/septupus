$(document).ready(() => {
    // sending a connect request to the server.
    socket = io.connect();

    function sentUpdate(el) {
        d = {
            module: el.closest('form').data('module'),
            name:   el.attr('name'),
            value:  el.val()
        }
        $('form[data-module="' + d.module + '"] .form-group[data-name="' + d.name + '"] span.value').text(d.value)
        socket.emit('generic.update', d);
        console.log(d)
    }

    $('input.sync').on('input', function(event) {
        sentUpdate($(this))
    });

    $('input:radio.sync, select.sync').on('change', function(event) {
        sentUpdate($(this))
    });

    // $('select.sync').on('change', function(event) {
    //     sentUpdate($(this))
    // });
    // socket.on('after connect', function(msg) {
    //    console.log('After connect', msg);
    // });
    // socket.on('update value', function(msg) {
    //      //console.log('Slider value updated');
    //      $('#slider1').val(msg.data);
    // })
});


$(() => {
    var hash = window.location.hash;
    hash && $('ul.nav a[href="' + hash + '"]').tab('show');

    $('.nav-tabs a').click(function (e) {
        $(this).tab('show');
        var scrollmem = $('body').scrollTop() || $('html').scrollTop();
        window.location.hash = this.hash;
        $('html,body').scrollTop(scrollmem);
    });
});
