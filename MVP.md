# 新闻聚合网站 MVP 完整方案

## 1. 项目概述

开发一个每日自动更新的新闻聚合网站，专注于**开发者技术圈**，按大类展示最新、最热的新闻。网站只展示新闻标题、摘要和原文链接，所有内容版权归原网站所有。目标是快速上线一个最小可行产品（MVP），采用全免费技术栈，零成本运行。

### 当前状态：✅ 已上线

## 2. 核心功能

### 已实现功能 ✅

- **定时抓取**：通过 GitHub Actions 自动运行爬虫，从预定义的 RSS/YouTube/arXiv 源获取新闻。
- **六分类展示**：新闻分为 AI、前端、后端、云原生、区块链、其他 六个互斥分类。
- **智能分类**：混合来源的文章通过关键词匹配自动重分类到正确的分类。
- **列表浏览**：每个分类下按时间倒序或热度排序显示新闻卡片，支持分页（可选 10/20/50/100 条/页）。
- **新闻详情**：点击卡片跳转至原文阅读（在新标签页打开）。
- **热度排序**：基于发布时间和来源权重计算热度分，提供“最热”排序选项。
- **响应式界面**：使用 Tailwind CSS 实现 Mobile-first 设计，完美适配手机和桌面。
- **性能优化**：Flask-Caching API 缓存、SQLite 复合索引、前端骨架屏加载。

## 3. 技术选型（全免费）

| 模块 | 技术 | 说明 |
| ---- | ---- | ---- |
| **后端框架** | Python Flask + Flask-Caching | 轻量级 API 服务，支持内存/Redis 缓存 |
| **数据库** | SQLite | 文件数据库，零成本，支持复合索引 |
| **ORM** | SQLAlchemy | 方便数据库操作和模型定义 |
| **爬虫** | feedparser + requests | 解析 RSS/YouTube/arXiv，支持视频和论文源 |
| **分类器** | 关键词匹配 | 动态分类混合来源的文章 |
| **任务调度** | GitHub Actions | 每天定时运行爬虫脚本 |
| **后端部署** | Render（免费） | 托管 Flask 应用 |
| **前端** | Vue 3 + Vite + Tailwind CSS | 响应式单页应用 |
| **前端部署** | Vercel（免费） | 自动从 GitHub 部署 |
| **版本控制** | GitHub | 所有代码托管 |

## 4. 数据源列表（已实现）

### 当前分类体系（6 个互斥分类）

| 分类 | 数据源数量 | 代表性来源 |
| ---- | ---------- | ---------- |
| **AI** | 18+ | OpenAI Blog, DeepMind, arXiv AI/ML/CV/NLP, Hugging Face, Google Research |
| **前端** | 11+ | MDN Blog, web.dev, JavaScript Weekly, CSS Tricks, Chrome Developers |
| **后端** | 12+ | 美团技术团队, Martin Fowler, Rust Blog, .NET Blog, AWS Architecture |
| **云原生** | 10+ | Kubernetes Blog, CNCF, Docker Blog, Istio, Prometheus |
| **区块链** | 7+ | Ethereum Blog, CoinDesk, Bitcoin Magazine, ChainGPT |
| **其他** | 6+ | Hacker News, Reddit r/programming, 开源中国, InfoQ, 阮一峰的网络日志 |

### 数据源类型

- **RSS 源**：标准 RSS/Atom 订阅源
- **YouTube 源**：频道 RSS 订阅（标记为视频内容）
- **arXiv 源**：学术论文订阅（合并至 AI 分类）

### 动态分类机制

以下来源的文章会根据标题关键词自动重分类：
- Hacker News, Reddit r/programming, 开源中国, InfoQ
- 阿里云开发者社区, 阮一峰的网络日志
- YouTube 频道（尚硅谷, 黑马程序员, Tech With Tim, Computerphile）

> **注意**：部分源可能需要科学上网。详见 `backend/crawler.py` 和 `backend/category_classifier.py`。

## 5. 数据库设计（已实现）

表名：`news`

| 字段 | 类型 | 说明 |
| ---- | ---- | ---- |
| id | INTEGER | 主键，自增 |
| title | TEXT | 新闻标题（非空） |
| summary | TEXT | 摘要（截取前 500 字符） |
| link | TEXT | 原文链接（唯一约束，用于去重） |
| published | DATETIME | 发布时间（RSS 中的时间） |
| source | TEXT | 来源名称 |
| category | TEXT | 分类：AI/前端/后端/云原生/区块链/其他 |
| hot_score | REAL | 热度分，默认 0.0 |
| is_video | BOOLEAN | 是否为视频内容 |
| source_type | STRING | 来源类型：rss/youtube/arxiv |
| created_at | DATETIME | 记录创建时间 |

### 索引设计

```sql
-- 单列索引
CREATE INDEX idx_news_category ON news (category);
CREATE INDEX idx_news_published ON news (published);
CREATE INDEX idx_news_hot_score ON news (hot_score);

-- 复合索引（用于分类+排序查询）
CREATE INDEX idx_category_published ON news (category, published);
CREATE INDEX idx_category_hot_score ON news (category, hot_score);
```

## 6. 爬虫设计（已实现）

### 6.1 整体流程

1. 遍历预定义的 RSS/YouTube/arXiv 源列表（按分类分组）。
2. 对每个源调用 `feedparser.parse(url)`。
3. 解析每条新闻：
   - 标题、链接、摘要、发布时间、来源
   - 检测来源类型（rss/youtube/arxiv）
   - 对混合来源进行动态分类
4. 去重：检查数据库中是否已存在相同 `link`。
5. 计算热度分。
6. 存入数据库。
7. 清理 30 天前的旧新闻。

### 6.2 去重策略

基于 `link` 字段唯一性，先查询是否存在，不存在则添加。

### 6.3 热度算法

```
hot_score = 1 / (hours_since_published + 2) * source_weight
```

- `hours_since_published`：当前时间减去发布时间的小时数
- `source_weight`：来源权重（1.0-1.3），权威来源如 OpenAI、Nature Machine Intelligence 设为 1.2-1.3

### 6.4 动态分类机制

混合来源（Hacker News、Reddit、开源中国等）的文章会根据标题关键词自动分类：

- 匹配前端关键词 → 前端
- 匹配后端关键词 → 后端
- 匹配云原生关键词 → 云原生
- 匹配 AI 关键词 → AI
- 匹配区块链关键词 → 区块链
- 无匹配 → 其他

详见 `backend/category_classifier.py`。

### 6.5 定时调度（GitHub Actions）

```yaml
name: Daily Crawler
on:
  schedule:
    - cron: '0 0 * * *'  # UTC 0点
  workflow_dispatch:

jobs:
  crawl:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: pip install -r backend/requirements.txt
      - name: Run crawler
        run: python backend/crawler.py
      - name: Commit database
        run: |
          git config user.name "github-actions"
          git config user.email "actions@github.com"
          git add backend/news.db
          git diff --quiet && git diff --staged --quiet || git commit -m "Auto update news"
          git push
```

## 7. API 设计（已实现）

Flask 应用提供以下 RESTful 接口：

### 7.1 获取分类新闻列表

`GET /api/news?category=<分类>&sort=<newest|hottest>&page=<页码>&per_page=<条数>`

- `category`：可选，分类名称（AI/前端/后端/云原生/区块链/其他）
- `sort`：排序方式，默认 `newest`，可选 `hottest`
- `page`：页码，默认 1
- `per_page`：每页条数，默认 20，最大 100

返回 JSON：

```json
{
  "items": [
    {
      "id": 1,
      "title": "新闻标题",
      "summary": "摘要...",
      "link": "https://...",
      "source": "来源名",
      "published": "2025-03-12T10:00:00",
      "category": "AI",
      "hot_score": 0.85,
      "is_video": false,
      "source_type": "rss"
    }
  ],
  "total": 100,
  "page": 1,
  "pages": 5
}
```

### 7.2 获取单条新闻详情

`GET /api/news/<id>` 返回单条新闻的完整信息。

### 7.3 获取分类列表

`GET /api/categories` 返回所有分类：

```json
["AI", "前端", "后端", "云原生", "区块链", "其他"]
```

### 7.4 健康检查

`GET /api/health` 返回服务状态。

### 7.5 清除缓存

`POST /api/admin/clear-cache` 清除 API 缓存。

## 8. 前端设计（已实现）

### 8.1 页面结构

- **首页**：顶部 Header 显示网站标题，下方为分类标签栏（支持横向滚动），右侧为排序切换按钮
- **分类导航**：全部 / AI / 前端 / 后端 / 云原生 / 区块链 / 其他
- **排序切换**：最新 / 最热
- **新闻列表**：双列网格布局（移动端单列），支持分页和每页条数选择
- **新闻卡片**：显示标题、摘要、来源、发布时间，视频和论文有特殊图标标识
- **分页组件**：支持跳页、每页条数选择（10/20/50/100）

### 8.2 技术实现

- **框架**：Vue 3 + Vite
- **样式**：Tailwind CSS（Mobile-first 响应式设计）
- **组件**：
  - `App.vue`：主页面，包含状态管理和 API 调用
  - `NewsCard.vue`：新闻卡片组件
  - `SkeletonCard.vue`：加载骨架屏

### 8.3 用户体验优化

- **骨架屏加载**：避免白屏等待
- **分类标签硬编码**：首屏立即显示，无需等待 API
- **分页保留位置**：切换页码后滚动到顶部
- **分类横向滚动**：支持触摸滑动，带淡入淡出指示器
- **响应式布局**：`flex-wrap` 实现自动换行，排序按钮右对齐

## 9. 部署方案（已实现）

### 9.1 架构说明

- **爬虫**：在 GitHub Actions 中运行，更新仓库中的 `news.db` 并提交
- **后端**：Render 部署时自动拉取最新代码（包含 `news.db`），提供只读 API 服务
- **前端**：Vercel 自动部署静态文件

### 9.2 后端部署（Render）

1. 连接 GitHub 仓库
2. Root Directory: `backend`
3. Build Command: `pip install -r requirements.txt`
4. Start Command: `gunicorn app:app`
5. 环境变量（首次部署）：`FORCE_INIT_DB_ON_START=1`

### 9.3 前端部署（Vercel）

1. 连接 GitHub 仓库
2. Root Directory: `frontend`
3. Build Command: `npm run build`
4. Output Directory: `dist`
5. 环境变量：`VITE_API_BASE=<backend-url>`

### 9.4 域名

使用 Vercel/Render 提供的免费子域名。

## 10. 项目状态

### 已完成 ✅

- 后端 API（Flask + Flask-Caching + SQLAlchemy）
- 数据库设计与索引优化
- 爬虫（RSS + YouTube + arXiv）
- 智能分类系统（关键词匹配）
- 前端页面（Vue 3 + Tailwind CSS）
- GitHub Actions 自动化
- Render + Vercel 部署

### 运维监控

- API 健康检查：`/api/health`
- 缓存清理：`POST /api/admin/clear-cache`
- 日志：Render 控制台查看

## 11. 注意事项

- **版权合规**：所有新闻只展示标题和摘要，并提供原文链接。页脚已添加免责声明。
- **RSS 源维护**：定期检查源是否有效，如有失效及时替换。
- **爬虫频率**：每天一次，避免对源站造成压力。
- **数据库维护**：自动清理 30 天前的旧新闻。
- **免费额度**：Render 750 小时/月，GitHub Actions 2000 分钟/月，Vercel 免费版足够。

## 12. 后续可扩展功能

- [ ] 接入搜索功能
- [ ] 用户收藏和阅读历史
- [ ] 个性化推荐
- [ ] 管理后台动态配置源和权重
- [ ] 接入更多数据源（如 Dev.to、Medium）
- [ ] 支持多语言（英文/中文）
