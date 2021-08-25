<h1 align="center">
    <img src="https://i.jpg.dog/file/jpg-dog/384700feddc6e66db4a0638166b937ac.png" alt="SSRSpeedN" width="200">
    <br>SSRSpeedN
</h1>
<p align="center">
Batch speed measuring tool based on Shadowsocks(R) and V2Ray
</p>
<p align="center">
  <a href="https://github.com/PauperZ/SSRSpeedN/tags"><img src="https://img.shields.io/github/tag/PauperZ/SSRSpeedN.svg"></a>
  <a href="https://github.com/PauperZ/SSRSpeedN/releases"><img src="https://img.shields.io/github/release/PauperZ/SSRSpeedN.svg"></a>
  <a href="https://github.com/PauperZ/SSRSpeedN/blob/master/LICENSE"><img src="https://img.shields.io/github/license/PauperZ/SSRSpeedN.svg"></a>
</p>

## 注意事项

- 测速及解锁测试仅供参考，不代表实际使用情况，由于网络情况变化、Netflix封锁及ip更换，测速具有时效性

- 本项目使用 [Python](https://www.python.org/) 编写，使用前请完成环境安装
- 首次运行前请执行 开始测速.bat 安装pip及相关依赖，也可使用 pip install -r requirements.txt 命令自行安装（其实我已经装好了，不过再走一遍传统步骤增加点仪式感也不错）
- logs文件夹用于记录测速日志，包含节点的详细信息及测速订阅，非必要请勿泄露
- 执行 开始测速.bat 批处理命令即可测速，测速结果保存在 results 文件夹下，不过大佬喜欢用命令行测也可以
- 因为需要依赖 Python 环境，且本项目仍在测试阶段，可能存在部分 bug ，可到 [tg 频道](https://t.me/SSRSpeedN) 进行反馈。
- Netflix 解锁测速结果说明:
~~~~text
Full Native             原生全解锁 
Full Dns                DNS 全解锁
Only original           仅解锁自制剧
None                    未解锁
其中原生解锁和DNS解锁只是解锁方式有区别，实际体验区别不大，在电视端使用时DNS解锁可能会提示使用代理。
~~~~

## 特性

本项目在原 SSRSpeed (已跑路) 的基础上，集成了如下特性

- 支持单线程/多线程同时测速，可以同时反映视频播放/多线程下载等场景的节点速度
- 支持 Netflix 解锁测试，分为 原生全解锁 / DNS全解锁 / 仅解锁自制剧 / 无解锁 四档
- 取消了原版的大红配色，默认为彩虹配色，并增加了新配色 (poor)
- 无耻地增加了频道tag，可以在 result/export_result.py 中改为自己的tag

## 相关依赖

Python第三方库
见 `requirements.txt`

Linux 依赖

- [libsodium](https://github.com/jedisct1/libsodium)
- [Shadowsocks-libev](https://github.com/shadowsocks/shadowsocks-libev)
- [Simple-Obfs](https://github.com/shadowsocks/simple-obfs)

## 支持平台

### 已测试平台

1. Windows 10 x64

放过要饭人士，MacOS和Linux属实没钱测/懒得测，期待更多后浪反馈

### 理论支持平台

支持 Python 及 Shadowsocks, ShadowsocksR, V2Ray 的平台

### 一定支持平台

支持 SSRSpeedN 的平台

## 致谢

- 原作者
  - [NyanChanMeow](https://github.com/NyanChanMeow)
- beta版测试
  - [ChenBilly](https://t.me/ChenBilly)
- 建议及支持
  - [jiexi](https://t.me/jiexi001)
  - [萌新黑客](https://t.me/yxkumad)
- 赞助
  - [便宜机场测速](https://t.me/cheap_proxy)

## 每日一个测速小技巧

### 命令行测速（建议大佬使用）

安装第三方库:

~~~~bash
pip install -r requirements.txt
~~~~

测速主程序及附加选项：

~~~~text
python ./main.py
Usage: main.py [options] arg1 arg2...

附加选项:
  --version             输出版本号并退出
  -h, --help            输出帮助信息并退出
  -c GUICONFIG, --config=GUICONFIG
                        通过节点配置文件加载节点信息.
  -u URL, --url=URL     通过节点订阅链接加载节点信息.
  --include             通过节点标识和组名筛选节点.
  --include-remark      通过节点标识筛选节点.
  --include-group       通过组名筛选节点.
  --exclude             通过节点标识和组名排除节点.
  --exclude-group       通过组名排除节点.
  --exclude-remark      通过节点标识排除节点.
  --use-ssr-cs          替换SSR内核 ShadowsocksR-libev --> ShadowsocksR-C# (Only Windows)
  -g GROUP              自定义测速组名.
  -y, --yes             跳过节点信息确认（我嫌那玩意太麻烦设成默认了）.
  -C RESULT_COLOR, --color=RESULT_COLOR
                    设定测速结果展示配色.
  -S SORT_METHOD, --sort=SORT_METHOD
                        选择节点排序方式 按速度排序/速度倒序/按延迟排序/延迟倒序
                        [speed,rspeed,ping,rping],默认不排序.
  -i IMPORT_FILE, --import=IMPORT_FILE
                        提供给不会p图的同学，偷偷改结果的json文件后重新输出结果.
  --skip-requirements-check
                        跳过确认.
  --debug               采用debug模式.
~~~~

使用样例 :

~~~~text
python main.py -c gui-config.json --include 韩国 --include-remark Azure --include-group YoYu
python main.py -u "https://home.yoyu.dev/subscriptionlink" --include 香港 Azure --include-group YoYu --exclude Azure
~~~~

## 自定义配置

- **自定义颜色**
  - 在 ssrspeed_config.json 文件下第 30 行，采用速度（MB/s）对应输出颜色 （RGB 256）方式
- **自定义字体**
  - 下载字体文件放入 /resources/fonts/ 文件夹下，修改 ssrspeed_config.json 文件下第 29 行，本项目自带两个字体
- **修改测速项目**
  - 在 ssrspeed_config.json 文件下第 16 行及第 21 行，可以设置是否进行udp类型及Netflix解锁测试，默认允许


## 详细使用方法

- 参见 [SSRSpeed N 使用说明](https://gta5cloud.rip/index.php/2021/08/25/ssrspeedn-%e4%bd%bf%e7%94%a8%e8%af%b4%e6%98%8e/)
