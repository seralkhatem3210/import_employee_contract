try:
    try: 
        x = ( categories.GROSS / 30 )
        Late = (x * worked_days.late.number_of_days ) + (( x / 8 ) * worked_days.late.number_of_hours)+ ((x/8/60)*worked_days.late.number_of_minutes)
    except:
        Late = 0
    try: 
        y= ( categories.GROSS / 30 )
        Leave = (y * worked_days.abs.number_of_days ) + (( y / 8 ) * worked_days.abs.number_of_hours)+ ((y/8/60)*worked_days.abs.number_of_minutes)
    except:
        Leave = 0
        
    try: 
        z = ( categories.GROSS / 30 )
        Unpaid = ( z * worked_days.LEAVE90.number_of_days ) + (( z / 8 ) * worked_days.LEAVE90.number_of_hours)+ ((z/8/60)*worked_days.LEAVE90.number_of_minutes)
    except:
        Unpaid = 0
            
    try: 
        xy = ( categories.GROSS / 30 )
        Unpaid99 = (xy * worked_days.leave99.number_of_days ) + (( xy / 8 ) * worked_days.leave99.number_of_hours)+ ((xy /8/60)*worked_days.leave99.number_of_minutes)
    except:
        Unpaid99 = 0
        
    result = Late + Leave + Unpaid  + Unpaid99
except:
    result = 0


try:
    x= 0
    result =0

except:
    result = 0
                    # Available variables:
                    #----------------------
                    # payslip: object containing the payslips
                    # employee: hr.employee object
                    # contract: hr.contract object
                    # rules: object containing the rules code (previously computed)
                    # categories: object containing the computed salary rule categories (sum of amount of all rules belonging to that category).
                    # worked_days: object containing the computed worked days.
                    # inputs: object containing the computed inputs.

                    # Note: returned value have to be set in the variable 'result'

                    # result = contract.wage * 0.10    