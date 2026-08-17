## ディレクトリ配置規則

```
.agents/
  rules/          # プロジェクトルール
  skills/         # スキル
docs/
  prd/            # PRD（要件定義）。00 が全体定義、01〜 が領域別
  design/         # UIデザイン（.pen）と設計判断の記録
  plans/          # 実装プラン（plan-management スキルの規則に従う）
```

### docs/design の正

- `ui.pen` … **確定UI。仕様の正。**
- `ui-legacy.pen` `ui-selection.pen` `duolingo-*.pen` … 過去の検討。参照しない
- `*.md` … 設計判断の記録。`ui.pen` と矛盾する場合は `ui.pen` を優先する

### 実装コード

技術スタック未定のため、配置規則は選定後に定義する。
