from hashlib import sha3_512
import pandas as pd
import os
import win32com.client as win32



def elegant_time(time) -> str:
    if int(time) == time:
        return str(int(time)).strip() + " Hours"
    hours = int(time)
    minutes = time - hours
    minutes_simplified = str(int(minutes * 60))
    return f"{hours}:{minutes_simplified} Hours"


def unelegant_time(time: str) -> float:
    """H:MM -> int"""
    hour, minutes = time.split(":")
    minutes = int(minutes) / 60
    return int(hour) + minutes


def hash_sha(password):
    sha = sha3_512()
    sha.update(password.encode('utf-8'))
    hashed_password = sha.hexdigest()
    return hashed_password


def student_report(data: dict[str, dict[str, float]], save=True, output="output.xlsx"):
    headers = ["Name"]
    first_name = list(data.keys())[0]
    headers.extend(data[first_name].keys())
    print(headers)
    result = {k: [] for k in headers}
    for name, materials in data.items():
        result['Name'].append(name)
        for k, v in materials.items():
            if v >= 15:
                n = "فصل نهائي"
            elif v >= 10:
                n = "فصل اولي"
            elif v >= 5:
                n = "أنذار"
            elif v >= 3:
                n = "تنبيه"
            else:
                n = "لا يوجد حالة"
            result[k].append(n)
    data = pd.DataFrame(result)
    if save:
        data.to_excel(output, "Report", index=False)
    return data


def sending_email(emails, file='output.xlsx'):

    OutLook_App = win32.Dispatch('Outlook.Application')
    Outlook_NameSpace = OutLook_App.GetNameSpace('MAPI')

    MailItem = OutLook_App.CreateItem(0)
    MailItem.Subject = 'Update From Automated Attendance and Absence System'
    MailItem.BodyFormat = 1
    MailItem.Body = "Good Evening,\n" \
                    "This Is The Latest Version Of The Students Absence Ratio,\n" \
                    "Kindly Open The File And View It In Your Device,\n\n" \
                    "Best Regards,\n" \
                    "University of Information Technology and Communications."
    MailItem.To = emails
    MailItem.Attachments.Add(os.path.join(os.getcwd(), file))
    MailItem.Display()