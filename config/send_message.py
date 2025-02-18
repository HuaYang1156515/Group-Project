from services import dbText

def sendmessage(subject,recipient,sender,content):
    
   sql = f"""INSERT INTO messagebox (subject, recipient,sender,content,status) VALUES ('{subject}','{recipient}','{sender}','{content}','1')"""
   dbText.db_execute(sql)
   return True

def update_message(message_id):
   sql = f"""update messagebox set status = '0' where id = '{message_id}'"""
   dbText.db_execute(sql)
   return True


