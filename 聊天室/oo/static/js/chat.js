$(document).ready(function() {
    // Connect to the Socket.IO server
    // We assume the server is the same as the one serving the page for now, 
    // or we could use the server_url from session if passed to template.
    // For this implementation, auto-discovery is safest for B/S.
    var socket = io();

    // Join event
    socket.on('connect', function() {
        socket.emit('join', {username: currentUser});
    });

    // Receive status updates (join/leave)
    socket.on('status', function(data) {
        $('#chat-messages').append('<div class="system-message">' + data.msg + '</div>');
        scrollToBottom();
    });

    // Receive messages
    socket.on('message', function(data) {
        var msgClass = (data.username === currentUser) ? 'my-message' : 'other-message';
        var html = '<div class="message ' + msgClass + '">' +
                   '<div class="message-info">' + data.username + '</div>' +
                   '<div class="message-content">' + data.msg + '</div>' +
                   '</div>';
        $('#chat-messages').append(html);
        scrollToBottom();
    });

    // Send message
    $('#send-btn').click(function() {
        sendMessage();
    });

    $('#msg-input').keypress(function(e) {
        if(e.which == 13) { // Enter key
            sendMessage();
        }
    });

    function sendMessage() {
        var msg = $('#msg-input').val();
        if(msg.trim() !== "") {
            socket.emit('message', {username: currentUser, msg: msg});
            $('#msg-input').val('');
        }
    }

    function scrollToBottom() {
        var chatMsgs = document.getElementById('chat-messages');
        chatMsgs.scrollTop = chatMsgs.scrollHeight;
    }
});

// Helper functions for buttons (exposed to global scope)
function insertText(text) {
    var input = document.getElementById('msg-input');
    input.value += text;
    input.focus();
}

function insertEmoji(emoji) {
    var input = document.getElementById('msg-input');
    input.value += emoji;
    input.focus();
}

function showHistory() {
    alert("History feature is under construction.");
}
