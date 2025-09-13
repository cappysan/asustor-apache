# Asustor - Vim

Asustor APK package for GNU bash, the Bourne Again SHell.


# Table of contents
1. [Installation](#installation)  
2. [Building](#building)  
    a. [cloning](#cloning)  
    a. [requirements](#requirements)  
    a. [bash](#bash)  
    c. [apk](#apk)  
3. [Support & Sponsorship](#support)  
4. [License](#license)  
5. [Links](#links)  


## Installation <a name="installation"></a>

This section is currently a placeholder until Asustor validates the package and adds it to the Asustor App Central.

The APK application will also be made available on [https://www.asustorapps.org/](https://www.asustorapps.org/)


## Building <a name="building"></a>

In order to builds `bash`, and the APK, you first must have a working cross compiler toolchain. Please refer to [the toolchain procject](https://gitlab.com/cappysan/asustor/toolchain) to build your cross compiler.


### Cloning <a name="cloning"></a>

Once this project is cloned, update the repository to download the submodules:

~~~
git submodule update --init --recursive
~~~


### Requirements <a name="requirements"></a>

Some applications, in addition to those required when building the cross compiler, are required to build this project. On Debian, and similar distributions, you can install those dependencies with the following commands:

~~~bash
sudo apt-get update
sudo apt-get install -y --no-install-recommends fakeroot
~~~


### bash <a name="bash"></a>

In order to build `bash`, a helper script exists. Run it to build `bash`:

~~~bash
./bash.sh
~~~


### apk <a name="apk"></a>

A `Makefile` target exists to build the apk. The `apk` will then be found at the root of this project folder.

##
~~~bash
make apk
~~~


## Support & Sponsorship <a name="support"></a>

You can help support this project, and all Cappysan projects, through the following actions:

- ⭐Star the repository on GitLab, GitHub, or both to increase visibility and community engagement.

- 💬 Join the Discord community: [https://discord.gg/SsY3CAdp4Q](https://discord.gg/SsY3CAdp4Q) to connect, contribute, share feedback, and/or stay updated.

- 🛠️ Contribute by submitting issues, improving documentation, or creating pull requests to help the project grow.

- ☕ Support financially through [Buy Me a Coffee](https://buymeacoffee.com/cappysan), [Patreon](https://www.patreon.com/c/cappysan), [GitHub](https://github.com/sponsors/cappysan), or [Bitcoin (bc1qdhad5rhu577p025ywwf2vevy83np8uvd0tgugm)](https://addrs.to/pay?token=BTC&address=bc1qdhad5rhu577p025ywwf2vevy83np8uvd0tgugm&name=cappysan). Your contributions directly sustain ongoing development and maintenance, including server costs.

Your support ensures these projects continue to improve, expand, and remain freely available to everyone.


## License <a name="license"></a>

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

Please refer to the upstream software documentation for details on their respective licenses.


## Links <a name="links"></a>

  * GitLab: [https://gitlab.com/cappysan/asustor/bash](https://gitlab.com/cappysan/asustor/bash)
  * GitHub: [https://github.com/cappysan/asustor-bash](https://github.com/cappysan/asustor-bash)
  * Discord: [https://discord.gg/SsY3CAdp4Q](https://discord.gg/SsY3CAdp4Q)
