function modalCancel(){
    $(document).ready(function() {
        $('#cancel')
          .modal('setting', 'closable', false)
          .modal('show')
        ;
    });
}

function modalDandm(){
    $(document).ready(function() {
        $('#dandm')
          .modal('show')
        ;
    });
}


function modalCmc(){
    $(document).ready(function() {
        $('#mcm')
          .modal('show')
        ;
    });
}


function modalGoldmedal(){
    $(document).ready(function() {
        $('#goldmedal')
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

function bookingRequestModal(id){
    $(document).ready(function() {
        $('#booking-request-'.concat(id)).modal('show');
    });
}

function bookingDetailsModal(id){
    $(document).ready(function() {
        ('#booking-details-'.concat(id)).modal('show');
    });
}
