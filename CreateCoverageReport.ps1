# -----------------------------------------
# Run tests and create code coverage report

# SPDX-FileCopyrightText: (c) 2028-2023 Siemens
# SPDX-License-Identifier: MIT
# -----------------------------------------

# 2021-12-20, T. Graf

poetry run coverage run -m pytest
poetry run coverage report -m --omit "*/site-packages/*.py"
poetry run coverage html --omit "*/site-packages/*.py"


# -----------------------------------
# -----------------------------------
