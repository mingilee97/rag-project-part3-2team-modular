"""Anthropic Messages API를 한 번 호출한다. 원문 오류와 키는 출력하지 않는다."""
import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
from rfp_rag.providers.openai_api import ProviderError


class AnthropicClient:
    def __init__(self, api_key: str, timeout: float = 90):
        if not api_key.strip() or any(ch in api_key for ch in '\r\n'):
            raise ValueError('Anthropic API 키를 입력하세요.')
        self._key, self.timeout = api_key.strip(), timeout
        self.usage: list[dict] = []

    def post(self, endpoint: str, payload: dict) -> dict:
        if endpoint != 'messages':
            raise ValueError('지원하지 않는 API입니다.')
        request = Request('https://api.anthropic.com/v1/messages',
                          data=json.dumps(payload).encode('utf-8'),
                          headers={'x-api-key': self._key, 'anthropic-version': '2023-06-01',
                                   'Content-Type': 'application/json'}, method='POST')
        try:
            with urlopen(request, timeout=self.timeout) as response:
                result = json.load(response)
        except HTTPError as error:
            code = error.code
            error.close()
            raise ProviderError(f'Anthropic HTTP {code}. 키 권한·잔액·요청 설정을 확인하세요.') from None
        except (URLError, TimeoutError, OSError, ValueError):
            raise ProviderError('Anthropic 연결 또는 응답 읽기에 실패했습니다.') from None
        if not isinstance(result, dict):
            raise ProviderError('Anthropic 응답 형식이 맞지 않습니다.')
        self.usage.append({'endpoint': endpoint, 'model': result.get('model', payload['model']),
                           'usage': result.get('usage', {})})
        return result
