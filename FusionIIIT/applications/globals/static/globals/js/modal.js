function modalCancel(){
    $(document).ready(function() {
        $('#cancel')
          .modal('setting', 'closable', false)
          .modal('show')
        ;
    });
}

function modalCheckIn(){
    $(document).ready(function() {
        $('#checkInModal')
          .modal('show')
        ;
    });
}

function modalAddItem(){
    $(document).ready(function() {
        $('#addItemModal')
          .modal('show')
        ;
    });
}

function bookingActionModal(id, token){

  $.ajax({
    type: 'POST',
    url: '/visitorhostel/booking-details/',
    data: {
        'csrfmiddlewaretoken' : token,
        'id' : id
    },
    success: function(data) {
      $('#bookingActionModal').modal('show');
      $("#request_modal").append(data);
    },
    error: function(data, err) {
        alert(err.message);
    }
  });
}

