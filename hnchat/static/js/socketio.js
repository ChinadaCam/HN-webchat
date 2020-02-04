
    var socket = io.connect( 'http://' + document.domain + ':' + location.port )
      // broadcast a message
      socket.on( 'connect', function() {
        socket.emit( 'my event', {
          data: 'User Connected'
        } )
        var form = $( 'form' ).on( 'submit', function( e ) {
          e.preventDefault()
          let user_name = $( 'input.username' ).val()
          let user_input = $( 'input.message' ).val()
          socket.emit( 'my event', {
            user_name : user_name,
            message : user_input
          } )
          // empty the input field
          $( 'input.message' ).val( '' ).focus()
        } )
      } )

      // capture message
      socket.on( 'my response', function( msg ) {
        console.log( msg )
        if( typeof msg.message !== 'undefined' ) {
          $( 'div.msg_card_body' ).append("<div class=' d-flex justify-content-start mb-4'><div class='img_cont_msg'><img src='static/img/profile.png' class='rounded-circle user_img_msg'></div><div class='msg_cotainer'><span class='msg_user'>"+msg.user_name+"</span><br>"+msg.message+"</div></div>")
          
        }
      } )