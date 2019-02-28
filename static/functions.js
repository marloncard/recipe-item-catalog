
    function truncate () {
        $('.card-text').each(function(i) {
            if ($(this).text().length > 200) {
            var shortCard = $.trim($(this).text()).substring(0,200).split(" ").slice(0,-1).join(" ") + "...";
            $(this).text(shortCard);
            }
        });
    };
