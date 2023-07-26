#!/bin/bash
# Parameters: $1 = output file name, $2 = Blue agent, $3 = Red agent, $4 = number of episodes

# Remove the output file if it exists
if [ -f $1 ]; then
    rm $1
fi

# If the blue agent is not specified, use the defaults
if [ -z "$2" ]; then
    python3 test.py > $1
else
    # If the red agent is not specified, use the blue agent
    if [ -z "$3" ]; then
        python3 test.py -b $2 > $1
    else
        if [ -z "$4" ]; then
            python3 test.py -b $2 -r $3 > $1
        else
            # Else, use the blue and red agents specified
            python3 test.py -b $2 -r $3 -s $4 > $1
        fi
    fi
fi

# Copy the output to the visualisation folder
cp $1 visualisation/logs_to_vis

# Change directory to visualisation folder
cd visualisation

# Make the gif
python3 gif_maker.py logs_to_vis/$1

# Rename the img/results.gif to the name of the output file
mv img/results.gif img/$1.gif

# Change directory back to Tutorial folder
cd ..

# Open the gif
xdg-open visualisation/img/$1.gif


