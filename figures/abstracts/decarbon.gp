set terminal cairolatex pdf monochrome size 22cm,7.1cm font ",9"
set output "decarbon-plot.tex"
set datafile separator comma
set datafile columnheaders
unset key
unset grid
set border 3 linewidth 1.2 linecolor rgb "black"
set tics out nomirror scale .3
set format x "%.0f"
set format y "%.0f"
set xrange [2024.5:2037.4]
set xtics (2025,2030,2035)
set xlabel "Modeled transition year" offset 0,-.5
set style line 1 linecolor rgb "black" linewidth 1.4 dashtype 1 pointtype 5 pointsize .65
set style line 2 linecolor rgb "black" linewidth 1.4 dashtype 2 pointtype 9 pointsize .65
set style line 3 linecolor rgb "black" linewidth 1.4 dashtype 3 pointtype 7 pointsize .65
set style line 4 linecolor rgb "black" linewidth 1.4 dashtype 4 pointtype 13 pointsize .65
set multiplot layout 1,2
set lmargin at screen .13
set rmargin at screen .44
set bmargin at screen .24
set tmargin at screen .84
set yrange [0:3600]
set ytics 1000
unset title
set ylabel "Tonnes of carbon dioxide equivalent" offset -2.3,0
set arrow 1 from graph 0, first 2173 to graph 1, first 2173 nohead dashtype 5 linewidth 1.1 linecolor rgb "black"
set label 1 "Diesel reference" at graph .97, first 2300 right
plot for [i=2:5] "../../../figures/abstracts/transition-results.csv" using 1:(column(i)) with linespoints linestyle (i-1), \
 for [i=2:5] "" using ($1==2035?$1:1/0):(column(i)):(sprintf("%.0f",column(i))) with labels left offset 1.3,0 textcolor rgb "black"
unset arrow 1
unset label 1
set lmargin at screen .655
set rmargin at screen .965
set yrange [-500:3500]
set ytics 1000
unset title
set ylabel "Return on investment (percent)" offset -2.0,0
set arrow 1 from graph 0, first 0 to graph 1, first 0 nohead dashtype 5 linewidth 1.1 linecolor rgb "black"
plot for [i=6:9] "../../../figures/abstracts/transition-results.csv" using 1:(column(i)) with linespoints linestyle (i-5), \
 for [i=6:9] "" using ($1==2035?$1:1/0):(column(i)):(sprintf("%.0f",column(i))) with labels left offset 1.3,0 textcolor rgb "black"
unset multiplot
set output
