# 海上修机师知识库

这是 `nuist-engineer-lion/docs` 的 Zensical 文档站源码。内容由本仓库的迁移脚本从 `../old-docs` 生成，并在生成过程中做目录重组、飞书导出标签转换和公开发布前的去敏处理。

## 开发

```bash
uv sync
uv run python scripts/migrate_old_docs.py
uv run python scripts/check_content.py
uv run python -m zensical build --clean
```

本地预览：

```bash
uv run python -m zensical serve
```

## 部署

Vercel 使用 `vercel.json` 中的构建配置：

- install: install `uv` if missing, then `uv sync --frozen`
- build: `uv run python -m zensical build --clean`
- output: `site`
