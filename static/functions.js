
function truncate () {
    $('.card-text').each(function(i) {
        if ($(this).text().length > 200) {
        var shortCard = $.trim($(this).text()).substring(0,200).split(" ").slice(0,-1).join(" ") + "...";
        $(this).text(shortCard);
        }
    })
}

function validateRecipe() {
    var valid = true;

    var fname = document.forms["recipeForm"]["name"].value;
    if(fname=="") {
        alert("Name is a required field");
        valid = false;
    }

    var fcategory = document.forms["recipeForm"]["category"].value;
    if(fcategory=="") {
        alert("Category is a required field");
        valid = false;
    }

    var finstructions = document.forms["recipeForm"]["instructions"].value;
    if(finstructions=="") {
        alert("Instructions is a required field");
        valid = false;
    }

    var fingredients = document.forms["recipeForm"]["ingredients"].value;
    if(fingredients=="") {
        alert("Ingredients is a required field");
        valid = false;
    }

    return valid;
}
