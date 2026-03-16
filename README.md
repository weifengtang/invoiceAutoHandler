# 🧾 发票自动处理工具

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![GitHub Stars](https://img.shields.io/github/stars/weifengtang/invoiceAutoHandler.svg)](https://github.com/weifengtang/invoiceAutoHandler/stargazers)

> 🚀 告别手动整理发票！自动解析 PDF 发票，智能分类并规范化命名

## ✨ 功能特性

- 🔍 **智能分类** - 自动识别发票类型（交通、餐饮、通信、住宿等 9 大类）
- 📅 **信息提取** - 自动提取开票日期、价税合计、发票号码
- 📝 **规范命名** - 统一格式 `类型-日期-金额-发票号码.pdf`
- 🔄 **增量处理** - 日志记录已处理文件，避免重复操作
- ⚙️ **配置灵活** - 关键词规则、默认目录均可自定义
- 📧 **邮件联动** - 可配合 Apple Mail 实现全自动处理

## 📦 快速开始

### 安装依赖

```bash
pip3 install pdfplumber
```

### 下载使用

```bash
# 克隆仓库
git clone https://github.com/weifengtang/invoiceAutoHandler.git
cd invoiceAutoHandler

# 运行脚本
python3 rename_invoice.py /path/to/invoices
```

### 使用方式

```bash
# 方式1：指定目录
python3 rename_invoice.py /path/to/invoices

# 方式2：使用默认目录（settings.json 配置）
python3 rename_invoice.py

# 方式3：处理单个文件
python3 rename_invoice.py invoice.pdf
```

## 📁 目录结构

```
invoiceAutoHandler/
├── rename_invoice.py      # 主脚本
├── settings.json          # 配置文件
├── invoice_log.json       # 处理日志（自动生成）
└── README.md
```

## ⚙️ 配置说明

编辑 `settings.json` 自定义规则：

```json
{
    "default_directory": "./202603",
    "categories": {
        "交通": ["出行", "滴滴", "打车", "机票", "火车", "高德", "曹操", "T3", ...],
        "餐饮": ["餐饮", "美食", "餐厅", "美团", "饿了么", ...],
        "通信": ["电信", "联通", "移动", "话费", ...],
        "住宿": ["酒店", "宾馆", "民宿", ...],
        "办公": ["文具", "打印", "设备", ...],
        "医疗": ["医院", "药店", "体检", ...],
        "培训": ["培训", "教育", "课程", ...],
        "购物": ["超市", "商场", "京东", ...],
        "快递": ["快递", "物流", "顺丰", ...]
    },
    "default_category": "其他"
}
```

## 📝 命名规则

**格式**：`类型-开票日期-开票金额-发票号码.pdf`

**示例**：
```
原始文件：高德打车电子发票.pdf
重命名后：交通-20260315-30.00-26327000000530134059.pdf

原始文件：美团外卖发票.pdf
重命名后：餐饮-20260315-45.50-26952000001052541706.pdf
```

## 🔧 信息提取优先级

| 字段 | 提取规则 |
|------|----------|
| 日期 | `开票日期：YYYY年MM月DD日` > `YYYY-MM-DD` > 文件修改时间 |
| 金额 | `价税合计（小写）¥XX.XX` > `价税合计：¥XX.XX` > `合计：¥XX.XX` |
| 发票号码 | `发票号码：XXXXXXXX` > `号码：XXXXXXXX` |
| 类型 | 根据关键词匹配文本和文件名 |

## 🔄 自动化工作流

配合邮件规则实现全自动化：

```mermaid
flowchart LR
    A[收到发票邮件] --> B[Mail规则检测]
    B --> C[自动下载PDF]
    C --> D[调用脚本重命名]
    D --> E[完成归档]
```

### Apple Mail 集成

1. 打开 Mail > 偏好设置 > 规则
2. 新建规则：主题/内容包含"发票"
3. 执行 AppleScript 下载附件并调用本脚本

详细配置请参考 [Wiki](https://github.com/weifengtang/invoiceAutoHandler/wiki)

## 📊 对比

| 维度 | 手动处理 | 本工具 |
|------|----------|--------|
| 操作步骤 | 下载→分类→重命名 | 零操作 |
| 处理时间 | 2-3分钟/张 | <1秒/张 |
| 错误率 | 易漏、易错 | 100%按规则执行 |
| 归档规范 | 混乱 | 统一格式 |

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 提交 Pull Request

## 📄 License

本项目采用 MIT 协议开源 - 查看 [LICENSE](LICENSE) 文件了解详情

## ⭐ Star History

如果这个项目对你有帮助，请给个 Star ⭐

[![Star History Chart](https://api.star-history.com/svg?repos=weifengtang/invoiceAutoHandler&type=Date)](https://star-history.com/#weifengtang/invoiceAutoHandler&Date)
