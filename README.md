# Caskoding

CaskaydiaMono Nerd Font와 D2Coding 한글을 하나로 합치고, 둘 다 없는 기호는 JuliaMono에서 채운 폰트입니다.

영문 폰트에 한글 폰트를 따로 붙여 쓰면 한글만 크게 보이거나 줄이 어긋나곤 합니다. Caskoding은 한글을 처음부터 같은 폰트 안에 넣어서, 영문과 한글의 크기와 간격이 잘 맞습니다. 영문, 숫자, 기호, Nerd Font 아이콘은 CaskaydiaMono 그대로입니다.

<!-- 스크린샷 자리 -->

## 원본

| 부분 | 원본 | 버전 |
|---|---|---|
| 영문, 기호, 아이콘 | [CaskaydiaMono Nerd Font Mono](https://github.com/ryanoasis/nerd-fonts) (Cascadia Mono 기반) | Nerd Fonts v3.5.1 |
| 그 밖의 한 칸 기호 (`⎿ ⏺ ✔ ⚠ ①`, 화살표, 수학 기호 등) | [JuliaMono](https://github.com/cormullion/juliamono) | 0.63.2 |
| 한글 (완성형 11,172자, 호환 자모), 한자, CJK 문장부호 | [D2Coding](https://github.com/naver/d2-coding-font) | 1.4.0 |

글자는 CaskaydiaMono → JuliaMono → D2Coding 순서로 찾습니다. 앞 폰트에 있으면 그 글자를 쓰고, 없을 때만 다음 폰트에서 채웁니다.

- JuliaMono는 터미널에서 한 칸을 차지하는 글자만 채웁니다. Cascadia와 같은 고정폭 산세리프이고, 각 스타일에 가까운 굵기를 씁니다.
- D2Coding은 두 칸을 차지하는 글자(한글, 한자 등)와 남은 글자를 채웁니다. D2Coding이 두 칸으로 그리는데 터미널은 한 칸으로 다루는 글자는 옆 글자와 겹치므로 D2Coding에서 가져오지 않습니다.
- 이모지는 넣지 않습니다. 터미널이 컬러 이모지 폰트로 그립니다.

원본은 빌드할 때 공식 릴리스에서 내려받으며, 체크섬으로 확인합니다.

## 스타일

Regular, Bold, Italic, BoldItalic 4종입니다. 터미널과 에디터가 쓰는 조합이 이 4개이고, D2Coding도 Regular와 Bold만 있어서 굵기를 더 나눠도 한글 굵기는 따라오지 않습니다. 이탤릭에서도 한글은 기울이지 않습니다.

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

[SIL Open Font License 1.1](LICENSE)입니다. 세 원본도 모두 OFL이며, 원본 라이선스 전문은 [licenses/](licenses/)에 있습니다.

OFL은 원본의 예약 이름(Reserved Font Name)을 수정본에 쓰지 못하게 합니다. 이 폰트가 "Cascadia Code"나 "D2Coding", "JuliaMono"가 아니라 "Caskoding"이라는 이름을 쓰는 이유입니다.
