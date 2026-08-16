FROM python:3.13
WORKDIR /usr/local/app

# Copy in the source code
COPY src ./src
COPY scripts ./scripts
COPY data ./data

# Install the application dependencies
COPY pyproject.toml .
RUN pip install --no-cache-dir .

ENV ORACLE_PASSWORD="${ORACLE_PASSWORD}"
ENV ORACLE_USER="${ORACLE_USER}"
ENV WALLET_LOCATION="wallet"
ENV ORACLE_DSN="${ORACLE_DSN}"
ENV ENTSOE_API_KEY="${ENTSOE_API_KEY}"
ENV COUNTRY_CODE="${COUNTRY_CODE}"

ARG ENCRIPTING_PASSWORD
RUN mkdir -p wallet && \
    openssl enc -d -aes-256-cbc -pbkdf2 -in ./data/wallet.zip.enc -out wallet.zip -pass env:ENCRIPTING_PASSWORD && \
    unzip -q wallet.zip -d wallet
