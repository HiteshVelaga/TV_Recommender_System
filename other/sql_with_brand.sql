-- With Brand
with diff_table
as
(
    select id,
        abs(cost-109132) diff_cost,
        abs(hdmi-4) diff_hdmi, 
        abs(quality-3) diff_quality,
        abs(ratings-5) diff_rating, 
        abs(size-65) diff_size, 
        abs(speaker-60) diff_speaker, 
        abs(usb-3) diff_usb
    from tv
    where brand='samsung'
) 
select tv.id, 
    tv.brand,
    tv.cost,
    tv.hdmi,
    quality_val.hd quality,
    tv.ratings,
    tv.size,
    tv.speaker,
    tv.usb,
    tv.buy_from,
    tv.img_url,
    sqrt(diff_hdmi*diff_hdmi + diff_rating*diff_rating + diff_size*diff_size + diff_speaker*diff_speaker + diff_usb*diff_usb + diff_cost*diff_cost) diff
from diff_table
join tv
on diff_table.id = tv.id
join quality_val
on tv.quality = quality_val.id
order by diff
limit 1;



-- {'brand': 'samsung',
--  'cost': 109132,
--  'hdmi': 4,
--  'quality': 'ultra hd 4k',
--  'rating': 5,
--  'size': 65,
--  'speaker': 60,
--  'usb': 3}
 
-- 4k - 3
-- full hd - 2
-- hd - 1
-- other = 0
