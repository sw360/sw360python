# ------------------
# Run quality checks
# ------------------

# 2022-07-15, T. Graf

poetry run flake8
npx -q markdownlint-cli *.md


# -----------------------------------
# -----------------------------------
