# lib2fas Python

Unofficial implementation of 2fas for Python (as a library).
This library serves as the backend for
the [robinvandernoord/2fas-python](https://github.com/robinvandernoord/2fas-python) CLI, a command-line tool that
provides an easy interface to interact with the 2fas TOTP.

## Installation

To install this project, use pip:

```bash
pip install lib2fas
# or to also install the cli tool:
pip install 2fas
```

## Usage

After installing the package, you can import it in your Python scripts as follows:

```python
import lib2fas

services = lib2fas.load_services("/path/to/file.2fas", passphrase="optional")  # -> TwoFactorStorage

services.generate()  # generate all TOTP keys

gmail = services["gmail"]  # exact match (case-insensitive), returns a list of 'TwoFactorAuthDetails' instances.

github = services.find("githbu")  # fuzzy match should find GitHub, returns a new TwoFactorStorage.

for label, services in github.items():
    # one label can have multiple services!
    for service in services:  # 'service' is a TwoFactorAuthDetails instance
        # Print label, service name, and TOTP code
        print("Label:", label)
        print("Service Name:", service.name)
        print("TOTP Code:", service.generate())  # or .generate_int() to get the code as a number.
```

The `passphrase` option of `load_services` is optional.
If you don't provide a password, but your file is encrypted, you will be prompted for the passphrase.
If possible, this will be safely stored in the keychain manager of your OS* until the next reboot.

* Note: only the "Secret Storage" keychain backend on Ubuntu Linux has been tested.

## License

This project is licensed under the MIT License.
