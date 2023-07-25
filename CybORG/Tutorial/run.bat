@REM parameters: %1 = output file name, %2 = Blue agent, %3 = Red agent %4 = number of episodes

@REM Remove the output file if it exists
if exist %1 del %1

@REM If the blue agent is not specified, use the defaults
if "%2"=="" (
    python test.py > %1
) else (
    @REM If the red agent is not specified, use the blue agent
    if "%3"=="" (
        python test.py -b %2 > %1
    ) else (
        if "%4"=="" (
            python test.py -b %2 -r %3 > %1
        ) else (
            @REM Else, use the blue and red agents specified
            python test.py -b %2 -r %3 -s %4 > %1
        )
    )
)

@REM Copy the output to the visualisation folder
copy %1 visualisation\logs_to_vis

@REM Change directory to visualisation folder
cd visualisation

@REM Make the gif
python .\gif_maker.py .\logs_to_vis\%1

@REM Rename the img\results.gif to the name of the output file
move .\img\results.gif .\img\%1.gif

@REM Change directory back to Tutorial folder
cd ..

@REM Open the gif
start .\visualisation\img\%1.gif