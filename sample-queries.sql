-- Check normalization of sky maps (everything should come out to 1)
SELECT
localization_id,
3.63319635e-18 * sum(
    probdensity * (upper(nested_range) - lower(nested_range))
) AS prob
FROM localization_tile GROUP BY localization_id;


-- Check area of tiles (should be about 47 deg2)
SELECT 1.19270801e-14 * sum(upper(nested_range) - lower(nested_range))
FROM field_tile GROUP BY telescope_name, field_id
LIMIT 10;


-- Calculate contained probability for each field
SELECT
localization_id, field_id,
3.63319635e-18 * sum(
    probdensity * (
        upper(localization_tile.nested_range * field_tile.nested_range) -
        lower(localization_tile.nested_range * field_tile.nested_range)
    )
) AS prob
FROM localization_tile INNER JOIN field_tile
ON localization_tile.nested_range && field_tile.nested_range
GROUP BY localization_id, field_id, telescope_name
ORDER BY prob DESC
LIMIT 10;
