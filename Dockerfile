# ベースイメージ
FROM python:3.11-slim

# 作業ディレクトリ
WORKDIR /app

# 依存関係をコピーしてインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリ本体をコピー
COPY . .

# FastAPI起動（Uvicornを使用）
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
