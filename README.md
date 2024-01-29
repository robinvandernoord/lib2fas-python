# lib2fas Python

Unofficial implementation of 2fas for Python (as a library).

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

services = lib2fas.load_services("/path/to/file.2fas", passphrase="optional") # -> TwoFactorStorage

services.generate() # generate all TOTP keys
github = services.find("githbu") # fuzzy match should find GitHub, returns a new TwoFactorStorage.

for label, services in github.items():
    # one label can have multiple services!
    for service in services:
        print(label, service.name, service.generate_int())

```

## License

This project is licensed under the MIT License.
