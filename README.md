# dcm-converter

## 목적

`dcm_converter.py`는 의료 영상 포맷인 DICOM 파일을 JPEG 이미지로 변환하는 도구입니다.  
특히, 압축된 DICOM 파일도 변환할 수 있도록 `pylibjpeg`, `gdcm` 라이브러리를 지원하며,  
단일 파일 변환과 폴더 내 일괄 변환 기능을 모두 제공합니다.

## 주요 기능

- DICOM(.dcm) 파일을 JPEG(.jpg)로 변환
- 압축된 DICOM 지원 (`pylibjpeg`, `gdcm` 라이브러리 사용 시)
- 단일 파일 및 폴더 일괄 변환
- 이미지 품질(quality) 설정 가능

## 사용법

### 1. 단일 파일 변환

```bash
python dcm_converter.py sample.dcm
```

### 2. 출력 경로 지정

```bash
python dcm_converter.py sample.dcm -o output.jpg
```

### 3. 폴더 내 모든 DICOM 파일 일괄 변환

```bash
python dcm_converter.py input_folder -b
```

### 4. 이미지 품질 설정 (기본값 95)

```bash
python dcm_converter.py sample.dcm -q 90
```

## 대화형 모드

명령행 인자가 없으면, 프로그램 실행 후 DICOM 파일 경로를 입력받아 변환할 수 있습니다.

## 의존성 설치

필수:
- pydicom
- numpy
- pillow

압축된 DICOM 지원 (권장):
- pylibjpeg
- pylibjpeg-libjpeg
- python-gdcm

설치 예시:
```bash
pip install pydicom numpy pillow
pip install pylibjpeg pylibjpeg-libjpeg  # (옵션)
pip install python-gdcm                  # (옵션)
```

## 라이브러리 지원 상태 확인

실행 시 아래와 같이 압축 해제 라이브러리 지원 여부를 출력합니다.
```
=== 압축 해제 라이브러리 상태 ===
pylibjpeg 사용 가능: True/False
gdcm 사용 가능: True/False
경고: 압축 해제 라이브러리가 없습니다. 압축된 DICOM 파일 변환에 제한이 있을 수 있습니다.
```

## 참고

- 변환된 JPEG 파일은 원본 DICOM 파일의 이름을 기준으로 자동 생성되며, 경로와 품질을 지정할 수 있습니다.
- 압축된 DICOM 변환을 위해서 `pylibjpeg`, `gdcm` 라이브러리 설치를 권장합니다.
