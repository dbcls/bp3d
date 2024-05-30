composite -gravity southeast messagebox_warning.png primitive.png -quality 95 w_primitive.png
composite -gravity southeast Warning_h.gif primitive.png -quality 95 w_primitive.png

mogrify -transparent white -geometry 10x10 -sharpen 0.7 error.png

composite -gravity southeast error.png primitive.png -quality 95 warning_primitive.png
composite -gravity southeast error.png 005.png -quality 95 warning_005.png
composite -gravity southeast error.png 015.png -quality 95 warning_015.png
composite -gravity southeast error.png 025.png -quality 95 warning_025.png
composite -gravity southeast error.png 035.png -quality 95 warning_035.png
composite -gravity southeast error.png 045.png -quality 95 warning_045.png
composite -gravity southeast error.png 050.png -quality 95 warning_050.png
composite -gravity southeast error.png 055.png -quality 95 warning_055.png
composite -gravity southeast error.png 065.png -quality 95 warning_065.png
composite -gravity southeast error.png 075.png -quality 95 warning_075.png
composite -gravity southeast error.png 085.png -quality 95 warning_085.png
composite -gravity southeast error.png 095.png -quality 95 warning_095.png
composite -gravity southeast error.png 099.png -quality 95 warning_099.png
composite -gravity southeast error.png 100.png -quality 95 warning_100.png

composite -gravity southeast error.png end_parts.png -quality 95 warning_end_parts.png
composite -gravity southeast error.png route_parts.png -quality 95 warning_route_parts.png
