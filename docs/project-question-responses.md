# Project Question Responses

## Summary

The project instructions include several business questions. The available data supports some of them directly, supports some partially, and does not support others for the first build.

## Question 1: What is the relationship between nurse staffing levels and hospital occupancy rates?

Status: Partially answered.

The project compares staffing coverage with bed utilization.

Staffing coverage is measured with total nurse hours per resident day and RN hours per resident day. Bed utilization is estimated with average daily census divided by certified bed count.

This can show whether facilities with higher bed utilization also have higher or lower staffing coverage. It does not prove cause and effect.

## Question 2: Which hospitals have the highest overtime hours for nurses?

Status: Not answered from the available data.

The PBJ staffing file includes worked hours by staff type. It does not include scheduled hours or overtime-specific hour fields.

The project can show facilities with the highest total nurse hours and highest contract staff ratio, but it should not label those values as overtime.

## Question 3: What are the average staffing levels by state and hospital type?

Status: Partially answered.

The project calculates average staffing levels by state using the gold metrics table.

Hospital type depends on the supporting provider fields available. If provider type is populated, the same gold table can group staffing metrics by state and provider type. If provider type is not reliable, ownership type can be used as the facility grouping instead.

## Question 4: What trends can you identify in patient length of stay over time?

Status: Not answered from the first build.

Length of stay needs admission and discharge dates or a validated ALOS field. The PBJ staffing file does not provide those fields.

The first build focuses on staffing, census, bed utilization, and contract staffing metrics instead.

## Final Position

The final metric set favors calculations that can be traced to available source columns. I did not force metrics that the current data does not support.
