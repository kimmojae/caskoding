# Caskoding

CaskaydiaMono Nerd Font와 D2Coding 한글을 하나로 합친 폰트입니다.

영문 폰트에 한글 폰트를 따로 붙여 쓰면 한글만 크게 보이거나 줄이 어긋나곤 합니다. Caskoding은 한글을 처음부터 같은 폰트 안에 넣어서, 영문과 한글의 크기와 간격이 잘 맞습니다. 영문, 숫자, 기호, Nerd Font 아이콘은 CaskaydiaMono 그대로입니다.

<!-- 스크린샷 자리 -->

## 원본

| 부분 | 원본 | 버전 |
|---|---|---|
| 영문, 기호, 아이콘 | [CaskaydiaMono Nerd Font Mono](https://github.com/ryanoasis/nerd-fonts) (Cascadia Mono 기반) | Nerd Fonts v3.5.1 |
| 한글 (완성형 11,172자, 호환 자모) | [D2Coding](https://github.com/naver/d2-coding-font) | 1.4.0 |

원본은 빌드할 때 공식 릴리스에서 내려받으며, 체크섬으로 확인합니다.

## 스타일

ExtraLight, Light, SemiLight, Regular, SemiBold, Bold와 각각의 Italic까지 12종입니다.
D2Coding은 Regular와 Bold만 있어서, SemiBold와 Bold에는 D2Coding Bold 한글을, 나머지에는 D2Coding Regular 한글을 씁니다. 이탤릭에서도 한글은 기울이지 않습니다.

## 설치 (macOS)

[uv](https://docs.astral.sh/uv/)가 필요합니다.

```sh
make install     # 원본 내려받기 → 빌드 → ~/Library/Fonts 에 복사
make uninstall   # ~/Library/Fonts/Caskoding-*.ttf 삭제
```

빌드만 하려면 `make fonts`를 실행합니다. 결과는 `fonts/`에 생깁니다.

## Ghostty 설정

```
font-family = "Caskoding"
```

설치하거나 다시 설치한 뒤에는 Ghostty를 완전히 종료하고 다시 실행해야 새 폰트를 인식합니다.

## 개발

```sh
make test
```

## 라이선스

[SIL Open Font License 1.1](LICENSE)입니다. 두 원본도 OFL이며, 원본 라이선스 전문은 [licenses/](licenses/)에 있습니다.

OFL은 원본의 예약 이름(Reserved Font Name)을 수정본에 쓰지 못하게 합니다. 이 폰트가 "Cascadia Code"나 "D2Coding"이 아니라 "Caskoding"이라는 이름을 쓰는 이유입니다.
