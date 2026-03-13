# 新闻聚合网站 MVP 完整方案

## 1. 项目概述

开发一个每日自动更新的新闻聚合网站，专注于**程序员圈**和**AI圈**，按大类展示最新、最热的新闻。网站只展示新闻标题、摘要和原文链接，所有内容版权归原网站所有。目标是快速上线一个最小可行产品（MVP），采用全免费技术栈，零成本运行。

## 2. 核心功能

- **每日定时抓取**：通过 GitHub Actions 每天自动运行爬虫，从预定义的 RSS 源获取新闻。
- **分类展示**：新闻分为“程序员圈”和“AI圈”两个大类，在首页通过标签或导航切换。
- **列表浏览**：每个分类下按时间倒序或热度排序显示新闻卡片，每页 20 条，支持分页。
- **新闻详情**：点击卡片跳转至原文阅读（在新标签页打开）。
- **热度排序**：基于发布时间和来源权重计算热度分，提供“最热”排序选项。
- **极简界面**：使用响应式设计，适配手机和桌面。

## 3. 技术选型（全免费）

| 模块               | 技术                                    | 说明                                       |
| ------------------ | --------------------------------------- | ------------------------------------------ |
| **后端框架** | Python Flask                            | 轻量级，适合 API 服务                      |
| **数据库**   | SQLite                                  | 文件数据库，零成本，随项目一起部署         |
| **ORM**      | SQLAlchemy                              | 方便数据库操作和模型定义                   |
| **爬虫**     | feedparser + requests                   | 解析 RSS，必要时补充抓取摘要               |
| **任务调度** | GitHub Actions                          | 每天定时运行爬虫脚本，将数据更新提交到仓库 |
| **后端部署** | Render（免费）或 PythonAnywhere（免费） | 托管 Flask 应用，绑定 SQLite 文件          |
| **前端**     | Vue 3 + Vite（或原生 HTML/CSS/JS）      | 单页应用或静态页面，通过 API 获取数据      |
| **前端部署** | Vercel / Netlify                        | 自动从 GitHub 部署静态文件                 |
| **版本控制** | GitHub                                  | 所有代码和数据库文件（SQLite）托管         |

## 4. 数据源列表（RSS）

### 程序员圈

- 美团技术团队：`https://tech.meituan.com/feed/`
- MDN Blog：`https://developer.mozilla.org/en-US/blog/rss.xml`
- web.dev：`https://web.dev/feed.xml`
- Microsoft Dev Blogs (.NET)：`https://devblogs.microsoft.com/dotnet/feed/`
- Hacker News：`https://news.ycombinator.com/rss`
- Reddit r/programming：`https://www.reddit.com/r/programming/.rss`
- 开源中国：`https://www.oschina.net/news/rss`
- InfoQ：`https://www.infoq.cn/feed`
- 阿里云开发者社区：`https://developer.aliyun.com/feed`
- 腾讯云开发者社区：`https://cloud.tencent.com/developer/devops/feed`

### AI圈

- OpenAI Blog：`https://openai.com/blog/rss.xml`
- Google AI Blog：`https://ai.googleblog.com/feeds/posts/default`
- DeepMind Blog：`https://deepmind.com/blog/feed`
- Hugging Face Blog：`https://huggingface.co/blog/feed.xml`
- Towards Data Science：`https://towardsdatascience.com/feed`
- Jay Alammar's Blog：`https://jalammar.github.io/feed.xml`
- BAIR (Berkeley AI Research)：`https://bair.berkeley.edu/blog/feed.xml`
- Facebook AI：`https://ai.facebook.com/blog/rss/`

> **注意**：部分源可能需要科学上网，请在国内可访问的环境下测试。如果某个源无法访问，可替换为同类源或使用 NewsAPI 免费层作为补充。

## 5. 数据库设计

表名：`news`

| 字段       | 类型     | 说明                           |
| ---------- | -------- | ------------------------------ |
| id         | INTEGER  | 主键，自增                     |
| title      | TEXT     | 新闻标题（非空）               |
| summary    | TEXT     | 摘要（截取前 500 字符）        |
| link       | TEXT     | 原文链接（唯一约束，用于去重） |
| published  | DATETIME | 发布时间（RSS 中的时间）       |
| source     | TEXT     | 来源名称（如“美团技术团队”） |
| category   | TEXT     | 分类：`程序员圈` 或 `AI圈` |
| hot_score  | REAL     | 热度分，默认 0.0               |
| created_at | DATETIME | 记录创建时间，用于调试         |

## 6. 爬虫设计

### 6.1 整体流程

1. 遍历预定义的 RSS 源列表（按分类分组）。
2. 对每个源调用 `feedparser.parse(url)`。
3. 解析每条新闻：
   - 标题：`entry.title`
   - 链接：`entry.link`
   - 摘要：`entry.summary` 或 `entry.description`（若太长则截断）
   - 发布时间：`entry.published_parsed` 转为 datetime
   - 来源：`feed.feed.title` 或手动指定
4. 去重：检查数据库中是否已存在相同 `link`，若存在则跳过。
5. 计算热度分（见 6.3）。
6. 存入数据库。

### 6.2 去重策略

基于 `link` 字段唯一性，使用 SQLAlchemy 的 `get_or_create` 逻辑：先查询是否存在，不存在则添加。

### 6.3 热度算法（简单有效）

由于无法获取评论/点赞数，采用基于时间衰减和来源权重的公式：

```
hot_score = 1 / (hours_since_published + 2) * source_weight
```

- `hours_since_published`：当前时间减去发布时间的小时数（最小为 0）。
- `source_weight`：可手动配置，例如 OpenAI、Google AI 等权威源权重设为 1.2，普通博客设为 1.0。
- 若发布时间无法解析，则设为当前时间，热度分较低。

权重表可存储在代码字典中，后续可改为数据库配置。

### 6.4 定时调度（GitHub Actions）

创建 `.github/workflows/crawler.yml`，每天 UTC 0 点运行：

```yaml
name: Daily Crawler
on:
  schedule:
    - cron: '0 0 * * *'
  workflow_dispatch:  # 允许手动触发

jobs:
  crawl:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run crawler
        run: python crawler.py
      - name: Commit database changes
        run: |
          git config user.name "github-actions"
          git config user.email "actions@github.com"
          git add news.db
          git diff --quiet && git diff --staged --quiet || git commit -m "Auto update news"
          git push
```

> **注意**：频繁提交 SQLite 文件到 Git 仓库不是最佳实践，但 MVP 阶段可行。若数据量增大，可考虑使用云数据库（如 Supabase 免费层）代替。

## 7. API 设计

Flask 应用提供以下 RESTful 接口：

### 7.1 获取分类新闻列表

`GET /api/news?category=<程序员圈|AI圈>&sort=<newest|hottest>&page=<页码>`

- `category`：可选，不传则返回所有分类（但 MVP 前端按分类切换，可传参）
- `sort`：排序方式，默认 `newest`（按发布时间倒序），`hottest` 按热度分倒序
- `page`：页码，默认 1
- 每页数量固定 20 条

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
      "category": "程序员圈",
      "hot_score": 0.85
    }
  ],
  "total": 100,
  "page": 1,
  "pages": 5
}
```

### 7.2 获取单条新闻详情（可选）

`GET /api/news/<id>` 返回单条新闻的完整信息（同列表项格式）。如果不需要详情页，可省略。

### 7.3 获取分类列表

`GET /api/categories` 返回所有分类（用于前端导航）：

```json
["程序员圈", "AI圈"]
```

## 8. 前端设计

### 8.1 页面结构

- **首页**：顶部有两个标签（程序员圈 / AI圈），默认显示程序员圈新闻列表。列表上方有“最新”和“最热”排序切换按钮。列表底部有“加载更多”按钮或分页控件。
- **新闻卡片**：每张卡片显示标题、摘要、来源名称、发布时间、分类标签。点击卡片区域在新标签页打开原文链接。
- **无搜索功能**，完全符合 MVP 要求。

### 8.2 技术实现建议

- 使用 Vue 3 + Vite 快速搭建 SPA。
- 样式采用 Tailwind CSS 或自己写简单 CSS，保证移动端适配。
- 前端部署在 Vercel：将代码推送到 GitHub，Vercel 自动部署。

### 8.3 API 调用示例（原生 JS）

```javascript
async function loadNews(category, sort, page) {
  const url = `https://your-backend.com/api/news?category=${category}&sort=${sort}&page=${page}`;
  const res = await fetch(url);
  const data = await res.json();
  // 渲染 data.items
}
```

## 9. 部署方案

### 9.1 后端部署（Render）

1. 在 [Render](https://render.com) 注册账号，使用 GitHub 登录。
2. 创建新 Web Service，连接存放 Flask 应用的仓库。
3. 设置构建命令：`pip install -r requirements.txt`
4. 启动命令：`gunicorn app:app`
5. 环境变量无需额外设置（SQLite 文件会保存在容器磁盘中，注意 Render 免费版磁盘非持久，但重启后文件会丢失？实际上 Render 的磁盘是临时但每个服务有独立存储，重启不丢失，但服务睡眠后再次启动可能丢失？需确认。另一种方案：将 SQLite 文件放在 GitHub 仓库并通过 Actions 更新，后端读取仓库中的文件。但 Render 无法直接写入 GitHub。推荐方案：使用 GitHub Actions 运行爬虫并提交数据库，后端从仓库的 raw 文件 URL 读取？但那样只能读不能写。更简单：后端直接使用 Render 上的 SQLite，爬虫也在 Render 上定时运行？但 Render 免费版不支持定时任务。所以 GitHub Actions 爬虫 + Render 后端读取同一 SQLite 文件需要共享存储。一个巧妙的办法：将 SQLite 文件也托管在 GitHub 仓库，后端 API 从仓库的 raw 文件 URL 读取（只读），而爬虫通过 GitHub Actions 更新文件。这样后端是只读的，无需写入数据库，完美。且 GitHub raw 文件有缓存，但新闻每天更新一次，可接受。后端只需读取 SQLite 文件并提供 API。）

因此，调整架构：

- 爬虫在 GitHub Actions 中运行，更新仓库中的 `news.db` 并提交。
- 后端 Flask 应用从当前目录读取 `news.db`（通过 git clone 或部署时拉取最新代码），提供 API 服务。Render 部署时会自动拉取最新代码，包含最新的 `news.db`。
- 这样后端始终读取最新的数据库，无需额外存储。

### 9.2 前端部署（Vercel）

1. 将前端代码推送到 GitHub 仓库（可与后端同仓库或分开）。
2. 在 Vercel 导入项目，设置构建命令（如 `npm run build` 或直接部署静态文件）。
3. 环境变量中配置后端 API 地址（如 `VITE_API_BASE=https://your-backend.onrender.com`）。
4. 每次推送自动部署。

### 9.3 域名

使用 Vercel 提供的子域名（如 `news.vercel.app`）或 Render 提供的子域名，无需购买域名。

## 10. 开发步骤（供 Qoder 参考）

1. **初始化项目结构**：创建 GitHub 仓库，包含 `backend/` 和 `frontend/` 文件夹。
2. **后端开发**：
   - 编写 `requirements.txt`：flask, flask-sqlalchemy, feedparser, requests, gunicorn
   - 创建 `app.py` 实现 API 接口
   - 创建 `models.py` 定义数据库模型
   - 创建 `crawler.py` 实现爬虫逻辑
   - 本地测试 API 和爬虫
3. **前端开发**：
   - 创建 `index.html`，引入 Vue 或原生 JS
   - 实现分类切换、排序切换、分页加载
   - 样式美化
4. **配置 GitHub Actions**：
   - 编写 `.github/workflows/crawler.yml` 定时运行爬虫
5. **部署**：
   - 将后端部署到 Render，前端部署到 Vercel
6. **测试上线**：验证每日自动更新和访问。

## 11. 注意事项

- **版权合规**：所有新闻只展示标题和摘要，并提供原文链接。在网站页脚添加免责声明，说明内容版权归原作者所有。
- **RSS 源维护**：定期检查源是否有效，如有失效及时替换。
- **爬虫频率**：每天一次，避免对源站造成压力。
- **数据库大小**：SQLite 适合小数据量，随着新闻增多，可定期清理一个月前的旧新闻（在爬虫中加入清理逻辑）。
- **免费额度**：Render 免费版每月 750 小时，足够；GitHub Actions 免费 2000 分钟/月；Vercel 免费版足够。注意不要超出。

## 12. 后续可扩展功能（非 MVP）

- 增加更多分类（如金融圈、娱乐圈）
- 接入搜索功能
- 用户收藏和阅读历史
- 个性化推荐
- 管理后台动态配置源和权重
