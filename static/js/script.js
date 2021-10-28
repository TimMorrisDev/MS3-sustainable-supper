$(document).ready(function () {
    $('.sidenav').sidenav({
        edge: "right"
    });
    $('.slider').slider({
        duration: 4000,
        indicators: false,
    });

    $('#add-ingredient').on('click', function () {
        $('<div class="row ingredient-row valign-wrapper"><div class="input-field col s2"><i class="fas fa-list-ul prefix light-blue-text text-darken-4"></i><input id="ingredients" name="ingredients" type="text" class="validate"placeholder="Add Ingredient Here" required><label for="ingredients">Ingredients</label></div><div class="input-field col s2"><input id="quantity" name="quantity" type="text" class="validate" placeholder="Add Quantity Here"required><label for="quantity">Quantities</label></div><div class="input-field col s5"><input id="ingredient-prep" name="ingredient-prep" type="text" class="validate"placeholder="Preparation instructions" required><label for="ingredient-prep">Preparation instructions</label></div><div class="col s3"><button type="button" id="remove-ingredient" class="waves-effect waves-light btn red">Remove</button></div></div>').insertBefore('#add-ingredient-row');
    });

    $('#remove-ingredient').on('click', function () {
        $(this).closest('.ingredient-row').remove()
    });

    $('#add-step').on('click', function () {
        $('<div class="row method-row valign-wrapper"><div class="input-field col s8"><i class="fas fa-list-ul prefix light-blue-text text-darken-4"></i><textarea id="method" name="method" type="text" class="validate" required></textarea><label for="method">Add Step Here</label></div><div class="col s4"><button type="button" id="remove-step" class="waves-effect waves-light btn red">Remove</button></div></div>').insertBefore('#add-step-row');
    });

    $('#remove-step').on('click', function () {
        $(this).closest('.method-row').remove()
    });


});