proc import datafile="/home/u44593168/timesheets_sas.csv"
		out=work.raw
		dbms=csv
		replace;
	getnames=no;
run;

data work.clean;
	set work.raw;
	project = VAR1;
	date = VAR2;
	hours = VAR3;
	drop VAR1 VAR2 VAR3;
run;

proc sort data=work.clean;
	by project date;
run;

proc timeseries data=work.clean
		out=work.final;
	by project;
	id date interval=day accumulate=total;
	var hours;
run;

