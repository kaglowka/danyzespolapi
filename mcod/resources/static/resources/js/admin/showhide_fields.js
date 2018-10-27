(function ($) {
    $(function () {

        var $select = $('input[id*="external"]');
        var $file_input = $('[type=file][id="id_file"]');
        var $link_input = $('[type=url][id="id_link"]');

        if ($file_input.val() == "") {
            $select.prop("checked", true)
        }

        var $file = $file_input.closest('fieldset');
        var $input = $link_input.closest('fieldset');

            $file.hide();
            $input.hide();

            externalHandler = function (is_external) {
                if (is_external == true) {

                    $input.show();
                    $file.hide();
                }
                else
                {
                    $input.hide();
                    $file.show();
                }
            };

        $select.on('click', function () {
            externalHandler($(this).is(":checked"));
        });

        externalHandler($select.is(":checked"));
    });
})(django.jQuery);