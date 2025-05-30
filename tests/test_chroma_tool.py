import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from db import chroma_tool


def test_add_and_list_chroma():
    test_id = 999
    test_content = "ChromaDB 테스트용 문서"
    chroma_tool.add_document_to_chroma(test_id, test_content)
    client = chroma_tool.get_chroma()
    col = client.get_or_create_collection(chroma_tool.COLLECTION_NAME)
    docs = col.get(ids=[str(test_id)])
    assert docs["documents"] and docs["documents"][0] == test_content
    # 정리: 테스트 문서 삭제
    col.delete(ids=[str(test_id)])
    print("ChromaDB add/list 테스트 통과")


if __name__ == "__main__":
    test_add_and_list_chroma()
