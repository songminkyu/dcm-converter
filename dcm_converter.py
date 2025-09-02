import pydicom
import numpy as np
from PIL import Image
import os
import argparse
from pathlib import Path
import warnings

# DICOM 압축 해제를 위한 추가 라이브러리들
try:
    import pylibjpeg
    import pylibjpeg_libjpeg
    PYLIBJPEG_AVAILABLE = True
except ImportError:
    PYLIBJPEG_AVAILABLE = False

try:
    import gdcm
    GDCM_AVAILABLE = True
except ImportError:
    GDCM_AVAILABLE = False

# 경고 메시지 무시
warnings.filterwarnings("ignore")


def dcm_to_jpg(dcm_path, output_path=None, quality=95):
    """
    DICOM 파일을 JPG로 변환하는 함수
    
    Args:
        dcm_path (str): DICOM 파일 경로
        output_path (str, optional): 출력 JPG 파일 경로. None이면 자동 생성
        quality (int): JPG 품질 (1-100, 기본값: 95)
    
    Returns:
        str: 생성된 JPG 파일 경로
    """
    try:
        # DICOM 파일 읽기
        dicom = pydicom.dcmread(dcm_path, force=True)
        
        # 압축된 픽셀 데이터 처리
        if hasattr(dicom, 'pixel_array'):
            try:
                pixel_array = dicom.pixel_array
            except Exception as e:
                print(f"픽셀 데이터 추출 시도 중 오류: {str(e)}")
                
                # 압축 해제 플러그인 없이도 시도해보기
                try:
                    dicom.decompress()
                    pixel_array = dicom.pixel_array
                except:
                    # 원시 픽셀 데이터 직접 접근 시도
                    if hasattr(dicom, 'PixelData'):
                        print(f"원시 픽셀 데이터로 변환 시도: {dcm_path}")
                        return convert_raw_pixels(dicom, output_path, quality)
                    else:
                        raise Exception("픽셀 데이터를 찾을 수 없습니다.")
        else:
            if hasattr(dicom, 'PixelData'):
                return convert_raw_pixels(dicom, output_path, quality)
            else:
                raise Exception("픽셀 데이터를 찾을 수 없습니다.")
        
        # 데이터 타입에 따라 정규화
        if pixel_array.dtype != np.uint8:
            # 16비트나 다른 형식을 8비트로 변환
            pixel_array = pixel_array.astype(np.float64)
            pixel_array = (pixel_array - pixel_array.min()) / (pixel_array.max() - pixel_array.min())
            pixel_array = (pixel_array * 255).astype(np.uint8)
        
        # PIL Image로 변환
        if len(pixel_array.shape) == 2:
            # 흑백 이미지
            image = Image.fromarray(pixel_array, mode='L')
        elif len(pixel_array.shape) == 3:
            # 컬러 이미지
            if pixel_array.shape[2] == 3:
                image = Image.fromarray(pixel_array, mode='RGB')
            elif pixel_array.shape[2] == 4:
                image = Image.fromarray(pixel_array, mode='RGBA')
            else:
                # 첫 번째 채널만 사용
                image = Image.fromarray(pixel_array[:, :, 0], mode='L')
        
        # 출력 경로 설정
        if output_path is None:
            base_path = Path(dcm_path).stem
            output_path = f"{base_path}.jpg"
        
        # JPG로 저장
        image.save(output_path, 'JPEG', quality=quality)
        print(f"변환 완료: {dcm_path} -> {output_path}")
        return output_path
        
    except Exception as e:
        print(f"에러 발생: {dcm_path} - {str(e)}")
        return None


def convert_raw_pixels(dicom, output_path=None, quality=95):
    """
    압축된 DICOM의 원시 픽셀 데이터를 직접 처리하는 함수
    """
    try:
        # DICOM 헤더 정보 추출
        rows = dicom.get('Rows', 512)
        cols = dicom.get('Columns', 512)
        samples_per_pixel = dicom.get('SamplesPerPixel', 1)
        bits_allocated = dicom.get('BitsAllocated', 16)
        bits_stored = dicom.get('BitsStored', bits_allocated)
        high_bit = dicom.get('HighBit', bits_stored - 1)
        pixel_representation = dicom.get('PixelRepresentation', 0)
        
        # 원시 픽셀 데이터
        raw_data = dicom.PixelData
        
        # 데이터 타입 결정
        if bits_allocated <= 8:
            dtype = np.uint8
        elif bits_allocated <= 16:
            dtype = np.uint16 if pixel_representation == 0 else np.int16
        else:
            dtype = np.uint32 if pixel_representation == 0 else np.int32
        
        # 바이트 배열을 numpy 배열로 변환
        pixel_array = np.frombuffer(raw_data, dtype=dtype)
        
        # 배열 reshape
        if samples_per_pixel == 1:
            pixel_array = pixel_array.reshape(rows, cols)
        else:
            pixel_array = pixel_array.reshape(rows, cols, samples_per_pixel)
        
        # 8비트로 정규화
        if pixel_array.dtype != np.uint8:
            pixel_array = pixel_array.astype(np.float64)
            pixel_array = (pixel_array - pixel_array.min()) / (pixel_array.max() - pixel_array.min())
            pixel_array = (pixel_array * 255).astype(np.uint8)
        
        # PIL Image로 변환
        if len(pixel_array.shape) == 2:
            image = Image.fromarray(pixel_array, mode='L')
        else:
            image = Image.fromarray(pixel_array, mode='RGB')
        
        # 출력 경로 설정
        if output_path is None:
            base_path = Path(dicom.filename if hasattr(dicom, 'filename') else 'unknown').stem
            output_path = f"{base_path}_raw.jpg"
        
        # JPG로 저장
        image.save(output_path, 'JPEG', quality=quality)
        print(f"원시 데이터 변환 완료: {output_path}")
        return output_path
        
    except Exception as e:
        print(f"원시 픽셀 데이터 변환 실패: {str(e)}")
        return None


def batch_convert(input_dir, output_dir=None, quality=95):
    """
    폴더 내 모든 DICOM 파일을 일괄 변환
    
    Args:
        input_dir (str): 입력 폴더 경로
        output_dir (str, optional): 출력 폴더 경로. None이면 입력 폴더와 동일
        quality (int): JPG 품질
    """
    input_path = Path(input_dir)
    
    if output_dir is None:
        output_path = input_path
    else:
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
    
    # DCM 파일 찾기
    dcm_files = list(input_path.glob("*.dcm")) + list(input_path.glob("*.DCM"))
    
    if not dcm_files:
        print(f"DICOM 파일을 찾을 수 없습니다: {input_dir}")
        return
    
    print(f"{len(dcm_files)}개의 DICOM 파일을 찾았습니다.")
    
    # 일괄 변환
    success_count = 0
    for dcm_file in dcm_files:
        jpg_filename = dcm_file.stem + ".jpg"
        jpg_path = output_path / jpg_filename
        
        if dcm_to_jpg(str(dcm_file), str(jpg_path), quality):
            success_count += 1
    
    print(f"변환 완료: {success_count}/{len(dcm_files)}개 파일")


def main():
    parser = argparse.ArgumentParser(description="DICOM 파일을 JPG로 변환")
    parser.add_argument("input", help="입력 DICOM 파일 또는 폴더 경로")
    parser.add_argument("-o", "--output", help="출력 파일 또는 폴더 경로")
    parser.add_argument("-q", "--quality", type=int, default=95, 
                       help="JPG 품질 (1-100, 기본값: 95)")
    parser.add_argument("-b", "--batch", action="store_true", 
                       help="폴더 내 모든 DCM 파일 일괄 변환")
    
    args = parser.parse_args()
    
    # 압축 해제 라이브러리 상태 확인
    print("=== 압축 해제 라이브러리 상태 ===")
    print(f"pylibjpeg 사용 가능: {PYLIBJPEG_AVAILABLE}")
    print(f"gdcm 사용 가능: {GDCM_AVAILABLE}")
    if not PYLIBJPEG_AVAILABLE and not GDCM_AVAILABLE:
        print("경고: 압축 해제 라이브러리가 없습니다. 압축된 DICOM 파일 변환에 제한이 있을 수 있습니다.")
        print("해결 방법:")
        print("1. pip install pylibjpeg pylibjpeg-libjpeg")
        print("2. 또는 pip install python-gdcm")
    print()
    
    input_path = Path(args.input)
    
    if args.batch or input_path.is_dir():
        # 일괄 변환
        batch_convert(args.input, args.output, args.quality)
    else:
        # 단일 파일 변환
        if input_path.is_file():
            dcm_to_jpg(args.input, args.output, args.quality)
        else:
            print(f"파일을 찾을 수 없습니다: {args.input}")


if __name__ == "__main__":
    # 사용 예시
    print("=== DICOM to JPG 변환기 (압축 지원) ===")
    print("사용 방법:")
    print("1. 단일 파일 변환: python dcm_converter.py sample.dcm")
    print("2. 출력 경로 지정: python dcm_converter.py sample.dcm -o output.jpg")
    print("3. 폴더 일괄 변환: python dcm_converter.py input_folder -b")
    print("4. 품질 설정: python dcm_converter.py sample.dcm -q 90")
    print()
    print("압축된 DICOM 파일 지원을 위해 다음 라이브러리 설치를 권장합니다:")
    print("pip install pylibjpeg pylibjpeg-libjpeg")
    print("또는")
    print("pip install python-gdcm")
    print()
    
    # 명령행 인자가 없으면 대화형 모드
    import sys
    if len(sys.argv) == 1:
        dcm_file = input("DICOM 파일 경로를 입력하세요: ")
        if os.path.exists(dcm_file):
            dcm_to_jpg(dcm_file)
        else:
            print("파일이 존재하지 않습니다.")
    else:
        main()