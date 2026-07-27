# Source Data Overview

## Purpose

This document summarizes the source files used for the Healthcare Staffing Metrics project.

## Main Source

Primary file:

- `PBJ_Daily_Nurse_Staffing_Q2_2024.csv`

This file contains daily provider-level staffing hours and census information.

## Supporting Files

Supporting nursing home files provide facility details, quality measures, provider ratings, survey information, ownership, penalties, and other context.

## Early Assumption

The master PBJ staffing file will drive the main staffing metrics. Supporting files will be joined when they provide useful facility, rating, bed count, or quality information.

## Key Join Field

Expected provider key:

- `PROVNUM`

This will be validated during source profiling.
