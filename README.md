# Lemon TTS

Home Assistant용 커스텀 TTS(Text-to-Speech) 통합 구성요소입니다.
입력 텍스트는 언어에 상관없이 자동으로 일본어로 번역되어 일본어 음성으로 출력됩니다.

---

## 기능

- **자동 번역**: 한국어, 영어 등 어떤 언어로 입력해도 자동으로 일본어로 번역 후 TTS 생성
- **다양한 화자**: API에서 제공하는 화자 목록을 동적으로 조회하여 선택 가능
- **세밀한 음성 조절**: 리듬, 감정, 속도, 스타일 등 다양한 파라미터를 옵션으로 전달 가능
- **UI 기반 설정**: `configuration.yaml` 수정 없이 Home Assistant UI에서 바로 설정
- **HACS 지원**: HACS를 통해 간단하게 설치 및 업데이트 가능

---

## 설치

### HACS를 통한 설치 (권장)

1. HACS → 통합 구성요소 → 우측 상단 메뉴 → **사용자 지정 저장소 추가**
2. URL: `https://github.com/Lemon-HACS/lemon_tts`, 카테고리: `통합 구성요소`
3. **Lemon TTS** 검색 후 다운로드
4. Home Assistant 재시작

### 수동 설치

1. 이 저장소를 클론하거나 ZIP으로 다운로드
2. `custom_components/lemon_tts/` 폴더를 Home Assistant의 `config/custom_components/` 경로에 복사
3. Home Assistant 재시작

---

## 설정

설치 후 Home Assistant UI에서 설정합니다.

**설정 → 기기 및 서비스 → 통합 구성요소 추가 → Lemon TTS**

### 1단계: 서버 연결

| 항목 | 설명 |
|---|---|
| **서버 주소** | Lemon TTS API 서버의 base URL (예: `https://your-server.example.com`) |
| **API 키** | Bearer 인증에 사용하는 API 키 |

입력 후 서버에 연결을 시도하여 화자 목록을 불러옵니다. 연결에 실패하면 에러가 표시됩니다.

### 2단계: 기본 화자 선택

서버에서 받아온 화자 목록 중 기본으로 사용할 화자를 선택합니다.
기본값은 `Arona`입니다.

설정 완료 후 **옵션**에서 기본 화자를 변경할 수 있습니다.

---

## 사용법

### 자동화 / 스크립트에서 호출

```yaml
service: tts.speak
target:
  entity_id: tts.lemon_tts
data:
  media_player_entity_id: media_player.your_speaker
  message: "안녕하세요, 오늘 날씨가 좋네요."
```

입력 텍스트는 한국어, 영어 등 어떤 언어든 자동으로 일본어로 번역됩니다.

### 옵션 파라미터 사용

`options` 필드를 통해 음성 생성 방식을 세밀하게 조절할 수 있습니다.

```yaml
service: tts.speak
target:
  entity_id: tts.lemon_tts
data:
  media_player_entity_id: media_player.your_speaker
  message: "오늘 날씨가 정말 좋아요!"
  options:
    speaker_name: Elaina
    length: 0.9
    noise: 0.7
    style_text: "やった！すごい！"
    style_weight: 0.3
    translation_prompt: "반말로 번역해줘"
```

---

## 옵션 파라미터 상세

| 파라미터 | 타입 | 기본값 | 설명 |
|---|---|---|---|
| `speaker_name` | string | 설정한 기본 화자 | 사용할 화자 이름. `/api/tts/speakers`에서 조회한 목록 중 하나 |
| `sdp_ratio` | float | `0.5` | SDP/DP 혼합 비율. `0`에 가까울수록 일정한 리듬, `1`에 가까울수록 자연스러운 리듬 변화. 추천: `0.3~0.7` |
| `noise` | float | `0.6` | 감정/표현 다양성. 낮을수록 단조롭고 안정적, 높을수록 감정이 풍부하지만 불안정해질 수 있음. 추천: `0.4~0.8` |
| `noisew` | float | `0.9` | 음소 길이 예측의 랜덤성. 낮을수록 기계적인 박자, 높을수록 자연스러운 불규칙 박자. 추천: `0.6~1.0` |
| `length` | float | `1.0` | 말하기 속도 배율. `1.0`이 기본 속도. `0.8` = 20% 빠르게, `1.2` = 20% 느리게. 추천: `0.8~1.3` |
| `style_text` | string | - | 스타일 참조 문장 (일본어). 이 문장의 감정/말투를 발화에 반영. 짧고 감정이 명확한 문장일수록 효과적 (예: `やった！すごい！`) |
| `style_weight` | float | `0` | `style_text` 스타일의 반영 비율. `0`이면 무시, 높을수록 원본 내용이 묻힐 수 있음. 추천: `0.2~0.4` |
| `translation_prompt` | string | - | 번역 시 적용할 어투/스타일 프롬프트. TTS 음성 자체가 아닌 번역 단계에만 영향 (예: `반말로 번역해줘`, `귀엽고 친근한 말투로`) |

---

## API 구조

이 통합 구성요소는 다음 API 엔드포인트를 사용합니다.

### `GET /api/tts/speakers`
사용 가능한 화자 목록을 반환합니다. 설정 시 자동으로 호출됩니다.

```json
{
  "speakers": ["Arona", "Elaina"]
}
```

### `GET /api/tts`
TTS 음성을 생성하여 WAV 파일로 반환합니다.

**인증**: `Authorization: Bearer <api_key>`

**파라미터**: 위 옵션 파라미터 표 참고. `text`는 필수, 나머지는 선택.

---

## 요구 사항

- Home Assistant 2023.x 이상
- HACS (권장)
- Python 패키지: `httpx>=0.27.0` (자동 설치)
