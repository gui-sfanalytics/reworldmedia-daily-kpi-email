FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Assure-toi que playwright est installé (requis même si requirements le fait déjà)
RUN python -c "import playwright; print('playwright OK')"

# Installer les navigateurs au build time
RUN playwright install --with-deps chromium 

ENV PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

COPY . .

CMD ["python", "main.py"]