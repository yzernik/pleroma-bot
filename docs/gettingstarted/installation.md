## Installation method

First you need to intall ```pleroma-bot``` on your system. There are multiple methods available:

=== "Using PyPi"

    * System-wide:
    ```console
    $ pip install pleroma-bot
    ```
    * Or in a [virtual environment :octicons-file-code-24:](https://docs.python.org/3/tutorial/venv.html):
    ```console
    $ python3 -m venv myvenv
    $ source myvenv/bin/activate
    (myenv) $ pip install pleroma-bot
    ```
    

=== "Using AUR package"

    ```console
    $ yay -S python-pleroma-bot
    ```

=== "Using Git"

    ```console
    $ git clone https://github.com/robertoszek/pleroma-bot.git
    $ cd pleroma-bot/
    ```



!!! warning "If you choose to use Git, note that you will also need to install the needed dependecies manually"

!!! info "On the other hand, if you use ```pip``` or the AUR package, all dependencies will be installed automatically with no manual intervention required"

Either way, here's a list of the dependencies in case you need them:

| Name            | Git repo                                       | Docs
| --------------- | ---------------------------------------------- | ----------------------------------------------------------- |
| python-oauthlib | [GitHub](https://github.com/oauthlib/oauthlib) | [Documentation](https://oauthlib.readthedocs.io/en/latest/) |
| python-pyaml | [GitHub](https://github.com/yaml/pyyaml) | [Documentation](https://pyyaml.org/wiki/PyYAMLDocumentation) |
| python-requests | [GitHub](https://github.com/psf/requests) | [Documentation](https://requests.readthedocs.io/) |
| python-requests-oauthlib | [GitHub](https://github.com/requests/requests-oauthlib) | [Documentation](https://requests-oauthlib.readthedocs.org) |


## Test the installation

Once installed using your preferred method, test that the package has been correctly installed using the appropiate command.


=== "Using PyPi"

    ```console
    $ pleroma-bot -h


                            `^y6gB@@BBQA{,
                          :fB@@@@@@BBBBBQgU"
                        `f@@@@@@@@BBBBQgg80H~
                        H@@B@BB@BBBB#Qgg&0RNT
                       z@@&B@BBBBBBQgg80RD6HK
                      ;@@@QB@BBBB#Qgg&0RN6WqS
                      q@@@@@BBBBQgg80RN6HAqSo          _             _
                     z@@@@BBBB#Qg8&0RN6WqSUhr         | |           | |
                   -H@@@@BBBBQQg80RD6HAqSKh(       ___| |_ ___  _ __| | __
                  rB@@@BBBB#6Lm00DN6WqSUhfv       / __| __/ _ \| '__| |/ /
                 f@@@@BBBBf= |0RD6HAqSKhfv        \__ \ || (_) | |  |   <
               =g@@@BBBBF=  "RDN6WqSUhff{         |___/\__\___/|_|  |_|\_|
              c@@@@BBgu_   ~WD9HAqSKhfkl`
            _6@@@BBNr     'qN6WqSUhhfXI'     .                           .       .
           rB@@@B0r      `S6HAqSKhfkoCr  ,-. |  ,-. ,-. ,-. ,-,-. ,-.    |-. ,-. |-
         `X@@@BQx       `I6WASShhfXFIy_  | | |  |-' |   | | | | | ,-| -- | | | | |
        _g@@@Q\`        JHAqSKhfXoCwJz_  |-' `' `-' '   `-' ' ' ' `-^    `-' `-' `'
       rB@@#x`         }WASShhfXsIyzuu,  |
     `y@@&|          .IAqSKhfXoCwJzu1lr  '
    `D@&|           :KqSUhffXsIyzuu1llc,
    ff=            `==:::""",,,,________


    usage: cli.py [-h] [-c CONFIG] [-l LOG] [-n] [--forceDate [FORCEDATE]] [-s]
                  [--verbose] [--version]

    Bot for mirroring one or multiple Twitter accounts in Pleroma/Mastodon.

    optional arguments:
      -h, --help            show this help message and exit
      -c CONFIG, --config CONFIG
                            path of config file (config.yml) to use and parse. If
                            not specified, it will try to find it in the current
                            working directory.
      -l LOG, --log LOG     path of log file (error.log) to create. If not
                            specified, it will try to store it at your config file
                            path
      -n, --noProfile       skips Fediverse profile update (no background image,
                            profile image, bio text, etc.)
      --forceDate [FORCEDATE]
                            forces the tweet retrieval to start from a specific
                            date. The twitter_username value (FORCEDATE) can be
                            supplied to only force it for that particular user in
                            the config
      -s, --skipChecks      skips first run checks
      --verbose, -v
      --version             show program's version number and exit
    ```

=== "Using AUR package"

    ```console
    $ pleroma-bot -h


                            `^y6gB@@BBQA{,
                          :fB@@@@@@BBBBBQgU"
                        `f@@@@@@@@BBBBQgg80H~
                        H@@B@BB@BBBB#Qgg&0RNT
                       z@@&B@BBBBBBQgg80RD6HK
                      ;@@@QB@BBBB#Qgg&0RN6WqS
                      q@@@@@BBBBQgg80RN6HAqSo          _             _
                     z@@@@BBBB#Qg8&0RN6WqSUhr         | |           | |
                   -H@@@@BBBBQQg80RD6HAqSKh(       ___| |_ ___  _ __| | __
                  rB@@@BBBB#6Lm00DN6WqSUhfv       / __| __/ _ \| '__| |/ /
                 f@@@@BBBBf= |0RD6HAqSKhfv        \__ \ || (_) | |  |   <
               =g@@@BBBBF=  "RDN6WqSUhff{         |___/\__\___/|_|  |_|\_|
              c@@@@BBgu_   ~WD9HAqSKhfkl`
            _6@@@BBNr     'qN6WqSUhhfXI'     .                           .       .
           rB@@@B0r      `S6HAqSKhfkoCr  ,-. |  ,-. ,-. ,-. ,-,-. ,-.    |-. ,-. |-
         `X@@@BQx       `I6WASShhfXFIy_  | | |  |-' |   | | | | | ,-| -- | | | | |
        _g@@@Q\`        JHAqSKhfXoCwJz_  |-' `' `-' '   `-' ' ' ' `-^    `-' `-' `'
       rB@@#x`         }WASShhfXsIyzuu,  |
     `y@@&|          .IAqSKhfXoCwJzu1lr  '
    `D@&|           :KqSUhffXsIyzuu1llc,
    ff=            `==:::""",,,,________


    usage: cli.py [-h] [-c CONFIG] [-l LOG] [-n] [--forceDate [FORCEDATE]] [-s]
                  [--verbose] [--version]

    Bot for mirroring one or multiple Twitter accounts in Pleroma/Mastodon.

    optional arguments:
      -h, --help            show this help message and exit
      -c CONFIG, --config CONFIG
                            path of config file (config.yml) to use and parse. If
                            not specified, it will try to find it in the current
                            working directory.
      -l LOG, --log LOG     path of log file (error.log) to create. If not
                            specified, it will try to store it at your config file
                            path
      -n, --noProfile       skips Fediverse profile update (no background image,
                            profile image, bio text, etc.)
      --forceDate [FORCEDATE]
                            forces the tweet retrieval to start from a specific
                            date. The twitter_username value (FORCEDATE) can be
                            supplied to only force it for that particular user in
                            the config
      -s, --skipChecks      skips first run checks
      --verbose, -v
      --version             show program's version number and exit
    ```

=== "Using Git"

    ```console
    $ python3 -m pleroma_bot.cli -h


                            `^y6gB@@BBQA{,
                          :fB@@@@@@BBBBBQgU"
                        `f@@@@@@@@BBBBQgg80H~
                        H@@B@BB@BBBB#Qgg&0RNT
                       z@@&B@BBBBBBQgg80RD6HK
                      ;@@@QB@BBBB#Qgg&0RN6WqS
                      q@@@@@BBBBQgg80RN6HAqSo          _             _
                     z@@@@BBBB#Qg8&0RN6WqSUhr         | |           | |
                   -H@@@@BBBBQQg80RD6HAqSKh(       ___| |_ ___  _ __| | __
                  rB@@@BBBB#6Lm00DN6WqSUhfv       / __| __/ _ \| '__| |/ /
                 f@@@@BBBBf= |0RD6HAqSKhfv        \__ \ || (_) | |  |   <
               =g@@@BBBBF=  "RDN6WqSUhff{         |___/\__\___/|_|  |_|\_|
              c@@@@BBgu_   ~WD9HAqSKhfkl`
            _6@@@BBNr     'qN6WqSUhhfXI'     .                           .       .
           rB@@@B0r      `S6HAqSKhfkoCr  ,-. |  ,-. ,-. ,-. ,-,-. ,-.    |-. ,-. |-
         `X@@@BQx       `I6WASShhfXFIy_  | | |  |-' |   | | | | | ,-| -- | | | | |
        _g@@@Q\`        JHAqSKhfXoCwJz_  |-' `' `-' '   `-' ' ' ' `-^    `-' `-' `'
       rB@@#x`         }WASShhfXsIyzuu,  |
     `y@@&|          .IAqSKhfXoCwJzu1lr  '
    `D@&|           :KqSUhffXsIyzuu1llc,
    ff=            `==:::""",,,,________


    usage: cli.py [-h] [-c CONFIG] [-l LOG] [-n] [--forceDate [FORCEDATE]] [-s]
              [--verbose] [--version]

    Bot for mirroring one or multiple Twitter accounts in Pleroma/Mastodon.

    optional arguments:
      -h, --help            show this help message and exit
      -c CONFIG, --config CONFIG
                            path of config file (config.yml) to use and parse. If
                            not specified, it will try to find it in the current
                            working directory.
      -l LOG, --log LOG     path of log file (error.log) to create. If not
                            specified, it will try to store it at your config file
                            path
      -n, --noProfile       skips Fediverse profile update (no background image,
                            profile image, bio text, etc.)
      --forceDate [FORCEDATE]
                            forces the tweet retrieval to start from a specific
                            date. The twitter_username value (FORCEDATE) can be
                            supplied to only force it for that particular user in
                            the config
      -s, --skipChecks      skips first run checks
      --verbose, -v
      --version             show program's version number and exit
    ```

