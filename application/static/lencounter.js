
function update_counter() {
    $('#contentslength').html($('#contents').val().length);
}
$('#contents').keyup(update_counter);
$('#contents').change(update_counter);