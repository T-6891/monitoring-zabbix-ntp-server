[# NTP Server Monitoring with Zabbix

This guide will help you set up a Python script that checks the availability and response time of an NTP server and integrates it with Zabbix for monitoring.

## Prerequisites

- Python 3 installed
- Zabbix server and Zabbix agent 2 installed and connected
- NTP server for monitoring

## Step 1: Install Required Python Libraries

Our script uses the `ntplib` Python library, so first, you need to install this library. Run the following command:

```bash
pip install ntplib
```

## Step 2: Setup the Python Script

Create a new Python script, for example `ntp_check.py`, and paste the following code:

```python
import time
from ntplib import NTPClient, NTPException
import sys

def check_ntp_server(server_address):
    client = NTPClient()

    try:
        start_time = time.time()
        response = client.request(server_address)
        end_time = time.time()
        # Return the response time
        return end_time - start_time
    except NTPException:
        # Return error code 1
        return 1

if __name__ == "__main__":
    response_time = check_ntp_server('192.168.62.75')
    if response_time == 1:
        print(1) # Server is unavailable
        sys.exit(1)
    else:
        print(0) # Server is available
        print(response_time) # Response time
```

Don't forget to replace `'192.168.62.75'` with the IP address of your NTP server.

## Step 3: Configure Zabbix Agent

Now you need to tell the Zabbix agent to use this script. Open the Zabbix agent configuration file (usually located at `/etc/zabbix/zabbix_agentd.conf` or `/etc/zabbix/zabbix_agent2.conf`) and add the following lines:

```
UserParameter=ntp.check,/path/to/your/ntp_check.py
UserParameter=ntp.response.time,/path/to/your/ntp_check.py
```

Replace `/path/to/your/ntp_check.py` with the actual path to your Python script.

After you've made these changes, save the configuration file and restart the Zabbix agent to apply the changes. Depending on your system, the command to restart the Zabbix agent might look like this:

```bash
sudo systemctl restart zabbix-agent
```

## Step 4: Add Items in Zabbix Server

Log in to your Zabbix server's web interface, go to `Configuration -> Hosts`, and click on the host you want to monitor. 

Go to `Items` and click `Create Item`. 

- For the first item, the `Name` could be "NTP Server Availability", the `Key` should be "ntp.check", the `Type` should be "Zabbix agent", and the `Type of information` should be "Numeric (unsigned)". 

- For the second item, the `Name` could be "NTP Server Response Time", the `Key` should be "ntp.response.time", the `Type` should be "Zabbix agent", and the `Type of information` should be "Numeric (float)".

After you've created these items, Zabbix will start monitoring the availability and response time of your NTP server.

## Note

When the script is run via the Zabbix Agent, it will execute with the same permissions as the agent. Ensure that the agent has the necessary permissions to execute the script and read its output.

## Conclusion

You've now set up monitoring of an NTP server's availability and response time using a Python script and Zabbix. This will give you insight into your NTP server's performance and alert you 
