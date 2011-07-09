= SETTINGS =

    There's two options for declaring customisations to the zen_settings. You
    can either use a `my_zen_settings.py` with a global level dict
    `my_zen_settings` or you can use `zen-settings.sublime-settings` and declare
    the settings in JSON.

    If both are declared the JSON will `win`.

    == my_zen_settings.py ==

        This can be in either of two places, the first of which found will be
        used.

            * ~/my_zen_settings.py
            * $PACKAGES_PATH/my_zen_setting

    == zen-settings.sublime-settings ==

        Create a $PACKAGES_PATH/ZenCoding/zen-settings.sublime-settings
        and create a settings dict:

        {
            "debug" : false,
            "my_zen_settings" : {
                "html": {
                    "abbreviations": {
                        "jq": "<script type=\"text/javascript\" src=\"http://ajax.googleapis.com/ajax/libs/jquery/1.3.2/jquery.min.js\"></script>",
                        "demo": "<div id=\"demo\"></div>"
                    }
                }
            }
        }

    == Dict Format ==

    See https://github.com/sergeche/zen-coding/blob/master/python/zencoding/zen_settings.py
    to see what settings you can override/ extend.

    {
        'css': {
            'filters': 'html,css,fc'
        }
    }

= HELP =
    http://www.sublimetext.com/forum/viewtopic.php?f=2&t=580&p=10654#p10654