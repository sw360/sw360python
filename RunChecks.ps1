# ---------------------------------------------
# Run quality checks
#
# SPDX-FileCopyrightText: (c) 2019-2023 Siemens
# SPDX-License-Identifier: MIT
# ---------------------------------------------

# 2024-05-10, T. Graf

Write-Host "flake8 ..."
poetry run flake8

Write-Host "markdownlint ..."
npx -q markdownlint-cli *.md

Write-Host "isort ..."
poetry run isort .

Write-Host "mypy ..."
poetry run mypy .

Write-Host "codespell ..."
poetry run codespell .

Write-Host "done."


# -----------------------------------
# -----------------------------------
