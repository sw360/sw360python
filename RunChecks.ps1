# ---------------------------------------------
# Run quality checks
#
# SPDX-FileCopyrightText: (c) 2019-2023 Siemens
# SPDX-License-Identifier: MIT
# ---------------------------------------------

# 2022-07-15, T. Graf

poetry run flake8
npx -q markdownlint-cli *.md


# -----------------------------------
# -----------------------------------
