# test script that implements LiNan's LC matlab code. This is in preparation for the web version

# prep environment before calling:  TMPDIR=/Sastemp or /tmp

# how called:
#  --restore  (store all functions, etc. in .Rdata in the project folder to minimize processing of them);

#  --gui=none

# BATCH = --restore --save --no-readline --gui=none  + redirected I/O

# Screen LC_data  ;

  # The web script has created a 'tmpdir' subdirectory name which will be used for all the calculations
  # and removed once the application exits (during the cleanup screen)

  # file upload occurs via perl and CGI::Application    The data file is placed into the CWD and is
  # called 'lcdata.txt'  

  # filechecking
  #inhdl=file("lcdata.txt",open="r");

  # for now, lcdata.txt is just numbers; we add here a routine which tries alternative ways of reading the file (test for text on the first line, test for comma separated values, and does the right thing)
  # 

  f.ReadLCData<-function(inhandle){
    # needs modification for robustness
    # FUTURE option of getting 
    LCdata=read.table('lcdata.txt');
    agelist=c(0,1,seq(5,85,5));
    yrlist = 1950:1994;
    return(list(data=LCdata,ages=agelist,yrs=yrlist));
  };

  LCdata=f.ReadLCData();

  f.TestLCData<- function(myLCdata){
    # routine that performs regularity checks on data, e.g. Mx in range
    if(problemdetected){ stop("bad data")}
  };

  f.TestLCData(LCdata);

  f.WriteParmsFromData <- function(myLCdata){
    # if datafile 
  # possibly print summary and/or store summary of parameter in a file for use in LC_params
  #  LC_Params.txt
  #   AgeGroups: 0 1 5 10 15 20 25 30 35 40 45 50 55 60 65 70 75 80 85
  #   Years: 1950 1994

  # end R session for this screen; this leaves a copy of the read data
  # in the tmpdir location for subsequent access by further screens


# Screen LC_params

  # parameters are communicated to R in the crudest way: each parameter is stored
  # in a distinct file with the same name as the parameter.  This means no special parsing
  #

  # read values from each file
  # File and parameter name        Example value
  # ----------------------         -------------
  #  Title                         My meaningful title
  #  AgeGroups                     0 1 5 10 15 20 25 30 35 40 45 50 55 60 65 70 75 80 85
  #  YearsOnRecordStart            1950
  #  YearsOnRecordEnd              1994
  #  YearsToForecast               60
  #  Trajectories                  100
  #  SaveMxForecasts               1

  f.readparams<-function(){
    # read and save (globally) the parameter values from their container files
    Title <<- scan('Title',what=character(0),n=1);
    AgeGroups <<- scan('AgeGroups',what=numeric(0));
    YearsOnRecordStart  <<- scan('YearsOnRecordStart',what=numeric(0),n=1);
    YearsOnRecordEnd <<- scan('YearsOnRecordEnd',what=numeric(0),n=1);
    YearsToForecast <<- scan('YearsToForecast',what=numeric(0),n=1);
    Trajectories <<- scan('Trajectories',what=numeric(0),n=1);
    SaveMxForecasts <<- scan('SaveMxForecasts',what=numeric(0),n=1);
  };


# Screen LC_cleanup
  
