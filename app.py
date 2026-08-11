from __future__ import annotations

import importlib
import json
import os
import uuid
from datetime import date

import streamlit as st

from marketing_mvp.capa_service import (DEFAULT_CAPA_SHEET_CSV_URL, GoogleSheetCapaService)
from marketing_mvp import copy_service as copy_service_module
from marketing_mvp import extractor as extractor_module
from marketing_mvp import integration_contract as contract_module
from marketing_mvp import home_display_insights as home_display_insights_module
from marketing_mvp import movie_ppv_insights as movie_ppv_insights_module
from marketing_mvp import ppm_insights as ppm_insights_module
from marketing_mvp import knowledge_contract as knowledge_contract_module
from marketing_mvp import models as models_module
from marketing_mvp import workflow as workflow_module
from marketing_mvp.repository import CampaignRepository

# Streamlit keeps imported modules in memory during hot reloads. Reload the
# frequently edited modules so a running development server picks up updates.
copy_service_module = importlib.reload(copy_service_module)
extractor_module = importlib.reload(extractor_module)
contract_module = importlib.reload(contract_module)
home_display_insights_module = importlib.reload(home_display_insights_module)
movie_ppv_insights_module = importlib.reload(movie_ppv_insights_module)
ppm_insights_module = importlib.reload(ppm_insights_module)
knowledge_contract_module = importlib.reload(knowledge_contract_module)
models_module = importlib.reload(models_module)
workflow_module = importlib.reload(workflow_module)
generate_copy = copy_service_module.generate_copy
copy_name_alternatives = copy_service_module.copy_name_alternatives
recommend_home_display = home_display_insights_module.recommend_home_display
assess_movie_copy = movie_ppv_insights_module.assess_movie_copy
assess_ppm_campaign = ppm_insights_module.assess_ppm_campaign
SLOT_CONTRACTS = knowledge_contract_module.SLOT_CONTRACTS
recommendation_to_assets = knowledge_contract_module.recommendation_to_assets
unresolved_issues = knowledge_contract_module.unresolved_issues
extract_fields = extractor_module.extract_fields
extract_reward_scheme = extractor_module.extract_reward_scheme
extract_reference_urls = extractor_module.extract_reference_urls
normalize_product_name = extractor_module.normalize_product_name
KNOWN_PPM_PRODUCTS = extractor_module.KNOWN_PPM_PRODUCTS
BANNER_SPECS = contract_module.BANNER_SPECS
OBSERVED_GNB_VALUES = contract_module.OBSERVED_GNB_VALUES
TEXT_SPEC_SOURCE = contract_module.TEXT_SPEC_SOURCE
empty_asset = contract_module.empty_asset
fit_banner_text = contract_module.fit_banner_text
make_mermaid = contract_module.make_mermaid
validate_asset = contract_module.validate_asset
validate_contract = contract_module.validate_contract
empty_campaign = models_module.empty_campaign
validate_basic_info = models_module.validate_basic_info
validate_planning_info = models_module.validate_planning_info
validate_for_confirmation = models_module.validate_for_confirmation
benefit_recommendation = workflow_module.benefit_recommendation
is_benefit_presence_response = workflow_module.is_benefit_presence_response
is_benefit_recommendation_request = workflow_module.is_benefit_recommendation_request
extract_copy_option_choice = workflow_module.extract_copy_option_choice
is_copy_generation_request = workflow_module.is_copy_generation_request
is_copy_revision_request = workflow_module.is_copy_revision_request
is_display_plan_request = workflow_module.is_display_plan_request
is_contextual_display_plan_request = workflow_module.is_contextual_display_plan_request
is_period_recommendation_request = workflow_module.is_period_recommendation_request
period_recommendation = workflow_module.period_recommendation
is_affirmative_response = workflow_module.is_affirmative_response
is_campaign_reset_request = workflow_module.is_campaign_reset_request
is_contextual_no_benefit_response = workflow_module.is_contextual_no_benefit_response
next_question = workflow_module.next_question
to_admin_payload = workflow_module.to_admin_payload
ADMIN_BASE_URL = os.getenv(
    "ADMIN_BASE_URL",
    "https://btvcuration.github.io/campaign/",
)


st.set_page_config(page_title="AX 마케팅 매니저", page_icon="🔷", layout="wide")
st.markdown(
    """
    <style>
    .block-container {max-width: 1500px; padding-top: 1.5rem;}
    [data-testid="stChatMessage"] {
        width: fit-content;
        max-width: 88%;
        min-width: 0;
        margin: .4rem 0;
        padding: .48rem .7rem;
        border: 0;
        border-radius: 16px;
        gap: .55rem;
        box-shadow: none;
    }
    [data-testid="stChatMessage"][aria-label="assistant message"] {
        background: #f3f5f8;
        border-top-left-radius: 5px;
    }
    [data-testid="stChatMessage"][aria-label="user message"] {
        margin-left: auto;
        background: #6d28d9;
        border-top-right-radius: 5px;
        flex-direction: row-reverse;
    }
    [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] p,
    [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] li {
        font-size: .84rem;
        line-height: 1.35;
    }
    [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] p {
        margin-bottom: .15rem;
    }
    [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] p:last-child {
        margin-bottom: 0;
    }
    [data-testid="stChatMessageAvatarUser"],
    [data-testid="stChatMessageAvatarAssistant"] {
        width: 1.75rem;
        height: 1.75rem;
        flex: 0 0 1.75rem;
    }
    [data-testid="stChatInput"] textarea {
        font-size: .86rem;
    }
    [data-testid="stChatMessage"][aria-label="user message"] [data-testid="stMarkdownContainer"] p,
    [data-testid="stChatMessage"][aria-label="user message"] [data-testid="stMarkdownContainer"] li {
        color: #ffffff;
    }
    [data-testid="stColumn"]:has([data-testid="stChatInput"]) {
        background: #ffffff;
        border: 1px solid #e5e7eb;
        border-radius: 20px;
        padding: 1rem 1rem .8rem;
        box-shadow: 0 12px 32px rgba(15, 23, 42, .10);
    }
    [data-testid="stChatInput"] {
        border: 1px solid #8b5cf6;
        border-radius: 12px;
        overflow: hidden;
    }
    [data-testid="stChatInputSubmitButton"] {
        color: #6d28d9;
    }
    .stApp {background: #f4f5f7;}
    div[data-testid="stMetric"] {background: #f7f8fb; padding: .8rem; border-radius: 12px;}
    .campaign-status-bar {
        display: flex;
        align-items: center;
        gap: .7rem;
        margin: .25rem 0 .65rem;
        padding: .58rem .75rem;
        background: #f7f8fb;
        border: 1px solid #e5e7eb;
        border-radius: 10px;
        color: #667085;
        font-size: .78rem;
    }
    .campaign-status-bar strong {
        color: #1f2937;
        font-weight: 600;
    }
    .campaign-status-bar .status-dot {color: #c4c9d2;}
    </style>
    """,
    unsafe_allow_html=True,
)

repo = CampaignRepository()
capa_service = GoogleSheetCapaService(
    os.getenv("CAPA_SHEET_CSV_URL", DEFAULT_CAPA_SHEET_CSV_URL)
)


def campaign_capacity_type(campaign: dict) -> str:
    reward_type = (campaign.get("reward_scheme") or {}).get("reward_type")
    exposure_method = campaign.get("exposure_method")
    needs_banner = exposure_method in {"팝업", "배너"}
    needs_coupon = reward_type == "COUPON"
    if needs_banner and needs_coupon:
        return "both"
    return "coupon" if needs_coupon else "banner"


def check_campaign_capa(campaign: dict) -> tuple[dict | None, str]:
    try:
        result = capa_service.check(
            campaign["start_date"],
            campaign["end_date"],
            int(campaign["target_capa"]),
            campaign_capacity_type(campaign),
        )
    except Exception as exc:
        campaign["capa_checked"] = False
        campaign["available_capa"] = None
        st.session_state.capa_result = None
        return None, f"실시간 Capa 조회에 실패했어요: {exc}"

    campaign["available_capa"] = result["available_capa"]
    campaign["capa_checked"] = True
    st.session_state.capa_result = result
    capacity_type = result.get("capacity_type")
    if capacity_type == "both":
        banner = result["minimum_banner_available"]
        coupon = result["minimum_coupon_available"]
        banner_status = "가능" if banner >= int(campaign["target_capa"]) else "부족"
        coupon_status = "가능" if coupon >= int(campaign["target_capa"]) else "부족"
        message = (
            f"Google Sheet 최신 데이터에서 {campaign['start_date']}~{campaign['end_date']} "
            f"일자별 슬롯을 확인했어요. 최저 배너 잔여 **{banner:,}**({banner_status}), "
            f"최저 쿠폰 잔여 **{coupon:,}**({coupon_status})입니다."
        )
    else:
        label = result.get("capacity_label", "잔여 슬롯")
        status = "진행 가능" if result["is_possible"] else f"{result['shortfall']:,} 부족"
        message = (
            f"Google Sheet 최신 데이터에서 {campaign['start_date']}~{campaign['end_date']} "
            f"일자별 슬롯을 확인했어요. 최저 {label}는 "
            f"**{result['available_capa']:,}**으로 **{status}**입니다."
        )
    if result.get("covered_days") != result.get("expected_days"):
        message += " 일부 일자의 데이터가 없어 운영 담당자 확인이 필요해요."
    return result, message

if "campaign" not in st.session_state:
    campaign = empty_campaign()
    campaign["campaign_id"] = f"CMP-{uuid.uuid4().hex[:8].upper()}"
    st.session_state.campaign = campaign
for key, default_value in empty_campaign().items():
    st.session_state.campaign.setdefault(key, default_value)

stored_product_name = st.session_state.campaign.get("product_name", "")
normalized_stored_product = normalize_product_name(stored_product_name)
if stored_product_name and normalized_stored_product != stored_product_name:
    if not normalized_stored_product:
        for message in reversed(st.session_state.get("messages", [])):
            if message.get("role") != "user":
                continue
            recovered = extract_fields(message.get("content", ""))
            if recovered.get("product_name"):
                normalized_stored_product = recovered["product_name"]
                if recovered.get("product_type"):
                    st.session_state.campaign["product_type"] = recovered["product_type"]
                if recovered.get("product_category"):
                    st.session_state.campaign["product_category"] = recovered["product_category"]
                break
    st.session_state.campaign["product_name"] = normalized_stored_product
    st.session_state.campaign["event_name"] = ""
    st.session_state.campaign["copy"] = ""
    st.session_state.campaign["exposure_areas"] = []
    st.session_state.campaign["assets"] = []
    st.session_state.campaign["mermaid_code"] = ""
    st.session_state.campaign["userflow_confirmed"] = False
    st.session_state.campaign["review_passed"] = False
    st.session_state.campaign["status"] = "DRAFT"
    st.session_state.pending_display_recommendation = None
    st.session_state.admin_payload = None
    repo.save(st.session_state.campaign)

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "안녕하세요. AX Manager입니다. 진행할 상품과 기간, MASS/TARGET, 혜택을 알려주세요.",
        }
    ]
if "admin_payload" not in st.session_state:
    st.session_state.admin_payload = None
if "capa_result" not in st.session_state:
    st.session_state.capa_result = None
if "pending_display_recommendation" not in st.session_state:
    st.session_state.pending_display_recommendation = None
if "pending_copy_names" not in st.session_state:
    st.session_state.pending_copy_names = []
if "redirect_to_admin" not in st.session_state:
    st.session_state.redirect_to_admin = False

# Older saved drafts could have been marked as basic-confirmed before event
# copy became a required field. Reopen those campaigns as drafts.
if (
    st.session_state.campaign.get("status") == "BASIC_CONFIRMED"
    and validate_basic_info(st.session_state.campaign)
):
    st.session_state.campaign["status"] = "DRAFT"


def save() -> None:
    repo.save(st.session_state.campaign)


def reset_campaign_state() -> None:
    campaign = empty_campaign()
    campaign["campaign_id"] = f"CMP-{uuid.uuid4().hex[:8].upper()}"
    st.session_state.campaign = campaign
    st.session_state.pending_display_recommendation = None
    st.session_state.pending_copy_names = []
    st.session_state.admin_payload = None
    st.session_state.capa_result = None
    st.session_state.redirect_to_admin = False
    st.session_state["selected_banner_types"] = []


def invalidate_confirmation() -> None:
    if st.session_state.campaign["status"] != "DRAFT":
        st.session_state.campaign["status"] = "DRAFT"
        st.session_state.admin_payload = None


BANNER_FIELD_LABELS = {
    "topText": "로고",
    "mainTitle": "메인 문구",
    "subText": "서브 문구",
    "previewTitle": "프리뷰 제목",
    "previewSub": "프리뷰 문구",
    "bannerCopy": "배너 문구",
    "mainCopy": "메인 문구",
    "subCopy": "서브 문구",
    "copy": "상단 문구",
    "subTitle": "하단 문구",
}


def format_display_proposal(recommendation: dict[str, object]) -> str:
    areas = recommendation.get("areas", [])
    area_lines = "\n".join(
        f"{index}. {area}"
        for index, area in enumerate(areas, start=1)
    )
    return (
        "전시 영역과 추천 배너를 제안했습니다.\n\n"
        f"**추천 전시 영역**\n{area_lines}\n\n"
        f"**권장 흐름**\n{recommendation.get('flow', '')}\n\n"
        f"**추천 이유**\n{recommendation.get('reason', '')}\n\n"
        "이 전시안으로 확정하면 각 영역 규격에 맞는 카피를 만들고 "
        "배너 필드와 Userflow를 자동으로 채웁니다."
    )


def format_banner_copy_result(
    assets: list[dict[str, object]],
    intro: str = "전시안을 확정하고 영역별 카피를 자동 적용했습니다.",
) -> str:
    sections = [intro]
    for asset in assets:
        banner_type = str(asset["type"])
        spec = BANNER_SPECS[banner_type]
        lines = [f"**{spec['label']}**"]
        data = asset["data"]
        for key, limit in spec.get("text_limits", {}).items():
            value = data.get(key, "")
            if value:
                label = BANNER_FIELD_LABELS.get(key, key)
                lines.append(f"- {label}: {value} ({len(value)}/{limit}자)")
        if len(lines) > 1:
            sections.append("\n".join(lines))
    sections.append("왼쪽 기획안에 카피와 Userflow가 채워졌습니다.")
    return "\n\n".join(sections)


def format_copy_name_options(options: list[str]) -> str:
    option_lines = "\n".join(
        f"{index}. **{option}**"
        for index, option in enumerate(options, start=1)
    )
    return (
        "카피명을 다른 방향으로 다시 제안할게요.\n\n"
        f"{option_lines}\n\n"
        "원하는 번호를 말씀해 주시면 모든 배너 문구에 맞춰 다시 적용할게요."
    )


def offer_copy_name_alternatives() -> tuple[bool, str]:
    campaign = st.session_state.campaign
    if not campaign.get("exposure_areas") or not campaign.get("assets"):
        return False, "먼저 전시안을 확정하면 카피명을 여러 방향으로 다시 제안할 수 있어요."
    options = copy_name_alternatives(campaign)
    st.session_state.pending_copy_names = options
    return True, format_copy_name_options(options)


def apply_copy_name_choice(choice: int) -> tuple[bool, str]:
    options = st.session_state.pending_copy_names
    if not options or not 0 <= choice < len(options):
        return False, "추천한 카피명 중 원하는 번호를 말씀해 주세요."
    campaign = st.session_state.campaign
    campaign["event_name"] = options[choice]
    assets = recommendation_to_assets(campaign["exposure_areas"], campaign)
    campaign["assets"] = assets
    campaign["mermaid_code"] = make_mermaid(assets)
    campaign["review_passed"] = False
    campaign["status"] = "BASIC_CONFIRMED"
    st.session_state["selected_banner_types"] = [
        asset["type"] for asset in assets
    ]
    st.session_state.pending_copy_names = []
    st.session_state.admin_payload = None
    save()
    return True, format_banner_copy_result(
        assets,
        intro="선택한 카피명으로 영역별 문구를 다시 적용했습니다.",
    )


def confirm_display_plan() -> tuple[bool, str]:
    recommendation = st.session_state.pending_display_recommendation
    if not recommendation:
        return False, "먼저 전시 영역과 추천 배너를 제안받아 주세요."
    campaign = st.session_state.campaign
    movie_policy = assess_movie_copy(campaign)
    if not movie_policy["ready"]:
        return False, movie_policy["message"]
    generated = generate_copy(campaign)
    campaign.update(generated)
    campaign["exposure_areas"] = recommendation["areas"]
    assets = recommendation_to_assets(recommendation["areas"], campaign)
    campaign["assets"] = assets
    campaign["mermaid_code"] = make_mermaid(assets)
    campaign["userflow_confirmed"] = True
    campaign["review_passed"] = False
    campaign["status"] = "BASIC_CONFIRMED"
    st.session_state["selected_banner_types"] = [
        asset["type"] for asset in assets
    ]
    st.session_state.pending_display_recommendation = None
    st.session_state.pending_copy_names = []
    st.session_state.admin_payload = None
    st.session_state.redirect_to_admin = True
    save()
    return True, format_banner_copy_result(assets)


if st.session_state.redirect_to_admin:
    st.session_state.redirect_to_admin = False
    target_url_json = json.dumps(ADMIN_BASE_URL)
    st.info("영역별 카피 적용이 완료되었습니다. 캠페인 제작 화면으로 이동합니다.")
    st.html(
        f"""
        <script>
          const targetUrl = {target_url_json};
          window.location.replace(targetUrl);
        </script>
        """,
        unsafe_allow_javascript=True,
    )
    st.link_button(
        "캠페인 제작 화면으로 이동",
        ADMIN_BASE_URL,
        type="primary",
        width="stretch",
    )
    st.stop()


st.title("🔷 AX 마케팅 매니저")
st.caption(f"캠페인 ID · {st.session_state.campaign['campaign_id']}")

state_col, chat_col = st.columns([1.2, 0.8], gap="large")

with chat_col:
    st.markdown("#### 🔷 AX Manager")
    st.caption("캠페인 기획 대화")
    with st.container(height=520, border=False):
        for message in st.session_state.messages:
            avatar = "assets/ax_manager.svg" if message["role"] == "assistant" else None
            with st.chat_message(message["role"], avatar=avatar):
                st.write(message["content"])
    prompt = st.chat_input("예: 군체 프로모션을 7/28~8/12 TARGET으로 진행해줘...")
    if prompt:
        if is_campaign_reset_request(prompt):
            reset_campaign_state()
            st.session_state.messages = [
                {
                    "role": "assistant",
                    "content": "이전 기획을 취소하고 새 프로모션 기획을 시작할게요. 진행할 상품을 알려주세요.",
                }
            ]
            save()
            st.rerun()
        st.session_state.messages.append({"role": "user", "content": prompt})
        previous_assistant = next(
            (
                message["content"]
                for message in reversed(st.session_state.messages[:-1])
                if message["role"] == "assistant"
            ),
            "",
        )
        reference_urls = extract_reference_urls(prompt)
        if reference_urls:
            existing_urls = st.session_state.campaign.get("reference_urls", [])
            st.session_state.campaign["reference_urls"] = list(
                dict.fromkeys(existing_urls + reference_urls)
            )
        benefit_recommendation_requested = is_benefit_recommendation_request(prompt)
        benefit_presence_only = is_benefit_presence_response(prompt)
        affirmative_requested = is_affirmative_response(prompt)
        period_recommendation_requested = is_period_recommendation_request(
            prompt,
            previous_assistant,
        )
        copy_revision_requested = is_copy_revision_request(prompt)
        copy_option_choice = extract_copy_option_choice(
            prompt,
            len(st.session_state.pending_copy_names),
        )
        display_plan_confirmation_requested = (
            affirmative_requested
            and st.session_state.pending_display_recommendation is not None
        )
        copy_generation_requested = is_copy_generation_request(prompt)
        display_recommendation_requested = is_contextual_display_plan_request(
            prompt,
            previous_assistant,
        )
        extracted = extract_fields(prompt)
        if is_contextual_no_benefit_response(prompt, previous_assistant):
            extracted["benefit"] = "혜택 없음"
            extracted["benefit_pending"] = False
        if benefit_presence_only:
            extracted.pop("benefit", None)
            extracted.pop("reward_scheme", None)
            extracted.pop("benefit_pending", None)
        if benefit_recommendation_requested:
            # A recommendation question can contain confirmed fields such as
            # MASS/TARGET. Keep those fields, but do not mistake the question
            # itself for a confirmed benefit.
            extracted.pop("benefit", None)
            extracted.pop("benefit_pending", None)
        if copy_option_choice is not None and st.session_state.pending_copy_names:
            _, reply = apply_copy_name_choice(copy_option_choice)
        elif display_plan_confirmation_requested:
            campaign = st.session_state.campaign
            if extracted:
                invalidate_confirmation()
                campaign.update(extracted)
            missing = validate_planning_info(campaign)
            if missing:
                reply = "전시안 확정 전 필요한 항목: " + ", ".join(missing)
            else:
                _, reply = confirm_display_plan()
        elif display_recommendation_requested:
            campaign = st.session_state.campaign
            if extracted:
                invalidate_confirmation()
                campaign.update(extracted)
            missing = validate_planning_info(campaign)
            if missing:
                reply = "전시 영역 추천 전 필요한 항목: " + ", ".join(missing)
            else:
                recommendation = recommend_home_display(campaign)
                st.session_state.pending_display_recommendation = recommendation
                reply = format_display_proposal(recommendation)
        elif benefit_presence_only:
            reply = (
                "좋아요. 어떤 혜택인가요? 할인, 쿠폰, 포인트백, 추첨 경품 중 "
                "편하게 말씀해 주세요."
            )
        elif period_recommendation_requested:
            reply = period_recommendation(st.session_state.campaign)
        elif copy_revision_requested:
            _, reply = offer_copy_name_alternatives()
        elif copy_generation_requested:
            if st.session_state.pending_display_recommendation:
                reply = (
                    "먼저 제안된 전시 영역과 추천 배너를 확정해 주세요. "
                    "확정하면 각 영역 규격에 맞는 카피를 자동 생성합니다."
                )
            elif not st.session_state.campaign.get("exposure_areas"):
                reply = (
                    "카피보다 먼저 전시 영역과 추천 배너를 정해야 합니다. "
                    "‘전시안 추천해줘’라고 말씀해 주세요."
                )
            else:
                reply = (
                    "확정된 배너 카피는 왼쪽 기획안에 적용되어 있습니다. "
                    "수정할 영역과 문구 방향을 말씀해 주세요."
                )
        elif extracted:
            invalidate_confirmation()
            campaign_before_update = dict(st.session_state.campaign)
            if any(key in extracted for key in ("start_date", "end_date", "target_capa", "audience_type")):
                st.session_state.campaign["capa_checked"] = False
                st.session_state.campaign["available_capa"] = None
                st.session_state.capa_result = None
            st.session_state.campaign.update(extracted)
            labels = {
                "product_name": "상품명", "product_category": "상품 유형",
                "product_type": "PPV/PPM",
                "start_date": "시작일", "end_date": "종료일",
                "audience_type": "방식", "benefit": "혜택", "target_capa": "목표 Capa",
                "schedule_pending": "일정 미정 상태",
                "benefit_pending": "혜택 미정 상태",
                "reward_scheme": "혜택 구조",
                "schedule_note": "일정 메모",
                "target_condition": "타겟 조건", "exposure_method": "노출 방식",
            }
            changed_keys = [
                key for key, value in extracted.items()
                if key not in ("schedule_pending", "benefit_pending") or value is True
            ]
            actual_changed_keys = [
                key
                for key in changed_keys
                if campaign_before_update.get(key) != extracted.get(key)
            ]
            has_schedule_input = any(
                key in extracted
                for key in ("start_date", "end_date", "schedule_pending", "schedule_note")
            )
            if has_schedule_input:
                start_value = st.session_state.campaign.get("start_date")
                end_value = st.session_state.campaign.get("end_date")
                schedule_note_value = st.session_state.campaign.get("schedule_note")
                if actual_changed_keys:
                    if start_value and end_value:
                        reply = f"일정을 {start_value}부터 {end_value}까지로 저장했습니다."
                    elif start_value:
                        reply = f"시작일을 {start_value}로 저장했습니다."
                    else:
                        reply = "일정을 미정 상태로 저장했습니다."
                    if schedule_note_value:
                        reply += f" 일정 메모도 반영했습니다: {schedule_note_value}"
                else:
                    reply = (
                        f"일정은 이미 {start_value}부터 {end_value}까지로 저장되어 있습니다. "
                        "변경할 내용이 있으면 말씀해 주세요."
                    )
                reply += f" {next_question(st.session_state.campaign)}"
            elif actual_changed_keys:
                changed = ", ".join(labels[key] for key in actual_changed_keys)
                if benefit_recommendation_requested:
                    reply = (
                        f"{changed} 내용을 기획안에 반영했어요.\n\n"
                        f"{benefit_recommendation(st.session_state.campaign)}"
                    )
                elif "product_name" in actual_changed_keys:
                    product_name = st.session_state.campaign["product_name"]
                    product_type = st.session_state.campaign.get("product_type") or "미정"
                    type_label = "PPM 월정액" if product_type == "PPM" else product_type
                    reply = (
                        f"상품명은 **{product_name}**, 유형은 **{type_label}**으로 저장했어요. "
                        f"{next_question(st.session_state.campaign)}"
                    )
                elif "audience_type" in actual_changed_keys:
                    reply = (
                        f"진행 방식은 **{st.session_state.campaign['audience_type']}**로 저장했어요. "
                        f"{next_question(st.session_state.campaign)}"
                    )
                elif "benefit" in actual_changed_keys:
                    reply = (
                        f"혜택은 **{st.session_state.campaign['benefit']}**으로 저장했어요. "
                        f"{next_question(st.session_state.campaign)}"
                    )
                else:
                    reply = (
                        f"{changed} 내용을 기획안에 반영했어요. "
                        f"{next_question(st.session_state.campaign)}"
                    )
            else:
                if benefit_recommendation_requested:
                    reply = benefit_recommendation(st.session_state.campaign)
                else:
                    reply = (
                        "말씀하신 내용은 현재 기획안에 이미 반영되어 있어요. "
                        f"{next_question(st.session_state.campaign)}"
                    )

            campaign = st.session_state.campaign
            if (
                set(actual_changed_keys)
                & {
                    "target_capa", "start_date", "end_date",
                    "benefit", "reward_scheme", "exposure_method",
                }
                and campaign.get("audience_type") == "TARGET"
                and campaign.get("start_date")
                and campaign.get("end_date")
            ):
                _, capa_message = check_campaign_capa(campaign)
                reply += f"\n\n{capa_message}"
        elif benefit_recommendation_requested:
            reply = benefit_recommendation(st.session_state.campaign)

        elif reference_urls:
            reply = (
                "참고 URL을 상태판에 저장했습니다. "
                "웹 검색 API 연결 후 작품 정보와 카피 생성 근거로 사용합니다."
            )
        elif affirmative_requested:
            reply = "좋아요. " + next_question(st.session_state.campaign)
        else:
            next_step = next_question(st.session_state.campaign)
            if next_step.startswith("기본 기획 정보가 준비되었습니다"):
                reply = (
                    "현재 기획 내용은 그대로 유지하고 있어요. "
                    "수정할 항목이나 원하는 작업을 조금 더 알려주세요."
                )
            else:
                reply = (
                    "말씀하신 내용은 확인했어요. 현재 기획 내용은 그대로 유지하고, "
                    f"다음 항목을 이어서 확인할게요. {next_step}"
                )
        st.session_state.messages.append({"role": "assistant", "content": reply})
        save()
        st.rerun()

    if st.session_state.pending_display_recommendation:
        st.caption("전시안 확인 대기 · 확정 후 영역별 카피가 생성됩니다.")
        if st.button(
            "전시안 확정 · 영역별 카피 만들기",
            type="primary",
            width="stretch",
            key="confirm_display_plan_chat",
        ):
            _, reply = confirm_display_plan()
            st.session_state.messages.append(
                {"role": "assistant", "content": reply}
            )
            st.rerun()

    st.caption("AI 지식·규격 정보")
    with st.expander("현재 AI 지식 연결 상태", expanded=False):
        st.markdown(
            """
            - ✅ 캠페인 상태판의 확정 정보
            - ✅ 영화 PPV 마케팅 인사이트 PDF — 카피 안전 기준에 연결
            - ✅ 방송 월정액 PPM·B tv+ 인사이트 — 상품 분류·전시·카피 기준에 연결
            - ✅ HOME_DISPLAY 핵심 전시 구좌 인사이트 PDF — 로컬 추천 로직에 연결
            - ⏳ 웹 검색·최신 작품 정보 — API 연결 전
            - ✅ B tv JSON·Mermaid 시스템 계약 — 로컬 검증기에 연결
            - ✅ Google Sheets 배너·텍스트 규격 — 배너별 글자 수 제한에 연결
            """
        )
    with st.expander("지식·시스템 규격 정리표", expanded=False):
        st.dataframe(
            SLOT_CONTRACTS,
            column_config={
                "knowledge_name": "지식문서 구좌명",
                "json_type": "JSON type",
                "settings": "고정 적용 규칙",
                "owner": "판단 근거",
                "status": "상태",
            },
            hide_index=True,
            width="stretch",
        )
        issues = unresolved_issues()
        if issues:
            st.warning(
                "확인 필요 항목은 시스템 계약 담당자 확인 전 자동 출력하지 않습니다."
            )
            for issue in issues:
                st.markdown(
                    f"**{issue['id']} · {issue['topic']}**  \n"
                    f"{issue['issue']}  \n"
                    f"임시 규칙: {issue['temporary_rule']}"
                )

with state_col:
    st.subheader("현재 캠페인")
    c = st.session_state.campaign

    st.caption("상품 정보")
    product_col, product_type_col, product_detail_col = st.columns([2.1, 0.9, 1.1])
    with product_type_col:
        product_type = st.selectbox(
            "상품 유형",
            ["", "PPV", "PPM"],
            index=["", "PPV", "PPM"].index(c.get("product_type", ""))
            if c.get("product_type", "") in ("", "PPV", "PPM") else 0,
            format_func=lambda value: {
                "": "선택",
                "PPV": "PPV · 단건",
                "PPM": "PPM · 월정액",
            }[value],
            help="대화에서 자동 분류되며 필요한 경우 바로잡을 수 있습니다.",
        )
    with product_col:
        if product_type == "PPM":
            ppm_product_options = [""] + KNOWN_PPM_PRODUCTS + ["기타"]
            current_product = c.get("product_name", "")
            current_ppm_option = (
                current_product
                if current_product in KNOWN_PPM_PRODUCTS
                else "기타" if current_product else ""
            )
            selected_ppm_product = st.selectbox(
                "월정액 상품명",
                ppm_product_options,
                index=ppm_product_options.index(current_ppm_option),
                format_func=lambda value: value or "선택",
            )
            if selected_ppm_product == "기타":
                product = st.text_input(
                    "상품명 직접 입력",
                    value=current_product if current_product not in KNOWN_PPM_PRODUCTS else "",
                )
            else:
                product = selected_ppm_product
        else:
            product_label = "콘텐츠명" if product_type == "PPV" else "상품명"
            product = st.text_input(product_label, value=c["product_name"])
    with product_detail_col:
        if product_type == "PPV":
            genre_options = ["", "영화", "TV 방송", "애니메이션", "키즈", "기타"]
            current_genre = c.get("product_category", "")
            product_category = st.selectbox(
                "장르",
                genre_options,
                index=genre_options.index(current_genre)
                if current_genre in genre_options else 0,
                format_func=lambda value: value or "선택",
            )
        elif product_type == "PPM":
            product_category = "B tv+" if product == "B tv+" else "방송 월정액"
            st.text_input("상품군", value=product_category, disabled=True)
        else:
            st.text_input("유형 상세", value="상품 유형 선택 후 표시", disabled=True)
            product_category = ""

    st.caption("일정 및 대상")
    start_col, end_col, pending_col = st.columns([1, 1, 0.55])
    with pending_col:
        schedule_pending = st.checkbox(
            "일정 미정",
            value=c.get("schedule_pending", False),
            help="미정 상태에서도 상품·타겟·배너 기획을 먼저 진행할 수 있습니다.",
        )
    with start_col:
        start = st.date_input(
            "시작일",
            value=date.fromisoformat(c["start_date"]) if c["start_date"] else None,
            disabled=schedule_pending,
        )
    with end_col:
        end = st.date_input(
            "종료일",
            value=date.fromisoformat(c["end_date"]) if c["end_date"] else None,
            disabled=schedule_pending,
        )

    audience_col, campaign_detail_col = st.columns([0.82, 3.43])
    with audience_col:
        audience = st.selectbox(
            "진행 방식",
            ["", "MASS", "TARGET"],
            index=["", "MASS", "TARGET"].index(c["audience_type"])
            if c["audience_type"] in ("MASS", "TARGET") else 0,
            format_func=lambda value: value or "선택",
        )
    with campaign_detail_col:
        if audience == "TARGET":
            capa_col, benefit_col, benefit_pending_col = st.columns(
                [1, 2.15, 0.58]
            )
            with capa_col:
                target_capa = st.number_input(
                    "목표 Capa",
                    min_value=0,
                    step=10_000,
                    value=int(c["target_capa"] or 0),
                )
        else:
            benefit_col, benefit_pending_col = st.columns([2.85, 0.58])
            target_capa = None
        with benefit_pending_col:
            benefit_pending = st.checkbox(
                "혜택 미정",
                value=c.get("benefit_pending", False),
                help="미정이어도 전시 구조를 먼저 기획할 수 있습니다.",
            )
        with benefit_col:
            benefit = st.text_input(
                "혜택",
                value=c["benefit"],
                disabled=benefit_pending,
                placeholder="예: 신규 가입 시 첫 달 50% 할인",
            )

    reward_scheme = c.get("reward_scheme") or {}
    if reward_scheme:
        reward_type_labels = {
            "DISCOUNT": "즉시 할인",
            "COUPON": "할인 쿠폰",
            "POINTBACK": "포인트·캐시백",
            "RAFFLE": "추첨 경품",
            "GIFT": "일반 증정",
        }
        timing_labels = {
            "BEFORE_PURCHASE": "구매 전",
            "INSTANT": "즉시 적용",
            "AFTER_PURCHASE": "구매 후",
            "UNSPECIFIED": "시점 미정",
        }
        st.caption(
            "리워드 구조 · "
            f"{reward_type_labels.get(reward_scheme.get('reward_type'), '기타')} · "
            f"{timing_labels.get(reward_scheme.get('timing'), '시점 미정')}"
        )

    copy_ready = bool(c.get("assets"))
    if copy_ready:
        st.caption("확정 카피")
        event_col, copy_col = st.columns([1, 2])
        with event_col:
            event_name = st.text_input("이벤트명", value=c["event_name"])
        with copy_col:
            copy_text = st.text_area(
                "이벤트 카피",
                value=c.get("copy", ""),
                height=76,
            )
    else:
        event_name = c.get("event_name", "")
        copy_text = c.get("copy", "")
        st.caption("전시안을 확정하면 이벤트명과 영역별 카피가 자동으로 채워집니다.")

    with st.expander("추가 설정 · 필요할 때만 입력", expanded=False):
        facts_label = "작품 공식 정보·줄거리" if product_type == "PPV" else "상품 참고 정보"
        work_facts = st.text_area(
            facts_label,
            value=c.get("work_facts", ""),
            height=78,
            placeholder="확인된 공식 정보와 카피 근거만 입력",
            help="입력된 공식 정보만 카피 근거로 사용합니다.",
        )
        note_col, reference_col = st.columns(2)
        with note_col:
            schedule_note = st.text_input(
                "일정 메모",
                value=c.get("schedule_note", ""),
                placeholder="예: 성과에 따라 기간 단축 검토",
            )
        with reference_col:
            reference_urls_text = st.text_area(
                "참고 URL",
                value="\n".join(c.get("reference_urls", [])),
                height=70,
                placeholder="공식 페이지·예고편·기사 URL",
            )
        target_col, assignee_col = st.columns([2, 1])
        with target_col:
            target_condition = st.text_input(
                "타겟 조건",
                value=c.get("target_condition", "") if audience == "TARGET" else "",
                disabled=audience != "TARGET",
            )
        with assignee_col:
            assignee = st.text_input("Jira 담당자", value=c.get("assignee", ""))
        coupon_col, coupon_benefit_col = st.columns([0.8, 2.2])
        with coupon_col:
            has_coupon = st.selectbox(
                "쿠폰 여부",
                ["N", "Y"],
                index=1 if c.get("has_coupon") == "Y" else 0,
            )
        with coupon_benefit_col:
            coupon_benefit = st.text_input(
                "쿠폰 혜택",
                value=c.get("coupon_benefit", ""),
                disabled=has_coupon != "Y",
            )

    edited = {
        "product_name": product,
        "product_type": product_type,
        "product_category": product_category,
        "work_facts": work_facts,
        "start_date": "" if schedule_pending else (start.isoformat() if start else ""),
        "end_date": "" if schedule_pending else (end.isoformat() if end else ""),
        "schedule_pending": schedule_pending,
        "schedule_note": schedule_note,
        "audience_type": audience,
        "benefit": "" if benefit_pending else benefit,
        "benefit_pending": benefit_pending,
        "reward_scheme": {} if benefit_pending else extract_reward_scheme(benefit),
        "target_capa": (target_capa or None) if audience == "TARGET" else None,
        "event_name": event_name,
        "copy": copy_text,
        "reference_urls": [
            url.strip()
            for url in reference_urls_text.splitlines()
            if url.strip()
        ],
        "target_condition": target_condition if audience == "TARGET" else "",
        "assignee": assignee,
        "has_coupon": has_coupon,
        "coupon_benefit": coupon_benefit if has_coupon == "Y" else "",
    }
    preview_campaign = dict(c)
    preview_campaign.update(edited)
    missing_planning_preview = validate_planning_info(preview_campaign)

    def apply_edited_campaign() -> None:
        planning_sensitive_keys = (
            "product_name", "work_facts", "start_date", "end_date",
            "product_type", "product_category",
            "audience_type", "benefit", "target_capa",
        )
        planning_sensitive = any(
            edited[key] != c.get(key)
            for key in planning_sensitive_keys
        )
        capa_sensitive = any(
            edited[key] != c.get(key)
            for key in ("start_date", "end_date", "audience_type", "target_capa")
        )
        invalidate_confirmation()
        c.update(edited)
        if planning_sensitive:
            st.session_state.pending_display_recommendation = None
            c["exposure_areas"] = []
            c["assets"] = []
            c["mermaid_code"] = ""
            c["userflow_confirmed"] = False
            c["review_passed"] = False
        if capa_sensitive:
            c["capa_checked"] = False
            c["available_capa"] = None
            st.session_state.capa_result = None

    status_label = {
        "DRAFT": "작성 중",
        "BASIC_CONFIRMED": "기본정보 확정",
        "CONFIRMED": "최종 확정",
    }.get(c["status"], c["status"])
    capa_status = (
        f"{c['available_capa']:,}명"
        if c.get("available_capa")
        else "미조회"
    )
    st.markdown(
        (
            '<div class="campaign-status-bar">'
            f'<span>상태 <strong>{status_label}</strong></span>'
            '<span class="status-dot">·</span>'
            f'<span>Capa <strong>{capa_status}</strong></span>'
            '<span class="status-dot">·</span>'
            f'<span>추천 배너 <strong>{len(c.get("assets", []))}개</strong></span>'
            "</div>"
        ),
        unsafe_allow_html=True,
    )

    save_col, plan_col = st.columns([0.72, 1.65])
    with save_col:
        save_draft = st.button("임시 저장", width="stretch")
    with plan_col:
        suggest_display = st.button(
            "전시 영역 제안받기 →",
            width="stretch",
            type="primary",
            disabled=bool(missing_planning_preview),
        )

    if save_draft:
        apply_edited_campaign()
        c["status"] = "DRAFT"
        save()
        st.success("작성 중인 내용을 임시 저장했습니다.")
        st.rerun()

    if missing_planning_preview:
        st.caption("전시안 제안 전 필요: " + ", ".join(missing_planning_preview))

    if suggest_display:
        apply_edited_campaign()
        if (
            c["audience_type"] == "TARGET"
            and c.get("start_date")
            and c.get("end_date")
            and c.get("target_capa")
        ):
            check_campaign_capa(c)
        recommendation = recommend_home_display(c)
        st.session_state.pending_display_recommendation = recommendation
        st.session_state.messages.append(
            {"role": "assistant", "content": format_display_proposal(recommendation)}
        )
        save()
        st.rerun()


st.divider()
st.subheader("Userflow 및 배너 에셋")
st.caption("배너 type과 data Key는 B tv 시스템 연동 계약에 따라 고정됩니다.")
st.markdown(
    f"텍스트 글자 수는 [B tv 배너 규격 Google Sheets]({TEXT_SPEC_SOURCE})를 적용합니다."
)

existing_by_type = {
    asset["type"]: asset
    for asset in st.session_state.campaign.get("assets", [])
}
selected_types = list(existing_by_type.keys())
if selected_types:
    st.success("확정한 전시안의 배너와 카피가 자동으로 적용되었습니다.")
    st.markdown(
        " → ".join(BANNER_SPECS[banner_type]["label"] for banner_type in selected_types)
    )
    st.caption("운영값을 바꾸려면 아래 배너별 직접 수정 영역을 펼쳐 주세요.")
else:
    st.info("채팅에서 전시안을 확정하면 추천 배너, 카피, Userflow가 여기에 자동으로 채워집니다.")
draft_assets = []
for banner_index, banner_type in enumerate(selected_types):
    asset = existing_by_type.get(banner_type, empty_asset(banner_type))
    spec = BANNER_SPECS[banner_type]
    with st.expander(f"직접 수정 · {banner_index + 1}. {spec['label']}", expanded=False):
        asset_name = st.text_input(
            "name",
            value=asset["name"],
            key=f"asset_name_{banner_type}",
        )
        asset_data = {}
        for key in spec["keys"]:
            widget_key = f"asset_{banner_type}_{key}"
            if key == "gnb":
                if spec.get("fixed_gnb"):
                    st.text_input(
                        "gnb (고정)",
                        value=", ".join(spec["fixed_gnb"]),
                        disabled=True,
                        key=f"{widget_key}_fixed",
                    )
                    asset_data[key] = list(spec["fixed_gnb"])
                else:
                    asset_data[key] = st.multiselect(
                        "gnb",
                        OBSERVED_GNB_VALUES,
                        default=[value for value in asset["data"].get(key, []) if value in OBSERVED_GNB_VALUES],
                        key=widget_key,
                    )
            elif key in spec.get("enums", {}):
                values = spec["enums"][key]
                current = asset["data"].get(key)
                asset_data[key] = st.selectbox(
                    key,
                    values,
                    index=values.index(current) if current in values else 0,
                    key=widget_key,
                )
            else:
                text_limit = spec.get("text_limits", {}).get(key)
                current_value = asset["data"].get(key, "")
                if text_limit and len(current_value) > text_limit:
                    st.warning(
                        f"{key} 기존 값이 최대 {text_limit}자를 초과해 "
                        "규격에 맞게 줄여 표시합니다."
                    )
                    current_value = fit_banner_text(
                        banner_type,
                        key,
                        current_value,
                    )
                asset_data[key] = st.text_input(
                    f"{key} · 최대 {text_limit}자" if text_limit else key,
                    value=current_value,
                    max_chars=text_limit,
                    help=(
                        f"Google Sheets 배너 규격 기준 최대 {text_limit}자"
                        if text_limit
                        else None
                    ),
                    key=widget_key,
                )
        draft_assets.append({"name": asset_name, "type": banner_type, "data": asset_data})

if selected_types and st.button(
    "운영값 수정 내용 적용",
    width="stretch",
    key="apply_asset_edits",
):
    invalidate_confirmation()
    st.session_state.campaign["assets"] = draft_assets
    st.session_state.campaign["mermaid_code"] = make_mermaid(draft_assets)
    st.session_state.campaign["userflow_confirmed"] = True
    st.session_state.campaign["review_passed"] = False
    save()
    st.success("수정 내용과 Userflow를 함께 적용했습니다.")
    st.rerun()

if st.session_state.campaign.get("mermaid_code"):
    with st.expander("확정 대상 Mermaid 코드", expanded=False):
        st.code(st.session_state.campaign["mermaid_code"], language="mermaid")

st.divider()
display_recommendation = recommend_home_display(st.session_state.campaign)
with st.expander("홈 전시 구좌 추천 · 인사이트 근거", expanded=False):
    st.markdown(
        f"""
        **추천 구좌:** {' · '.join(display_recommendation['areas'])}

        **권장 흐름:** {display_recommendation['flow']}

        **추천 이유:** {display_recommendation['reason']}

        **카피 방향:** {display_recommendation['copy_guidance']}

        **출처:** {display_recommendation['source']}

        **주의:** {display_recommendation['caution']}
        """
    )

movie_copy_policy = assess_movie_copy(st.session_state.campaign)
if movie_copy_policy["applies"]:
    with st.expander("영화 PPV 카피 인사이트 적용 상태", expanded=False):
        readiness = "카피 작성 가능" if movie_copy_policy["ready"] else "공식 작품 정보 필요"
        st.markdown(
            f"""
            **상태:** {readiness}

            **적용 방향:** {movie_copy_policy['guidance']}

            **출처:** [{movie_copy_policy['source']}]({movie_ppv_insights_module.SOURCE_URL})
            """
        )

ppm_policy = assess_ppm_campaign(st.session_state.campaign)
if ppm_policy["applies"]:
    with st.expander("PPM 월정액 지식 적용 상태", expanded=False):
        source_lines = "\n".join(
            f"- [{name}]({url})" for name, url in ppm_policy["sources"]
        )
        recommendation = ppm_policy["recommendation"] or "현재 확정 정보 범위에서 별도 일정·타겟 조정 제안은 없습니다."
        operations_name, operations_url = ppm_policy["operations_source"]
        st.markdown(
            f"""
            **적용 트랙:** {ppm_policy['track']}

            **카피·기획 방향:** {ppm_policy['guidance']}

            **조건별 제안:** {recommendation}

            **출처:**
            {source_lines}

            **운영 데이터:** [{operations_name}]({operations_url}) — 실시간 API 조회 전

            **주의:** {ppm_policy['caution']}
            """
        )
st.subheader("다음 단계")
current_campaign = st.session_state.campaign

if not current_campaign.get("assets"):
    if st.session_state.pending_display_recommendation:
        st.info("채팅에서 추천 전시안을 확인하고 확정해 주세요.")
    else:
        st.info("캠페인 정보를 입력한 뒤 ‘전시 영역·추천 배너 제안’을 진행해 주세요.")
elif not current_campaign.get("review_passed"):
    st.caption("영역별 카피와 Userflow가 자동 적용되었습니다. 규격 검사를 진행합니다.")
    if st.button(
        "기획안 검수 완료",
        width="stretch",
        type="primary",
        key="review_plan",
    ):
        errors = []
        for asset in current_campaign.get("assets", []):
            errors.extend(validate_asset(asset))
        if not current_campaign.get("userflow_confirmed"):
            errors.append("Userflow가 생성되지 않았습니다.")
        if errors:
            st.error("\n".join(errors))
        else:
            current_campaign["review_passed"] = True
            save()
            st.success("카피·배너 규격과 Userflow 검수를 통과했습니다.")
            st.rerun()
elif not st.session_state.admin_payload:
    if st.button(
        "최종 확정 · JSON 생성",
        width="stretch",
        type="primary",
        key="finalize_plan",
    ):
        missing = validate_for_confirmation(current_campaign)
        if missing:
            st.error("최종 출력 전 필요한 항목: " + ", ".join(missing))
        else:
            payload = to_admin_payload(current_campaign)
            errors = validate_contract(payload)
            if errors:
                st.error("시스템 연동 규격 불일치:\n" + "\n".join(errors))
            else:
                current_campaign["status"] = "CONFIRMED"
                st.session_state.admin_payload = payload
                save()
                st.rerun()
else:
    output_col, admin_col = st.columns(2)
    payload = st.session_state.admin_payload
    with output_col:
        st.download_button(
            "JSON 다운로드",
            json.dumps(payload, ensure_ascii=False, indent=2),
            file_name=f"{current_campaign['campaign_id']}.json",
            mime="application/json",
            width="stretch",
        )
    with admin_col:
        st.link_button("B tv 어드민 이동", ADMIN_BASE_URL, width="stretch")
if st.session_state.capa_result:
    result = st.session_state.capa_result
    if result["is_possible"]:
        st.success(f"현재 일정에서 목표 Capa를 충족합니다. 가능 Capa: {result['available_capa']:,}명")
    else:
        st.warning(
            f"현재 일정은 {result['shortfall']:,}명이 부족합니다. "
            f"가능 Capa: {result['available_capa']:,}명"
        )
        if result["alternatives"]:
            st.write("대안 일정")
            st.dataframe(result["alternatives"], width="stretch", hide_index=True)

if st.session_state.admin_payload:
    st.json(st.session_state.admin_payload)
