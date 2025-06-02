# PyPhiRenderer
> 本项目是一个基于 **Phigros 玩法** 制作的播放器  
> 本项目**仅供研究学习目的，请勿用于商业用途**，侵删。

## 特别感谢
- 部分代码参考了 [K0nGbawa/Re-PyPhiPlayer](https://github.com/K0nGbawa/Re-PyPhiPlayer/) 和 [qaqFei/phispler](https://github.com/qaqFei/phispler/)。

## 使用方法
- 安装 `python` 。（推荐版本3.12.10，3.13往上音频渲染无法正常运行）
- 首次使用前，点击文件资源管理器地址栏，输入 `cmd` ，在弹出的窗口中输入 `pip install -r requirements.txt` ，下载依赖库。
- 双击 [`main.py`](main.py) 运行程序。

## 参数说明
|参数名|作用|默认值|
|-|-|-|
|--chart|指定谱面|-|
|--music|指定音乐|-|
|--illustration|指定曲绘|-|
|--name|曲名|-|
|--level|难度|-|
|--composer|曲师|-|
|--charter|谱师|-|
|--illustrator|画师|-|
|--combotips|COMBO文本|"COMBO"|
|--aspectratio|限制宽高比|"16:9"|
|--bgalpha|背景变暗|0.1|
|--showbar|显示曲名前竖线|-|
|--noautoplay|禁用自动播放|-|
|--illblur|曲绘模糊半径|80|
|--width|窗口宽度|1200|
|--height|窗口高度|900|
|--fps|渲染视频的帧数|60|
|--render|开启渲染|-|
|--bitrate|渲染视频的码率|15000|
|--resource|资源路径|".\\Resources"|
|--preview|渲染预览|-|
|--output|渲染视频导出位置|"%Y-%m-%d %H-%M-%S name_level.mp4"|

## 兼容
- [ ] Phi
    - [x] formatVersion
        - [x] 1
        - [ ] 2
        - [x] 3
    - [x] offset
    - [x] judgeLineList
        - [x] bpm
        - [x] notesAbove
        - [x] notesBelow
        - [x] speedEvents
        - [x] judgeLineMoveEvents
        - [x] judgeLineRotateEvents
        - [x] judgeLineDisappearEvents

- [ ] RPE
    - [x] BPMList
    - [ ] META
        - [x] RPEVersion
        - [x] background
        - [x] charter
        - [x] composer
        - [ ] duration
        - [ ] id
        - [x] illustration
        - [x] level
        - [x] name
        - [x] offset
        - [x] song
    - [ ] chartTime (没用)
    - [ ] judgeLineGroup (没用)
    - [ ] judgeLineList
        - [ ] Group (没用)
        - [ ] Name (没用)
        - [x] Texture
        - [ ] alphaControl
        - [ ] posControl
        - [ ] sizeControl
        - [ ] skewControl
        - [ ] yControl
        - [x] attachUI
        - [x] anchor
        - [x] bpmfactor
        - [x] eventLayers
            - [x] alphaEvents
            - [x] moveXEvents
            - [x] moveYEvents
            - [x] rotateEvents
            - [x] speedEvents
        - [ ] extended
            - [ ] inclineEvents
            - [x] colorEvents
            - [x] scaleXEvents
            - [x] scaleYEvents
            - [x] textEvents
            - [x] paintEvents
            - [ ] gifEvents
        - [x] father
        - [x] isCover
        - [ ] isGif
        - [x] notes
            - [x] above
            - [x] alpha
            - [x] endTime
            - [x] isFake
            - [x] positionX
            - [x] size
            - [x] speed
            - [x] startTime
            - [x] type
            - [x] visibleTime
            - [x] yOffset
            - [x] hitsound
            - [ ] zIndex
            - [ ] zIndexHitEffects
            - [x] tint
            - [x] tintHitEffects
        - [ ] numOfNotes (没用)
        - [x] zOrder
        - [x] scaleOnNotes
    - [ ] multiLineString (没用)
    - [ ] multiScale (没用)
    - [ ] timeTags (没用)

- PEC
    - [ ] bp
    - [ ] n
    - [ ] #
    - [ ] &
    - [ ] cm
    - [ ] cp
    - [ ] cr
    - [ ] ca
    - [ ] cf
    - [ ] cd
    - [ ] cv

- phira extra
    - [ ] bpm
    - [ ] effects
    - [ ] videos

- phira resource pack
    - [ ] click.png
    - [ ] click_mh.png
    - [ ] drag.png
    - [ ] drag_mh.png
    - [ ] hold.png
    - [ ] hold_mh.png
    - [ ] flick.png
    - [ ] flick_mh.png
    - [ ] hit_fx.png
    - [ ] click.ogg
    - [ ] drag.ogg
    - [ ] flick.ogg
    - [ ] ending.mp3
    - [ ] info.yml
        - [ ] name
        - [ ] author
        - [ ] description
        - [ ] hitFx
        - [ ] holdAtlas
        - [ ] holdAtlasMH
        - [ ] hitFxDuration
        - [ ] hitFxScale
        - [ ] hitFxRotate
        - [ ] hitFxTinted
        - [ ] hideParticles
        - [ ] holdKeepHead
        - [ ] holdRepeat
        - [ ] holdCompact
        - [ ] colorPerfect
        - [ ] colorGood