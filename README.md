
# dcm-converter

## Purpose

`dcm_converter.py` is a tool for converting DICOM files (medical image format) to JPEG images.  
It supports compressed DICOM files with `pylibjpeg` and `gdcm` libraries,  
and provides both single file conversion and batch conversion for all files in a folder.

## Key Features

- Convert DICOM (.dcm) files to JPEG (.jpg)
- Supports compressed DICOM files (with `pylibjpeg`, `gdcm`)
- Single file and batch folder conversion
- Image quality setting available

## Usage

### 1. Single File Conversion

```bash
python dcm_converter.py sample.dcm
```

### 2. Specify Output Path

```bash
python dcm_converter.py sample.dcm -o output.jpg
```

### 3. Batch Convert All DICOM Files in a Folder

```bash
python dcm_converter.py input_folder -b
```

### 4. Set Image Quality (Default: 95)

```bash
python dcm_converter.py sample.dcm -q 90
```

## Interactive Mode

If no command-line arguments are provided, the program will prompt for the DICOM file path after starting, and then perform the conversion.

## Dependencies

Required:
- pydicom
- numpy
- pillow

Compressed DICOM support (recommended):
- pylibjpeg
- pylibjpeg-libjpeg
- python-gdcm

Installation Example:
```bash
pip install pydicom numpy pillow
pip install pylibjpeg pylibjpeg-libjpeg  # (optional)
pip install python-gdcm                  # (optional)
```

## Library Support Status

When running, the program prints the status of decompression library support as follows:
```
=== Decompression Library Status ===
pylibjpeg available: True/False
gdcm available: True/False
Warning: No decompression libraries are available. There may be limitations when converting compressed DICOM files.
```

## Notes

- The converted JPEG file is automatically created based on the original DICOM file name; you can specify the path and quality.
- For converting compressed DICOM files, it is recommended to install the `pylibjpeg` and `gdcm` libraries.
