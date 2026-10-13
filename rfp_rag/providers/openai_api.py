"""OpenAI HTTP API 연결. 키와 공급자 오류 원문은 출력하지 않는다."""
import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class ProviderError(RuntimeError):
    pass


class OpenAIClient:
    def __init__(self, api_key: str, timeout: float = 90):
        if not api_key.strip() or any(ch in api_key for ch in '\r\n'):
            raise ValueError('OpenAI API 키를 입력하세요.')
        self._key = api_key.strip()
        self.timeout = timeout
        self.usage: list[dict] = []

    def post(self, endpoint: str, payload: dict) -> dict:
        if endpoint not in ('embeddings', 'responses'):
            raise ValueError('지원하지 않는 API입니다.')
        request = Request('https://api.openai.com/v1/' + endpoint,
                          data=json.dumps(payload).encode('utf-8'),
                          headers={'Authorization': 'Bearer ' + self._key,
                                   'Content-Type': 'application/json'}, method='POST')
        try:
            with urlopen(request, timeout=self.timeout) as response:
                result = json.load(response)
        except HTTPError as error:
            code = error.code
            error.close()
            raise ProviderError(f'OpenAI HTTP {code}. 키 권한·사용 한도·요청 설정을 확인하세요.') from None
        except (URLError, TimeoutError, OSError, ValueError):
            raise ProviderError('OpenAI 연결 또는 응답 읽기에 실패했습니다.') from None
        if not isinstance(result, dict):
            raise ProviderError('OpenAI 응답 형식이 맞지 않습니다.')
        self.usage.append({'endpoint': endpoint, 'model': payload['model'],
                           'usage': result.get('usage', {})})
        return result
