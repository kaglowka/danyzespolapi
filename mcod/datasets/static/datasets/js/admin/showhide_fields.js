(function ($) {
    $(function () {

        var $tab = $('.suit-tab-resources');
        var onExternal = function () {

            //$('.field-description').hide();

            var $chks = $('input[type=checkbox][id$="is_external"]'),
                externalHandler = function (isExternal, $input, $file) {
                    if (isExternal) {
                        $input.show();
                        $file.hide();
                    }
                    else {
                        $input.hide();
                        $file.show();
                    }
                };

            $chks.each(function () {
                var $chk = $(this)
                var $chkParent = $chk.closest('fieldset');
                var $file = $chkParent.siblings().find('[type=file][id$="file"]').closest('fieldset');
                var $input = $chkParent.siblings().find('[type=url][id$="link"]').closest('fieldset');


                if ($chkParent.siblings().find('[type=file][id$="file"]').val() == "" && $chkParent.siblings().find('[type=url][id$="link"]').val() != "") {
                    $chk.prop("checked", true);
                }

                $file.hide();
                $input.hide();

                $chk.on('click', function () {
                    externalHandler($(this).is(":checked"), $input, $file);
                });


                externalHandler($chk.is(":checked"), $input, $file);

            });
        }
        onExternal();


        setTimeout(function () {
            var $addRow = $tab.find('.add-row');
            var $old = $addRow.find('a').hide();

            // hide existing button and trigger click on it when needed
            $('<a></a>', {
                text: $old.text(),
                href: '#',
                click: function (e) {
                    e.preventDefault();

                    $old.trigger('click');
                    window.scrollTop
                    onExternal();
                }
            }).appendTo($addRow);

            // go to the top of the page
            $('<a></a>', {
                class: 'pull-right',
                text: 'GO UP',
                href: '#',
                click: function (e) {
                    e.preventDefault();

                    $(window).scrollTop(0);
                }
            }).appendTo($addRow);

        }, 0);

    });
})(django.jQuery);