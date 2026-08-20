FROM python:3.13
WORKDIR /usr/local/app

# Copy in the source code
COPY src ./src
COPY scripts ./scripts
COPY data ./data
COPY dashboard.py .
COPY .streamlit ./.streamlit

# Install the application dependencies
COPY pyproject.toml .
RUN pip install .

ENV ORACLE_PASSWORD="${ORACLE_PASSWORD}"
ENV ORACLE_USER="${ORACLE_USER}"
ENV WALLET_LOCATION="wallet"
ENV ORACLE_DSN="${ORACLE_DSN}"
ENV ENTSOE_API_KEY="${ENTSOE_API_KEY}"
ENV COUNTRY_CODE="${COUNTRY_CODE}"
ENV WALLET_ENCRIPTING_PASSWORD="${WALLET_ENCRIPTING_PASSWORD}"