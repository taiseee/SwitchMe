# 日本の習慣改善・自己管理系アプリ 広告出稿の実地横断調査（2026-08-09）

対象範囲: SwitchMe（GPS・カメラ・マイクによるセンサー自動検証×実金銭・自己完結型ペナルティの習慣改善アプリ、個人開発、日本市場想定）の広告出稿検討にあたり、これまで海外アプリ（Duolingo・stickK・Beeminder・Forfeit等）とあすけん・みんチャレ・メザミー・Alarmyの4社に限られていた実地調査を、**日本の同系統アプリに広げ、実際にどの広告透明性ツールで広告実物・広告主を確認できたか（できなかったか）を横断的に記録する**。競合のMECE分析は [2026-08-08-habit-app-market-research.md](./2026-08-08-habit-app-market-research.md)、広告チャネル・クリエイティブの詳細は [2026-08-09-habit-app-ad-channels-and-creative.md](./2026-08-09-habit-app-ad-channels-and-creative.md)、メディア別の仕様・費用感は [2026-08-09-habit-app-ad-media-channel-breakdown.md](./2026-08-09-habit-app-ad-media-channel-breakdown.md) を参照。

---

## 0. 要約

- **今回新たに実地確認した12アプリ（Studyplus・シューカン・GoalSpace・SIZLY・スーパーアラーム・OWN.・FiNC・カロミル・dot fit・RIZAP関連・Simple Habit・継続する技術・HabitKit）のうち、Meta Ad Library・Google Ads Transparency Center・TikTok Creative Centerのいずれでも「そのアプリ自身の広告」が確認できたのはFiNCのみだった。** ただしFiNCの広告は、コンシューマー向け習慣化・ダイエットアプリとしてのFiNCではなく、**法人向け健康経営SaaS事業（biz.finc.com）へ完全に軸足を移した後の広告**であり、性質が大きく異なる（3.6節）。
- **罰金・コミットメント型の国内4社（シューカン・GoalSpace・SIZLY・スーパーアラーム）は、Meta・Googleのいずれでも広告が1件も確認できなかった。** 前回調査のstickK・Beeminder・Forfeit・メザミー・みんチャレと合わせると、**日本・海外を問わず罰金・コミットメント型アプリはMeta広告ライブラリ／Google広告透明性センターに広告実績が見当たらないという傾向が、今回さらに4社分裏付けられた**。
- **FiNC Technologiesは2019年に女優・中村アンを起用した全国テレビCMを実施した実績が公式プレスリリースで確認できる一方、2026年8月時点でのGoogle広告は法人向け健康経営SaaS（グッピーヘルスケア／biz.finc.com）の検索広告4件のみで、コンシューマー向けアプリの広告は確認できなかった。** 累計資金調達額は150億円強（2020年時点、TechCrunch報道）に達したが、売上原価が売上を上回る厳しい経営状況だったとの報道もあり、**「大型調達→マス広告→事業転換」という一連の流れが広告出稿の変遷から読み取れる**ことが今回の新しい発見。
- **RIZAPグループは、習慣化アプリ単体ではなく実店舗事業（chocoZAP・RIZAP English・RIZAP GOLF等）でMeta広告を極めて活発に出稿していた（検索結果260件以上、8月時点ですべてアクティブ）。** 資金力のある企業ほど広告投資規模が大きいという前回調査の傾向が、フィットネス系の実店舗ビジネスモデルでも再確認できた（3.9節）。
- **TikTok Creative Center（日本・Health & Fitnessカテゴリ、直近180日）のトップ広告上位4件、Educationカテゴリ上位4件のいずれにも、今回の調査対象アプリは1件も含まれていなかった。** 上位に出てくるのは海外の学習AIアプリ（Gauth、Learna AI）や韓国の美容クリニックで、国内の習慣改善系アプリはTikTokの上位広告枠に食い込めていない（3.10節）。
- dot fit・Simple Habit・継続する技術・HabitKit・カロミル・Studyplusは、いずれの媒体でも広告実物・広告主ページを確認できなかった（**広告0件、または対象アプリと同定できる広告主が見当たらず**）。Studyplusは逆に「Studyplus Ads」という**自社が広告枠を販売する側**のビジネスを展開していることが分かった（3.1節）。

---

## 1. 調査方法と出典の信頼性について

前回2回の調査と同じ4段階区分を踏襲する。

| 表記 | 意味 |
|---|---|
| **広告実物を確認** | Meta Ad Library・Google Ads Transparency Center・TikTok Creative Center等の広告透明性ツールで、広告・コピーそのものを直接取得したもの |
| **一次発信** | 公式プレスリリース（PR TIMES等）・IR資料・公式ブログ・公式ヘルプセンターなど、当事者企業が自ら説明したもの |
| **二次（マーケ事例記事・報道）** | 第三者の業界メディア・ニュースサイト・個人ブログが紹介・分析したもの |
| **不明** | 今回の調査で確認できなかった、またはアクセス制約により検証できなかった |

広告が「0件」だった場合も、前回2回の調査同様、それ自体を重要な結果として明記する。なお、Meta・Google双方の検索エンジンは英字・カタカナの短い単語に対して**意味的に緩いマッチング（あいまい検索）を行う**ことを本調査で確認した（例：「Studyplus」で検索すると無関係な「Study Gateway」という海外ブランドがヒットする）。そのため各表では「検索結果件数」と「そのうち対象アプリ自身の広告と確認できた件数」を分けて記載する。

### 1.1 実地調査の対象と手法

- **Meta Ad Library**（[facebook.com/ads/library](https://www.facebook.com/ads/library/)、地域=日本、フレーズ完全一致検索）：12アプリすべてで検索を実施。
- **Google Ads Transparency Center**（[adstransparency.google.com](https://adstransparency.google.com/)、地域=日本、広告主オートコンプリート検索）：Studyplus・シューカン・GoalSpace・SIZLY・スーパーアラーム・OWN.・FiNC・カロミル・dot fitの9アプリで検索を実施（優先度の高い罰金型・フィットネス系を中心）。
- **TikTok Creative Center Top Ads Dashboard**（[ads.tiktok.com/business/creativecenter/inspiration/topads](https://ads.tiktok.com/business/creativecenter/inspiration/topads/pc/en)、地域=Japan、業種＝Health & Fitness／Education、期間＝直近180日）：業種別の上位広告一覧を確認し、対象アプリの有無を確認。この検索インターフェースは広告主名でのフリーテキスト絞り込みには対応しておらず、前回調査と同様に業種カテゴリでの一覧確認にとどめた。
- 加えて各社の公式プレスリリース（PR TIMES等）・ニュース記事でTVCM・資金調達等のマス施策実績をWeb検索で確認した。

---

## 2. 一覧表：どの媒体で広告を確認できたか

| アプリ／会社 | 分類 | Meta Ad Library | Google Ads Transparency Center | TikTok Creative Center | TVCM等マス広告の実績 |
|---|---|---|---|---|---|
| Studyplus | 学習記録 | 0件（無関係な「Study Gateway」がヒット） | 0件（advertiser候補なし） | Educationカテゴリ上位に該当なし | 確認できず（自社は逆に広告枠販売事業「Studyplus Ads」を運営、1.1節参照） |
| シューカン（株式会社メカニズム） | 罰金型 | 0件（無関係な韓流ドラマ広告2件のみ） | 0件（advertiser候補なし） | 未実施（罰金型優先で個別未検索） | 確認できず |
| GoalSpace（合同会社NoCodeCamp） | 罰金・ステーク型 | 0件（該当なし） | 0件（advertiser候補なし） | 未実施 | 確認できず |
| SIZLY／シズリー（アイザック株式会社） | 罰金型 | 0件（該当なし） | 0件（advertiser候補なし） | 未実施 | 確認できず |
| スーパーアラーム | ミッション式アラーム | 0件（無関係な睡眠アプリ「リナイト」がヒット） | 0件（advertiser候補なし） | 未実施 | 確認できず |
| OWN.（東京通信グループ） | フィットネス | 検索語が一般語のため検索不能（3.5節） | advertiser候補なし（類似の「Owned株式会社」等は無関係） | Health & Fitness上位4件に該当なし | 具体的なTVCM実施情報は確認できず |
| **FiNC（FiNC Technologies）** | 健康管理（→B2B転換） | **広告主「FiNC」名義で3件確認、ただしKirin商品のアフィリエイト広告** | **広告主「株式会社FiNC Technologies」名義で4件確認、すべて法人向け健康経営SaaS** | Health & Fitness上位4件に該当なし | **2019年に女優・中村アン起用の全国TVCM（一次発信で確認済み）** |
| カロミル | 食事管理 | 0件（該当なし） | Google未検索（時間の都合で罰金型・フィットネス系を優先） | 未実施 | 確認できず |
| dot fit | フィットネス | 0件（無関係なアパレル広告1件のみ） | advertiser候補なし（類似の「dot. FITNESS CLUB」は別の店舗ブランド） | 未実施 | 「dot fit」という名称のアプリの実在自体を確認できず |
| RIZAP系（chocoZAP／RIZAP English／RIZAP GOLF等） | フィットネス（実店舗） | **260件以上、すべてアクティブ（3.9節）** | 未検索 | 未検索 | RIZAPグループとして広範なテレビCM実績が既に広く知られている（本調査では未検証） |
| Simple Habit | 習慣トラッカー | 0件（無関係な「Bible Offline」等の海外聖書アプリがヒット） | 未検索 | 未実施 | 確認できず |
| 継続する技術 | 習慣トラッカー | 0件（該当なし） | 未検索 | 未実施 | 確認できず |
| HabitKit | 習慣トラッカー | 0件（該当なし） | 未検索 | 未実施 | 確認できず |

※「0件」はMeta/Google双方とも、キーワードに一致する広告・広告主がライブラリ上に見当たらなかったことを指す（前回調査と同じ基準）。あいまい検索でヒットした無関係な広告は括弧内に付記した。

---

## 3. アプリ別の詳細

### 3.1 Studyplus（学習記録SNS）

Meta Ad Library・Google Ads Transparency Centerとも「Studyplus」自身の広告・広告主は確認できなかった（広告実物を確認、0件）。Meta側の検索では、あいまいマッチにより「Study Gateway」という無関係な米国の聖書学習ブランドの広告がヒットした。TikTok Creative CenterのEducationカテゴリ上位（日本・直近180日）4件にもStudyplusは含まれておらず、上位に出てきたのは海外の学習AIアプリ「Gauth: AI Study Companion」「Learna AI: French Learning App」だった（広告実物を確認）。

一方、**Studyplus自身は逆に「広告枠を売る側」のビジネス（Studyplus Ads）を運営している**ことが公式サイトで確認できた（一次発信、[ads.studyplus.co.jp](https://ads.studyplus.co.jp/)）。中高生・大学生向けにアプリ内の静止画・動画広告、DM型広告等を販売しており、価格は静止画・動画で40万円〜、DM型・DSP/SNS型で50万円〜とされる。累計会員数は2025年6月時点で1,000万人を突破し、教育カテゴリで月間利用率No.1としている（一次発信に準ずる、media-radar.jp・info.studyplus.co.jp）。**自社アプリの広告出稿より先に、広告収益事業（Studyplus Ads）を確立している**という点は、他の家計簿・習慣化アプリとは異なる収益構造として留意すべき事実である。

### 3.2 シューカン（株式会社メカニズム）

Meta Ad Libraryで「シューカン」を完全一致フレーズ検索したところ0件（広告実物を確認）、あいまいマッチにより無関係な韓流ドラマ配信サービス「Dramas For U」の広告2件がヒットしたのみだった。Google Ads Transparency Centerでも「シューカン」に一致する広告主・ウェブサイト候補はオートコンプリートに一切表示されず（広告実物を確認、0件）。

公式には2022年1月11日、PR TIMESで「日本初！習慣化しないと課金される三日坊主防止アプリ『シューカン』を公開」というプレスリリースを配信している（一次発信、[prtimes.jp](https://prtimes.jp/main/html/rd/p/000000003.000067260.html)）。1日100円以上の自己設定額を課金する仕組みで、最低14日間は解約できない設計とされる。TVCM等のマス広告実施情報は今回の調査範囲では見つからなかった（**不明**）。

### 3.3 GoalSpace（合同会社NoCodeCamp）

Meta Ad Libraryで「GoalSpace」を検索したところ0件で、あいまいマッチによる無関係な広告も表示されなかった（広告実物を確認）。Google Ads Transparency Centerでも広告主候補は見つからなかった（広告実物を確認、0件）。

公式には2023年9月18日付でアプリがリニューアルされたというプレスリリースが確認できる（一次発信に準ずる、value-press.com経由のNoCodeCampプレスリリース）。「モチベーションに頼らない目標達成支援アプリ」を謳い、目標達成に向けて自分にとって重要なものを「ステーク（賭ける）」する仕組みが特徴とされる。なお運営元のNoCodeCampは2025年3月、株式会社Biz Freakへ持分譲渡（事業譲渡）されたことがプレスリリースで確認できる（一次発信、jiji.com・livedoor news経由）。事業譲渡後にGoalSpace自体がどう運営されているかの詳細、広告出稿実績は確認できなかった（**不明**）。

### 3.4 SIZLY／シズリー（アイザック株式会社）

Meta Ad Libraryで「SIZLY」を検索したところ0件（広告実物を確認）。Google Ads Transparency Centerでも広告主候補は見つからなかった（広告実物を確認、0件）。

公式には2021年、PR TIMESで「三日坊主ならお金没収。行動を促す習慣アプリ『SIZLY（シズリー）』をリリース」というプレスリリースが確認できる（一次発信、[prtimes.jp](https://prtimes.jp/main/html/rd/p/000000023.000017594.html)）。「挫折したらお金没収、習慣化できたら返金」という設計で、行動データや専門家の知見をもとに開発されたとされる。運営元のアイザック株式会社は法人向け架電自動化ツール「オトコル」やアート管理クラウド「ArtX」等も手がける多角化企業で、SIZLYは複数事業のひとつという位置づけであることが分かった。広告出稿の実績は確認できなかった（**不明**）。

### 3.5 スーパーアラーム

Meta Ad Libraryで「スーパーアラーム」を検索したところ0件（広告実物を確認）、あいまいマッチにより無関係な睡眠アプリ「リナイト（renight）」の広告3件がヒットした。Google Ads Transparency Centerでも広告主候補は見つからなかった（広告実物を確認、0件）。

App Store公式ページで、数学問題・記憶ゲーム・バーコードスキャン・物体スキャン・Face ID・歩行など多様な起床ミッションを提供するアプリであることが確認できる（一次発信に準ずる、App Store公式ページ）。広告・マーケティング施策に関する情報は今回の調査範囲では見つからなかった（**不明**）。

### 3.6 FiNC（FiNC Technologies）── 唯一「自社ブランドの広告」を確認できたケース

今回調査した12アプリの中で唯一、Meta・Google双方で「そのアプリの広告主自身」の広告を確認できたのがFiNCだった。ただし、その内容は大きく変化していた。

**Meta Ad Library実地調査（広告実物を確認）**: 「FiNC」を検索すると230件がヒットしたが、大半はあいまいマッチによる無関係な広告（Finch、Fincan等の海外ブランド）だった。その中に**広告主「FiNC」名義の広告3件（すべて同一クリエイティブの重複、2026年7月28〜29日掲載開始、アクティブ）**が含まれていた。内容は「＼キリンが開発／アンケート回答でお得なお知らせ 【日本初※】おなか周りの脂肪と免疫にWでアプローチするサプリメントが初回限定でお得に」というコピーで、リンク先はキリンの`wellbeing.kirin.co.jp`（キリンiMUSE 免疫ケア・内臓脂肪ダウン、初回限定980円）。**FiNCアプリ本体の広告ではなく、キリンが開発したサプリメントのアフィリエイト的な送客広告**だった。

**Google Ads Transparency Center実地調査（広告主ページで直接確認、広告実物を確認）**: 「FiNC株式会社」で検索すると、広告主「株式会社FiNC Technologies」（本人確認済み）のページがヒットし、**検索テキスト広告4件**が確認できた。すべて法人向けの健康経営SaaS事業（`biz.finc.com`、`guppy.healthcare`＝グッピーヘルスケア）の広告で、コピーは「健康管理と福利厚生を両立-従業員の健康を見える化」「社内コミュニケーション活性化-従業員の運動不足を楽しく解消」「ストレスチェックも簡単に対応-従業員の健康を見える化」など、**完全にBtoB（健康経営・離職防止・SaaS）向けの訴求**だった。コンシューマー向けの元祖「FiNC」アプリのダイエット訴求広告は見当たらなかった。

**過去の広告実績（一次発信で確認）**: FiNCは2019年7月12日、女優・中村アンをブランドアンバサダーに起用した全国テレビCMを放映している（公式プレスリリース、[company.finc.com/news/12213](https://company.finc.com/news/12213)）。同時に「FiNC GIFT CARD」のローソン販売、「FiNC BAND」の新デバイス投入も発表されており、**当時は大型資金調達を背景にマス広告＋新デバイス投入という積極投資フェーズ**にあったことが分かる。

**資金調達と経営状況（二次情報を含む）**: 2018年9月に約55億円強、2020年1月に約50億円の第三者割当増資を実施し、創業からの累計調達額は150億円強に達した（TechCrunch Japan報道）。一方で売上高が7億4,671万円に対し売上原価が11億7,337万円と、売上総利益がマイナスの厳しい経営状況だったとの分析記事もある（NewsPicks等、二次情報）。

**解釈**: FiNCは「大型資金調達→有名女優起用の全国TVCM→デバイス投入」という積極投資期を経て、**2026年8月時点ではコンシューマー向けダイエットアプリの広告展開から撤退し、法人向け健康経営SaaS（グッピーヘルスケア／biz.finc.com）にGoogle検索広告を絞って出稿する形に転換していた**。これは前回・前々回の調査で見た「資金力のある企業ほどマス広告に踏み込む」という傾向の続き、すなわち**「マス広告投資が事業のマネタイズに直結しなかった場合、BtoB事業への転換とともに広告予算・チャネルも絞り込まれる」という、今回初めて実地で確認できた事後的なパターン**である。

### 3.7 カロミル

Meta Ad Libraryで「カロミル」を検索したところ0件で、あいまいマッチによる無関係な広告も表示されなかった（広告実物を確認）。時間の都合によりGoogle Ads Transparency Center・TikTok Creative Centerでの検索は未実施（**不明**）。

### 3.8 dot fit

Meta Ad Libraryで「dot fit」を検索したところ0件（広告実物を確認）、あいまいマッチにより無関係なアパレルブランドの広告1件がヒットした。Google Ads Transparency Centerのオートコンプリートでは「dot fit」に一致する広告主は見つからず、代わりに無関係な「dot. FITNESS CLUB」（`dotfitnessclub.com`、日本、約6件の広告）という別のジムブランドが候補に表示された。Web検索でも「dot fit」という名称の習慣化・フィットネスアプリそのものの一次情報（公式サイト・運営会社）を明確に特定できず、**調査対象として想定していたアプリの実在・詳細を確認できなかった**（**不明**）。

### 3.9 RIZAP系（参考：フィットネス大手グループの広告出稿状況）

Meta Ad Libraryで「RIZAP」を検索したところ約260件がヒットし、その多くが**RIZAPグループ傘下の実店舗系サービスによるアクティブな広告**だった（広告実物を確認）。

| ブランド | 内容 |
|---|---|
| チョコザップ（chocoZAP） | 「月会費最大2カ月無料」等のキャンペーン広告が多数、2026年8月3〜4日掲載開始のものが集中。「2000店舗突破」「RIZAP監修の初心者向け24時間ジム」を訴求 |
| RIZAP English（ライザップイングリッシュ） | 「短期集中でスコアアップしたいなら独学よりRIZAP」、レッスン満足度98%を訴求 |
| RIZAP GOLF（ライザップゴルフ） | 「GOLFではあなたの課題を徹底分析。短期間で100切りが目指せる」 |
| マルコ株式会社（RIZAPグループの補整下着ブランド） | MEGUMI氏の美容本での紹介を切り口にしたアンケート訴求型広告 |
| job_styling（RIZAPグループの人材派遣事業） | Instagram経由の転職・派遣訴求広告 |

**解釈**: SwitchMeが直接参考にできる「習慣改善アプリ単体」の広告ではないが、**資金力・店舗網を持つ企業ほどMeta広告に多面的かつ高頻度で投資している**という、前回・前々回調査の傾向（Duolingo・あすけん等）が、フィットネス業界の実店舗ビジネスモデルでも成立することを裏付ける参考データとして記録した。

### 3.10 Simple Habit・継続する技術・HabitKit（習慣トラッカー系、個人開発規模を想定）

3アプリともMeta Ad Libraryで検索したが、いずれも広告主として一致する結果は見つからなかった（広告実物を確認、いずれも0件）。「Simple Habit」はあいまいマッチにより約4,800件がヒットしたが、上位に頻出したのは無関係な聖書アプリ「Bible Offline」（"Simple habit, big difference"というコピーで反復出稿）等であり、瞑想アプリ「Simple Habit」自体の広告は見当たらなかった。「継続する技術」「HabitKit」は完全に0件だった。

時間の都合によりGoogle Ads Transparency Center・TikTok Creative Centerでの個別検索は未実施（**不明**）。ただしこれらは個人開発・小規模運営が想定されるアプリ群であり、前回・前々回調査で確認した「罰金型アプリ・小規模アプリはMeta広告に依存していない」という傾向と整合する結果と言える。

### 3.11 TikTok Creative Center：Health & Fitness／Education上位広告に対象アプリなし

TikTok Creative Center Top Ads Dashboard（日本・直近180日）を、業種「Apps > Health & Fitness」と「Apps > Education」の2カテゴリで確認した（2026年8月9日時点、広告実物を確認）。

- **Health & Fitness**：上位4件はいずれも今回の調査対象アプリと無関係だった（韓国語の美容クリニック広告「YeosinTicket」、中国語の病院受付アプリ広告、日本語の「そのカロリー」という食事管理系広告、実店舗フィットネス機器のリード獲得広告）。
- **Education**：上位4件も同様に無関係だった（海外の学習AIアプリ「Gauth: AI Study Companion」「Learna AI: French Learning App」が上位を占め、Studyplus等の国内アプリは含まれず）。

前回調査ではBetterMe（海外フィットネスアプリ）がHealth & Fitnessカテゴリの直近180日トップ広告に含まれていたが、今回の検索時点では入れ替わっており、**TikTok上位広告の顔ぶれは短期間で流動的**であることも分かった。いずれにせよ、**国内の習慣改善・フィットネス系アプリがTikTokの上位広告枠に入っている実例は、前回・今回を通じて1件も確認できていない**。

---

## 4. 示唆：今回新たに分かったこと

前回2本の調査記録（「罰金型は広告なしが多い」「資金力のある企業ほどマス広告に踏み込む」）の結論自体は今回さらに裏付けられた。ここでは重複を避け、**今回新たに分かったこと**に絞って記す。

1. **「罰金・コミットメント型はMeta/Google広告に依存しない」という傾向は、日本の4社（シューカン・GoalSpace・SIZLY・スーパーアラーム）でも例外なく再現された。** 前回のstickK・Beeminder・Forfeit・メザミー・みんチャレと合わせると、国・運営規模を問わず、この種のアプリはほぼ一貫して有料広告に頼らずPR TIMES等での単発リリース発信のみに留まっている。SwitchMeが罰金型として同じ道を選ぶことに、市場慣行としての違和感はないと言える。
2. **「資金調達→マス広告投資」の先に何が起きるかが、FiNCの事例で初めて具体的に見えた。** 2019年の女優起用TVCMという最盛期を経て、2026年時点ではコンシューマー向け広告を完全に手放し、BtoB SaaS事業（健康経営）のGoogle検索広告のみに絞られていた。**大型資金調達とマス広告は「その時点でのブランド認知」を作れても、事業の持続的なマネタイズを保証しない**という、前回までの調査では見えなかった「その後」の展開が確認できた。
3. **広告出稿以外の関与の仕方として、Studyplusの「広告枠を売る側」というポジションは新しい発見だった。** 自社の広告を出す代わりに、若年層ユーザー基盤（累計1,000万会員）を武器に他社の広告を売るビジネスモデルは、個人開発のSwitchMeが直接模倣できるものではないが、「習慣化・学習系アプリがある程度の会員基盤を築いた後にどうマネタイズし得るか」の一つの選択肢として記録に値する。
4. **TikTok上位広告枠は海外アプリと美容系ジャンルに偏っており、国内の習慣改善系アプリの参入余地は前回・今回を通じて確認できなかった。** 前回確認したBetterMe（海外アプリ）ですら、180日という短い期間で上位から入れ替わっている。TikTokで戦うなら、上位事例の模倣よりも独自のクリエイティブ実験が必要になりそうだという示唆が、今回の再調査で補強された。
5. **RIZAPグループの事例は、「フィットネス業界で資金力のある企業が実際に何を広告するか」を具体的に見せてくれた。** 単一アプリのブランディングではなく、実店舗網を持つ複数ブランド（ジム・英会話・ゴルフ・下着・人材派遣）を並行して高頻度出稿するという手法で、個人開発のSwitchMeとは前提条件が違いすぎるため直接の参考にはならないが、「習慣改善アプリ単体」で戦う道と「実店舗・複数事業を横展開する」道の違いを対比する材料になる。

**SwitchMeにとっての意味合い**: 今回の調査は「有料広告に投資すべきだ」という結論を補強するものではない。むしろ、日本の同系統アプリ12社中11社が広告透明性ツール上に広告実物を残していないという事実は、**罰金・コミットメント型かつ個人開発規模のアプリにとって、有料広告はそもそも検討の主戦場になっていない**ことを改めて示している。前回・前々回で示したPR TIMES配信・オーガニックSNS発信・ASO投資という優先順位に変更を迫る材料は、今回の調査では見つからなかった。

---

## 付録：主な情報源

**共通・実地調査**: [Meta Ad Library](https://www.facebook.com/ads/library/)（2026年8月9日、claude-in-chrome経由。Studyplus・シューカン・GoalSpace・SIZLY・スーパーアラーム・OWN.・FiNC・カロミル・dot fit・RIZAP・Simple Habit・継続する技術・HabitKitで検索）、[Google Ads Transparency Center](https://adstransparency.google.com/)（同日、地域=日本。シューカン・GoalSpace・SIZLY・スーパーアラーム・OWN.・FiNC・カロミル・dot fit・Studyplusで検索）、[TikTok Creative Center Top Ads Dashboard](https://ads.tiktok.com/business/creativecenter/inspiration/topads/pc/en)（同日、地域Japan・業種Apps > Health & Fitness／Apps > Education・期間180日で確認）

**Studyplus**: [Studyplus Ads公式サイト](https://ads.studyplus.co.jp/)、[info.studyplus.co.jp](https://info.studyplus.co.jp/service/ads)

**シューカン**: [PR TIMES（株式会社メカニズム）](https://prtimes.jp/main/html/rd/p/000000003.000067260.html)、[株式会社メカニズム公式サイト](https://mechanisms.co.jp/)

**GoalSpace**: [value-press（合同会社NoCodeCampプレスリリース）](https://www.value-press.com/pressrelease/325069)、[NoCodeCamp持分譲渡に関する報道（jiji.com）](https://www.jiji.com/jc/article?k=000000011.000139584&g=prt)

**SIZLY**: [PR TIMES（アイザック株式会社）](https://prtimes.jp/main/html/rd/p/000000023.000017594.html)、[アイザック株式会社（INITIAL企業情報）](https://initial.inc/companies/A-43072)

**OWN.**: [東京通信グループ公式ブログ](https://blog.tokyo-tsushin.com/20220715-1638/)、[App Store 1位達成プレスリリース](https://tokyo-tsushin.com/news/20220517-737/)

**FiNC**: [FiNC TVCM出演プレスリリース（company.finc.com）](https://company.finc.com/news/12213)、[TechCrunch Japan（50億円調達報道）](https://jp.techcrunch.com/2020/01/06/finc-technologies-fundraising/)、[NewsPicks（経営状況の分析記事）](https://newspicks.com/news/7325555/body/)、[VisionaryBase（資金調達の全体像）](https://visionarybase.com/n/n3336e2505e7c?gs=f7ffa9205527)

**dot fit**: 公式情報源を特定できず（本文3.8節参照）

**RIZAP系**: Meta Ad Library実地確認のみ（本文3.9節参照）

---

※本ドキュメントの情報はWeb検索・claude-in-chromeでの広告透明性ツール実地確認により2026年8月9日時点で収集したもの。時間の都合によりGoogle Ads Transparency Center・TikTok Creative Centerでの検索は罰金型・フィットネス系を優先し、カロミル・RIZAP・Simple Habit・継続する技術・HabitKitについては一部未検索の項目があり、本文中に「未検索」「不明」と明記した。Meta・Google双方の検索エンジンは短い英字・カタカナ語に対してあいまいマッチングを行うため、検索結果件数と「対象アプリ自身の広告と確認できた件数」は本文中で区別して記載している。dot fitについては対象アプリの実在自体を特定できなかった。
