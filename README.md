# Blender-CM3D2-Converter
　3Dアダルトゲーム「[カスタムメイド3D2](http://kisskiss.tv/cm3d2/)」で使用されるモデルファイル形式(.model)を  
　フリー3D統合環境である「[Blender](https://www.blender.org/)」で扱うためのアドオンです。  
　ある程度Blenderの基本操作をできる人を対象にしています、  
　初めての人は[Blenderのチュートリアル](https://www.google.co.jp/#q=Blender+%E3%83%81%E3%83%A5%E3%83%BC%E3%83%88%E3%83%AA%E3%82%A2%E3%83%AB)などから始めましょう。  
　慣れてきたら[CM3D2 Converterのチュートリアル](http://seesaawiki.jp/eastpoint/d/blender_MOD01)もやってみましょう。  

## インストール (Installation)
　まず、Blender2.7以上([2.76b](http://download.blender.org/release/Blender2.76/)推奨)がインストールされており[日本語化](http://ch.nicovideo.jp/hiiragik/blomaga/ar501365)している事が前提です。  
　画面右上の緑色の「Clone or download」→「[Download ZIP](https://github.com/CM3Duser/Blender-CM3D2-Converter/archive/master.zip)」からファイルをダウンロード・解凍し、  
　Windows7なら「C:\Users\ユーザー名\AppData\Roaming\Blender Foundation\  
　Blender\2.75\scripts\addons\CM3D2 Converter\＊.py」となるように配置してください。  
　もしかしたらフォルダが存在しないかもしれませんが、その場合は作成してください。  
　![配置](http://i.imgur.com/QvbMDR1.jpg)  
　Blenderを起動しユーザー設定のアドオンタブで「cm3d」等で検索、  
　「Import-Export: CM3D2 Converter」をオンにすれば一時的に有効になります。  
　次回起動時からも有効にしておきたい場合は「ユーザー設定の保存」をクリックして下さい。  
　![有効化](http://i.imgur.com/6jmFWxQ.jpg)  
　一度インストールしてしまえば、アドオン設定画面かヘルプメニューからアップデート可能です。  
　![更新](http://i.imgur.com/KFvMeH0.jpg)  

## 使い方 (How to Use)
　各種ファイルは.arcファイルから[CM3D2 Tool](http://www.hongfire.com/forum/showthread.php/445616)等で取り出しておいて下さい。  
　  
　.modelの読み込みは  
　　ファイル > インポート > CM3D2 Model (.model)  
　.modelの書き出しも同じように  
　　ファイル > エクスポート > CM3D2 Model (.model)  
　![model入出力手順](http://i.imgur.com/p2V7D5m.jpg)  
　  
　.texの読み込みは  
　　UV/画像エディター > 画像 > texファイルを開く  
　.texの書き出しも同じように  
　　UV/画像エディター > 画像 > texファイルを保存  
　![tex入出力手順](http://i.imgur.com/K7EZfz2.jpg)  
　  
　.mateの読み込みは  
　　プロパティ > マテリアル > mateから  
　.mateの書き出しは  
　　プロパティ > マテリアル > フォルダアイコンのボタン  
　![mate入出力手順](http://i.imgur.com/eRMFTFZ.jpg)  
　  
　どれもファイル選択時の左下にオプションがあります。  

## メモ (Note)

### ボーン
　ボーン情報は「BoneData」と「LocalBoneData」というテキストデータ、  
　![テキスト](http://i.imgur.com/pvgSZy5.jpg)  
　もしくは、オブジェクトかアーマチュアデータ内のカスタムプロパティに保存されています。  
　![カスタムプロパティ](http://i.imgur.com/HHzvdAK.jpg)  
　エクスポート時にどれを参照するかを選ぶ事が可能です。  
　これらを編集すればボーン設定を変更することも可能ですが、慣れない内は変えない事をおすすめします。  
　なお、[有志のアドオン](https://github.com/trzr/Blender-CM3D2-BoneUtil)によってボーン情報を簡単に編集可能になったようです。  

### オブジェクト
　読み込んだモデルによってはオブジェクトの中心点が3D空間の中心とズレている場合があります。  
　その場合は出力時にもその位置に中心点を合わせてからエクスポートして下さい。  

### メッシュ
　四角ポリゴンがあっても自動で三角ポリゴンに変換して出力しますが、手動で三角化した方が綺麗です。  
　五角ポリゴン以上でも一応出力できますが、予想した形状とはならない可能性が高いのでこちらも手動で三角化を推奨。  
　ウェイトが割り当てられていない頂点があった場合、エラーを出して中止します。  
　ウェイト値の合計が1.0でなくても、エクスポート時に自動的に調整します。  
　ウェイトの数が5つ以上でも、自動的に割り当てが大きい順で4つ選ばれます。  
　頂点数は65535未満でないと中止します。  
　(UVが分離されている頂点は重複してカウントされるので、65535未満でもエラーを出す可能性あり。)  

### マテリアル
　マテリアル情報は、マテリアルとテクスチャと画像の設定値によって保管しています。  
　シェーダーの種類(CM3D2/Toony_Lighted_Outlineなど)は、  
　マテリアルタブの上部で変更可能です。  
　![マテリアルタブ上部](http://i.imgur.com/t6fhfXt.jpg)  
　  
　またマテリアル情報をテキストでも保管しているので(名前は「Material:0」等)出力時に設定を変えれば  
　そちらを参照する事も可能です。自分が編集しやすい方を活用して下さい。  
　  
　インポート時にマテリアルの見た目が変更されることがありますが、エクスポート時には関係ありません。  

### テクスチャ
　![テクスチャタブ](http://i.imgur.com/4UxSChV.jpg)  
　テクスチャタブでマテリアルの見た目についての詳細設定を行います。  
　設定値の種類には大きく分けて3種類あります。  
#### 「テクスチャ」タイプ
　　![テクスチャタイプ](http://i.imgur.com/YwwtNqQ.jpg)  
　　唯一、画像を指定します。  
　　テクスチャパスは一致していなくても動作に問題ありませんが、  
　　テクスチャ名は.texファイル名をきちんと指定しましょう。  
#### 「色」タイプ
　　![色タイプ](http://i.imgur.com/RwIFreJ.jpg)  
　　名前の通り色を指定します。  
#### 「値」タイプ
　　![値タイプ](http://i.imgur.com/vmMxRCW.jpg)  
　　小数も指定可能な数値を設定します。  
#### 設定値の一例
##### 　　_MainTex
###### 　　　　面の色を決めるテクスチャ。
##### 　　_ShadowTex
###### 　　　　面が陰になった部分の色を決めるテクスチャ。
##### 　　_Color
###### 　　　　追加の色。おそらく乗算なので白で無効。
##### 　　_ShadowColor
###### 　　　　影になった部分の色。おそらく乗算なので白で無効。
##### 　　_RimColor
###### 　　　　メッシュの縁にできる反射光の色。黒で無効。
##### 　　_OutlineColor
###### 　　　　輪郭線の色。
##### 　　_Shininess
###### 　　　　光沢の強さ(Blenderでいうスペキュラー)。
##### 　　_OutlineWidth
###### 　　　　輪郭線の太さ。
##### 　　_RimPower
###### 　　　　メッシュの縁にできる反射光の濃さ・強度。
##### 　　_RimShift
###### 　　　　メッシュの縁にできる反射光の幅。

### その他
　元の.modelに上書きする必要はありません。  
　データ名が「○○.001」のように末尾に連番が付いていても自動的に削除されます。  

## おまけツール (Misc Tools)
　　このアドオンで追加された機能はアイコン「![専用アイコン](http://i.imgur.com/4RSwhad.png)」で統一されています。  
### CM3D2用マテリアルを新規作成
　　このアドオンで使える仕様のマテリアルを新規作成できます。  
　　「マテリアル」タブ > 「CM3D2用マテリアルを新規作成」ボタン。  
　　出来るだけ汎用的な初期値にしていますが、細かい調整は必要になると思われます。  
　　![CM3D2用マテリアルを新規作成](http://i.imgur.com/l6TgmhY.jpg)
### クイック・ウェイト転送
　　メッシュデータの転送(ウェイト転送)を使いやすくしたものです。  
　　参考にするモデル → 割り当てるモデル の順で選択し、  
　　「メッシュデータ」タブ > 「頂点グループ」パネル > 「▼」ボタン > 「クイック・ウェイト転送」ボタン。  
　　オプションを変更しなければ、不要な頂点グループを削除してくれます。  
　　![クイック・ウェイト転送](http://i.imgur.com/r7Bq6ux.jpg)  
### 頂点グループぼかし
　　頂点グループ(ウェイト)をぼかしてスムーズにします。  
　　モデルを選択し、「メッシュデータ」タブ > 「頂点グループ」パネル >  
　　>「▼」ボタン > 「頂点グループぼかし」ボタン。  
　　ウェイト転送でコピーしたウェイトがガタガタの時などにどうぞ。  
　　![頂点グループぼかし](http://i.imgur.com/p3HNTVR.jpg)  
### シェイプキー強制転送
　　最も近い面(頂点)からシェイプキーをコピーします。  
　　参考にするモデル → 割り当てるモデル の順で選択し、  
　　「メッシュデータ」タブ > 「シェイプキー」パネル > 「▼」ボタン > 「シェイプキー強制転送」ボタン。  
　　あらかじめ参考にするモデルを分割しておくことで、コピーの精度を上げることが可能です。  
　　![シェイプキー強制転送](http://i.imgur.com/6y1s8Vd.jpg)  
### シェイプキーの変形を拡大/縮小
　　シェイプキーの変形を強くしたり、もしくは弱くできます。  
　　モデルを選択し「メッシュデータ」タブ > 「シェイプキー」パネル >  
　　> 「▼」ボタン > 「シェイプキーの変形を拡大/縮小」ボタン。  
　　シェイプキーを転送したにも関わらず身体が服を突き抜ける場合などに、  
　　これで変形を大きくすると修正できるかもしれません。  
　　![シェイプキーの変形を拡大/縮小](http://i.imgur.com/vw9NO6Z.jpg)  
### シェイプキーをぼかす
　　シェイプキーの変形をぼかしてスムーズにします。  
　　モデルを選択し「メッシュデータ」タブ > 「シェイプキー」パネル >  
　　> 「▼」ボタン > 「シェイプキーをぼかす」ボタン。  
　　「シェイプキー強制転送」でコピーした変形がガタガタの時などにどうぞ。  
　　![シェイプキーをぼかす](http://i.imgur.com/P69O44k.jpg)  
### ボーン/頂点グループ名をCM3D2用←→Blender用に変換
　　ボーンと頂点グループの名前をBlenderで左右対称編集できるように変換したり元に戻せます。  
　　メッシュを選択し「メッシュデータ」タブ > 「頂点グループ」パネル >  
　　> 「▼」ボタン > 「頂点グループ名を～」ボタン。  
　　もしくはアーマチュアを選択し「アーマチュアデータ」タブ > 「ボーン名を～」ボタン。  
　　![ボーン/頂点グループ名をCM3D2用←→Blender用に変換](http://i.imgur.com/6O5K5gm.jpg)

## 機能一覧
* 「プロパティ」エリア → 「アーマチュアデータ」タブ
	- ボーン名をCM3D2用→Blender用に変換
		* CM3D2で使われてるボーン名をBlenderで左右対称編集できるように変換します
	- ボーン名をBlender用→CM3D2用に変換
		* CM3D2で使われてるボーン名に元に戻します
	- ボーン情報をコピー
		* カスタムプロパティのボーン情報をクリップボードにコピーします
	- ボーン情報を貼り付け
		* カスタムプロパティのボーン情報をクリップボードから貼り付けます
	- ボーン情報を削除
		* カスタムプロパティのボーン情報を全て削除します
* 「プロパティ」エリア → 「モディファイア」タブ
	- モディファイア強制適用
		* シェイプキーのあるメッシュのモディファイアでも強制的に適用します
* 「プロパティ」エリア → 「メッシュデータ」タブ → 「頂点グループ」パネル
	- 頂点グループ名をCM3D2用→Blender用に変換
		* CM3D2で使われてるボーン名(頂点グループ名)をBlenderで左右対称編集できるように変換します
	- 頂点グループ名をBlender用→CM3D2用に変換
		* CM3D2で使われてるボーン名(頂点グループ名)に戻します
* 「UV/画像エディター」エリア → ヘッダー
* 「UV/画像エディター」エリア → プロパティ → 「画像」パネル
* 画面右上 (「情報」エリア → ヘッダー)
	- 頂点数をチェック
		* 選択メッシュがConverterで出力可能な頂点数に収まっているかをチェックします
* 「3Dビュー」エリア → 追加(Shift+A) → CM3D2
	- CM3D2用の素体をインポート
		* CM3D2関係の素体を現在のシーンにインポートします
* 「3Dビュー」エリア → 追加(Shift+A) → カーブ
	- 髪の房を追加
		* アニメ調の髪の房を追加します
* 画面上部 (「情報」エリア → ヘッダー) → ヘルプ
	- CM3D2 Converterを更新
		* GitHubから最新版のCM3D2 Converterアドオンをダウンロードし上書き更新します
	- CM3D2 Converterの設定画面を開く
		* CM3D2 Converterアドオンの設定画面を表示します
* 「プロパティ」エリア → 「マテリアル」タブ
	- CM3D2用マテリアルを新規作成
		* Blender-CM3D2-Converterで使用できるマテリアルを新規で作成します
	- クリップボードからマテリアルを貼り付け
		* クリップボード内のマテリアル情報から新規マテリアルを作成します
	- クリップボードからマテリアルを貼り付け
		* クリップボード内のテキストからマテリアル情報を上書きします
	- マテリアルをクリップボードにコピー
		* 表示しているマテリアルをテキスト形式でクリップボードにコピーします
	- マテリアルを装飾
		* スロット内のマテリアルを全て設定に合わせて装飾します
	- このテクスチャを見る
		* このテクスチャを見る
* 「プロパティ」エリア → 「メッシュデータ」タブ → 「シェイプキー」パネル → ▼ボタン
	- クイック・シェイプキー転送
		* アクティブなメッシュに他の選択メッシュのシェイプキーを高速で転送します
	- 空間ぼかし・シェイプキー転送
		* アクティブなメッシュに他の選択メッシュのシェイプキーを遠いほどぼかして転送します
	- シェイプキーの変形に乗算
		* シェイプキーの変形に数値を乗算し、変形の強度を増減させます
	- シェイプキーぼかし
		* アクティブ、もしくは全てのシェイプキーをぼかします
	- このシェイプキーをベースに
		* アクティブなシェイプキーを他のシェイプキーのベースにします
* 「プロパティ」エリア → 「メッシュデータ」タブ → 「頂点グループ」パネル → ▼ボタン
	- クイック・ウェイト転送
		* アクティブなメッシュに他の選択メッシュの頂点グループを高速で転送します
	- 空間ぼかし・ウェイト転送
		* アクティブなメッシュに他の選択メッシュの頂点グループを遠いほどぼかして転送します
	- 頂点グループぼかし
		* アクティブ、もしくは全ての頂点グループをぼかします
	- 旧・頂点グループぼかし
		* アクティブ、もしくは全ての頂点グループをぼかします
	- 頂点グループに乗算
		* 頂点グループのウェイトに数値を乗算し、ウェイトの強度を増減させます
	- 割り当てのない頂点グループを削除
		* どの頂点にも割り当てられていない頂点グループを全て削除します
* 「プロパティ」エリア → 「オブジェクト」タブ
	- ボーン情報をコピー
		* カスタムプロパティのボーン情報をクリップボードにコピーします
	- ボーン情報を貼り付け
		* カスタムプロパティのボーン情報をクリップボードから貼り付けます
	- ボーン情報を削除
		* カスタムプロパティのボーン情報を全て削除します
* 「プロパティ」エリア → 「オブジェクト」タブ → 「トランスフォーム」パネル
	- オブジェクトの位置を合わせる
		* アクティブオブジェクトの中心位置を、他の選択オブジェクトの中心位置に合わせます
* 「プロパティ」エリア → 「レンダー」タブ → 「ベイク」パネル
	- ベイク用の画像を作成
		* アクティブオブジェクトに素早くベイク用の空の画像を用意します
	- AO・ベイク
		* アクティブオブジェクトに素早くAOをベイクします
	- 擬似AO・ベイク
		* アクティブオブジェクトに素早く擬似AOをベイクします
	- ヘミライト・ベイク
		* アクティブオブジェクトに素早くヘミライトの陰をベイクします
	- 影・ベイク
		* アクティブオブジェクトに素早く影をベイクします
	- 側面陰・ベイク
		* アクティブオブジェクトに素早く側面陰をベイクします
	- グラデーション・ベイク
		* アクティブオブジェクトに素早くグラデーションをベイクします
	- 金属・ベイク
		* アクティブオブジェクトに素早く金属風にベイクします
	- ヘアー・ベイク
		* アクティブオブジェクトに素早くCM3D2の髪風のテクスチャをベイクします
	- UV縁・ベイク
		* アクティブオブジェクトに素早くUVの縁を黒くベイクします
	- メッシュ縁・ベイク
		* アクティブオブジェクトに素早くメッシュの縁を黒くベイクします
	- 密度・ベイク
		* アクティブオブジェクトに素早く密度をベイクします
	- メッシュ間距離・ベイク
		* アクティブオブジェクトに他オブジェクトとの距離をベイクします
	- 膨らみ・ベイク
		* アクティブオブジェクトに膨らんでいる部分を白くベイクします
	- 白い液体・ベイク
		* アクティブオブジェクトに白い液体をベイクします
* 「プロパティ」エリア → 「レンダー」タブ → 「レンダー」パネル
	- CM3D2メニュー用のアイコンをレンダリング
		* CM3D2内のアイコン画像に使用できそうな画像をレンダリングします
* 「プロパティ」エリア → 「テクスチャ」タブ
	- 画像を表示
		* 指定の画像をUV/画像エディターに表示します
	- テクスチャを探す
		* CM3D2本体のインストールフォルダからtexファイルを探して開きます
	- 設定をプレビューに同期
		* 設定値をテクスチャのプレビューに適用してわかりやすくします
	- トゥーンを選択
		* CM3D2にデフォルトで入っているトゥーンテクスチャを選択できます
	- 色設定値を自動設定
		* 色関係の設定値をテクスチャの色情報から自動で設定します
	- texで保存
		* テクスチャの画像を同フォルダにtexとして保存します
	- 色設定値を設定
		* 色タイプの設定値を設定します
* 「テキストエディター」エリア → ヘッダー
	- テキストを表示
		* 指定したテキストをこの領域に表示します
	- テキストのボーン情報をコピー
		* テキストのボーン情報をカスタムプロパティへ貼り付ける形にしてクリップボードにコピーします
	- テキストのボーン情報を貼り付け
		* クリップボード内のボーン情報をテキストデータに貼り付けます
	- マテリアル情報テキストを全削除
		* CM3D2で使用できるマテリアルテキストを全て削除します
* 「3Dビュー」エリア → メッシュ編集モード → 「W」キー
	- 選択面の描画順を最前面に
		* 選択中の面の描画順を最も前面/背面に並び替えます
* 「3Dビュー」エリア → ポーズモード → Ctrl+A (ポーズ → 適用)
	- 現在のポーズで素体化
		* 現在のポーズで衣装をモデリングしやすくする素体を作成します
* 「3Dビュー」エリア → 「ウェイトペイント」モード → ツールシェルフ → 「ウェイトツール」パネル
	- 選択部分の頂点グループをぼかす
		* 選択メッシュの頂点グループの影響をぼかします

## 規約 (Agreement)
[公式のMOD規約](http://kisskiss.tv/kiss/diary.php?no=558)を厳守して下さい。  

## .modelのフォーマット (.model Format)
* (String) 「CM3D2_MESH」固定
* (Int) バージョン番号
* (String) モデル名
* (String) 基点ボーン名
* (Int) ボーン数
* for ボーン数
	- (String) ボーン名
	- (Char) フラグ？
* for ボーン数
	- (Int) 親番号
* for ボーン数
	- (Float×3) ボーン位置
	- (Float×4) ボーン回転
* (Int) 頂点数
* (Int) メッシュ数 (マテリアル数)
* (Int) 使用ボーン数
* for 使用ボーン数
	- (String) ボーン名
* for 使用ボーン数
	- (Float×16) ボーン変換行列
* for 頂点数
	- (Float×3) 頂点位置
	- (Float×3) 法線方向
	- (Float×2) UV位置
* (Int) 不明な数 (0もしくは頂点数と同じ)
* for 不明な数
	- (Float×4) 不明な数値
* for 頂点数
	- (Short×4) 割り当てるボーン番号×4
	- (Float×4) 割り当てるウェイト×4
* for メッシュ数
	- (Int) 面数
	- for 面数
		* (Short) 頂点番号
* (Int) マテリアル数 (メッシュ数)
* for マテリアル数
	- (String) マテリアル名
	- (String) 使用シェーダー
	- (String) 使用シェーダー
	- while
		* (String) 設定値タイプ
		* if 設定値タイプ == "tex"
			- (String) テクスチャ名
			- (String) テクスチャタイプ
			- if テクスチャタイプ == "tex2d"
				* (String) 画像名
				* (String) 画像パス
				* (Float×4) 色 (RGBA)
		* else if 設定値タイプ == "col"
			- (String) 色名
			- (Float×4) 色 (RGBA)
		* else if 設定値タイプ == "f"
			- (String) 値名
			- (Float) 値
		* else if 設定値タイプ == "end"
			- break
* while
	- (String) 設定値タイプ
	- if 設定値タイプ == "morph"
		* (String) モーフ名
		* (Int) 変更頂点数
		* for 変更頂点数
			- (Short) 頂点番号
			- (Float×3) 頂点位置
			- (Float×3) 法線方向
	- else if 設定値タイプ == "end"
		* break

## 課題 (Assignment)
* ボーン情報を人力で編集可能な形にする([有志のアドオンにより実現](https://github.com/trzr/Blender-CM3D2-BoneUtil))
* 一部のmodelに含まれる「頂点数xFloatx4」分のデータを解析、入出力可能に
* モーションファイル(.anm)関係の完全対応
