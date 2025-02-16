$("#your-polls-btn").on('click', function (event) { console.log('hi'); openTab(event,'your-polls');});
$("#completed-polls-btn").on('click', function (event) { console.log('hi'); openTab(event,'completed-polls');});


function openTab(event, tabName) {

    // Hide all elements with class "tabcontent"
    $(".tabcontent").hide();

    // Remove "active" class from all elements with class "tablinks"
    $(".tablinks").removeClass("active");

    // Show the current tab, and add an "active" class to the button that opened the tab
    $(`#${tabName}`).show();
    $(event.currentTarget).addClass("active");
}
