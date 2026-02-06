# GitHub 新手最短上手（你可以照着做）

## 方式1：网页创建仓库（最稳）

1. 打开 `https://github.com/new`
2. Repository name 填：`codex-cn-patch-guide`
3. 勾选 `Public`
4. 不用勾选 README（本地已有）
5. 点击 `Create repository`
6. 复制新仓库地址（例如 `https://github.com/<yourname>/codex-cn-patch-guide.git`）

创建后在本地执行：

```bash
cd /Users/zyh/Downloads/appUI
git add .
git commit -m "docs: add codex desktop chinese patch guide + publish kit"
git branch -M main
git remote add origin <你的仓库URL>
git push -u origin main
```

如果推送时要求登录：
- 用户名：你的 GitHub 用户名
- 密码：使用 GitHub Personal Access Token（不是账号密码）

---

## 方式2：安装 gh 命令行（后续更方便）

```bash
brew install gh
gh auth login
```

登录后可一条命令创建并推送：

```bash
cd /Users/zyh/Downloads/appUI
gh repo create codex-cn-patch-guide --public --source=. --remote=origin --push
```
