"""현재 프로세스 환경 또는 기존 Windows 암호화 저장소에서 OpenAI 키만 사용한다."""
import base64
import ctypes
from ctypes import wintypes
import json
import os
from pathlib import Path

SCHEMA = 'team-rag-current-user-dpapi-v1'
ENTROPY = b'CodexReview/team-rag-validation/current-user/v1'


def store_path() -> Path | None:
    base = os.environ.get('LOCALAPPDATA')
    return Path(base) / 'CodexReview/team-rag-validation/keys.dpapi.json' if base else None


def key_is_saved() -> bool:
    """실제 키를 복호화하지 않고 공개 저장 여부만 읽는다."""
    path = store_path()
    if os.name != 'nt' or path is None or not path.exists():
        return False
    try:
        packet = json.loads(path.read_text(encoding='utf-8'))
        return (packet.get('schema') == SCHEMA
                and packet.get('present', {}).get('OPENAI_API_KEY') is True)
    except (OSError, ValueError, AttributeError):
        return False


class Blob(ctypes.Structure):
    _fields_ = [('cbData', wintypes.DWORD), ('pbData', ctypes.POINTER(ctypes.c_ubyte))]


def load_key(name: str = 'OPENAI_API_KEY') -> str:
    if name not in ('OPENAI_API_KEY', 'ANTHROPIC_API_KEY'):
        raise ValueError('지원하지 않는 API 키입니다.')
    label = 'OpenAI' if name == 'OPENAI_API_KEY' else 'Anthropic'
    value = os.environ.get(name, '').strip()
    if value:
        if any(ch in value for ch in '\r\n'):
            raise ValueError(f'{label} API 키 형식이 맞지 않습니다.')
        return value
    path = store_path()
    if os.name != 'nt' or path is None or not path.exists():
        raise ValueError(f'RAG API 키 설정에서 {label} 키를 저장하거나 {name}를 설정하세요.')
    target = Blob()
    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    kernel.LocalFree.argtypes = [ctypes.c_void_p]
    kernel.LocalFree.restype = ctypes.c_void_p
    try:
        if path.stat().st_size > 131072:
            raise ValueError('암호화 파일 크기가 맞지 않습니다.')
        packet = json.loads(path.read_text(encoding='utf-8'))
        if packet.get('schema') != SCHEMA or packet.get('protection') != 'Windows DPAPI CurrentUser':
            raise ValueError('암호화 파일 형식이 맞지 않습니다.')
        cipher = base64.b64decode(packet['protected_values'], validate=True)
        buffer = ctypes.create_string_buffer(cipher)
        extra = ctypes.create_string_buffer(ENTROPY)
        source = Blob(len(cipher), ctypes.cast(buffer, ctypes.POINTER(ctypes.c_ubyte)))
        entropy = Blob(len(ENTROPY), ctypes.cast(extra, ctypes.POINTER(ctypes.c_ubyte)))
        operation = ctypes.WinDLL('crypt32', use_last_error=True).CryptUnprotectData
        operation.argtypes = [ctypes.POINTER(Blob), ctypes.c_void_p, ctypes.POINTER(Blob),
                             ctypes.c_void_p, ctypes.c_void_p, wintypes.DWORD, ctypes.POINTER(Blob)]
        operation.restype = wintypes.BOOL
        if not operation(ctypes.byref(source), None, ctypes.byref(entropy), None, None, 1, ctypes.byref(target)):
            raise ValueError('복호화 실패')
        values = json.loads(ctypes.string_at(target.pbData, target.cbData).decode('utf-8'))
        value = values.get(name, '').strip()
        values.clear()
        if not value or any(ch in value for ch in '\r\n'):
            raise ValueError('키 미입력')
        return value
    except (OSError, ValueError, KeyError, TypeError, AttributeError):
        raise ValueError(f'{label} 암호화 키를 읽지 못했습니다. RAG API 키 설정에서 저장하세요.') from None
    finally:
        if target.pbData:
            ctypes.memset(target.pbData, 0, target.cbData)
            kernel.LocalFree(target.pbData)
