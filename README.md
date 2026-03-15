# Lemon TTS

Home Assistant용 커스텀 TTS(Text-to-Speech) 통합 구성요소입니다.
입력 텍스트는 언어에 상관없이 자동으로 일본어로 번역되어 일본어 음성으로 출력됩니다.

---

## 기능

- **자동 번역**: 한국어, 영어 등 어떤 언어로 입력해도 자동으로 일본어로 번역 후 TTS 생성
- **화자별 엔티티**: API에서 화자 목록을 자동 조회하여 각 화자마다 독립된 TTS 엔티티 생성
- **Assist 파이프라인 연동**: 파이프라인별로 다른 화자를 지정 가능 (A 어시스턴트 → Arona, B 어시스턴트 → Elaina)
- **전체 Mute**: HA 엔티티 하나로 모든 TTS 출력을 일괄 ON/OFF (자동화 수정 불필요)
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

| 항목 | 필수 | 설명 |
|---|---|---|
| **서버 주소** | ✅ | Lemon TTS API 서버의 base URL (예: `https://your-server.example.com`) |
| **API 키** | ✅ | Bearer 인증에 사용하는 API 키 |
| **Mute 엔티티** | ❌ | TTS ON/OFF를 제어할 엔티티 ID. 비워두면 항상 재생됩니다. (예: `input_boolean.tts_enabled`) |
| **Mute 활성화 상태** | ❌ | 위 엔티티의 상태값이 이 값일 때 TTS가 재생됩니다. (기본값: `on`) |

서버 주소와 API 키를 입력하면 화자 목록을 자동으로 불러오고, 각 화자마다 TTS 엔티티가 생성됩니다.

> **재설정**: 설정 → 기기 및 서비스 → Lemon TTS → 우측 메뉴 → **재설정** 에서 언제든 변경 가능합니다.

---

## 전체 Mute 기능

Mute 엔티티를 설정하면 해당 엔티티 상태에 따라 모든 TTS 출력을 일괄 제어할 수 있습니다.
기존 자동화를 수정할 필요 없이 컴포넌트 내부에서 처리됩니다.

### 설정 예시 (`input_boolean` 사용)

1. **헬퍼 생성**: 설정 → 기기 및 서비스 → 헬퍼 → `input_boolean` 생성 (예: entity_id `input_boolean.tts_enabled`)
2. **Lemon TTS 재설정**: Mute 엔티티에 `input_boolean.tts_enabled`, 활성화 상태에 `on` 입력
3. **대시보드에 토글 카드 추가** (선택)

### 동작 방식

| 상황 | 동작 |
|------|------|
| Mute 엔티티 미설정 | 항상 정상 재생 |
| 엔티티 상태 = 활성화 상태 | 정상 재생 |
| 엔티티 상태 ≠ 활성화 상태 | TTS 스킵 (API 호출 없음) |
| 엔티티가 HA에 존재하지 않음 | 정상 재생 (fail-open) |

### `input_boolean` 외 다른 엔티티 사용 예시

| 엔티티 종류 | entity_id 예시 | 활성화 상태값 |
|---|---|---|
| `input_boolean` | `input_boolean.tts_enabled` | `on` |
| `binary_sensor` | `binary_sensor.home_occupied` | `on` |
| `input_select` | `input_select.home_mode` | `홈` |
| `sensor` | `sensor.mode` | `active` |

---

## Assist 파이프라인 연동

각 화자가 독립된 TTS 엔티티로 생성되므로, Assist 파이프라인별로 다른 화자를 지정할 수 있습니다.

**설정 → 음성 어시스턴트 → 파이프라인 편집 → 텍스트 음성 변환(TTS)**

예시:
- `파이프라인 A` → `Lemon TTS Arona`
- `파이프라인 B` → `Lemon TTS Elaina`

---

## 사용법

### 자동화 / 스크립트에서 호출

```yaml
action: tts.speak
target:
  entity_id: tts.lemon_tts_arona
data:
  media_player_entity_id: media_player.your_speaker
  message: "안녕하세요, 오늘 날씨가 좋네요."
```

입력 텍스트는 한국어, 영어 등 어떤 언어든 자동으로 일본어로 번역됩니다.

### 옵션 파라미터 사용

```yaml
action: tts.speak
target:
  entity_id: tts.lemon_tts_arona
data:
  media_player_entity_id: media_player.your_speaker
  message: "오늘 날씨가 정말 좋아요!"
  options:
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
| `sdp_ratio` | float | `0.5` | SDP/DP 혼합 비율. `0`에 가까울수록 일정한 리듬, `1`에 가까울수록 자연스러운 리듬 변화. 추천: `0.3~0.7` |
| `noise` | float | `0.6` | 감정/표현 다양성. 낮을수록 단조롭고 안정적, 높을수록 감정이 풍부하지만 불안정해질 수 있음. 추천: `0.4~0.8` |
| `noisew` | float | `0.9` | 음소 길이 예측의 랜덤성. 낮을수록 기계적인 박자, 높을수록 자연스러운 불규칙 박자. 추천: `0.6~1.0` |
| `length` | float | `1.0` | 말하기 속도 배율. `1.0`이 기본 속도. `0.8` = 20% 빠르게, `1.2` = 20% 느리게. 추천: `0.8~1.3` |
| `style_text` | string | - | 스타일 참조 문장 (일본어). 이 문장의 감정/말투를 발화에 반영. 짧고 감정이 명확한 문장일수록 효과적 (예: `やった！すごい！`) |
| `style_weight` | float | `0` | `style_text` 스타일의 반영 비율. `0`이면 무시, 높을수록 원본 내용이 묻힐 수 있음. 추천: `0.2~0.4` |
| `translation_prompt` | string | - | 번역 시 적용할 어투/스타일 프롬프트. 번역 단계에만 영향 (예: `반말로 번역해줘`, `귀엽고 친근한 말투로`) |

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

**파라미터**: 위 옵션 파라미터 표 참고. `text`, `speaker_name`은 필수, 나머지는 선택.

---

## 요구 사항

- Home Assistant 2023.3 이상
- HACS (권장)
- Python 패키지: `httpx>=0.27.0` (자동 설치)
