from app.schemas.sign_schemas import SignOptions
from app.services.embedding_plan import build_embedding_plan


def test_sign_options_supports_embedding_plan_flag() -> None:
    default_options = SignOptions()
    assert default_options.return_embedding_plan is False

    enabled_options = SignOptions(return_embedding_plan=True)
    assert enabled_options.return_embedding_plan is True


def test_build_embedding_plan_returns_codepoint_operations() -> None:
    visible_text = "abc"
    signed_text = "a\ufe00b\U000e0100c"

    plan = build_embedding_plan(visible_text=visible_text, signed_text=signed_text)

    assert plan is not None
    assert plan.index_unit == "codepoint"
    assert plan.operations[0].insert_after_index == 0
    assert plan.operations[0].marker == "\ufe00"
    assert plan.operations[1].insert_after_index == 1
    assert plan.operations[1].marker == "\U000e0100"
