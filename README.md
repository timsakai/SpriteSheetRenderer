<img src="https://i.imgur.com/nrnT2ze.png" alt="サムネ" title="サムネ">

# 説明
blender 4.2 向けアドオン。
アニメーションから、スプライトシートを作成するスクリプト。

# 使用法
## インストール
 - references > Add-ons > Install from Disk　からzipを指定、SpriteSheetRendererにェックで有効化
## 場所 
 - Nパネル（プロパティサイドバー）>  SpriteSheetRenderer

1. Install Pillow ボタンからPythonモジュールをBlenderにインストール。
- Pillow : https://pillow.readthedocs.io/en/stable/about.html 

2. アニメーションアクションを作成

3. スプライトシート作成をするアクションをチェックボックスで指定

4. 対象のアーマチュアを選択

5. Render Actions ボタンでスプライトシート作成！
<img src="https://i.imgur.com/4OIR0uF.png" alt="説明" title="説明">

# 仕様
- Blender の　FrameStep でレンダリングするフレームの倍数を指定できます。
- 背景透過には、Film > Transparent を使用してください。
- 64x64でレンダリングのテストを行うことを推奨します。

# 仕組み
- レンダリング処理はBlender標準のバッチレンダーを使用します。
- レンダリング処理後、Pillowの画像処理によって画像を横並びに一つのファイルにします。
