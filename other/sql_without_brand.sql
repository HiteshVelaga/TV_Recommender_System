-- Without Brand
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
) 
select tv.id, 
    tv.brand,
    tv.cost,
    tv.hdmi,
    tv.quality,
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
limit 3;
