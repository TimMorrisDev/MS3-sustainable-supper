$(document).ready(function () {

    // materialize initialise functions
    $('.sidenav').sidenav({
        edge: "right"
    });

    $('.slider').slider({
        duration: 4000,
        indicators: false,
    });

    $('.modal').modal();

    $('.tabs').tabs();

    $('.collapsible').collapsible();

    // add ingredient row to recipe form
    $('#add-ingredient').on('click', function () {
        let ingredient = '<div class="row ingredient-row valign-wrapper"><div class="input-field col s4"><i class="fas fa-list-ul prefix"></i><input id="ingredients" name="ingredients" type="text" class="validate ingredient"placeholder="Add Ingredient Here" required><label for="ingredients"></label></div><div class="input-field col s5"><input id="ingredient-prep" name="ingredient-prep" type="text" class="validate"placeholder="Preparation instructions"><label for="ingredient-prep"></label></div><div class="col s3"><button type="button" id="remove-ingredient" class="waves-effect waves-light btn red">Remove</button></div></div>';
        $(ingredient).insertBefore('#add-ingredient-row');
        $('.ingredient').last().focus();
    });

    // remove ingredient row from recipe form
    $(document).on('click', '#ingredient-row-parent #remove-ingredient', function () {
        $(this).closest('.ingredient-row').remove();
        $('.ingredient').last().focus();
    });

    // add method step row to recipe form
    $('#add-step').on('click', function () {
        let methodStep = '<div class="row method-row valign-wrapper"><div class="input-field col s8"><i class="fas fa-list-ul prefix"></i><textarea id="method" name="method" class="validate method-step" required></textarea><label for="method">Add Step Here</label></div><div class="col s4"><button type="button" id="remove-step" class="waves-effect waves-light btn red">Remove</button></div></div>';
        $(methodStep).insertBefore('#add-step-row');
        $('.method-step').last().focus();
    });

    // remove method step row from recipe form
    $(document).on('click', '#method-row-parent #remove-step', function () {
        $(this).closest('.method-row').remove();
        $('.method-step').last().focus();
    });

    // add ingredient row to user pantry form
    $('#add-user-ingredient').on('click', function () {
        let user_ingredient = '<div class="row user-ingredient-row valign-wrapper"><div class="input-field col s8"><i class="fas fa-list-ul prefix"></i><input id="user-ingredients" name="user-ingredients" type="text" class="validate user-ingredient"placeholder="Add Ingredient Here" required><label for="user-ingredients"></label></div><div class="col s3"><button type="button" id="remove-user-ingredient"class="waves-effect waves-light btn red">Remove</button></div></div>';
        $(user_ingredient).insertBefore('#add-user-ingredient-row');
        $('.user-ingredient').last().focus();
    });

    // remove ingredient row from user pantry form
    $(document).on('click', '#user-ingredient-row-parent #remove-user-ingredient', function () {
        $(this).closest('.user-ingredient-row').remove();
        $('.user-ingredient').last().focus();
    });

});