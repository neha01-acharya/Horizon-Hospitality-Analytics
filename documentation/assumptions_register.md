# Assumptions Register

| ID | Assumption | Why needed | Validation / control |
|---|---|---|---|
| A01 | Exactly 3 hotels in each of 5 cities | Makes the 15-hotel scope balanced | Count hotels grouped by city |
| A02 | Approximately 1,500 rooms | Establishes inventory scale | Count rooms; report actual total |
| A03 | Each booking reserves one room | Keeps booking grain simple | One room_id per booking |
| A04 | At most one feedback submission per booking | Avoids duplicate weighting | Unique booking_id in feedback |
| A05 | Hotels and rooms operate throughout the analysis period | Avoids modelling opening/closure histories in this version | Document scope; maintenance tracked daily |
| A06 | Checkout date is exclusive | Standard hotel-stay convention | Validate room-night dates against [check-in, checkout) |
| A07 | All room revenue is accommodation revenue | Keeps ADR and RevPAR definitions consistent | Revenue source and calculation checks |
| A08 | Maintenance rooms are not sellable | Defines available-room denominator | Check is_sellable and is_occupied logic |
| A09 | Internal transfers are not company exits | Prevents inflated employee turnover | Validate separation_type and employment periods |
| A10 | Employment intervals are hire-inclusive and exit-exclusive | Supports daily headcount | Date-boundary validation |
| A11 | All data is synthetic | Assignment requires generated sample data | Disclose in reports and dashboard |
| A12 | 2026 dates after the generation run date are simulated future records | Five-year period ends 2026-12-31 | Label in documentation and inference |
| A13 | Power BI Service access is blocked by organisation policy at present | Dashboard route is not yet available | Reassess approved access route before dashboard phase |
| A14 | MySQL local_infile is disabled | Avoids changing server import security settings | Use Python batch loading initially |

Assumptions are not original assignment requirements. If an assumption changes, update this register, the data dictionary, schema and validation plan before implementation.
