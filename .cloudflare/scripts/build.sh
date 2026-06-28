# Cloudflare Pages 构建脚本
# 用于 Cloudflare Pages 控制台配置「构建命令」时引用
# 也可本地执行验证：bash .cloudflare/scripts/build.sh
set -e

echo "==> 安装 Python 依赖（MkDocs Material）"
pip install --no-cache-dir \
  "mkdocs>=1.6" \
  "mkdocs-material>=9.5" \
  "mkdocs-material-extensions>=1.3" \
  "pymdown-extensions>=10.7"

echo "==> 构建文档站到 site/ 目录"
mkdocs build --clean

echo "==> 构建完成，产物在 site/"
ls -la site/ | head -10
