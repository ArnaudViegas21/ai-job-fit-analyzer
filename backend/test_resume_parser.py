from resume_parser import parse_resume


def test_parse_txt_resume():
    text = parse_resume("resume.txt", b"Hello world\nSoftware Engineer")
    assert text == "Hello world\nSoftware Engineer"


def test_parse_resume_unsupported_file_type():
    try:
        parse_resume("resume.doc", b"unsupported")
    except ValueError as exc:
        assert "Unsupported file type" in str(exc)
    else:
        raise AssertionError("Expected ValueError for unsupported file type")
