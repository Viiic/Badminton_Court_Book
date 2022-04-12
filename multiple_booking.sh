#/bin/bash

rm /Users/WeifanWang/workspace/Badminton_Court_Book/debug_log_*.txt
rm screenshot_*

hour=$1
if [[ -z "$1" ]]; then
    echo "Please specify the booking hour"
    exit 1
fi
name1="wang"
name2="he"
name3="liu"
name4="yuan"
name5="cheng"

python3 cba_court_reg.py --hour ${hour} --name ${name1} &
python3 cba_court_reg.py --hour ${hour} --name ${name2} &
python3 cba_court_reg.py --hour ${hour} --name ${name3} &
python3 cba_court_reg.py --hour ${hour} --name ${name4} &
python3 cba_court_reg.py --hour ${hour} --name ${name5} 

wait
