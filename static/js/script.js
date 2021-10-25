$(document).ready(function () {
    $('.sidenav').sidenav({
        edge: "right"
    });
    $('.slider').slider({
        duration: 4000,
        indicators: false,
    });

    $('#add-ingredient').on('click', function () {
        $('<div class="input-group add-on ingredient-block" id="ingredient-block"><input type="text" class="form-control ingredient" name="ingredients" id="ingredients" placeholder="Add New Ingredient"><div class="input-group-append"><button type="button" class="btn btn-delete delete-ingredient-button">Delete</button></div>').insertBefore('#new-ingredient');
    });
});