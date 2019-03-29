
$(document).ready(function(){
    //connect to the socket server.
    var socket = io.connect('http://' + document.domain + ':' + location.port + '/test');
    
    //receive details from server
    socket.on('newnumber', function(msg){
        $('#loc').html(msg.number[0]);
        $('#gas').html(msg.number[1]);
	$('#hum').html(msg.number[1]);
	$('#temp').html(msg.number[1]);
        
    });

});