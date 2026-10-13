"""로컬 문서를 읽는다. PDF는 pypdf, HWP 5는 olefile이 필요하다."""
import csv
from pathlib import Path
import struct
import zlib
from rfp_rag.contracts import Document


def _hwp_text(path: Path) -> str:
    try:
        import olefile
    except ImportError:
        raise ValueError('HWP를 읽으려면 pip install -e ".[documents]"를 실행하세요.') from None
    with olefile.OleFileIO(path) as hwp:
        header = hwp.openstream('FileHeader').read()
        flags = struct.unpack_from('<I', header, 36)[0]
        if flags & (2 | 4):
            raise ValueError('암호화·배포용 HWP는 지원하지 않습니다. 일반 PDF 또는 TXT로 변환하세요.')
        sections = sorted((item for item in hwp.listdir() if len(item) == 2
                           and item[0] == 'BodyText' and item[1].startswith('Section')),
                          key=lambda item: int(item[1][7:]))
        paragraphs = []
        for section in sections:
            data = hwp.openstream(section).read()
            if flags & 1:
                data = zlib.decompress(data, -15)
            offset = 0
            while offset + 4 <= len(data):
                record = struct.unpack_from('<I', data, offset)[0]
                tag, size = record & 1023, record >> 20
                offset += 4
                if size == 4095:
                    size = struct.unpack_from('<I', data, offset)[0]
                    offset += 4
                if offset + size > len(data):
                    raise ValueError('HWP 본문 레코드가 손상되었습니다.')
                if tag == 67:
                    # 복합 제어문은 8개 UTF-16 단위이므로 통째로 건너뛴다.
                    units = struct.unpack('<' + 'H' * (size // 2), data[offset:offset + size])
                    chars, cursor = [], 0
                    while cursor < len(units):
                        code = units[cursor]
                        if code in (1, 2, 3, 11, 12, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23):
                            cursor += 8
                            continue
                        if code >= 32 or code in (9, 10, 13):
                            chars.append(code)
                        cursor += 1
                    paragraphs.append(struct.pack('<' + 'H' * len(chars), *chars).decode('utf-16-le', errors='replace'))
                offset += size
        return '\n'.join(paragraphs)


def load_documents(data_dir: Path) -> list[Document]:
    if not data_dir.is_dir():
        raise ValueError('문서 폴더를 찾지 못했습니다.')
    documents = []
    for path in sorted(data_dir.rglob('*')):
        if not path.is_file() or any(part.startswith('.') for part in path.relative_to(data_dir).parts):
            continue
        suffix = path.suffix.lower()
        metadata = {'source': path.relative_to(data_dir).as_posix()}
        if suffix in ('.txt', '.md'):
            text = path.read_text(encoding='utf-8-sig')
        elif suffix == '.csv':
            with path.open(encoding='utf-8-sig', newline='') as stream:
                text = '\n'.join(' | '.join(row) for row in csv.reader(stream))
        elif suffix == '.pdf':
            try:
                from pypdf import PdfReader
            except ImportError:
                raise ValueError('PDF를 읽으려면 pip install -e ".[documents]"를 실행하세요.') from None
            reader = PdfReader(path)
            for number, page in enumerate(reader.pages, 1):
                text = page.extract_text() or ''
                if text.strip():
                    documents.append(Document(metadata['source'] + f':p{number}', text,
                                              {**metadata, 'page': number}))
            if not any(doc.metadata.get('source') == metadata['source'] for doc in documents):
                raise ValueError(f'{path.name}: PDF에 추출 가능한 글이 없습니다. OCR은 미구현입니다.')
            continue
        elif suffix == '.hwp':
            text = _hwp_text(path)
        else:
            continue
        if not text.strip():
            raise ValueError(f'{path.name}: 추출한 본문이 비어 있습니다.')
        documents.append(Document(metadata['source'], text, metadata))
    if not documents:
        raise ValueError('문서가 없습니다. TXT·MD·CSV·PDF·HWP를 문서 폴더에 넣으세요.')
    return documents
