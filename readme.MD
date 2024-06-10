# QR Keychain Generator

This Python script generates 3D printable dual-sided QR code tags or keychains. The keychains feature a unique QR code
on both sides, along with customizable text. The script is designed to efficiently generate multiple keychains and
arrange them on a build plate for 3D printing.

## Features

- Generates dual-sided QR code keychains with customizable dimensions and styling
- Automatically arranges keychains on a build plate for efficient 3D printing
- Customizable keychain hole size and position
- Adjustable text font, size, and border
- Supports generating a range of keychains with sequential numbering
- Outputs separate STL files for the keychain body and colored components

## Requirements

- Python 3.11 or higher
- Poetry (Python dependency management tool)

## Installation

1. Install Poetry using the instructions provided on the [official website](https://python-poetry.org/docs/).

    ```bash
    curl -sSL https://install.python-poetry.org | python3 -
    ```

2. Clone the repository:

    ```bash
    git clone https://github.com/yourusername/qr-keychain.git
    cd qr-keychain
    ```

3. Install the required dependencies using Poetry:

   ```bash
   poetry install
   ```

## Usage

To generate QR keychains, run the script with the desired command-line arguments:

```bash
poetry run qr-keychain --start-index 1 --end-index 10 --output-dir output
```

The available command-line arguments are:

- `--start-index`: Starting index for keychain tags
- `--end-index`: Ending index for keychain tags
- `--output-dir`: Output directory for STL files (default: "output")
- `--token-width`: Width of the keychain token (default: 50.0)
- `--token-height`: Height of the keychain token (default: 60.0)
- `--token-depth`: Depth of the keychain token (default: 3.0)
- `--token-corner-radius`: Corner radius of the keychain token (default: 4.0)
- `--token-fillet-radius`: Fillet radius of the keychain token (default: 1.0)
- `--qr-border`: Border width around the QR code (default: 3.0)
- `--colored-print-depth`: Depth of colored print (default: 0.6)
- `--text-font`: Font for the text (default: "Helvetica")
- `--text-size`: Size of the text (default: 7.0)
- `--text-border`: Border around the text (default: 3.0)
- `--hole-radius`: Radius of the keychain hole (default: 3.0)
- `--hole-offset`: Offset of the keychain hole (default: 3.0)
- `--build-plate-width`: Width of the build plate (default: 254.0)
- `--build-plate-height`: Height of the build plate (default: 254.0)
- `--build-plate-spacing`: Spacing between keychains on the build plate (default: 1.0)

The script will generate separate STL files for the keychain body and colored components in the specified output
directory. The keychains will be automatically arranged on build plates to maximize printing efficiency.

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.