from agent import _extract_json


def test_extract_json_from_clean_json():
    assert _extract_json('{"match_score": 85, "strengths": ["Python"]}') == {
        "match_score": 85,
        "strengths": ["Python"],
    }


def test_extract_json_from_wrapped_text():
    text = "Analysis result:\n{\"match_score\": 70, \"matched_skills\": [\"AWS\"]}\nEnd"
    assert _extract_json(text) == {
        "match_score": 70,
        "matched_skills": ["AWS"],
    }
