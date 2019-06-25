$(document).ready(function(){
    // sending a connect request to the server.
    var socket = io.connect('http://localhost:5000');

    function sentUpdate(el) {
        d = {
            module: el.closest('form').data('module'),
            name:   el.attr('name'),
            value:  el.val()
        }
        socket.emit('generic-update', d);
        //console.log(d)
    }

    $('input.sync').on('input', function(event) {
        sentUpdate($(this))
    });

    $('input:radio.sync').on('change', function(event) {
        sentUpdate($(this))
    });
    // socket.on('after connect', function(msg) {
    //    console.log('After connect', msg);
    // });
    socket.on('update value', function(msg) {
         //console.log('Slider value updated');
         $('#slider1').val(msg.data);
    })
});
